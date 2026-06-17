from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Literal['admin', 'coordinator', 'advisor', 'student']
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    suap_id: str

class UserResponse(UserBase):
    id: UUID
    suap_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    user: UserResponse
    # O access token será enviado por cookie httpOnly, mas opcionalmente retornamos aqui os dados do user
    # Para o front-end saber que está logado. O JSON retornado no callback/me conterá o user.

class TaskBase(BaseModel):
    title: str
    description: str
    status: Literal['todo', 'in_progress', 'done'] = 'todo'
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: str
    description: str
    status: Literal['todo', 'in_progress', 'done']
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None

class TaskStatusUpdate(BaseModel):
    status: Literal['todo', 'in_progress', 'done']

class TaskResponse(TaskBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    title: str
    description: str
    repository_url: Optional[str] = None

class ProjectCreate(ProjectBase):
    member_ids: list[UUID]

class ProjectUpdate(ProjectBase):
    member_ids: list[UUID]

class ProjectResponse(ProjectBase):
    id: UUID
    advisor_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    advisor: Optional[UserResponse] = None
    members: list[UserResponse] = []
    tasks: list[TaskResponse] = []

    class Config:
        from_attributes = True

# ── Submissions ──────────────────────────────────────────────────────────────

class SubmissionResponse(BaseModel):
    id: UUID
    project_id: UUID
    version: int
    file_path: str
    filename: str
    original_filename: Optional[str] = None
    uploader_id: Optional[UUID] = None
    uploader: Optional[UserResponse] = None
    task_title: Optional[str] = None
    feedback: Optional[str] = None
    status: Literal['pending', 'evaluated']
    created_at: datetime

    class Config:
        from_attributes = True

class EvaluateRequest(BaseModel):
    feedback: str

class SubmissionEvaluate(BaseModel):
    feedback: str
