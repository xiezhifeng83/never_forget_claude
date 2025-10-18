# Research: Cross-Platform Todo List

**Date**: 2025-10-17
**Feature**: Cross-Platform Todo List (001)
**Purpose**: Resolve technical unknowns and establish technology choices for Android, Windows, and backend components

## Research Questions

### 1. Backend Language/Framework Choice

**Question**: Should we use Python/FastAPI, Node.js/Express, or Go for the backend?

**Research Findings**:

- **Python/FastAPI**:
  - Pros: Fast development, excellent async support, automatic OpenAPI docs, type hints
  - Cons: Slightly slower than Go, requires more memory
  - Use case: Rapid prototyping, good for small-medium scale

- **Node.js/Express**:
  - Pros: JavaScript everywhere (if web client planned), large ecosystem, good async
  - Cons: Callback complexity, less type safety than alternatives
  - Use case: Teams with JS expertise, real-time features

- **Go**:
  - Pros: Excellent performance, low memory, built-in concurrency, single binary deployment
  - Cons: More verbose, smaller ecosystem for web frameworks
  - Use case: High performance, scalability, simple deployment

**Decision**: **Python with FastAPI**

**Rationale**:
- Aligns with constitution principle IV (Code Clarity Over Cleverness): FastAPI provides clean, readable code with automatic validation
- Faster development velocity for MVP (constitution principle IV: no over-optimization)
- Automatic OpenAPI schema generation simplifies client integration
- Async support handles concurrent device sync efficiently
- Type hints improve code maintainability
- Project scale (single-user, hundreds of tasks) doesn't require Go's performance

**Alternatives Considered**:
- Go: Rejected because premature optimization; Python performance is sufficient for expected scale
- Node.js: Rejected because no web client planned, no JavaScript synergy benefit

---

### 2. Windows UI Framework

**Question**: Should we use WPF or WinUI 3 for the Windows client?

**Research Findings**:

- **WPF (Windows Presentation Foundation)**:
  - Pros: Mature, extensive documentation, works on Windows 7-11, large community
  - Cons: Older API, less modern UI by default, XAML verbose
  - Use case: Maximum compatibility, proven stability

- **WinUI 3**:
  - Pros: Modern Fluent Design, better performance, Windows 10+ features, future-proof
  - Cons: Windows 10 1809+ only, newer (less mature), smaller community
  - Use case: Modern apps targeting Windows 10/11

**Decision**: **WinUI 3**

**Rationale**:
- Constitution principle I (Platform-Native Simplicity): WinUI 3 provides modern Fluent Design that better aligns with iOS/Mac design principles
- Target platform is Windows 10/11 (spec), so compatibility with Windows 7 not needed
- Better system tray integration for status bar feature
- Future-proof choice for long-term maintenance

**Alternatives Considered**:
- WPF: Rejected because older design language doesn't meet "符合iOS、Mac设计" requirement as well as WinUI 3

---

### 3. Backend Database

**Question**: Should we use PostgreSQL, MySQL, or SQLite for backend storage?

**Research Findings**:

- **PostgreSQL**:
  - Pros: Feature-rich, excellent JSON support, strong data integrity, scalable
  - Cons: Heavier setup, overkill for simple schema
  - Use case: Complex queries, large scale, strong consistency needs

- **MySQL**:
  - Pros: Widely used, good performance, mature ecosystem
  - Cons: Less modern than PostgreSQL, mediocre JSON handling
  - Use case: Traditional relational data, proven production deployments

- **SQLite**:
  - Pros: Zero configuration, single file, embedded, perfect for small scale
  - Cons: Limited concurrency, no network access, size limits
  - Use case: Single-user apps, embedded systems, development/testing

**Decision**: **PostgreSQL**

**Rationale**:
- Even though scale is small, PostgreSQL's JSON support is valuable for flexible task metadata future-proofing
- Constitution principle IV (Code Clarity): PostgreSQL's strong typing and constraints make data model explicit
- Better concurrency support for multiple devices syncing simultaneously
- Still simple enough to not violate "no over-optimization" - FastAPI + PostgreSQL is standard stack
- Production-ready out of the box (SQLite would need migration path for multi-user future)

**Alternatives Considered**:
- SQLite: Rejected because insufficient concurrency for multi-device sync scenario
- MySQL: Rejected because PostgreSQL's JSON and modern features better support simple, explicit schema

---

### 4. Backend Testing Framework

**Question**: What testing framework should we use for the backend?

