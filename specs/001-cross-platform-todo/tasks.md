# Tasks: Cross-Platform Todo List

**Input**: Design documents from `specs/001-cross-platform-todo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: NOT requested in specification - tasks focus on implementation only per constitution principle V (Test Pragmatism)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Per constitution: **3 separate repositories** (android-client, windows-client, backend)

This tasks.md covers **BACKEND** implementation. Separate task lists needed for Android and Windows clients.

**Backend paths** (this repo):
- `backend/src/` - Source code
- `backend/tests/` - Optional tests

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for backend

- [X] T001 Create backend directory structure per plan.md (backend/src/, backend/tests/)
- [X] T002 Initialize Python project with FastAPI dependencies in backend/requirements.txt
- [X] T003 [P] Create PostgreSQL database schema from data-model.md in backend/src/database.py
- [X] T004 [P] Configure environment variables for DATABASE_URL, CORS origins in backend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Setup FastAPI application instance with CORS middleware in backend/src/main.py
- [X] T006 [P] Create Task SQLAlchemy model per data-model.md in backend/src/models/task.py
- [X] T007 [P] Implement device token validation middleware in backend/src/middleware/auth.py
- [X] T008 Create database connection pool with async SQLAlchemy in backend/src/database.py
- [X] T009 [P] Implement error handling middleware for API exceptions in backend/src/middleware/error_handler.py
- [X] T010 Create health check endpoint in backend/src/api/health.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Task Capture (Priority: P1) 🎯 MVP

**Goal**: Enable users to add tasks quickly with text-only input, save locally, and sync to backend

**Independent Test**: Launch app, add task with text only, verify it appears in list within 1 second and syncs to backend

### Implementation for User Story 1

- [X] T011 [US1] Create POST /tasks endpoint in backend/src/api/tasks.py
- [X] T012 [US1] Implement task creation service with UUID generation in backend/src/services/task_service.py (merged into T011 per constitution)
- [X] T013 [US1] Add task validation (text length, device token) in backend/src/services/task_service.py (implemented via Pydantic in T011)
- [X] T014 [US1] Implement database insert for new tasks in backend/src/services/task_service.py (merged into T011 per constitution)
- [X] T015 [US1] Add automatic timestamp generation (createdAt, updatedAt) in backend/src/models/task.py (completed in T006)

**Checkpoint**: At this point, User Story 1 backend is complete - clients can create tasks via POST /tasks

---

## Phase 4: User Story 2 - Status Bar Quick Access (Priority: P1)

**Goal**: Provide API endpoints for retrieving tasks to display in status bar and dropdown

**Independent Test**: Query GET /tasks, verify returns tasks ordered by position, first task is top priority

### Implementation for User Story 2

- [X] T016 [US2] Create GET /tasks endpoint with device token filtering in backend/src/api/tasks.py
- [X] T017 [US2] Implement task retrieval service ordered by position in backend/src/services/task_service.py (merged into T016 per constitution)
- [X] T018 [US2] Add query parameter for limiting results (e.g., ?limit=15 for dropdown) in backend/src/api/tasks.py
- [X] T019 [US2] Add since parameter for delta sync (?since=timestamp) in backend/src/api/tasks.py (completed in T016)
- [X] T020 [US2] Optimize database query with indexes on (device_token, position) per data-model.md (completed in T006)

**Checkpoint**: At this point, User Story 2 backend is complete - clients can retrieve ordered task lists

---

## Phase 5: User Story 3 - Task Management (Priority: P2)

**Goal**: Enable task editing, deletion, and reordering with conflict resolution

**Independent Test**: Edit task text, delete task, reorder tasks - verify all operations persist and sync correctly

### Implementation for User Story 3

- [X] T021 [P] [US3] Create GET /tasks/{id} endpoint for single task retrieval in backend/src/api/tasks.py
- [X] T022 [P] [US3] Create PUT /tasks/{id} endpoint for task updates in backend/src/api/tasks.py
- [X] T023 [US3] Implement task update service with timestamp comparison in backend/src/services/task_service.py (merged into T022 per constitution)
- [X] T024 [US3] Add last-write-wins conflict detection (compare updatedAt) in backend/src/services/task_service.py (implemented in T022)
- [X] T025 [US3] Return 409 Conflict response with server version when client update is older in backend/src/api/tasks.py (implemented in T022)
- [X] T026 [P] [US3] Create DELETE /tasks/{id} endpoint in backend/src/api/tasks.py
- [X] T027 [US3] Implement task deletion service in backend/src/services/task_service.py (merged into T026 per constitution)
- [X] T028 [US3] Add position reordering logic (batch update positions) in backend/src/services/task_service.py (client handles via multiple PUT requests)
- [X] T029 [US3] Implement automatic updatedAt trigger per data-model.md SQL in backend/src/models/task.py (completed in T006)

**Checkpoint**: At this point, User Story 3 backend is complete - full CRUD operations available

---

## Phase 6: User Story 4 - Multi-Platform Consistency (Priority: P2)

**Goal**: Implement batch sync endpoint for efficient cross-device synchronization

**Independent Test**: Send pending changes from one device, verify sync endpoint returns current state and resolves conflicts

### Implementation for User Story 4

- [X] T030 [US4] Create POST /tasks/sync batch endpoint in backend/src/api/sync.py
- [X] T031 [US4] Implement sync request parser (pendingChanges array) in backend/src/services/sync_service.py (merged into T030 per constitution)
- [X] T032 [US4] Process create actions from sync request in backend/src/services/sync_service.py (implemented in T030)
- [X] T033 [US4] Process update actions with conflict detection in backend/src/services/sync_service.py (implemented in T030)
- [X] T034 [US4] Process delete actions in backend/src/services/sync_service.py (implemented in T030)
- [X] T035 [US4] Build full sync response with all tasks for device token in backend/src/services/sync_service.py (implemented in T030)
- [X] T036 [US4] Add conflicts array to response when server version wins in backend/src/services/sync_service.py (implemented in T030)
- [X] T037 [US4] Include serverTime in response for client sync tracking in backend/src/api/sync.py (implemented in T030)
- [X] T038 [US4] Optimize batch operations with transaction support in backend/src/services/sync_service.py (implemented in T030)

**Checkpoint**: All user stories backend implementation complete - full sync capability ready

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and deployment readiness

- [X] T039 [P] Add API request logging with device token (masked) in backend/src/middleware/logging.py
- [X] T040 [P] Create OpenAPI documentation generation in backend/src/main.py (FastAPI auto-generates at /docs and /redoc)
- [ ] T041 [P] Add rate limiting per device token (e.g., 100 req/min) in backend/src/middleware/rate_limit.py (optional - deferred)
- [X] T042 [P] Create Docker configuration for backend deployment in backend/Dockerfile
- [X] T043 [P] Add database migration script from data-model.md schema in backend/migrations/001_initial.sql
- [X] T044 [P] Create README.md with setup instructions in backend/README.md
- [X] T045 Validate quickstart.md instructions against implemented backend
- [X] T046 Performance optimization: Add database connection pooling in backend/src/database.py (completed in T003)
- [X] T047 Security hardening: Validate UUID format for device tokens in backend/src/middleware/auth.py (completed in T007)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel after foundation (if backend-only scope)
  - Or sequentially in priority order (P1 → P1 → P2 → P2)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Task Capture)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - Status Bar)**: Can start after Foundational (Phase 2) - No dependencies (just reads tasks)
- **User Story 3 (P2 - Management)**: Can start after Foundational (Phase 2) - Builds on US1 (uses same Task model)
- **User Story 4 (P2 - Sync)**: Can start after Foundational (Phase 2) - Integrates all previous stories into batch endpoint

### Within Each User Story

- Models and middleware before services
- Services before API endpoints
- Core implementation before optimization
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T004)
- All Foundational tasks marked [P] can run in parallel (T006, T007, T009)
- User Story 1 and 2 can run in parallel (different endpoints, no shared code)
- Within User Story 3: T021 and T022 can run in parallel (different operations)
- Within User Story 3: T026 can run in parallel with T021-T025 (delete vs update)
- All Polish tasks marked [P] can run in parallel (T039-T044)

---

## Parallel Example: User Story 1 & 2

```bash
# These can be built simultaneously by different developers:
Task T011: "Create POST /tasks endpoint" (US1)
Task T016: "Create GET /tasks endpoint" (US2)

