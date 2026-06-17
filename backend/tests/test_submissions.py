"""
Testes de integração para o router de submissões.
Cobre: upload, listagem, download, avaliação e controle de acesso.
"""
import io
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Project, Submission
from app.auth_utils import create_access_token


# ── Fixtures auxiliares ───────────────────────────────────────────────────────

async def _create_user(db: AsyncSession, suap_id: str, role: str) -> User:
    user = User(
        suap_id=suap_id,
        name=f"User {role}",
        email=f"{suap_id}@ifal.edu.br",
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_project(db: AsyncSession, advisor: User, members: list[User]) -> Project:
    project = Project(
        title="Projeto Teste Submissions",
        description="Projeto para testes de submissão",
        advisor_id=advisor.id,
    )
    project.members = members
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


def _auth_cookie(user: User) -> dict:
    """Retorna cookie de autenticação para o usuário."""
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}


# ── Testes ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_submission(client: AsyncClient, db_session: AsyncSession):
    """Aluno faz upload de arquivo e recebe versão 1."""
    advisor = await _create_user(db_session, "adv001", "advisor")
    student = await _create_user(db_session, "std001", "student")
    project = await _create_project(db_session, advisor, [student])

    file_content = b"conteudo do arquivo de teste"
    response = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id), "task_title": "Revisão Bibliográfica"},
        files={"file": ("relatorio.pdf", io.BytesIO(file_content), "application/pdf")},
        cookies=_auth_cookie(student),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["version"] == 1
    assert body["original_filename"] == "relatorio.pdf"
    assert body["status"] == "pending"
    assert body["task_title"] == "Revisão Bibliográfica"


@pytest.mark.asyncio
async def test_upload_increments_version(client: AsyncClient, db_session: AsyncSession):
    """Segundo upload gera versão 2."""
    advisor = await _create_user(db_session, "adv002", "advisor")
    student = await _create_user(db_session, "std002", "student")
    project = await _create_project(db_session, advisor, [student])

    file_content = b"versao 1"
    for _ in range(2):
        resp = await client.post(
            "/api/submissions",
            data={"project_id": str(project.id)},
            files={"file": ("doc.pdf", io.BytesIO(file_content), "application/pdf")},
            cookies=_auth_cookie(student),
        )
        assert resp.status_code == 201

    assert resp.json()["version"] == 2


@pytest.mark.asyncio
async def test_list_submissions(client: AsyncClient, db_session: AsyncSession):
    """GET /api/submissions/{project_id} retorna histórico ordenado por versão DESC."""
    advisor = await _create_user(db_session, "adv003", "advisor")
    student = await _create_user(db_session, "std003", "student")
    project = await _create_project(db_session, advisor, [student])

    # Cria 3 submissões
    for i in range(3):
        await client.post(
            "/api/submissions",
            data={"project_id": str(project.id)},
            files={"file": (f"doc{i}.pdf", io.BytesIO(b"x"), "application/pdf")},
            cookies=_auth_cookie(student),
        )

    response = await client.get(
        f"/api/submissions/{project.id}",
        cookies=_auth_cookie(advisor),
    )
    assert response.status_code == 200
    versions = [s["version"] for s in response.json()]
    assert versions == sorted(versions, reverse=True)  # DESC
    assert len(versions) == 3


@pytest.mark.asyncio
async def test_evaluate_submission(client: AsyncClient, db_session: AsyncSession):
    """Orientador avalia submissão: status muda para evaluated e feedback é salvo."""
    advisor = await _create_user(db_session, "adv004", "advisor")
    student = await _create_user(db_session, "std004", "student")
    project = await _create_project(db_session, advisor, [student])

    # Upload
    upload_resp = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id)},
        files={"file": ("trabalho.pdf", io.BytesIO(b"conteudo"), "application/pdf")},
        cookies=_auth_cookie(student),
    )
    assert upload_resp.status_code == 201
    submission_id = upload_resp.json()["id"]

    # Avaliação
    eval_resp = await client.patch(
        f"/api/submissions/{submission_id}/evaluate",
        json={"feedback": "Excelente trabalho, parabéns!"},
        cookies=_auth_cookie(advisor),
    )
    assert eval_resp.status_code == 200
    body = eval_resp.json()
    assert body["status"] == "evaluated"
    assert body["feedback"] == "Excelente trabalho, parabéns!"


@pytest.mark.asyncio
async def test_evaluate_forbidden_for_student(client: AsyncClient, db_session: AsyncSession):
    """Aluno NÃO pode avaliar submissões — deve receber 403."""
    advisor = await _create_user(db_session, "adv005", "advisor")
    student = await _create_user(db_session, "std005", "student")
    project = await _create_project(db_session, advisor, [student])

    upload_resp = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id)},
        files={"file": ("tcc.pdf", io.BytesIO(b"abc"), "application/pdf")},
        cookies=_auth_cookie(student),
    )
    submission_id = upload_resp.json()["id"]

    eval_resp = await client.patch(
        f"/api/submissions/{submission_id}/evaluate",
        json={"feedback": "Tentativa indevida"},
        cookies=_auth_cookie(student),
    )
    assert eval_resp.status_code == 403
