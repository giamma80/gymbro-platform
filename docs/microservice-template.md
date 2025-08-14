# 🏗️ Standard Template per Microservizi GymBro

Questo è il template standardizzato per tutti i microservizi della piattaforma GymBro usando Poetry.

## 📁 Struttura Directory Standard

```
services/{service-name}/
├── app/                    # 📦 Codice applicazione
│   ├── __init__.py
│   ├── main.py            # 🚀 Entry point FastAPI
│   ├── config.py          # ⚙️ Configurazione
│   ├── models.py          # 📋 Pydantic schemas
│   ├── database.py        # 🗄️ SQLAlchemy models
│   ├── auth.py            # 🔐 Autenticazione
│   ├── services.py        # 💼 Business logic
│   └── api/               # 🌐 API endpoints
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── endpoints.py
├── tests/                 # 🧪 Test suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   ├── test_models.py     # Model tests
│   ├── test_auth.py       # Auth tests
│   ├── test_config.py     # Config tests
│   └── test_services.py   # Service tests
├── alembic/               # 📊 Database migrations
├── scripts/               # 🔧 Utility scripts
├── pyproject.toml         # 📦 Poetry configuration
├── poetry.lock            # 🔒 Lock file
├── README.md              # 📚 Documentation
├── .env.example           # 🔐 Environment template
├── .env.test              # 🧪 Test environment
└── Dockerfile             # 🐳 Container definition
```

## 📦 pyproject.toml Template

```toml
[tool.poetry]
name = "gymbro-{service-name}"
version = "1.0.0"
description = "GymBro Platform - {Service Name} Service"
authors = ["GymBro Team <team@gymbro-platform.com>"]
readme = "README.md"
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.116.0"
uvicorn = {extras = ["standard"], version = "^0.35.0"}
pydantic = {extras = ["email"], version = "^2.11.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.43"}
asyncpg = "^0.30.0"
redis = "^6.4.0"
python-jose = {extras = ["cryptography"], version = "^3.5.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.20"
sentry-sdk = {extras = ["fastapi"], version = "^2.34.0"}
structlog = "^24.4.0"
email-validator = "^2.2.0"
pydantic-settings = "^2.10.1"
httpx = "^0.28.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.4.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
black = "^25.1.0"
isort = "^6.0.0"
flake8 = "^7.3.0"
mypy = "^1.17.0"
pre-commit = "^4.0.1"
factory-boy = "^3.3.0"

[tool.poetry.group.test.dependencies]
pytest-mock = "^3.14.0"
pytest-xdist = "^3.6.0"
coverage = "^7.6.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# Tool configurations
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/venv/*", "*/__pycache__/*"]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

## 🧪 Test Structure Standard

### conftest.py
```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    # Test database session
    yield None

@pytest.fixture
async def client():
    # Test FastAPI client
    yield None
```

### test_models.py Template
```python
import pytest
from pydantic import ValidationError
from models import {ModelName}

class Test{ServiceName}Models:
    def test_model_validation(self):
        # Test model validation
        pass
        
    def test_enum_values(self):
        # Test enum values
        pass
```

## 🔧 Makefile Commands Standard

Ogni servizio avrà questi comandi standard:

```makefile
# Service-specific commands
install-{service}:
	@cd services/{service} && poetry install

test-{service}:
	@cd services/{service} && poetry run pytest tests/ -v --cov=app

lint-{service}:
	@cd services/{service} && poetry run flake8 . && poetry run mypy .

format-{service}:
	@cd services/{service} && poetry run black . && poetry run isort .

dev-{service}:
	@cd services/{service} && poetry run uvicorn main:app --reload --port {port}
```

## 🚀 CI/CD Pipeline Standard

```yaml
- name: Set up Poetry
  uses: snok/install-poetry@v1
  with:
    version: latest
    virtualenvs-create: true
    virtualenvs-in-project: true

- name: Cache Poetry dependencies
  uses: actions/cache@v3
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

- name: Install dependencies
  run: poetry install --no-interaction --no-ansi

- name: Run tests
  run: poetry run pytest tests/ -v --cov=app --cov-report=xml

- name: Run linting
  run: |
    poetry run black --check .
    poetry run isort --check-only .
    poetry run flake8 .
    poetry run mypy .
```

## 📝 Documentazione Standard

Ogni servizio avrà:

1. **README.md** con:
   - Descrizione del servizio
   - Setup instructions con Poetry
   - API documentation links
   - Test instructions

2. **Environment files**:
   - `.env.example` - Template per produzione
   - `.env.test` - Variabili per test

## 🔄 Migration Checklist

Per migrare un servizio esistente:

- [ ] Creare `pyproject.toml` dal template
- [ ] Rimuovere `requirements.txt` e `requirements-dev.txt`
- [ ] Creare struttura test standard
- [ ] Aggiornare Makefile commands
- [ ] Aggiornare CI/CD pipeline
- [ ] Aggiornare documentazione
- [ ] Testare che tutto funzioni

## ✨ Best Practices

1. **Dependency Groups**: Separare dev, test e produzione
2. **Lock File**: Sempre committare `poetry.lock`
3. **Version Pinning**: Usare constraint appropriati (^, ~, ==)
4. **Tool Configuration**: Centralizzare in `pyproject.toml`
5. **Testing**: Coverage >= 80% per ogni servizio
6. **Linting**: Zero warnings in produzione

Questo template garantisce consistenza e qualità in tutti i microservizi! 🎯