# They share the Task model (T006) but operate on different HTTP methods
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T010) - **CRITICAL checkpoint**
3. Complete Phase 3: User Story 1 (T011-T015) - Basic task creation
4. Complete Phase 4: User Story 2 (T016-T020) - Task retrieval for status bar
5. **STOP and VALIDATE**: Test task creation and retrieval independently
6. Deploy backend MVP (clients can add tasks and view in status bar)

### Incremental Delivery

1. Complete Setup + Foundational → Backend foundation ready
2. Add User Story 1 + 2 → Deploy (MVP! - Create and view tasks)
3. Add User Story 3 → Deploy (Full CRUD operations)
4. Add User Story 4 → Deploy (Cross-device sync)
5. Each story adds value without breaking previous functionality

### Parallel Team Strategy (Backend Only)

With multiple backend developers:

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - Developer A: User Story 1 (T011-T015)
   - Developer B: User Story 2 (T016-T020)
   - Developer C: User Story 3 (T021-T029) - can start after A finishes if needed
3. Developer D: User Story 4 (T030-T038) - integrates all previous work
4. All developers: Polish phase in parallel (T039-T047)

---

## Notes for Multi-Repository Setup

**IMPORTANT**: This tasks.md covers **BACKEND ONLY**.

**Additional Task Lists Needed**:

1. **Android Client** (`never-forget-android` repo):
   - Setup: Kotlin project, Room, Retrofit, WorkManager dependencies
   - Foundational: Device token generation, local SQLite database, API client
   - US1: Task capture UI with Jetpack Compose, local task DAO
   - US2: Android NotificationManager status bar integration, dropdown UI
   - US3: Edit/delete/drag-to-reorder UI, position update logic
   - US4: Background sync worker with WorkManager, conflict resolution logic

2. **Windows Client** (`never-forget-windows` repo):
   - Setup: C# WinUI 3 project, Entity Framework Core, HTTP client dependencies
   - Foundational: Device token generation (DPAPI), local SQLite via EF Core
   - US1: Task capture UI with WinUI 3, local database context
   - US2: Windows system tray integration, dropdown context menu
   - US3: Edit/delete/drag UI with WinUI, reorder logic
   - US4: Background task registration, sync service, conflict handling

---

## Task Validation Checklist

✅ **Format Compliance**:
- All tasks have checkbox `- [ ]`
- All tasks have unique ID (T001-T047)
- User story tasks have [US#] label
- Parallel tasks have [P] marker
- All tasks include file paths

✅ **Organization**:
- Tasks grouped by user story
- Each story independently testable
- Clear checkpoints after each phase
- Dependencies documented

✅ **Coverage**:
- All functional requirements mapped to tasks
- All data model entities have creation tasks
- All API endpoints from contracts/ covered
- Backend-specific scope (3-repo separation noted)

✅ **Execution Readiness**:
- Each task is concrete and actionable
- File paths specified for code location
- No vague "implement X" without context
- Constitution compliance verified (no over-optimization, clear structure)
