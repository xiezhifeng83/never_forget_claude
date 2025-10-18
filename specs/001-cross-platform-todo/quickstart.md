# Quickstart Guide: Cross-Platform Todo List

**Date**: 2025-10-17
**Feature**: Cross-Platform Todo List (001)
**Purpose**: Quick reference for developers implementing this feature

## Overview

This guide provides the essential information needed to build the Never Forget Claude todo list app across Android, Windows, and backend platforms.

## Architecture Summary

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Android   │────────▶│   Backend   │◀────────│   Windows    │
│   Client    │         │  (FastAPI)  │         │   Client     │
│  (Kotlin)   │         │(PostgreSQL) │         │   (C# WinUI) │
└─────────────┘         └─────────────┘         └──────────────┘
      │                                                  │
      └──────── Device Token (UUID v4) ─────────────────┘
```

**Key Principle**: Local-first, async sync
- All operations write to local SQLite first
- Background worker syncs to backend
- Status bar updates within 2 seconds

## Quick Reference

### Device Token Generation

**First Launch Only**:
```kotlin
// Android (Kotlin)
val deviceToken = UUID.randomUUID().toString()
// Store in EncryptedSharedPreferences
```

```csharp
// Windows (C#)
var deviceToken = Guid.NewGuid().ToString();
// Store using DPAPI
```

### Task Data Model

**Core Fields**:
- `id`: UUID (client-generated)
- `deviceToken`: UUID (from first launch)
- `text`: String (max 500 chars)
- `position`: Int (0 = top priority)
- `createdAt`: Timestamp (UTC)
- `updatedAt`: Timestamp (UTC)
- `synced`: Bool (client-only)

### API Endpoints

**Base URL**: `https://api.neverforget.example.com/v1`

**Authentication**: `Authorization: Bearer <deviceToken>`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/tasks` | List all tasks for device |
| POST | `/tasks` | Create new task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| POST | `/tasks/sync` | Full batch sync |

**Full sync recommended** for simplicity - client sends all pending changes, server returns complete task list.

### Status Bar Integration

**Android**:
```kotlin
// NotificationCompat for persistent status bar
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle(firstTask.text)
    .setSmallIcon(R.drawable.ic_todo)
    .setOngoing(true)  // Persistent
    .build()
```

**Windows**:
```csharp
// System tray icon with context menu
var notifyIcon = new NotifyIcon();
notifyIcon.Icon = new Icon("todo.ico");
notifyIcon.Text = firstTask.Text;  // Tooltip
notifyIcon.ContextMenu = BuildTaskMenu();  // Dropdown
```

### Background Sync

**Android** (WorkManager):
```kotlin
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    1, TimeUnit.MINUTES  // Minimum interval
).build()

WorkManager.getInstance(context).enqueue(syncWork)
```

**Windows** (BackgroundTask):
```csharp
// Register background task on app startup
var trigger = new TimeTrigger(60, false);  // 60 minutes minimum
BackgroundTaskBuilder.Register<SyncTask>(trigger);
```

### Offline Queue Pattern

**All Platforms**:
1. User performs action (add/edit/delete/reorder)
2. Write to local SQLite with `synced=false`
3. Update UI immediately
4. Background worker wakes up
5. Query `WHERE synced=false`
6. Send to backend via `/tasks/sync`
7. On success: Update `synced=true`
8. On failure: Retry with exponential backoff

### Conflict Resolution

**Last-Write-Wins** (timestamp-based):
```python
# Backend logic
if client_task.updated_at > server_task.updated_at:
    # Client wins, update server
    db.update(client_task)
else:
    # Server wins, return conflict
    return {
        "conflicts": [{
            "localId": client_task.id,
            "resolution": "server_wins",
            "serverVersion": server_task
        }]
    }
```

**Client handling**:
```kotlin
// Apply server wins
for (conflict in response.conflicts) {
    localDb.update(conflict.serverVersion)
}
```

## Repository Structure

### Backend (this repo)

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   └── task.py          # Task SQLAlchemy model
│   ├── api/
│   │   ├── tasks.py         # Task endpoints
│   │   └── sync.py          # Sync endpoint
│   ├── services/
│   │   ├── sync_service.py  # Sync logic
│   │   └── conflict.py      # Conflict resolution
│   └── database.py          # DB connection
├── requirements.txt
├── Dockerfile
└── README.md
```

### Android Client (separate repo: `never-forget-android`)

```
app/
├── src/main/java/com/neverforget/
│   ├── ui/
│   │   ├── TaskListScreen.kt     # Main UI
│   │   └── StatusBarService.kt   # Notification service
│   ├── data/
│   │   ├── local/
│   │   │   ├── TaskDao.kt        # Room DAO
│   │   │   └── AppDatabase.kt
│   │   ├── remote/
│   │   │   └── TaskApi.kt        # Retrofit interface
│   │   └── repository/
│   │       └── TaskRepository.kt # Mediator
│   ├── workers/
│   │   └── SyncWorker.kt         # Background sync
│   └── models/
│       └── Task.kt               # Data class
```

