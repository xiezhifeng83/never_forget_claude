# Never Forget Claude Constitution

<!--
Sync Impact Report:
Version: 1.0.0 → 1.0.1
Reason: Clarification update to sync interval default (PATCH version)

Modified Sections:
- Data Flow Requirements > Background Sync: Updated default sync interval from "5 minutes" to "≤ 1 minute" to align with spec requirement FR-010 (status bar refresh ≤ 1 minute)

Impact Analysis:
- This is a clarification, not a breaking change
- Feature 001 spec.md and plan.md already specified ≤ 1 minute sync
- Constitution now matches specification requirements
- No code changes required (implementation not yet started)

Previous Sync Impact Report:
Version: 0.1.0 → 1.0.0
Reason: Initial constitution creation with complete principles and governance structure
Modified Principles: N/A (new constitution)
Added Sections: Core Principles (5 principles), Architecture Constraints, Quality Standards, Governance
Templates Status: All compatible

Follow-up TODOs: None
-->

## Core Principles

### I. Platform-Native Simplicity

The app MUST provide native user experiences on each platform (Android, Windows) while maintaining consistent core functionality. Platform-specific UI patterns and system integrations (status bar, notifications) are required. Design language follows iOS/Mac principles: clean, minimalist, intuitive.

**Rationale**: Cross-platform doesn't mean identical UI. Users expect native behaviors. iOS/Mac design principles provide a proven simplicity model that translates well to other platforms.

### II. Friction-Free Task Capture

Adding a new todo MUST be achievable in under 3 seconds from any screen. Quick-add shortcuts, minimal input fields (just the task text), and instant local storage are mandatory. No authentication required before adding a task.

**Rationale**: The primary user frustration with todo apps is the overhead of capturing thoughts. If adding a task requires navigation, multiple fields, or waiting for sync, users will abandon the tool.

### III. Sync-First Architecture

All clients and backend MUST operate in separate git repositories. The backend exposes a well-defined REST or GraphQL API. Clients sync asynchronously - local operations never block on network. Conflict resolution follows "last-write-wins" with timestamp arbitration.

**Rationale**: Separate repositories enable independent client and backend evolution. Async sync ensures the app remains responsive even offline. Simple conflict resolution avoids over-engineering.

### IV. Code Clarity Over Cleverness

Code MUST prioritize readability and maintainability. No premature optimization, no clever abstractions without demonstrated need. Prefer explicit code over magic. Document "why" decisions, not "what" the code does.

**Rationale**: The spec explicitly states "代码简洁, 结构合理, 不过渡优化" (clean code, reasonable structure, no over-optimization). Clever code becomes technical debt.

### V. Test Pragmatism

Tests are OPTIONAL unless explicitly requested. When tests are written, focus on integration tests for user journeys and contract tests for API boundaries. Unit tests only for complex business logic. No testing for trivial getters/setters or framework code.

**Rationale**: Over-testing increases maintenance burden without proportional value. Critical paths and integration points deserve tests; boilerplate doesn't.

## Architecture Constraints

### Repository Separation

- **Client Repositories**: One repository per platform (android-client, windows-client)
- **Backend Repository**: Single backend repository exposing sync API
- **Shared Schemas**: API contracts versioned independently, shared via npm/Maven packages or API documentation
- **No Shared Code**: Clients do NOT share code repositories (platform-specific implementations are acceptable)

### Data Flow Requirements

- **Local-First**: All UI operations write to local storage first
- **Background Sync**: Periodic background sync (configurable interval, default ≤ 1 minute to support 60-second status bar refresh requirement)
- **Conflict Handling**: Timestamp-based last-write-wins; no complex CRDT required
- **Offline Support**: App MUST function fully offline; sync queue persists pending changes

## Quality Standards

### User Experience Benchmarks

- **Add Task**: Maximum 3 seconds from intent to saved task
- **View Tasks**: Maximum 1 second to display current task list from cold start
- **Sync Latency**: Background sync SHOULD complete within 10 seconds on typical network
- **Status Bar Update**: Top priority task displayed in status bar, updates within 2 seconds of change

### Code Standards

- **Cyclomatic Complexity**: Maximum 10 per function (exceptions require comment justification)
- **File Size**: Maximum 300 lines per file (split at logical boundaries if exceeded)
- **Function Length**: Maximum 50 lines per function (extract helpers for longer logic)
- **Documentation**: All public APIs documented; internal "why" comments for non-obvious decisions

### Design Consistency

- **Visual Language**: Follow iOS Human Interface Guidelines as baseline, adapt to platform conventions
- **Color Palette**: Maximum 3 primary colors, 2 accent colors, standard grays
- **Typography**: Maximum 3 font sizes, consistent weight hierarchy
- **Spacing**: Use 8px grid system (8, 16, 24, 32, 40, 48...)

## Governance

### Amendment Process

1. Propose amendment via pull request to this constitution file
2. Document impact on existing code/architecture in PR description
3. Require approval from project lead or 2+ core contributors
4. Update `CONSTITUTION_VERSION` following semantic versioning rules
5. Update `LAST_AMENDED_DATE` to amendment date
6. Create migration plan if amendment affects existing implementations

### Versioning Policy

- **MAJOR**: Breaking principle changes requiring code rewrites (e.g., removing "Sync-First" principle)
- **MINOR**: New principle additions or substantial expansions (e.g., adding security principle)
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

### Compliance Review

- **During Planning**: `/speckit.plan` MUST include Constitution Check section validating alignment
- **During PR Review**: Reviewers MUST verify no principle violations or document justified exceptions
- **Quarterly Audit**: Review all exceptions/complexity justifications to identify technical debt

### Complexity Justification

Any violation of these principles MUST be documented in the `Complexity Tracking` section of `plan.md` with:
- Which principle is violated
- Why the violation is necessary
- What simpler alternative was rejected and why

**Version**: 1.0.1 | **Ratified**: 2025-10-17 | **Last Amended**: 2025-10-17
