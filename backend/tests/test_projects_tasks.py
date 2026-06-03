import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import User, Project, Task, AuditLog
from app.auth_utils import create_access_token

async def create_test_user(db_session, name: str, email: str, role: str, suap_id: str) -> User:
    user = User(
        name=name,
        email=email,
        role=role,
        suap_id=suap_id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

def authorize_client(client, user: User):
    token = create_access_token({"sub": str(user.id)})
    client.cookies.set("access_token", token)

@pytest.mark.asyncio
async def test_create_project_validation_and_audit(client, db_session):
    """Testa a criação de projetos: sucesso, validação de membro obrigatório e auditoria."""
    # 1. Cria orientador e aluno
    advisor = await create_test_user(db_session, "Orientador Teste", "advisor@test.com", "advisor", "adv01")
    student = await create_test_user(db_session, "Aluno Teste", "student@test.com", "student", "std01")
    
    # Autoriza como orientador
    authorize_client(client, advisor)

    # 2. Testa validação de no mínimo 1 membro aluno
    payload_no_members = {
        "title": "Projeto Alfa",
        "description": "Descrição do Projeto Alfa",
        "repository_url": "https://github.com/test/alfa",
        "member_ids": []
    }
    resp = await client.post("/api/projects", json=payload_no_members)
    assert resp.status_code == 400
    assert "pelo menos 1 aluno" in resp.json()["detail"]

    # 3. Cria com sucesso
    payload_success = {
        "title": "Projeto Alfa",
        "description": "Descrição do Projeto Alfa",
        "repository_url": "https://github.com/test/alfa",
        "member_ids": [str(student.id)]
    }
    resp = await client.post("/api/projects", json=payload_success)
    assert resp.status_code == 201
    project_data = resp.json()
    assert project_data["title"] == "Projeto Alfa"
    assert project_data["advisor_id"] == str(advisor.id)
    assert len(project_data["members"]) == 1
    assert project_data["members"][0]["id"] == str(student.id)

    # 4. Verifica auditoria no banco
    result_audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "create_project")
    )
    audit = result_audit.scalars().first()
    assert audit is not None
    assert audit.user_id == advisor.id
    assert audit.target_type == "project"
    assert audit.target_id == project_data["id"]

@pytest.mark.asyncio
async def test_project_endpoints_role_protection(client, db_session):
    """Testa se as rotas de criação/edição/remoção estão protegidas contra perfil não autorizado."""
    advisor = await create_test_user(db_session, "Orientador", "advisor@test.com", "advisor", "adv02")
    student = await create_test_user(db_session, "Aluno", "student@test.com", "student", "std02")
    
    # Cria projeto no banco associado ao orientador
    project = Project(
        title="Projeto Beta",
        description="Descrição Beta",
        advisor_id=advisor.id
    )
    project.members.append(student)
    db_session.add(project)
    await db_session.commit()

    # Autoriza como estudante (não tem permissão para cadastrar/editar/excluir projetos)
    authorize_client(client, student)

    # POST (Create)
    resp = await client.post("/api/projects", json={
        "title": "Projeto Novo",
        "description": "Desc",
        "member_ids": [str(student.id)]
    })
    assert resp.status_code == 403

    # PUT (Update)
    resp = await client.put(f"/api/projects/{project.id}", json={
        "title": "Projeto Alterado",
        "description": "Desc Alterada",
        "member_ids": [str(student.id)]
    })
    assert resp.status_code == 403

    # DELETE
    resp = await client.delete(f"/api/projects/{project.id}")
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_project_list_filtering(client, db_session):
    """Testa se a listagem filtra projetos conforme o perfil do usuário."""
    advisor1 = await create_test_user(db_session, "Orientador 1", "adv1@test.com", "advisor", "adv10")
    advisor2 = await create_test_user(db_session, "Orientador 2", "adv2@test.com", "advisor", "adv20")
    student = await create_test_user(db_session, "Aluno", "std@test.com", "student", "std10")

    # Projeto 1: advisor1 + student
    p1 = Project(title="Projeto 1", description="P1", advisor_id=advisor1.id)
    p1.members.append(student)
    
    # Projeto 2: advisor2
    p2 = Project(title="Projeto 2", description="P2", advisor_id=advisor2.id)

    db_session.add_all([p1, p2])
    await db_session.commit()

    # 1. Testa listagem como advisor1 (deve retornar apenas Projeto 1)
    authorize_client(client, advisor1)
    resp = await client.get("/api/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Projeto 1"

    # 2. Testa listagem como student (deve retornar apenas Projeto 1 onde é membro)
    authorize_client(client, student)
    resp = await client.get("/api/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Projeto 1"

    # 3. Testa listagem como admin (deve retornar todos)
    admin = await create_test_user(db_session, "Admin", "admin@test.com", "admin", "adm10")
    authorize_client(client, admin)
    resp = await client.get("/api/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 2

@pytest.mark.asyncio
async def test_tasks_crud_and_status_transition(client, db_session):
    """Testa a criação de tarefas, restrição de responsável ao projeto, atualização de status e atraso."""
    advisor = await create_test_user(db_session, "Orientador", "adv@test.com", "advisor", "adv_tasks")
    student1 = await create_test_user(db_session, "Aluno Membro", "std1@test.com", "student", "std_tasks_1")
    student2 = await create_test_user(db_session, "Aluno de Outro Projeto", "std2@test.com", "student", "std_tasks_2")

    # Cria projeto com student1 como membro
    project = Project(title="Projeto Kanban", description="PK", advisor_id=advisor.id)
    project.members.append(student1)
    db_session.add(project)
    await db_session.commit()

    # 1. Autoriza como student1 e cria tarefa
    authorize_client(client, student1)
    
    # Tenta criar tarefa com responsável que NÃO é membro do projeto
    payload_invalid_assignee = {
        "title": "Tarefa 1",
        "description": "Fazer X",
        "assigned_to": str(student2.id)
    }
    resp = await client.post(f"/api/tasks?project_id={project.id}", json=payload_invalid_assignee)
    assert resp.status_code == 400
    assert "deve ser um aluno membro" in resp.json()["detail"]

    # Cria com sucesso (responsável correto + prazo expirado no passado para testar is_overdue)
    past_due = datetime.utcnow() - timedelta(days=2)
    payload_success = {
        "title": "Tarefa 1",
        "description": "Fazer X",
        "assigned_to": str(student1.id),
        "due_date": past_due.isoformat()
    }
    resp = await client.post(f"/api/tasks?project_id={project.id}", json=payload_success)
    assert resp.status_code == 201
    task_data = resp.json()
    assert task_data["title"] == "Tarefa 1"
    assert task_data["status"] == "todo"
    assert task_data["is_overdue"] is True

    # 2. Atualiza status (PATCH /status) para in_progress e depois done
    resp = await client.patch(f"/api/tasks/{task_data['id']}/status", json={"status": "in_progress"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"
    assert resp.json()["is_overdue"] is True

    # Quando finalizada (done), não deve mais constar como atrasada
    resp = await client.patch(f"/api/tasks/{task_data['id']}/status", json={"status": "done"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"
    assert resp.json()["is_overdue"] is False

    # 3. Verifica auditoria da tarefa
    result_audit = await db_session.execute(
        select(AuditLog).where(AuditLog.action == "patch_task_status")
    )
    audit = result_audit.scalars().first()
    assert audit is not None
    assert audit.target_type == "task"
    assert audit.target_id == task_data["id"]
