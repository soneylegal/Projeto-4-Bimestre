import io
import pytest
import uuid
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import User, Project, Submission, AuditLog
from app.auth_utils import create_access_token
from .test_projects_tasks import create_test_user, authorize_client

@pytest.mark.asyncio
async def test_create_submission_success_and_versioning(client, db_session):
    """Testa upload de submissão com sucesso por membro e incremento de versão."""
    # 1. Cria orientador e alunos
    advisor = await create_test_user(db_session, "Advisor A", "advisor_a@test.com", "advisor", "suap_adv_a")
    student1 = await create_test_user(db_session, "Student A1", "student_a1@test.com", "student", "suap_std_a1")
    student2 = await create_test_user(db_session, "Student A2", "student_a2@test.com", "student", "suap_std_a2")

    # 2. Cria projeto
    project = Project(title="Projeto Alfa", description="Descrição Alfa", advisor_id=advisor.id)
    project.members.append(student1)
    db_session.add(project)
    await db_session.commit()

    # 3. Aluno 1 (membro) envia arquivo 1
    authorize_client(client, student1)
    file_content = b"content of first submission file"
    file_data = {"file": ("document_v1.pdf", io.BytesIO(file_content), "application/pdf")}
    
    resp = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id)},
        files=file_data
    )
    assert resp.status_code == 201
    sub_data = resp.json()
    assert sub_data["version"] == 1
    assert sub_data["filename"] == "document_v1.pdf"
    assert sub_data["status"] == "pending"
    assert sub_data["uploader_id"] == str(student1.id)

    # 4. Aluno 1 envia arquivo 2 (versão 2)
    file_content_v2 = b"content of second submission file"
    file_data_v2 = {"file": ("document_v2.pdf", io.BytesIO(file_content_v2), "application/pdf")}
    resp_v2 = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id)},
        files=file_data_v2
    )
    assert resp_v2.status_code == 201
    sub_data_v2 = resp_v2.json()
    assert sub_data_v2["version"] == 2
    assert sub_data_v2["filename"] == "document_v2.pdf"

    # 5. Verifica auditoria no banco
    result_audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "create_submission")
    )
    audits = result_audit.scalars().all()
    assert len(audits) == 2

@pytest.mark.asyncio
async def test_create_submission_forbidden(client, db_session):
    """Testa se aluno que não é membro do projeto tem o envio negado."""
    advisor = await create_test_user(db_session, "Advisor B", "advisor_b@test.com", "advisor", "suap_adv_b")
    student_member = await create_test_user(db_session, "Student Member", "member@test.com", "student", "suap_std_m")
    student_non_member = await create_test_user(db_session, "Student Non Member", "non_member@test.com", "student", "suap_std_nm")

    project = Project(title="Projeto Beta", description="Beta", advisor_id=advisor.id)
    project.members.append(student_member)
    db_session.add(project)
    await db_session.commit()

    # Autoriza aluno intruso
    authorize_client(client, student_non_member)
    file_data = {"file": ("document.pdf", io.BytesIO(b"some data"), "application/pdf")}
    resp = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id)},
        files=file_data
    )
    assert resp.status_code == 403
    assert "Acesso negado" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_create_submission_too_large(client, db_session):
    """Testa se o arquivo excede o limite de tamanho de 50 MB."""
    advisor = await create_test_user(db_session, "Advisor C", "advisor_c@test.com", "advisor", "suap_adv_c")
    student = await create_test_user(db_session, "Student C", "student_c@test.com", "student", "suap_std_c")

    project = Project(title="Projeto Gama", description="Gama", advisor_id=advisor.id)
    project.members.append(student)
    db_session.add(project)
    await db_session.commit()

    authorize_client(client, student)
    
    # 50 MB + 1 byte
    too_large_content = b"x" * (50 * 1024 * 1024 + 1)
    file_data = {"file": ("huge_file.zip", io.BytesIO(too_large_content), "application/zip")}
    
    resp = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id)},
        files=file_data
    )
    assert resp.status_code == 413
    assert "exceder o limite de 50 MB" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_list_submissions_history(client, db_session):
    """Testa a listagem de submissões ordenada decrescente por versão."""
    advisor = await create_test_user(db_session, "Advisor D", "advisor_d@test.com", "advisor", "suap_adv_d")
    student = await create_test_user(db_session, "Student D", "student_d@test.com", "student", "suap_std_d")

    project = Project(title="Projeto Delta", description="Delta", advisor_id=advisor.id)
    project.members.append(student)
    db_session.add(project)
    await db_session.commit()

    # Cria submissões mock direto no DB
    sub1 = Submission(project_id=project.id, version=1, file_path="uploads/mock_1.pdf", filename="mock_1.pdf", uploader_id=student.id, status="pending")
    sub2 = Submission(project_id=project.id, version=2, file_path="uploads/mock_2.pdf", filename="mock_2.pdf", uploader_id=student.id, status="pending")
    db_session.add_all([sub1, sub2])
    await db_session.commit()

    # Listagem como estudante
    authorize_client(client, student)
    resp = await client.get(f"/api/submissions/{project.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # Verifica ordenação DESC (versão 2 primeiro)
    assert data[0]["version"] == 2
    assert data[1]["version"] == 1

@pytest.mark.asyncio
async def test_download_and_evaluate_submission(client, db_session):
    """Testa download seguro de arquivo e a avaliação com feedback."""
    advisor = await create_test_user(db_session, "Advisor E", "advisor_e@test.com", "advisor", "suap_adv_e")
    student = await create_test_user(db_session, "Student E", "student_e@test.com", "student", "suap_std_e")
    other_student = await create_test_user(db_session, "Student Other", "other@test.com", "student", "suap_std_o")

    project = Project(title="Projeto Epsilon", description="Epsilon", advisor_id=advisor.id)
    project.members.append(student)
    db_session.add(project)
    await db_session.commit()

    # Cria arquivo físico no uploader
    authorize_client(client, student)
    file_content = b"original file contents"
    file_data = {"file": ("my_report.pdf", io.BytesIO(file_content), "application/pdf")}
    resp_upload = await client.post(
        "/api/submissions",
        data={"project_id": str(project.id)},
        files=file_data
    )
    sub_id = resp_upload.json()["id"]

    # 1. Tenta download como outro estudante (Forbidden)
    authorize_client(client, other_student)
    resp_dl_forbidden = await client.get(f"/api/submissions/{sub_id}/download")
    assert resp_dl_forbidden.status_code == 403

    # 2. Faz download como orientador (Success)
    authorize_client(client, advisor)
    resp_dl = await client.get(f"/api/submissions/{sub_id}/download")
    assert resp_dl.status_code == 200
    assert resp_dl.content == file_content

    # 3. Tenta avaliar como aluno (Forbidden)
    authorize_client(client, student)
    resp_eval_forbid = await client.patch(f"/api/submissions/{sub_id}/evaluate", json={"feedback": "Trabalho muito bom!"})
    assert resp_eval_forbid.status_code == 403

    # 4. Avalia como orientador (Success)
    authorize_client(client, advisor)
    resp_eval = await client.patch(f"/api/submissions/{sub_id}/evaluate", json={"feedback": "Aprovado com ressalvas."})
    assert resp_eval.status_code == 200
    data_eval = resp_eval.json()
    assert data_eval["status"] == "evaluated"
    assert data_eval["feedback"] == "Aprovado com ressalvas."

    # 5. Verifica auditoria de avaliação
    result_audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "evaluate_submission")
    )
    audit = result_audit.scalars().first()
    assert audit is not None
    assert audit.target_id == sub_id
    assert audit.details["feedback"] == "Aprovado com ressalvas."
