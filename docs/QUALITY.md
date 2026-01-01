# Quality Assurance

## Testing Strategy

### Framework Stack
| Tool | Purpose |
|------|---------|
| **pytest** | Test framework with fixtures |
| **pytest-asyncio** | Async test support |
| **httpx MockTransport** | External service mocking |
| **Firestore emulator** | Isolated NoSQL testing |
| **SQLite in-memory** | PostgreSQL substitute (conftest.py) |

### Test Coverage

**Unit Tests**
- Business logic validation
- Pydantic model validation
- Database model operations
- Service layer functions

**Integration Tests**
- API endpoint testing
- Database operations
- Authentication flows
- WebSocket connections

### Running Tests

```bash
# Run all tests
make test

# Run specific service tests
pytest services/user-service/tests/
pytest services/itinerary-service/tests/

# Run with coverage
pytest --cov=.

# Run with verbose output
pytest -v
```

---

## Code Quality

### Linting and Formatting

**Ruff** - Fast Python linter and formatter (configured in `pyproject.toml`)

```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

**CI Enforcement**
- Linting runs on every push via GitHub Actions
- Each service linted independently (parallel execution)
- Format violations must be fixed before merge

### Type Safety

**Current Status**: Optional
- mypy is available but not enforced in CI
- Type hints present in most code (Python 3.11+)


### Security

| Area | Implementation |
|------|----------------|
| **Authentication** | Firebase Admin SDK JWT verification |
| **Password Storage** | Handled by Firebase (no plaintext) |
| **SQL Injection** | Prevented via SQLAlchemy ORM |
| **Input Validation** | Pydantic models on all endpoints |
| **CORS** | Configured for allowed origins (`core/app.py`) |
| **Security Scanning** | Safety and Bandit in CI pipeline |

---

## CI/CD Pipeline

### Workflows

**1. CI Pipeline** (`.github/workflows/ci.yml`)
- Per-service linting (Ruff)
- Per-service testing (pytest with coverage)
- Docker validation (syntax and build)
- Configuration checks (Docker Compose, Python syntax)
- Security scanning (Safety, Bandit)

**2. Deploy Pipeline** (`.github/workflows/deploy.yml`)
- Pre-deployment validation (lint + test)
- Docker image builds (validation only)
- Database migrations (Alembic for PostgreSQL services)
- Infrastructure validation (Terraform format/validate)


---

## Quality Checklist

Before committing or deploying:

```bash
# 1. Code quality
ruff check . && ruff format .

# 2. Tests pass
make test

# 3. Type check (optional but recommended)
mypy services/

# 4. Security scan
safety check && bandit -r services/

# 5. Docker builds
docker compose build
```
