from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import User, Task, AcademicEvent
from ..auth_utils import get_current_user

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/events")
async def list_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna eventos acadêmicos e tarefas com prazo para calendário."""
    events = []

    # 1. Busca eventos acadêmicos manuais
    result = await db.execute(
        select(AcademicEvent).order_by(AcademicEvent.event_date)
    )
    academic_events = result.scalars().all()
    for e in academic_events:
        events.append({
            "id": str(e.id),
            "title": e.title,
            "description": e.description or "",
            "date": e.event_date.isoformat(),
            "type": e.event_type,
            "source": "academic_event"
        })

    # 2. Busca tarefas com prazo (due_date) dos projetos do usuário
    if current_user.role in ["admin", "coordinator"]:
        result = await db.execute(
            select(Task).where(Task.due_date.isnot(None))
        )
        tasks = result.scalars().all()
    elif current_user.role == "advisor":
        result = await db.execute(
            select(Task)
            .where(Task.due_date.isnot(None))
            .options(selectinload(Task.project))
        )
        tasks = [t for t in result.scalars().all()
                 if t.project and t.project.advisor_id == current_user.id]
    else:
        result = await db.execute(
            select(Task)
            .where(Task.due_date.isnot(None), Task.assigned_to == current_user.id)
            .options(selectinload(Task.project))
        )
        tasks = result.scalars().all()

    for t in tasks:
        is_overdue = t.due_date and t.due_date < datetime.utcnow() and t.status != "done"
        events.append({
            "id": str(t.id),
            "title": t.title,
            "description": f"Projeto: {t.project.title if t.project else 'N/A'} | Status: {t.status}",
            "date": t.due_date.isoformat(),
            "type": "deadline",
            "source": "task",
            "overdue": is_overdue
        })

    return events
