# Never Forget Claude

A cross-platform todo list application with real-time synchronization, designed for seamless task management across multiple devices.

## Overview

Never Forget Claude is a modern, minimalist task management system that synchronizes your todos across Windows desktop, Android, and web platforms. Built with a focus on simplicity and reliability, it uses a FastAPI backend with PostgreSQL/SQLite for robust data persistence and device-agnostic UUID-based authentication.

## Features

- **Cross-Platform Support**: Unified experience across Windows, Android, and web
- **Device-Based Sync**: No user accounts required - each device gets a unique token
- **Real-Time Synchronization**: Last-write-wins conflict resolution
- **Offline-First**: Works offline, syncs when connected
- **RESTful API**: Clean OpenAPI-documented endpoints
- **Modern Stack**: FastAPI, async SQLAlchemy 2.0, PostgreSQL/SQLite

## Architecture

```
never_forget_claude/
├── backend/           # FastAPI backend server
│   ├── src/
│   │   ├── main.py           # Application entry point
│   │   ├── database.py       # Database configuration
│   │   ├── models/           # SQLAlchemy models
│   │   ├── api/              # API endpoints
│   │   ├── middleware/       # Auth, logging, error handling
│   │   └── services/         # Business logic
│   ├── migrations/           # Database migrations
│   ├── tests/               # Backend tests
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Docker configuration
│   └── README.md           # Backend documentation
├── specs/                  # Feature specifications
└── README.md              # This file
```

## Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **Database**: PostgreSQL 15+ (production) or SQLite (development)
- **pip**: Python package manager

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/never_forget_claude.git
   cd never_forget_claude
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your database credentials
   ```

4. **Run the server**
   ```bash
   # Development with SQLite
   export DATABASE_URL="sqlite+aiosqlite:///./test_database.db"
   uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000

   # Production with PostgreSQL
   export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/neverforget"
   uvicorn backend.src.main:app --host 0.0.0.0 --port 8000
   ```

5. **Access the API**
   - **API**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

### Using the API

#### Authentication
All endpoints (except `/health`) require a device token in the Authorization header:

```bash
Authorization: Bearer <uuid-v4-device-token>
```

Generate a device token:
```bash
python -c "import uuid; print(uuid.uuid4())"
```

#### Example Requests

**Health Check** (no auth required)
```bash
curl http://localhost:8000/health
```

**Create a Task**
```bash
DEVICE_TOKEN="your-uuid-here"
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $DEVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Buy groceries",
    "position": 0
  }'
```

**List Tasks**
```bash
curl http://localhost:8000/tasks \
  -H "Authorization: Bearer $DEVICE_TOKEN"
```

**Update a Task**
```bash
TASK_ID="task-uuid-here"
curl -X PUT http://localhost:8000/tasks/$TASK_ID \
  -H "Authorization: Bearer $DEVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Buy groceries and cook dinner",
    "position": 0
  }'
```

**Delete a Task**
```bash
curl -X DELETE http://localhost:8000/tasks/$TASK_ID \
  -H "Authorization: Bearer $DEVICE_TOKEN"
```

**Batch Synchronization**
```bash
curl -X POST http://localhost:8000/tasks/sync \
  -H "Authorization: Bearer $DEVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "id": "uuid-1",
        "text": "Task 1",
        "position": 0,
        "updated_at": "2025-10-18T00:00:00Z"
      }
    ],
    "last_sync": "2025-10-17T00:00:00Z"
  }'
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | API welcome message | No |
| GET | `/health` | Health check | No |
| GET | `/tasks` | List all tasks | Yes |
| POST | `/tasks` | Create a new task | Yes |
| GET | `/tasks/{id}` | Get specific task | Yes |
| PUT | `/tasks/{id}` | Update a task | Yes |
| DELETE | `/tasks/{id}` | Delete a task | Yes |
| POST | `/tasks/sync` | Batch sync with conflict resolution | Yes |

## Development

### Database Migrations

The application uses SQLAlchemy's declarative models with automatic table creation on startup. For production, consider using Alembic:

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

### Docker Deployment

**Build the image**
```bash
cd backend
docker build -t never-forget-api .
```

**Run the container**
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host/db \
  -e CORS_ORIGINS=http://localhost:3000 \
  --name never-forget-api \
  never-forget-api
```

## Project Structure

### Backend (`backend/`)
- **FastAPI** application with async support
- **SQLAlchemy 2.0** for database operations
- **Pydantic** for data validation
- **UUID-based** authentication (no user accounts)
- **CORS** middleware for cross-platform clients

### Data Model
- **Task**: Core entity with UUID, device token, text, position, timestamps
- **Conflict Resolution**: Last-write-wins based on `updated_at`
- **Device Authentication**: Each device gets a unique UUID token

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Python**: 3.11+
- **Database**: PostgreSQL 15+ (production), SQLite (development)
- **ORM**: SQLAlchemy 2.0 (async)
- **Server**: Uvicorn
- **Validation**: Pydantic 2.5+

### Future Clients
- **Windows**: Electron + React
- **Android**: Kotlin + Jetpack Compose
- **Web**: React + TypeScript

## Configuration

Environment variables (set in `backend/.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `postgresql+asyncpg://...` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |
| `DEBUG` | Enable debug mode | `False` |

## Synchronization Strategy

1. **Last-Write-Wins**: Tasks are resolved based on `updated_at` timestamp
2. **Batch Sync**: `/tasks/sync` endpoint accepts array of tasks and `last_sync` timestamp
3. **Conflict Resolution**: Server returns all tasks modified after `last_sync`
4. **Offline Support**: Clients cache locally and sync when online

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Principles

- **Simplicity First**: No unnecessary complexity
- **Functions < 50 lines**: Keep code maintainable
- **Type Hints**: Full type annotations
- **Async by Default**: Use async/await throughout
- **Documentation**: Clear docstrings for all public APIs

## Troubleshooting

### Database Connection Errors
1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL format: `postgresql+asyncpg://user:pass@host:port/dbname`
3. Create database if needed: `createdb neverforget`

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### CORS Issues
Add your client origin to `CORS_ORIGINS` in `.env`:
```bash
CORS_ORIGINS=http://localhost:3000,app://android,http://localhost:5173
```

## Roadmap

- [x] Backend API with FastAPI
- [x] SQLAlchemy models and migrations
- [x] Device-based authentication
- [x] Batch synchronization endpoint
- [x] Docker support
- [ ] Windows desktop client (Electron)
- [ ] Android mobile app (Kotlin)
- [ ] Web client (React)
- [ ] Real-time WebSocket updates
- [ ] Task categories and tags
- [ ] Recurring tasks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Documentation

- **API Documentation**: http://localhost:8000/docs (when running)
- **Backend README**: [backend/README.md](backend/README.md)
- **Specifications**: [specs/](specs/)
- **Data Model**: [specs/001-cross-platform-todo/data-model.md](specs/001-cross-platform-todo/data-model.md)

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with Claude Code** - A modern task management solution for the multi-device era.