### Windows Client (separate repo: `never-forget-windows`)

```
NeverForget/
├── Models/
│   └── Task.cs
├── Services/
│   ├── TaskService.cs        # API client
│   ├── LocalDatabase.cs      # EF Core
│   └── SyncService.cs        # Background sync
├── Views/
│   ├── MainWindow.xaml       # Task list UI
│   └── StatusBarIcon.cs      # System tray
└── App.xaml.cs               # Entry point
```

## Development Workflow

### 1. Backend First
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### 2. Then Android or Windows

**Android**:
```bash
# Update BASE_URL in NetworkConfig.kt
./gradlew assembleDebug
```

**Windows**:
```powershell
# Update API_URL in appsettings.json
dotnet build
dotnet run
```

### 3. Testing Flow

1. ✅ Add task on Android → Verify appears in backend DB
2. ✅ Add task on Windows → Verify syncs to Android within 1 minute
3. ✅ Reorder task → Verify status bar updates within 2 seconds
4. ✅ Go offline → Add/edit tasks → Go online → Verify sync works
5. ✅ Edit same task on two devices offline → Verify last-write-wins

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Task add | < 3 seconds | Stopwatch from launch to task saved |
| UI update | < 1 second | Local DB write to UI render |
| Status bar update | < 2 seconds | Task reorder to status bar change |
| Cold start | < 1 second | App launch to task list visible |
| Sync latency | < 10 seconds | Background sync API call duration |

## Common Patterns

### Task Creation
```kotlin
// 1. Generate ID
val task = Task(
    id = UUID.randomUUID().toString(),
    deviceToken = getDeviceToken(),
    text = userInput,
    position = 0,
    createdAt = System.currentTimeMillis(),
    updatedAt = System.currentTimeMillis(),
    synced = false
)

// 2. Save locally
taskDao.insert(task)

// 3. Update UI (immediate)
_taskListState.value = taskDao.getAll()

// 4. Trigger sync (async)
WorkManager.getInstance().enqueue(syncWork)
```

### Task Reordering
```kotlin
// 1. Update positions in memory
val reorderedTasks = tasks.mapIndexed { index, task ->
    task.copy(position = index, synced = false)
}

// 2. Batch update local DB
taskDao.updateAll(reorderedTasks)

// 3. Update status bar (within 2 seconds)
updateStatusBar(reorderedTasks.first())

// 4. Sync in background
syncTasks()
```

### Full Sync
```kotlin
suspend fun syncTasks() {
    // Get pending changes
    val pending = taskDao.getUnsyncedTasks()

    // Build sync request
    val request = SyncRequest(
        lastSyncAt = getLastSyncTimestamp(),
        pendingChanges = pending.map { it.toSyncChange() }
    )

    // Call backend
    val response = apiClient.sync(request)

    // Apply server state
    taskDao.deleteAll()
    taskDao.insertAll(response.tasks)

    // Handle conflicts
    for (conflict in response.conflicts) {
        taskDao.update(conflict.serverVersion)
    }

    // Update last sync time
    saveLastSyncTimestamp(response.serverTime)
}
```

## Environment Configuration

### Backend
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/neverforget
CORS_ORIGINS=http://localhost:3000,app://android
PORT=8000
```

### Android
```kotlin
// gradle.properties or BuildConfig
API_BASE_URL=http://10.0.2.2:8000/v1  // Android emulator localhost
```

### Windows
```json
// appsettings.json
{
  "ApiSettings": {
    "BaseUrl": "http://localhost:8000/v1"
  }
}
```

## Troubleshooting

### Sync Not Working
1. Check device token is persisted correctly
2. Verify Authorization header includes `Bearer <token>`
3. Check backend logs for 401 errors
4. Confirm `synced=false` tasks exist in local DB

### Status Bar Not Updating
1. Android: Check notification channel enabled
2. Windows: Verify system tray icon initialized
3. Check status bar update logic triggers on data change
4. Ensure first task (position=0) is retrieved correctly

### Conflicts Always Losing
1. Verify client sends `updatedAt` in sync requests
2. Check system clocks are synchronized (use NTP)
3. Backend should compare timestamps correctly
4. Client should apply `serverVersion` on conflicts

## Next Steps

After understanding this quickstart:

1. Read [data-model.md](data-model.md) for detailed schema
2. Read [contracts/openapi.yaml](contracts/openapi.yaml) for full API spec
3. Implement backend API following research.md technology choices
4. Build Android client following platform-native patterns
5. Build Windows client following platform-native patterns
6. Run end-to-end sync tests across all platforms

## Key Reminders

✅ **Local-first**: Never block UI on network operations
✅ **Simple design**: Follow iOS/Mac design principles (clean, minimal)
✅ **No over-optimization**: Don't add complexity without demonstrated need
✅ **Constitution compliance**: Check `.specify/memory/constitution.md` for principles
✅ **Tests optional**: Only add if explicitly requested or for critical paths
