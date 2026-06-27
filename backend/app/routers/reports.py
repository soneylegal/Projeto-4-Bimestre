import io
import httpx
import markdown
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fpdf import FPDF

from ..config import settings
from ..database import get_db
from ..models import User, Project, Submission
from ..auth_utils import get_current_user, require_role
from ..schemas import ReportRequest, ReportResponse

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    req: ReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "coordinator", "advisor"]))
):
    result = await db.execute(
        select(Project)
        .where(Project.id == req.project_id)
        .options(
            selectinload(Project.advisor),
            selectinload(Project.members),
            selectinload(Project.tasks),
            selectinload(Project.submissions).selectinload(Submission.uploader),
        )
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    tasks_summary = "\n".join(
        f"- {t.title} ({t.status})"
        for t in project.tasks
    )
    submissions_summary = "\n".join(
        f"- v{s.version}: {s.filename or 'sem arquivo'} ({s.status})"
        for s in project.submissions
    )
    members_list = ", ".join(m.name for m in project.members)

    prompt = (
        f"Você é um assistente de relatórios acadêmicos do IFAL. "
        f"Gere um relatório em Markdown.\n\n"
        f"## Dados do Projeto\n"
        f"- Título: {project.title}\n"
        f"- Descrição: {project.description or 'Sem descrição'}\n"
        f"- Orientador: {project.advisor.name if project.advisor else 'Não designado'}\n"
        f"- Membros: {members_list or 'Nenhum'}\n\n"
        f"## Tarefas\n{tasks_summary or 'Nenhuma tarefa cadastrada.'}\n\n"
        f"## Submissões\n{submissions_summary or 'Nenhuma submissão realizada.'}\n\n"
        f"## Instruções Adicionais\n{req.context or 'Gere um relatório completo e profissional em português brasileiro.'}\n\n"
        f"O relatório deve conter: resumo executivo, descrição do projeto, "
        f"status das tarefas, histórico de entregas e recomendações finais. "
        f"Use formatação Markdown limpa."
    )

    if not settings.LLM_API_KEY:
        mock_report = (
            f"# Relatório do Projeto: {project.title}\n\n"
            f"*Este é um relatório mockado. Configure a variável LLM_API_KEY "
            f"no ambiente para gerar relatórios reais via IA.*\n\n"
            f"## Resumo Executivo\n\n"
            f"O projeto '{project.title}' está em andamento "
            f"com {len(project.tasks)} tarefas registradas "
            f"e {len(project.submissions)} submissões realizadas.\n\n"
            f"## Status das Tarefas\n\n{tasks_summary or 'Nenhuma tarefa cadastrada.'}\n\n"
            f"## Histórico de Entregas\n\n{submissions_summary or 'Nenhuma submissão.'}"
        )
        return ReportResponse(
            report=mock_report,
            project_id=project.id,
            generated_at=datetime.utcnow()
        )

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            settings.LLM_API_URL,
            headers={
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em gerar "
                                   "relatórios acadêmicos."
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            },
        )
        response.raise_for_status()
        data = response.json()
        report_text = data["choices"][0]["message"]["content"]

    return ReportResponse(
        report=report_text,
        project_id=project.id,
        generated_at=datetime.utcnow()
    )


@router.get("/{project_id}/pdf")
async def export_report_pdf(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "coordinator", "advisor"]))
):
    """Exporta relatório do projeto em PDF."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.advisor),
            selectinload(Project.members),
            selectinload(Project.tasks),
            selectinload(Project.submissions).selectinload(Submission.uploader),
        )
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, f"Relatorio do Projeto: {project.title}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Generated date
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, f"Gerado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Description
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Descricao do Projeto", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, project.description or "Sem descricao cadastrada.")
    pdf.ln(4)

    # Advisor and Members
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Equipe", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    advisor_name = project.advisor.name if project.advisor else "Nao designado"
    pdf.cell(0, 6, f"Orientador: {advisor_name}", new_x="LMARGIN", new_y="NEXT")
    members_list = ", ".join(m.name for m in project.members) if project.members else "Nenhum"
    pdf.multi_cell(0, 5, f"Membros: {members_list}")
    pdf.ln(4)

    # Tasks
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Tarefas ({len(project.tasks)})", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if project.tasks:
        for t in project.tasks:
            status_map = {"todo": "A Fazer", "in_progress": "Em Progresso", "done": "Concluido"}
            status = status_map.get(t.status, t.status)
            pdf.cell(0, 6, f"- {t.title} ({status})", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, "Nenhuma tarefa cadastrada.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Submissions
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Submissoes ({len(project.submissions)})", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    if project.submissions:
        for s in project.submissions:
            status = "Avaliado" if s.status == "evaluated" else "Pendente"
            pdf.cell(0, 6, f"- v{s.version}: {s.filename or 'sem arquivo'} ({status})", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, "Nenhuma submissao realizada.", new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="relatorio_{project.title}.pdf"'
        }
    )
