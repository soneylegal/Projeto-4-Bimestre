import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import User, Project, Task, AuditLog
from ..schemas import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from ..auth_utils import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

async def log_audit(db: AsyncSession, user_id: uuid.UUID, action: str, target_id: str, details: dict = None):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        target_type="task",
        target_id=target_id,
        details=details
    )
    db.add(audit)
    await db.commit()

async def verify_project_access(db: AsyncSession, project_id: uuid.UUID, user: User) -> Project:
    """Verifica se o usuário possui acesso ao projeto (orientador ou membro)."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.members))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    # Acesso total para admin/coordinator
    if user.role in ["admin", "coordinator"]:
        return project

    # Acesso se for o orientador do projeto
    if user.role == "advisor" and project.advisor_id == user.id:
        return project

    # Acesso se for membro (aluno) do projeto
    if user.role == "student" and any(m.id == user.id for m in project.members):
        return project

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso negado. Você não possui vínculo com este projeto."
    )

@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista as tarefas de um projeto específico."""
    project = await verify_project_access(db, project_id, current_user)
    
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project.id)
    )
    tasks = result.scalars().all()

    # Calcula is_overdue
    for t in tasks:
        t.is_overdue = t.due_date is not None and t.due_date < datetime.utcnow() and t.status != "done"

    return tasks

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria uma tarefa para o projeto especificado."""
    project = await verify_project_access(db, project_id, current_user)

    # Se for atribuído a alguém, valida se é membro do projeto
    if task_in.assigned_to:
        if not any(m.id == task_in.assigned_to for m in project.members):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O responsável designado deve ser um aluno membro do projeto."
            )

    new_task = Task(
        project_id=project.id,
        title=task_in.title,
        description=task_in.description,
        status="todo",
        assigned_to=task_in.assigned_to,
        due_date=task_in.due_date
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Auditoria
    await log_audit(db, current_user.id, "create_task", str(new_task.id), {"title": new_task.title})

    new_task.is_overdue = new_task.due_date is not None and new_task.due_date < datetime.utcnow() and new_task.status != "done"
    return new_task

@router.put("/{id}", response_model=TaskResponse)
async def update_task(
    id: uuid.UUID,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza os detalhes de uma tarefa."""
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")

    # Verifica acesso ao projeto da tarefa
    project = await verify_project_access(db, task.project_id, current_user)

    # Se for atribuído a alguém, valida se é membro do projeto
    if task_in.assigned_to:
        if not any(m.id == task_in.assigned_to for m in project.members):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O responsável designado deve ser um aluno membro do projeto."
            )

    task.title = task_in.title
    task.description = task_in.description
    task.status = task_in.status
    task.assigned_to = task_in.assigned_to
    task.due_date = task_in.due_date
    await db.commit()

    # Auditoria
    await log_audit(db, current_user.id, "update_task", str(task.id), {"title": task.title})

    task.is_overdue = task.due_date is not None and task.due_date < datetime.utcnow() and task.status != "done"
    return task

@router.patch("/{id}/status", response_model=TaskResponse)
async def update_task_status(
    id: uuid.UUID,
    status_in: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Move/atualiza o status de uma tarefa no Kanban."""
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")

    # Verifica acesso ao projeto
    await verify_project_access(db, task.project_id, current_user)

    old_status = task.status
    task.status = status_in.status
    await db.commit()

    # Auditoria
    await log_audit(
        db, 
        current_user.id, 
        "patch_task_status", 
        str(task.id), 
        {"title": task.title, "old_status": old_status, "new_status": task.status}
    )

    task.is_overdue = task.due_date is not None and task.due_date < datetime.utcnow() and task.status != "done"
    return task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exclui uma tarefa."""
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada.")

    # Verifica acesso ao projeto
    await verify_project_access(db, task.project_id, current_user)

    await db.delete(task)
    await db.commit()

    # Auditoria
    await log_audit(db, current_user.id, "delete_task", str(id), {"title": task.title})
