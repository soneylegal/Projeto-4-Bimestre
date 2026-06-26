import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import User, Project, Message
from ..auth_utils import get_current_user
from pydantic import BaseModel

router = APIRouter(tags=["chat"])


class MessageResponse(BaseModel):
    id: str
    project_id: str
    sender_id: str | None
    sender_name: str | None
    content: str
    created_at: str

    class Config:
        from_attributes = True


async def can_access_project(project_id: uuid.UUID, user: User, db: AsyncSession) -> Project | None:
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.members))
    )
    project = result.scalars().first()
    if not project:
        return None
    if user.role in ["admin", "coordinator"]:
        return project
    if user.role == "advisor" and project.advisor_id == user.id:
        return project
    if user.role == "student" and any(m.id == user.id for m in project.members):
        return project
    return None


@router.get("/api/projects/{project_id}/messages")
async def list_messages(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista mensagens de um projeto (acesso apenas a membros)."""
    project = await can_access_project(project_id, current_user, db)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado ou acesso negado.")

    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .options(selectinload(Message.sender))
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return [
        MessageResponse(
            id=str(m.id),
            project_id=str(m.project_id),
            sender_id=str(m.sender_id) if m.sender_id else None,
            sender_name=m.sender.name if m.sender else None,
            content=m.content,
            created_at=m.created_at.isoformat()
        )
        for m in messages
    ]


class MessageCreate(BaseModel):
    content: str


@router.post("/api/projects/{project_id}/messages")
async def send_message(
    project_id: uuid.UUID,
    msg_in: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Envia uma mensagem em um projeto."""
    project = await can_access_project(project_id, current_user, db)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado ou acesso negado.")

    message = Message(
        project_id=project_id,
        sender_id=current_user.id,
        content=msg_in.content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    return MessageResponse(
        id=str(message.id),
        project_id=str(message.project_id),
        sender_id=str(message.sender_id) if message.sender_id else None,
        sender_name=current_user.name,
        content=message.content,
        created_at=message.created_at.isoformat()
    )


# WebSocket connections per project
chat_connections: dict[str, list[WebSocket]] = {}


@router.websocket("/ws/chat/{project_id}")
async def chat_websocket(websocket: WebSocket, project_id: str):
    await websocket.accept()

    if project_id not in chat_connections:
        chat_connections[project_id] = []
    chat_connections[project_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all connected clients in the same project
            for conn in chat_connections.get(project_id, []):
                if conn != websocket:
                    try:
                        await conn.send_text(data)
                    except Exception:
                        pass
    except WebSocketDisconnect:
        pass
    finally:
        if project_id in chat_connections:
            chat_connections[project_id].remove(websocket)
            if not chat_connections[project_id]:
                del chat_connections[project_id]
