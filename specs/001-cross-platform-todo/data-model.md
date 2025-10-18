# Data Model: Cross-Platform Todo List

**Date**: 2025-10-17
**Feature**: Cross-Platform Todo List (001)
**Purpose**: Define data structures for backend and client storage

## Entity Definitions

### Task

Represents a single todo item with text content and ordering information.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the task |
| `deviceToken` | UUID | NOT NULL, INDEX | Device token that owns this task |
| `text` | VARCHAR(500) | NOT NULL | Task description/content |
| `position` | INTEGER | NOT NULL, DEFAULT 0 | Ordinal position in task list (0 = first/top priority) |
| `createdAt` | TIMESTAMP | NOT NULL, DEFAULT NOW() | UTC timestamp when task was created |
| `updatedAt` | TIMESTAMP | NOT NULL, DEFAULT NOW() | UTC timestamp of last modification |
| `synced` | BOOLEAN | NOT NULL, DEFAULT FALSE | Client-only: indicates if synced to backend |

**Validation Rules**:
- `text` must not be empty after trimming whitespace
- `text` maximum length 500 characters (FR from spec)
- `position` must be >= 0
- `deviceToken` must be valid UUID v4 format
- `updatedAt` must be >= `createdAt`

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `deviceToken` (for filtering tasks by device)
- COMPOSITE INDEX on `(deviceToken, position)` (for ordered retrieval)
- INDEX on `updatedAt` (for sync queries)

**State Transitions**:
```
[New] --create--> [Pending Sync] --sync--> [Synced]
                        |
                        v
                   [Modified] --sync--> [Synced]
                        |
                        v
                   [Deleted] --sync--> [Removed]
```

**Client-Side State** (`synced` field):
- `synced=false`: Local changes not yet persisted to backend
- `synced=true`: Local state matches backend state

---

### Device (implicit entity, not stored)

Devices are identified by their randomly generated token. No explicit device registration needed.

**Fields** (conceptual, for understanding):

| Field | Type | Description |
|-------|------|-------------|
| `deviceToken` | UUID | Unique identifier generated on first launch |
| `platform` | ENUM('android', 'windows') | Platform type (informational only) |
| `lastSyncAt` | TIMESTAMP | Last successful sync timestamp (client-only) |

**Notes**:
- Backend does NOT store device records
- `deviceToken` is generated client-side using UUID v4
- Stored securely in client keystore/data protection
- No device registration API endpoint needed

---

## Data Relationships

```
Device (token) ──1:N──> Task
```

- One device token can have many tasks
- Tasks belong to exactly one device token
- No shared tasks between devices (single-user model)

---

## Backend Database Schema (PostgreSQL)

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_token UUID NOT NULL,
    text VARCHAR(500) NOT NULL CHECK (length(trim(text)) > 0),
    position INTEGER NOT NULL DEFAULT 0 CHECK (position >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT updated_after_created CHECK (updated_at >= created_at)
);

CREATE INDEX idx_tasks_device_token ON tasks(device_token);
CREATE INDEX idx_tasks_device_position ON tasks(device_token, position);
CREATE INDEX idx_tasks_updated_at ON tasks(updated_at);

-- Trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

---

## Client Database Schema (SQLite)

### Android (Room)

```kotlin
@Entity(
    tableName = "tasks",
    indices = [
        Index(value = ["deviceToken"]),
        Index(value = ["deviceToken", "position"]),
        Index(value = ["updatedAt"])
    ]
)
data class Task(
    @PrimaryKey
    val id: String,  // UUID as string

    val deviceToken: String,  // UUID as string

    @ColumnInfo(name = "text")
    val text: String,

    val position: Int,

    @ColumnInfo(name = "createdAt")
    val createdAt: Long,  // Unix timestamp (milliseconds)

    @ColumnInfo(name = "updatedAt")
    val updatedAt: Long,  // Unix timestamp (milliseconds)

    val synced: Boolean = false  // Client-only field
)
```

### Windows (Entity Framework Core)

```csharp
public class Task
{
    [Key]
    public Guid Id { get; set; }

    [Required]
    public Guid DeviceToken { get; set; }

    [Required]
    [MaxLength(500)]
    public string Text { get; set; }

    [Required]
    public int Position { get; set; }

    [Required]
    public DateTime CreatedAt { get; set; }

    [Required]
    public DateTime UpdatedAt { get; set; }

    // Client-only field, not synced to backend
    [NotMapped] // Or separate column if needed for querying
    public bool Synced { get; set; }
}
```

---

## Sync Protocol Data Model

### Full Sync Request (Client → Backend)

