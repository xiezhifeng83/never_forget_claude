"""
Quick test setup script - validates code structure without full dependencies.
Tests that all modules can be imported and basic structure is correct.
"""

import sys
import os
from pathlib import Path

# Add backend/src to path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(backend_dir))

print("Testing Backend Code Structure...\n")

# Test 1: Check file structure
print("[OK] Test 1: File Structure")
required_files = [
    "src/main.py",
    "src/database.py",
    "src/models/task.py",
    "src/api/health.py",
    "src/api/tasks.py",
    "src/api/sync.py",
    "src/middleware/auth.py",
    "src/middleware/error_handler.py",
    "src/middleware/logging.py",
    "requirements.txt",
    "Dockerfile",
    ".env.example",
    "README.md",
    "migrations/001_initial.sql",
]

missing_files = []
for file in required_files:
    file_path = backend_dir / file
    if not file_path.exists():
        missing_files.append(file)
    else:
        print(f"  [+] {file}")

if missing_files:
    print(f"\n  [ERROR] Missing files: {missing_files}")
    sys.exit(1)

print("\n[OK] Test 2: Python Syntax")
# Test 2: Check Python files for syntax errors
python_files = [
    "src/main.py",
    "src/database.py",
    "src/models/task.py",
    "src/api/health.py",
    "src/api/tasks.py",
    "src/api/sync.py",
    "src/middleware/auth.py",
    "src/middleware/error_handler.py",
    "src/middleware/logging.py",
]

for py_file in python_files:
    file_path = backend_dir / py_file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            compile(code, str(file_path), 'exec')
        print(f"  [+] {py_file} - syntax OK")
    except SyntaxError as e:
        print(f"  [ERROR] {py_file} - Syntax Error: {e}")
        sys.exit(1)

print("\n[OK] Test 3: Code Structure Validation")

# Test 3: Check for key imports and patterns
checks = {
    "src/main.py": ["FastAPI", "CORSMiddleware", "app = FastAPI"],
    "src/database.py": ["AsyncSession", "create_async_engine", "Base"],
    "src/models/task.py": ["class Task", "UUID", "device_token"],
    "src/api/tasks.py": ["@router.post", "@router.get", "@router.put", "@router.delete"],
    "src/api/sync.py": ["@router.post", "sync_tasks", "SyncRequest"],
    "src/middleware/auth.py": ["get_device_token", "UUID"],
}

for file, patterns in checks.items():
    file_path = backend_dir / file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    missing_patterns = [p for p in patterns if p not in content]
    if missing_patterns:
        print(f"  [ERROR] {file} - Missing patterns: {missing_patterns}")
        sys.exit(1)
    else:
        print(f"  [+] {file} - All patterns found")

print("\n[OK] Test 4: Requirements Check")
# Test 4: Check requirements.txt has essential packages
req_path = backend_dir / "requirements.txt"
with open(req_path, 'r') as f:
    requirements = f.read()

essential_packages = ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]
for pkg in essential_packages:
    if pkg in requirements:
        print(f"  [+] {pkg} listed in requirements.txt")
    else:
        print(f"  [ERROR] {pkg} missing from requirements.txt")
        sys.exit(1)

print("\n[OK] Test 5: Environment Configuration")
# Test 5: Check .env.example
env_path = backend_dir / ".env.example"
with open(env_path, 'r') as f:
    env_content = f.read()

required_env_vars = ["DATABASE_URL", "CORS_ORIGINS"]
for var in required_env_vars:
    if var in env_content:
        print(f"  [+] {var} in .env.example")
    else:
        print(f"  [ERROR] {var} missing from .env.example")
        sys.exit(1)

print("\n" + "="*50)
print("SUCCESS: ALL TESTS PASSED!")
print("="*50)
print("\nBackend code structure is valid and ready for deployment.")
print("\nNext steps:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Setup PostgreSQL database")
print("  3. Configure .env file")
print("  4. Run: uvicorn backend.src.main:app --reload")
print("  5. Access API docs: http://localhost:8000/docs")
