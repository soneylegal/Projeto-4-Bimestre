import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import User, Project, AuditLog
from ..schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from ..auth_utils import get_current_user, require_role

router = APIRouter(prefix="/api/projects", tags=["projects"])

async def log_audit(db: AsyncSession, user_id: uuid.UUID, action: str, target_id: str, details: dict = None):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        target_type="project",
        target_id=target_id,
        details=details
    )
    db.add(audit)
    await db.commit()

@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista os projetos de acordo com as permissões do perfil do usuário."""
    if current_user.role in ["admin", "coordinator"]:
        result = await db.execute(
            select(Project)
            .options(selectinload(Project.advisor), selectinload(Project.members), selectinload(Project.tasks))
        )
        projects = result.scalars().all()
    elif current_user.role == "advisor":
        result = await db.execute(
            select(Project)
            .where(Project.advisor_id == current_user.id)
            .options(selectinload(Project.advisor), selectinload(Project.members), selectinload(Project.tasks))
        )
        projects = result.scalars().all()
    elif current_user.role == "student":
        result = await db.execute(
            select(Project)
            .join(Project.members)
            .where(User.id == current_user.id)
            .options(selectinload(Project.advisor), selectinload(Project.members), selectinload(Project.tasks))
        )
        projects = result.scalars().all()
    else:
        projects = []

    # Calcula is_overdue para cada tarefa
    for p in projects:
        for t in p.tasks:
            t.is_overdue = t.due_date is not None and t.due_date < datetime.utcnow() and t.status != "done"

    return projects

@router.get("/{id}", response_model=ProjectResponse)
async def get_project(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna detalhes de um projeto específico."""
    result = await db.execute(
        select(Project)
        .where(Project.id == id)
        .options(selectinload(Project.advisor), selectinload(Project.members), selectinload(Project.tasks))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    # Validação de acesso
    has_access = False
    if current_user.role in ["admin", "coordinator"]:
        has_access = True
    elif current_user.role == "advisor" and project.advisor_id == current_user.id:
        has_access = True
    elif current_user.role == "student" and any(m.id == current_user.id for m in project.members):
        has_access = True

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não possui vínculo com este projeto."
        )

    # Calcula is_overdue para cada tarefa
    for t in project.tasks:
        t.is_overdue = t.due_date is not None and t.due_date < datetime.utcnow() and t.status != "done"

    return project

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "coordinator", "advisor"]))
):
    """Cria um novo projeto. Requer perfil de orientador ou superior e no mínimo 1 aluno."""
    if not project_in.member_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É obrigatório associar pelo menos 1 aluno participante ao projeto."
        )

    # Valida membros existentes e com perfil 'student'
    result = await db.execute(select(User).where(User.id.in_(project_in.member_ids)))
    db_members = result.scalars().all()
    if len(db_members) != len(set(project_in.member_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um ou mais IDs de alunos fornecidos são inválidos."
        )
    
    for m in db_members:
        if m.role != "student":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O usuário {m.name} não possui papel de aluno ('student')."
            )

    # Cria o projeto
    new_project = Project(
        title=project_in.title,
        description=project_in.description,
        repository_url=project_in.repository_url,
        advisor_id=current_user.id
    )
    new_project.members = db_members
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    # Registra auditoria
    await log_audit(
        db, 
        user_id=current_user.id, 
        action="create_project", 
        target_id=str(new_project.id),
        details={"title": new_project.title}
    )

    # Recarrega relações
    result = await db.execute(
        select(Project)
        .where(Project.id == new_project.id)
        .options(selectinload(Project.advisor), selectinload(Project.members), selectinload(Project.tasks))
    )
    return result.scalars().first()

@router.put("/{id}", response_model=ProjectResponse)
async def update_project(
    id: uuid.UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "coordinator", "advisor"]))
):
    """Atualiza dados do projeto. Apenas o orientador responsável ou coordenador/admin."""
    result = await db.execute(
        select(Project)
        .where(Project.id == id)
        .options(selectinload(Project.members))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    # Apenas o orientador responsável, admin ou coordinator podem atualizar
    if current_user.role == "advisor" and project.advisor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não é o orientador deste projeto."
        )

    if not project_in.member_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É obrigatório associar pelo menos 1 aluno participante ao projeto."
        )

    # Valida membros existentes e com perfil 'student'
    result_users = await db.execute(select(User).where(User.id.in_(project_in.member_ids)))
    db_members = result_users.scalars().all()
    if len(db_members) != len(set(project_in.member_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um ou mais IDs de alunos fornecidos são inválidos."
        )
    
    for m in db_members:
        if m.role != "student":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O usuário {m.name} não possui papel de aluno ('student')."
            )

    # Atualiza
    project.title = project_in.title
    project.description = project_in.description
    project.repository_url = project_in.repository_url
    project.members = db_members
    await db.commit()

    # Registra auditoria
    await log_audit(
        db, 
        user_id=current_user.id, 
        action="update_project", 
        target_id=str(project.id),
        details={"title": project.title}
    )

    # Recarrega relações
    result = await db.execute(
        select(Project)
        .where(Project.id == project.id)
        .options(selectinload(Project.advisor), selectinload(Project.members), selectinload(Project.tasks))
    )
    return result.scalars().first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "coordinator", "advisor"]))
):
    """Exclui o projeto do sistema."""
    result = await db.execute(select(Project).where(Project.id == id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    if current_user.role == "advisor" and project.advisor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não é o orientador deste projeto."
        )

    await db.delete(project)
    await db.commit()

    # Registra auditoria
    await log_audit(
        db, 
        user_id=current_user.id, 
        action="delete_project", 
        target_id=str(id),
        details={"title": project.title}
    )
