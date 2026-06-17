import os
import uuid
from datetime import datetime
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import User, Project, Submission, AuditLog
from ..schemas import SubmissionResponse, SubmissionEvaluate
from ..auth_utils import get_current_user, require_role

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

async def log_audit(db: AsyncSession, user_id: uuid.UUID, action: str, target_id: str, details: dict = None):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        target_type="submission",
        target_id=target_id,
        details=details
    )
    db.add(audit)
    await db.commit()

def check_project_access(project: Project, user: User) -> bool:
    if user.role in ["admin", "coordinator"]:
        return True
    if user.role == "advisor" and project.advisor_id == user.id:
        return True
    if user.role == "student" and any(m.id == user.id for m in project.members):
        return True
    return False

@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    project_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Realiza o upload de uma entrega para um projeto, gerando uma nova versão."""
    # 1. Valida se o projeto existe
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.members), selectinload(Project.advisor))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    # 2. Valida acesso do usuário ao projeto
    if not check_project_access(project, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não possui vínculo com este projeto."
        )

    # 3. Valida tamanho do arquivo (limite 50 MB)
    content = await file.read(50 * 1024 * 1024 + 1)
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="O arquivo não pode exceder o limite de 50 MB."
        )
    await file.seek(0)

    # 4. Cria o diretório de uploads do projeto se não existir
    upload_dir = os.path.join("uploads", str(project_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # 5. Salva o arquivo no disco
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 6. Calcula a próxima versão incremental para este projeto
    result_versions = await db.execute(
        select(Submission.version).where(Submission.project_id == project_id)
    )
    versions = result_versions.scalars().all()
    next_version = max(versions) + 1 if versions else 1

    # 7. Cria a submissão no banco de dados
    new_submission = Submission(
        project_id=project_id,
        version=next_version,
        file_path=file_path,
        filename=file.filename,
        uploader_id=current_user.id,
        status="pending"
    )
    db.add(new_submission)
    await db.commit()
    await db.refresh(new_submission)

    # 8. Registra no log de auditoria
    await log_audit(
        db,
        user_id=current_user.id,
        action="create_submission",
        target_id=str(new_submission.id),
        details={"project_id": str(project_id), "filename": file.filename, "version": next_version}
    )

    # Recarrega uploader
    result_loaded = await db.execute(
        select(Submission)
        .where(Submission.id == new_submission.id)
        .options(selectinload(Submission.uploader))
    )
    return result_loaded.scalars().first()

@router.get("/{project_id}", response_model=list[SubmissionResponse])
async def list_submissions(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista o histórico de entregas (submissões) de um projeto."""
    # 1. Valida se o projeto existe
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.members), selectinload(Project.advisor))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    # 2. Valida acesso
    if not check_project_access(project, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não possui vínculo com este projeto."
        )

    # 3. Retorna histórico ordenado pela versão mais recente
    result_submissions = await db.execute(
        select(Submission)
        .where(Submission.project_id == project_id)
        .order_by(Submission.version.desc())
        .options(selectinload(Submission.uploader))
    )
    return result_submissions.scalars().all()

@router.get("/{id}/download")
async def download_submission(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Realiza o download de uma entrega de forma segura."""
    # 1. Valida se a submissão existe
    result_sub = await db.execute(
        select(Submission)
        .where(Submission.id == id)
    )
    submission = result_sub.scalars().first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega não encontrada.")

    # 2. Valida acesso ao projeto da submissão
    result_proj = await db.execute(
        select(Project)
        .where(Project.id == submission.project_id)
        .options(selectinload(Project.members), selectinload(Project.advisor))
    )
    project = result_proj.scalars().first()
    if not project or not check_project_access(project, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não possui vínculo com o projeto desta entrega."
        )

    # 3. Valida se o arquivo físico existe no servidor
    if not os.path.exists(submission.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O arquivo físico não foi encontrado no servidor."
        )

    # 4. Retorna o arquivo
    return FileResponse(
        path=submission.file_path,
        filename=submission.filename,
        media_type="application/octet-stream"
    )

@router.patch("/{id}/evaluate", response_model=SubmissionResponse)
async def evaluate_submission(
    id: uuid.UUID,
    evaluation: SubmissionEvaluate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "coordinator", "advisor"]))
):
    """Permite que o orientador avalie uma entrega registrando feedback textual."""
    # 1. Valida se a submissão existe
    result_sub = await db.execute(
        select(Submission)
        .where(Submission.id == id)
        .options(selectinload(Submission.uploader))
    )
    submission = result_sub.scalars().first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega não encontrada.")

    # 2. Valida se o orientador é o responsável pelo projeto
    result_proj = await db.execute(
        select(Project)
        .where(Project.id == submission.project_id)
    )
    project = result_proj.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto associado não encontrado.")

    if current_user.role == "advisor" and project.advisor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas o orientador do projeto pode avaliar esta entrega."
        )

    # 3. Atualiza os campos de avaliação
    submission.feedback = evaluation.feedback
    submission.status = "evaluated"
    await db.commit()
    await db.refresh(submission)

    # 4. Registra auditoria
    await log_audit(
        db,
        user_id=current_user.id,
        action="evaluate_submission",
        target_id=str(submission.id),
        details={"project_id": str(submission.project_id), "feedback": evaluation.feedback}
    )

    return submission