```json
{
  "deviceToken": "550e8400-e29b-41d4-a716-446655440000",
  "lastSyncAt": "2025-10-17T10:30:00Z",
  "pendingChanges": [
    {
      "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
      "action": "create",
      "text": "Buy groceries",
      "position": 0,
      "createdAt": "2025-10-17T10:25:00Z",
      "updatedAt": "2025-10-17T10:25:00Z"
    },
    {
      "id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
      "action": "update",
      "text": "Updated task text",
      "position": 1,
      "updatedAt": "2025-10-17T10:28:00Z"
    },
    {
      "id": "c3d4e5f6-a7b8-6c7d-0e1f-2a3b4c5d6e7f",
      "action": "delete",
      "updatedAt": "2025-10-17T10:29:00Z"
    }
  ]
}
```

### Full Sync Response (Backend → Client)

```json
{
  "serverTime": "2025-10-17T10:30:05Z",
  "tasks": [
    {
      "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
      "deviceToken": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Buy groceries",
      "position": 0,
      "createdAt": "2025-10-17T10:25:00Z",
      "updatedAt": "2025-10-17T10:25:00Z"
    },
    {
      "id": "d4e5f6a7-b8c9-7d8e-1f2a-3b4c5d6e7f8a",
      "deviceToken": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Task from another device",
      "position": 2,
      "createdAt": "2025-10-17T09:00:00Z",
      "updatedAt": "2025-10-17T10:15:00Z"
    }
  ],
  "conflicts": [
    {
      "localId": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
      "resolution": "server_wins",
      "serverVersion": {
        "id": "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
        "text": "Different text from another device",
        "position": 1,
        "updatedAt": "2025-10-17T10:29:30Z"
      }
    }
  ]
}
```

---

## Conflict Resolution Logic

### Last-Write-Wins by Timestamp

When the same task ID has different `updatedAt` timestamps:

1. **Backend receives update**: Compare client's `updatedAt` with backend's `updatedAt`
   - If `client.updatedAt > backend.updatedAt`: Accept client version
   - If `client.updatedAt <= backend.updatedAt`: Reject client version, return conflict

2. **Client receives full sync**: For each task in backend response:
   - If task ID doesn't exist locally: Insert
   - If task ID exists locally with `synced=false`: Keep local version if `local.updatedAt > server.updatedAt`, otherwise apply server version
   - If task ID exists locally with `synced=true`: Apply server version

3. **Deletion Conflicts**:
   - If client deletes a task that was modified on another device, deletion wins (simpler UX)
   - If another device deletes a task the client modified, deletion wins (backend removes it)

---

## Data Flow Examples

### Scenario 1: User Adds Task

1. User types task text and confirms
2. Client generates UUID for `id`
3. Client inserts into local SQLite with `synced=false`
4. UI updates immediately (< 1 second per SC-009)
5. Background sync worker wakes up
6. Client sends `{"action": "create", ...}` to backend
7. Backend inserts into PostgreSQL
8. Backend returns success
9. Client updates local record to `synced=true`

### Scenario 2: User Reorders Tasks

1. User drags task from position 3 to position 0
2. Client updates local positions: task moves to 0, tasks at 0-2 shift to 1-3
3. Client marks affected tasks as `synced=false`
4. UI updates immediately (< 1 second)
5. Status bar updates within 2 seconds (SC-003)
6. Background sync sends all modified tasks to backend
7. Backend updates positions
8. Client marks tasks as `synced=true`

### Scenario 3: Conflict Resolution

1. Device A modifies task X at 10:25:00
2. Device B modifies same task X at 10:26:00 (offline)
3. Device A syncs first (task X timestamp = 10:25:00 on backend)
4. Device B syncs second
5. Backend compares timestamps: 10:26:00 > 10:25:00
6. Backend accepts Device B's version (last-write-wins)
7. Device A fetches updates on next sync
8. Device A sees task X changed, overwrites local version

---

## Storage Size Estimates

### Per Task
- UUID (36 bytes) × 2 (id, deviceToken) = 72 bytes
- Text (max 500 bytes UTF-8)
- Integers (position) = 4 bytes
- Timestamps (8 bytes) × 2 = 16 bytes
- **Total**: ~600 bytes per task

### Practical Limits
- 1,000 tasks = ~600 KB
- 10,000 tasks = ~6 MB
- SQLite file size remains manageable for hundreds-thousands of tasks

---

## Security Considerations

### Device Token Storage
- **Android**: Store in `EncryptedSharedPreferences` or Android Keystore
- **Windows**: Store using Data Protection API (DPAPI)
- Never expose token in logs or error messages

### API Authentication
- All backend requests include `Authorization: Bearer <deviceToken>` header
- Backend validates UUID format
- Backend filters all queries by `WHERE device_token = <token>` to prevent cross-device data leakage

### Data Validation
- Backend enforces all constraints (text length, position >= 0, valid UUIDs)
- Client-side validation provides fast feedback but backend is authoritative
