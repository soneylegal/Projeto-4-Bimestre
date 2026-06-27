import asyncio
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from ..database import get_db
from ..models import User
from ..auth_utils import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Simple in-memory event queues per user
_event_queues: dict[str, asyncio.Queue] = {}


async def push_notification(user_id: str, event: dict):
    """Push a notification event to a user's queue."""
    if user_id not in _event_queues:
        _event_queues[user_id] = asyncio.Queue()
    await _event_queues[user_id].put(event)


async def event_generator(request: Request, user_id: str):
    """Generate SSE events for a user."""
    if user_id not in _event_queues:
        _event_queues[user_id] = asyncio.Queue()

    queue = _event_queues[user_id]

    try:
        while True:
            if await request.is_disconnected():
                break

            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {
                    "event": event.get("type", "notification"),
                    "data": json.dumps(event.get("data", {}))
                }
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "keepalive"}
    finally:
        if user_id in _event_queues:
            del _event_queues[user_id]


@router.get("/stream")
async def notification_stream(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """SSE endpoint for real-time notifications."""
    return EventSourceResponse(
        event_generator(request, str(current_user.id))
    )


@router.get("/test")
async def test_notification(
    current_user: User = Depends(get_current_user)
):
    """Test endpoint to send a notification to the current user."""
    await push_notification(str(current_user.id), {
        "type": "notification",
        "data": {
            "message": "Esta é uma notificação de teste!",
            "type": "info",
            "timestamp": datetime.utcnow().isoformat()
        }
    })
    return {"message": "Notificação de teste enviada."}
