# 💻 Development Workflow - NutriFit Platform

## 🎯 Overview

Questo documento definisce il workflow di sviluppo, coding standards, e best practices per la piattaforma NutriFit. Seguiamo un approccio **Domain-Driven Design** con architettura microservizi cloud-native.

## 🌿 Git Workflow

### Branch Strategy (Git Flow Semplificato)

```
main (production)
├── develop (integration)
├── feature/feature-name
├── hotfix/hotfix-name
└── release/version-number
```

#### Branch Types
- **`main`**: Production-ready code, sempre deployabile
- **`develop`**: Integration branch per features complete
- **`feature/*`**: Feature development branch
- **`hotfix/*`**: Critical fixes per production
- **`release/*`**: Release preparation branch

### Workflow Process

#### 1. Feature Development
```bash
# Start da develop
git checkout develop
git pull origin develop

# Crea feature branch
git checkout -b feature/ai-nutrition-coach

# Development...
git add .
git commit -m "feat(ai-coach): implement MCP server integration"

# Push e crea PR
git push origin feature/ai-nutrition-coach
```

#### 2. Commit Message Convention
Seguiamo [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: Nuova feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Scopes:**
- `calorie-balance`: Calorie Balance Service
- `meal-tracking`: Meal Tracking Service
- `health-monitor`: Health Monitor Service
- `notifications`: Notifications Service
- `ai-coach`: AI Nutrition Coach Service
- `mobile`: Flutter app
- `infra`: Infrastructure/deployment
- `docs`: Documentation

**Examples:**
```bash
feat(ai-coach): add MCP server for conversational coaching
fix(meal-tracking): resolve OpenFoodFacts API rate limiting
docs(arch): update microservices diagram with N8N integration
refactor(calorie-balance): improve domain model separation
```

#### 3. Pull Request Process
1. **Create PR** da feature branch verso `develop`
2. **PR Template** deve includere:
   - Descrizione feature/fix
   - Testing coverage report
   - Breaking changes (se presenti)
   - Screenshots (per UI changes)
3. **Code Review** richiesto da almeno 1 reviewer
4. **CI/CD Checks** devono passare:
   - Tests (coverage ≥ 80%)
   - Code quality (black, isort, flake8, mypy)
   - Security scan
   - Docker build
5. **Merge** con squash commit

#### 4. Release Process
```bash
# Create release branch
git checkout develop
git checkout -b release/v1.2.0

# Update version, changelog, docs
# Test release candidate

# Merge to main
git checkout main
git merge release/v1.2.0
git tag v1.2.0

# Deploy to production
git push origin main --tags
```

## 🐍 Python Coding Standards

### Code Style & Formatting

#### Tools Configuration
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "--cov=app --cov-report=term-missing --cov-fail-under=80"
testpaths = ["tests"]
```

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```

### Domain-Driven Design Patterns

#### Project Structure Standard
```
services/{service_name}/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── core/                   # Cross-cutting concerns
│   │   ├── config.py          # Settings
│   │   ├── database.py        # DB connection
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── security.py        # Auth utilities
│   ├── domain/                 # Domain layer (DDD)
│   │   ├── entities/          # Business entities
│   │   ├── value_objects/     # Immutable values
│   │   ├── aggregates/        # Aggregate roots
│   │   ├── repositories/      # Repository interfaces
│   │   └── services/          # Domain services
│   ├── application/            # Application services
│   │   ├── commands/          # Command handlers (CQRS)
│   │   ├── queries/           # Query handlers
│   │   ├── services/          # Application services
│   │   └── dto/               # Data Transfer Objects
│   ├── infrastructure/         # External integrations
│   │   ├── database/          # SQLAlchemy models
│   │   ├── external/          # External API clients
│   │   └── repositories/      # Repository implementations
│   └── api/                    # REST endpoints
│       ├── dependencies.py    # FastAPI dependencies
│       ├── routers/           # API route handlers
│       └── schemas/           # Pydantic models
└── tests/                      # Test suites
    ├── unit/                  # Unit tests
    ├── integration/           # Integration tests
    └── fixtures/              # Test fixtures
```

#### Entity Example
```python
# app/domain/entities/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class User:
    """User domain entity"""
    
    id: uuid.UUID
    email: str
    created_at: datetime
    age: Optional[int] = None
    height_cm: Optional[int] = None
    
    def __post_init__(self):
        """Domain validation"""
        if self.age is not None and (self.age < 13 or self.age > 120):
            raise ValueError("Age must be between 13 and 120")
        
        if self.height_cm is not None and (self.height_cm < 100 or self.height_cm > 250):
            raise ValueError("Height must be between 100 and 250 cm")
    
    def calculate_bmr(self, weight_kg: float, gender: str) -> float:
        """Calculate Basal Metabolic Rate"""
        if not self.age or not self.height_cm:
            raise ValueError("Age and height required for BMR calculation")
        
        if gender.upper() == "MALE":
            return 88.362 + (13.397 * weight_kg) + (4.799 * self.height_cm) - (5.677 * self.age)
        else:
            return 447.593 + (9.247 * weight_kg) + (3.098 * self.height_cm) - (4.330 * self.age)
```

#### Repository Pattern
```python
# app/domain/repositories/user_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from ..entities.user import User

class UserRepository(ABC):
    """User repository interface"""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user entity"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Find user by ID"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass

# app/infrastructure/repositories/sqlalchemy_user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.repositories.user_repository import UserRepository
from app.domain.entities.user import User
from .models import UserModel

class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, user: User) -> User:
        user_model = UserModel(
            id=user.id,
            email=user.email,
            age=user.age,
            height_cm=user.height_cm,
            created_at=user.created_at
        )
        self.session.add(user_model)
        await self.session.commit()
        return user
    
    async def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return User(
                id=user_model.id,
                email=user_model.email,
                age=user_model.age,
                height_cm=user_model.height_cm,
                created_at=user_model.created_at
            )
        return None
```

### FastAPI Best Practices

#### API Router Structure
```python
# app/api/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid

from app.api.dependencies import get_user_service
from app.api.schemas.user import UserResponse, UserCreate, UserUpdate
from app.application.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create new user"""
    try:
        user = await user_service.create_user(user_data)
        return UserResponse.from_entity(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by ID"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_entity(user)
```

#### Pydantic Schemas
```python
# app/api/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr
    age: Optional[int] = Field(None, ge=13, le=120)
    height_cm: Optional[int] = Field(None, ge=100, le=250)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=13, le=120)
    height_cm: Optional[int] = Field(None, ge=100, le=250)

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            age=user.age,
            height_cm=user.height_cm,
            created_at=user.created_at
        )
    
    class Config:
        from_attributes = True
```

## 🧪 Testing Standards

### Testing Strategy
- **Unit Tests**: 80%+ coverage per domain logic
- **Integration Tests**: API endpoints e database
- **E2E Tests**: Critical user journeys
- **Contract Tests**: Inter-service communication

### Test Structure
```python
# tests/unit/domain/test_user.py
import pytest
from datetime import datetime
import uuid
from app.domain.entities.user import User

class TestUser:
    def test_create_valid_user(self):
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            age=25,
            height_cm=175,
            created_at=datetime.now()
        )
        assert user.email == "test@example.com"
        assert user.age == 25
    
    def test_invalid_age_raises_error(self):
        with pytest.raises(ValueError, match="Age must be between"):
            User(
                id=uuid.uuid4(),
                email="test@example.com",
                age=150,  # Invalid age
                height_cm=175,
                created_at=datetime.now()
            )
    
    def test_calculate_bmr_male(self):
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            age=25,
            height_cm=175,
            created_at=datetime.now()
        )
        bmr = user.calculate_bmr(weight_kg=70, gender="MALE")
        assert isinstance(bmr, float)
        assert bmr > 0

# tests/integration/api/test_users.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json={
            "email": "test@example.com",
            "age": 25,
            "height_cm": 175
        })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
```

## 🔧 Development Commands

### Setup Environment
```bash
# Clone repository
git clone https://github.com/giamma80/gymbro-platform.git
cd gymbro-platform

# Setup development environment
make setup-dev
```

### Daily Development
```bash
# Start development environment
make dev-up

# Run tests
make test                    # All tests
make test-unit              # Unit tests only
make test-integration       # Integration tests only

# Code quality
make lint                   # Run all linters
make format                 # Format code (black + isort)
make type-check            # Run mypy

# Quality gate (run before commit)
make quality-check         # lint + test + type-check
```

### Service-Specific Commands
```bash
# Create new microservice
./scripts/create-service.sh meal-tracking meal-tracking

# Start specific service
make dev SERVICE=calorie-balance

# Run tests for specific service
make test SERVICE=meal-tracking

# View logs
make logs SERVICE=calorie-balance
```

## 📋 Definition of Done

### Feature Requirements
- [ ] Domain logic implemented with DDD patterns
- [ ] API endpoints documented (OpenAPI)
- [ ] Unit tests written (≥80% coverage)
- [ ] Integration tests for API endpoints
- [ ] Code passes all quality checks
- [ ] Documentation updated
- [ ] Performance impact assessed
- [ ] Security considerations reviewed

### Code Review Checklist
- [ ] Domain-Driven Design compliance
- [ ] Proper separation of concerns
- [ ] Error handling implemented
- [ ] Input validation complete
- [ ] Type hints provided
- [ ] Docstrings for public methods
- [ ] No hardcoded values
- [ ] Performance optimized
- [ ] Security best practices followed

---

## 🚀 Next Steps

Consulta anche:
- **[Testing Guide](TESTING_GUIDE.md)** - Testing strategy dettagliata *(da creare)*
- **[API Documentation](API_DOCUMENTATION.md)** - REST/GraphQL specifications *(da creare)*
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment procedures
