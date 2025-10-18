# Implementation Plan: Cross-Platform Todo List

**Branch**: `001-cross-platform-todo` | **Date**: 2025-10-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-cross-platform-todo/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Cross-platform todo list app for Android and Windows with system status bar integration. Core features: quick task capture (< 3 seconds), drag-to-reorder tasks, status bar displaying top task with dropdown showing up to 15 tasks, real-time backend sync with offline support. No user accounts - each device uses a randomly generated token for authentication. Design follows iOS/Mac principles for simplicity.

## Technical Context

**Language/Version**:
- Android: Kotlin 1.9+
- Windows: C# 10+ with .NET 8
- Backend: Python 3.11+ with FastAPI 0.104+

**Primary Dependencies**:
- Android: AndroidX, Room, Retrofit/OkHttp, WorkManager, Jetpack Compose
- Windows: WinUI 3, Entity Framework Core 8, Windows App SDK
- Backend: FastAPI, SQLAlchemy 2.0 (async), PostgreSQL driver

**Storage**:
- Client: SQLite (Android: Room, Windows: EF Core)
- Backend: PostgreSQL 15+

**Testing**:
- Android: JUnit, Espresso (if tests requested)
- Windows: xUnit (if tests requested)
- Backend: pytest (if tests requested)

**Target Platform**:
- Android: API 24+ (Android 7.0+, covers 95%+ devices)
- Windows: Windows 10/11

**Project Type**: mobile + desktop + API (3 separate repositories per constitution)

**Performance Goals**:
- Task add: < 1 second UI update, < 3 seconds total
- Status bar refresh: < 2 seconds after task reorder
- Cold start: < 1 second to display task list
- Sync latency: < 10 seconds under normal network conditions

**Constraints**:
- Offline-first: all operations must work without network
- Status bar update: within 2 seconds of changes
- Background sync: minimum every 60 seconds
- Task text limit: 500 characters

**Scale/Scope**:
- Expected users: single-user per device, no multi-user features
- Task volume: hundreds of tasks per user (practical limit)
- Platforms: 2 (Android, Windows)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Platform-Native Simplicity ✅ PASS

- ✅ Native apps planned for Android (Kotlin/Java) and Windows (C#)
- ✅ Platform-specific UI: Android Material Design, Windows Fluent Design
- ✅ Status bar integration uses native APIs (Android NotificationManager, Windows system tray)
- ✅ Design follows iOS/Mac principles (clean, minimalist) adapted to each platform

### II. Friction-Free Task Capture ✅ PASS

- ✅ No authentication required before adding tasks (device token auto-generated)
- ✅ Quick add: < 3 seconds from launch to task saved (SC-001)
- ✅ Minimal input: text-only, no mandatory additional fields (FR-002)
- ✅ Instant local storage, async backend sync (FR-011, FR-013)

### III. Sync-First Architecture ✅ PASS

- ✅ Separate repositories planned: android-client, windows-client, backend
- ✅ REST or GraphQL API for backend (to be decided in Phase 0)
- ✅ Async sync: local operations never block (FR-013)
- ✅ Last-write-wins conflict resolution with timestamps (FR-015)

### IV. Code Clarity Over Cleverness ✅ PASS

- ✅ Explicit requirement for clean, simple code (constitution principle)
- ✅ No over-optimization (stated in original requirements)
- ✅ Straightforward architecture: local SQLite + REST API + backend DB

### V. Test Pragmatism ✅ PASS

- ✅ Tests marked as OPTIONAL in task template
- ✅ Focus on integration/contract tests when needed (not unit testing boilerplate)

### Architecture Constraints ✅ PASS

- ✅ Repository separation: 3 separate repos (android-client, windows-client, backend)
- ✅ Local-first data flow: UI writes to SQLite first (FR-013)
- ✅ Background sync: configurable interval, default ≤ 1 minute (FR-010, constitution)
- ✅ Offline support: full functionality offline, queued sync (FR-013)

### Quality Standards ✅ PASS

All UX benchmarks from constitution align with success criteria:
- ✅ Add task: < 3 seconds (SC-001, constitution: < 3 seconds)
- ✅ View tasks: < 1 second cold start (SC-009, constitution: < 1 second)
- ✅ Sync latency: < 10 seconds typical (constitution: < 10 seconds)
- ✅ Status bar update: < 2 seconds (SC-003, constitution: < 2 seconds)

**Result**: All gates PASSED. No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```
specs/001-cross-platform-todo/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root - this repo is BACKEND only per constitution)

Per constitution requirement, we need 3 separate repositories:

1. **never-forget-android** (separate repo)
2. **never-forget-windows** (separate repo)
3. **never-forget-backend** (this repo or separate repo)

Since this is a mono-repo planning session, I'll define the structure for the backend here. Client repo structures will be documented in Phase 1.

```
backend/
├── src/
│   ├── models/          # Task, DeviceToken data models
│   ├── services/        # Business logic (sync, conflict resolution)
│   ├── api/             # REST/GraphQL endpoints
│   └── storage/         # Database layer
└── tests/               # Optional: contract tests for API
```

**Structure Decision**: Using "Mobile + API" pattern (Option 3) with separate repositories. This repo will contain backend only. Android and Windows clients will be in separate repos per constitution principle III (Sync-First Architecture - separate repositories).

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

No violations detected. All constitution principles align with feature requirements.
