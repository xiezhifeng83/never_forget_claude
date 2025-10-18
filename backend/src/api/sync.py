"""
Batch synchronization endpoint.

Per contracts/openapi.yaml: POST /tasks/sync for efficient cross-device sync.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone

from backend.src.database import get_db
from backend.src.models.task import Task
from backend.src.middleware.auth import get_device_token

router = APIRouter(prefix="/tasks", tags=["sync"])


# Pydantic models for sync request/response
class SyncCreateChange(BaseModel):
    """Sync create action per openapi.yaml."""
    action: Literal["create"]
    id: uuid.UUID
    text: str = Field(..., max_length=500)
    position: int = Field(..., ge=0)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class SyncUpdateChange(BaseModel):
    """Sync update action per openapi.yaml."""
    action: Literal["update"]
    id: uuid.UUID
    text: Optional[str] = Field(None, max_length=500)
    position: Optional[int] = Field(None, ge=0)
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class SyncDeleteChange(BaseModel):
    """Sync delete action per openapi.yaml."""
    action: Literal["delete"]
    id: uuid.UUID
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class SyncRequest(BaseModel):
    """Sync request schema per openapi.yaml."""
    last_sync_at: Optional[datetime] = Field(None, alias="lastSyncAt")
    pending_changes: List[SyncCreateChange | SyncUpdateChange | SyncDeleteChange] = Field(alias="pendingChanges")

    class Config:
        populate_by_name = True


class TaskResponseSync(BaseModel):
    """Task response for sync - matches openapi.yaml Task schema."""
    id: uuid.UUID
    device_token: uuid.UUID = Field(alias="deviceToken")
    text: str
    position: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class Conflict(BaseModel):
    """Conflict response per openapi.yaml."""
    local_id: uuid.UUID = Field(alias="localId")
    resolution: Literal["server_wins", "deleted"]
    server_version: Optional[TaskResponseSync] = Field(alias="serverVersion")

    class Config:
        populate_by_name = True


class SyncResponse(BaseModel):
    """Sync response schema per openapi.yaml."""
    server_time: datetime = Field(alias="serverTime")
    tasks: List[TaskResponseSync]
    conflicts: List[Conflict]

    class Config:
        populate_by_name = True


@router.post("/sync", response_model=SyncResponse)
async def sync_tasks(
    sync_data: SyncRequest,
    device_token: uuid.UUID = Depends(get_device_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Full synchronization endpoint.

    Per openapi.yaml POST /tasks/sync:
    - Processes pending changes (creates, updates, deletes)
    - Returns complete server state for device
    - Returns conflicts where server version won
    - Includes serverTime for client sync tracking

    Args:
        sync_data: Sync request with pending changes
        device_token: Device token from Authorization header
        db: Database session

    Returns:
        SyncResponse: Server state with conflicts
    """
    conflicts = []

    # Process each pending change
    for change in sync_data.pending_changes:
        if change.action == "create":
            await process_create(change, device_token, db)
        elif change.action == "update":
            conflict = await process_update(change, device_token, db)
            if conflict:
                conflicts.append(conflict)
        elif change.action == "delete":
            await process_delete(change, device_token, db)

    await db.commit()

    # Fetch all current tasks for this device
    result = await db.execute(
        select(Task).where(Task.device_token == device_token).order_by(Task.position)
    )
    all_tasks = result.scalars().all()

    return {
        "serverTime": datetime.now(timezone.utc),
        "tasks": all_tasks,
        "conflicts": conflicts,
    }


async def process_create(
    change: SyncCreateChange,
    device_token: uuid.UUID,
    db: AsyncSession,
):
    """
    Process create action from sync request.

    Args:
        change: Create action data
        device_token: Device token
        db: Database session
    """
    # Check if task already exists (idempotency)
    result = await db.execute(select(Task).where(Task.id == change.id))
    existing = result.scalar_one_or_none()

    if not existing:
        new_task = Task(
            id=change.id,
            device_token=device_token,
            text=change.text.strip(),
            position=change.position,
            created_at=change.created_at,
            updated_at=change.updated_at,
        )
        db.add(new_task)


async def process_update(
    change: SyncUpdateChange,
    device_token: uuid.UUID,
    db: AsyncSession,
) -> Optional[Conflict]:
    """
    Process update action from sync request.

    Implements last-write-wins conflict resolution.

    Args:
        change: Update action data
        device_token: Device token
        db: Database session

    Returns:
        Optional[Conflict]: Conflict if server version won, None otherwise
    """
    result = await db.execute(
        select(Task).where(Task.id == change.id, Task.device_token == device_token)
    )
    task = result.scalar_one_or_none()

    if not task:
        # Task doesn't exist - ignore update
        return None

    # Conflict detection: last-write-wins
    if change.updated_at <= task.updated_at:
        # Server version is newer - conflict
        return {
            "localId": change.id,
            "resolution": "server_wins",
            "serverVersion": TaskResponseSync.from_orm(task),
        }

    # Client version is newer - apply update
    if change.text is not None:
        task.text = change.text.strip()
    if change.position is not None:
        task.position = change.position
    task.updated_at = change.updated_at

    return None


async def process_delete(
    change: SyncDeleteChange,
    device_token: uuid.UUID,
    db: AsyncSession,
):
    """
    Process delete action from sync request.

    Deletion always wins (simpler UX per data-model.md).

    Args:
        change: Delete action data
        device_token: Device token
        db: Database session
    """
    result = await db.execute(
        select(Task).where(Task.id == change.id, Task.device_token == device_token)
    )
    task = result.scalar_one_or_none()

    if task:
        await db.delete(task)