**Decision**: **pytest**

**Rationale**:
- Standard Python testing framework
- Simple, readable syntax aligns with constitution principle IV
- If tests are requested (optional per constitution V), pytest provides good contract testing support
- FastAPI has excellent pytest integration

**Alternatives Considered**: N/A (pytest is de facto standard for FastAPI)

---

### 5. API Protocol: REST vs GraphQL

**Question**: Should the backend use REST or GraphQL?

**Research Findings**:

- **REST**:
  - Pros: Simple, standard, widely understood, good HTTP caching
  - Cons: Multiple endpoints, potential over-fetching
  - Use case: Simple CRUD, standard operations

- **GraphQL**:
  - Pros: Single endpoint, precise data fetching, strong typing
  - Cons: More complex, caching harder, overkill for simple operations
  - Use case: Complex data requirements, multiple client types

**Decision**: **REST**

**Rationale**:
- Constitution principle IV (Code Clarity Over Cleverness): REST is simpler and more explicit
- Constitution principle IV (no over-optimization): GraphQL adds unnecessary complexity for simple CRUD operations
- Task operations map cleanly to HTTP verbs: GET (list), POST (create), PUT (update), DELETE (delete), PATCH (reorder)
- Standard HTTP caching works well for task list fetching
- Simpler client implementation (no GraphQL client libraries needed)

**Alternatives Considered**:
- GraphQL: Rejected as over-engineering; REST fully meets all requirements with less complexity

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+ (async support)
- **Testing**: pytest (if requested)
- **Deployment**: Docker container (simple, portable)

### Android Client
- **Language**: Kotlin 1.9+
- **UI**: Jetpack Compose + Material Design 3
- **Local DB**: Room (SQLite wrapper)
- **Networking**: Retrofit + OkHttp
- **Background Sync**: WorkManager
- **Testing**: JUnit + Espresso (if requested)

### Windows Client
- **Language**: C# 10+ (.NET 8)
- **UI**: WinUI 3 + Fluent Design
- **Local DB**: Entity Framework Core 8 + SQLite
- **Networking**: HttpClient (built-in)
- **Background Sync**: Windows App SDK Background Tasks
- **Testing**: xUnit (if requested)

### API Protocol
- **REST** with JSON payloads
- **OpenAPI 3.0** schema (auto-generated by FastAPI)
- **Authentication**: Bearer token (device token in header)

---

## Best Practices Research

### Device Token Generation
- **Format**: UUID v4 (128-bit, cryptographically random)
- **Storage**: Android Keystore (Android), Data Protection API (Windows)
- **Transmission**: HTTPS with Bearer token in Authorization header
- **Rotation**: Not needed for MVP (stateless, no security expiry required)

### Status Bar Integration

**Android**:
- Use `NotificationCompat` for persistent notification
- Custom notification layout for dropdown expansion
- `NotificationListenerService` for tap handling

**Windows**:
- Use `NotifyIcon` (system tray icon)
- Custom `ContextMenu` for dropdown list
- `TaskbarIcon` library (Hardcodet.NotifyIcon.Wpf) for WinUI 3

### Background Sync Strategy
- **Periodic Sync**: Every 60 seconds minimum (per spec)
- **Immediate Sync**: On task add/edit/delete/reorder (best effort)
- **Retry Logic**: Exponential backoff (1s, 2s, 4s, max 30s)
- **Conflict Resolution**: Last-write-wins based on `updatedAt` timestamp
- **Queue**: Store pending changes in local DB with `synced` flag

### Offline-First Architecture
1. All operations write to local SQLite first
2. Mark operation as `synced=false`
3. Background service attempts sync
4. On success, mark `synced=true`
5. On conflict, backend timestamp wins, local updates accordingly

---

## Open Questions for Phase 1

1. ~~Backend language~~ → **Resolved: Python/FastAPI**
2. ~~Windows UI framework~~ → **Resolved: WinUI 3**
3. ~~Backend database~~ → **Resolved: PostgreSQL**
4. ~~API protocol~~ → **Resolved: REST**
5. Cross-device sharing mechanism → **Deferred to Phase 1 design** (assumption: manual token sharing, exact UX TBD)

---

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- WinUI 3 Documentation: https://learn.microsoft.com/en-us/windows/apps/winui/winui3/
- Android Background Work: https://developer.android.com/develop/background-work
- PostgreSQL JSON Support: https://www.postgresql.org/docs/current/datatype-json.html
