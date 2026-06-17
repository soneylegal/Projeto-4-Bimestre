import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import User, Project, Submission
from ..schemas import SubmissionResponse, EvaluateRequest
from ..auth_utils import get_current_user, require_role

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

# Diretório local para armazenar os arquivos enviados
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB em bytes


async def _get_project_or_404(project_id: uuid.UUID, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")
    return project


async def _get_submission_or_404(submission_id: uuid.UUID, db: AsyncSession) -> Submission:
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.uploader))
    )
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submissão não encontrada.")
    return submission


def _check_project_access(project: Project, current_user: User):
    """Verifica se o usuário tem acesso ao projeto."""
    if current_user.role in ["admin", "coordinator"]:
        return
    if current_user.role == "advisor" and project.advisor_id == current_user.id:
        return
    if current_user.role == "student":
        # members são carregados via selectinload onde necessário
        member_ids = [m.id for m in project.members] if project.members else []
        if current_user.id in member_ids:
            return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso negado. Você não possui vínculo com este projeto."
    )


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def upload_submission(
    project_id: uuid.UUID = Form(...),
    task_title: str = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Faz upload de um arquivo como nova submissão para o projeto.
    Gera versão incremental automaticamente (v1, v2, ...).
    Limite: 50 MB (RNF009).
    """
    # Busca projeto com membros
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.members))
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    _check_project_access(project, current_user)

    # Lê o arquivo e valida tamanho (50 MB)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo excede o limite de 50 MB (tamanho recebido: {len(contents) // (1024*1024)} MB)."
        )

    # Calcula próxima versão para este projeto
    result_version = await db.execute(
        select(Submission)
        .where(Submission.project_id == project_id)
    )
    existing = result_version.scalars().all()
    next_version = len(existing) + 1

    # Salva o arquivo em disco
    project_dir = os.path.join(UPLOAD_DIR, str(project_id))
    os.makedirs(project_dir, exist_ok=True)

    safe_filename = f"v{next_version}_{file.filename}"
    file_path = os.path.join(project_dir, safe_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    # Cria registro no banco
    submission = Submission(
        project_id=project_id,
        version=next_version,
        file_path=file_path,
        original_filename=file.filename,
        uploader_id=current_user.id,
        task_title=task_title,
        status="pending"
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    # Recarrega com uploader
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission.id)
        .options(selectinload(Submission.uploader))
    )
    return result.scalars().first()


@router.get("/{project_id}", response_model=list[SubmissionResponse])
async def list_submissions(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista o histórico de submissões de um projeto, ordenado por versão decrescente.
    """
    result_project = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.members))
    )
    project = result_project.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado.")

    _check_project_access(project, current_user)

    result = await db.execute(
        select(Submission)
        .where(Submission.project_id == project_id)
        .options(selectinload(Submission.uploader))
        .order_by(Submission.version.desc())
    )
    return result.scalars().all()


@router.get("/{submission_id}/download")
async def download_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Serve o arquivo de uma submissão para download.
    """
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.uploader))
    )
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submissão não encontrada.")

    # Verifica acesso ao projeto
    result_project = await db.execute(
        select(Project)
        .where(Project.id == submission.project_id)
        .options(selectinload(Project.members))
    )
    project = result_project.scalars().first()
    _check_project_access(project, current_user)

    if not os.path.exists(submission.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado no servidor. O serviço pode ter sido reiniciado (disco efêmero)."
        )

    return FileResponse(
        path=submission.file_path,
        filename=submission.original_filename,
        media_type="application/octet-stream"
    )


@router.patch("/{submission_id}/evaluate", response_model=SubmissionResponse)
async def evaluate_submission(
    submission_id: uuid.UUID,
    body: EvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "coordinator", "advisor"]))
):
    """
    Salva feedback textual e muda status da submissão para 'evaluated'.
    Restrito a orientadores, coordenadores e administradores.
    """
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission_id)
        .options(selectinload(Submission.uploader))
    )
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submissão não encontrada.")

    # Orientador só pode avaliar submissões do próprio projeto
    if current_user.role == "advisor":
        result_project = await db.execute(
            select(Project).where(Project.id == submission.project_id)
        )
        project = result_project.scalars().first()
        if not project or project.advisor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Você não é o orientador deste projeto."
            )

    submission.feedback = body.feedback
    submission.status = "evaluated"
    await db.commit()

    # Recarrega
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission.id)
        .options(selectinload(Submission.uploader))
    )
    return result.scalars().first()
