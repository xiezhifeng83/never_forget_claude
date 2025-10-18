"""
Task API endpoints.

Implements CRUD operations for tasks per contracts/openapi.yaml.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from backend.src.database import get_db
from backend.src.models.task import Task
from backend.src.middleware.auth import get_device_token
from pydantic import BaseModel, Field, validator

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Pydantic models for request/response validation
class TaskCreate(BaseModel):
    """Task creation request schema per openapi.yaml."""
    id: uuid.UUID = Field(..., description="Client-generated UUID v4 for the task")
    text: str = Field(..., min_length=1, max_length=500, description="Task description")
    position: int = Field(..., ge=0, description="Position in task list (0 = top)")

    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Task text cannot be empty or whitespace only')
        return v


class TaskUpdate(BaseModel):
    """Task update request schema per openapi.yaml."""
    text: Optional[str] = Field(None, min_length=1, max_length=500, description="New task text")
    position: Optional[int] = Field(None, ge=0, description="New position")
    updated_at: datetime = Field(..., description="Client's timestamp for conflict detection")

    @validator('text')
    def text_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Task text cannot be empty or whitespace only')
        return v


class TaskResponse(BaseModel):
    """Task response schema per openapi.yaml."""
    id: uuid.UUID
    device_token: uuid.UUID
    text: str
    position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class TaskListResponse(BaseModel):
    """Task list response with server time per openapi.yaml."""
    tasks: List[TaskResponse]
    server_time: datetime = Field(alias="serverTime")

    class Config:
        populate_by_name = True


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    since: Optional[datetime] = None,
    limit: Optional[int] = None,
    device_token: uuid.UUID = Depends(get_device_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tasks for the authenticated device.

    Per openapi.yaml GET /tasks:
    - Returns tasks ordered by position
    - Optional 'since' parameter for delta sync
    - Optional 'limit' parameter for dropdown (e.g., limit=15)
    - Includes serverTime for client sync tracking

    Args:
        since: Optional - only return tasks modified after this timestamp
        limit: Optional - maximum number of tasks to return (for dropdown)
        device_token: Device token from Authorization header
        db: Database session

    Returns:
        TaskListResponse: List of tasks with server timestamp
    """
    # Build query - filter by device token and order by position
    query = select(Task).where(Task.device_token == device_token).order_by(Task.position)

    # Add timestamp filter if provided
    if since:
        query = query.where(Task.updated_at > since)

    # Add limit if provided (for status bar dropdown - max 15 per spec)
    if limit:
        query = query.limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return {
        "tasks": tasks,
        "serverTime": datetime.now(timezone.utc),
    }


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    device_token: uuid.UUID = Depends(get_device_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task.

    Per openapi.yaml POST /tasks:
    - Client generates UUID
    - Device token from Authorization header
    - Returns 201 Created with task
    - Returns 409 Conflict if task ID already exists

    Args:
        task_data: Task creation data
        device_token: Device token from Authorization header
        db: Database session

    Returns:
        TaskResponse: Created task

    Raises:
        HTTPException 409: Task ID already exists
        HTTPException 400: Invalid task data
    """
    # Check if task ID already exists
    result = await db.execute(
        select(Task).where(Task.id == task_data.id)
    )
    existing_task = result.scalar_one_or_none()

    if existing_task:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Task ID already exists"},
        )

    # Create new task
    new_task = Task(
        id=task_data.id,
        device_token=device_token,
        text=task_data.text.strip(),
        position=task_data.position,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    device_token: uuid.UUID = Depends(get_device_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific task by ID.

    Per openapi.yaml GET /tasks/{taskId}:
    - Returns task if it belongs to the authenticated device
    - Returns 404 if task not found or doesn't belong to device

    Args:
        task_id: UUID of the task
        device_token: Device token from Authorization header
        db: Database session

    Returns:
        TaskResponse: Task details

    Raises:
        HTTPException 404: Task not found
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.device_token == device_token)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"},
        )

    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    device_token: uuid.UUID = Depends(get_device_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing task.

    Per openapi.yaml PUT /tasks/{taskId}:
    - Uses last-write-wins conflict resolution based on updatedAt
    - Returns 409 Conflict if server version is newer
    - Returns 404 if task not found

    Args:
        task_id: UUID of the task
        task_data: Task update data with conflict detection timestamp
        device_token: Device token from Authorization header
        db: Database session

    Returns:
        TaskResponse: Updated task

    Raises:
        HTTPException 404: Task not found
        HTTPException 409: Conflict - server has newer version
    """
    # Fetch existing task
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.device_token == device_token)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"},
        )

    # Conflict detection: last-write-wins per data-model.md
    # If client's timestamp is older than server's, reject the update
    if task_data.updated_at <= task.updated_at:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Conflict: server version is newer",
                "serverVersion": TaskResponse.from_orm(task).dict(),
            },
        )

    # Update task fields
    if task_data.text is not None:
        task.text = task_data.text.strip()
    if task_data.position is not None:
        task.position = task_data.position

    # Timestamp will auto-update via onupdate=func.now() in model
    await db.commit()
    await db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    device_token: uuid.UUID = Depends(get_device_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a task.

    Per openapi.yaml DELETE /tasks/{taskId}:
    - Returns 204 No Content on success
    - Returns 404 if task not found

    Args:
        task_id: UUID of the task
        device_token: Device token from Authorization header
        db: Database session

    Raises:
        HTTPException 404: Task not found
    """
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.device_token == device_token)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"},
        )

    await db.delete(task)
    await db.commit()
