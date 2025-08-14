# 👤 GymBro User Management Service

Servizio di gestione utenti per la piattaforma GymBro con autenticazione JWT e gestione profili completa.

## 📋 Changelog

### v0.1.1 (15 Gennaio 2025)
#### 🚀 CI/CD Integration
- **Docker Registry**: Integrato con GitHub Container Registry
- **Automated Testing**: Pipeline CI/CD con 14 test passanti
- **Quality Gates**: Coverage 80%, code formatting, security scan
- **Container Image**: `ghcr.io/giamma80/gymbro-user-management`

#### 🔧 Technical Improvements
- **Poetry Migration**: Dockerfile aggiornato per usare Poetry
- **Pydantic v2**: Migrazione completa con model_config
- **Environment Setup**: Script automatizzato per testing
- **SQLAlchemy 2.0**: Compatibility fixes per raw queries

### v0.1.0 (14 Agosto 2025)
#### 🎉 Initial Release
- **Service Launch**: Prima versione stabile del servizio User Management
- **Core Authentication**: Sistema completo di registrazione e login

#### ✨ Features
- `/auth/register` - Registrazione nuovi utenti con validazione email
- `/auth/login` - Login con JWT token generation
- `/auth/refresh` - Refresh token per sessioni persistenti
- `/users/profile` - CRUD completo per profili utente
- `/users/preferences` - Gestione preferenze personalizzate
- `/auth/change-password` - Cambio password con validazione
- `/admin/users` - Endpoints amministrativi per gestione utenti

#### 🔧 Technical Details
- **Framework**: FastAPI con supporto async nativo
- **Database**: PostgreSQL con SQLAlchemy async ORM
- **Cache**: Redis per sessioni e rate limiting
- **Authentication**: JWT con access/refresh token pattern
- **Validation**: Pydantic models con validazione completa

#### 📊 Performance Metrics
- Response time: <200ms (95th percentile)
- Database queries: Ottimizzate con connection pooling
- Rate limiting: 60 requests/minute per user
- Uptime target: 99.9%

#### 🔗 Dependencies
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- FastAPI 0.116+

#### 🛡️ Security Features
- Password hashing con bcrypt
- JWT tokens con expiration
- Rate limiting per endpoint
- Input validation e sanitization
- CORS configurato correttamente

#### 📚 Documentation
- API Docs: `http://localhost:8001/docs`
- Health Check: `http://localhost:8001/health`
- OpenAPI Schema: `http://localhost:8001/openapi.json`

---

## 🚀 Caratteristiche

- Registrazione e autenticazione utenti
- Gestione profili utente completa
- Sistema di ruoli e permessi
- Integrazione con JWT per l'autenticazione
- Cache Redis per performance ottimali
- Rate limiting e sicurezza avanzata

## 🛠️ Sviluppo

### Prerequisiti

- Python 3.11+
- Poetry
- PostgreSQL 15+
- Redis 7+

### Installazione

```bash
poetry install
```

### Avvio del servizio

```bash
# Da root del progetto
make dev-user

# O direttamente nella cartella servizio
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Test

```bash
poetry run pytest tests/ -v --cov=.
```

### Linting e formattazione

```bash
poetry run black .
poetry run flake8 .
poetry run mypy .
```

## 📚 API Documentation

Una volta avviato il servizio, la documentazione è disponibile su:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🐳 Docker Deployment

### Container Image
- **Registry**: GitHub Container Registry (GHCR)
- **Image**: `ghcr.io/giamma80/gymbro-user-management:latest`
- **Base**: Python 3.11-slim con Poetry

### Docker Commands
```bash
# Pull dell'immagine (automatico da CI/CD)
docker pull ghcr.io/giamma80/gymbro-user-management:latest

# Run del container
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e REDIS_URL="redis://host:6379" \
  ghcr.io/giamma80/gymbro-user-management:latest
```

### CI/CD Integration
- **Automatic builds** su ogni push al main branch
- **Test automatici** con 14 test coverage
- **Security scanning** con Trivy vulnerability detection
- **Multi-stage build** per immagini ottimizzate

## Struttura del progetto

```
user-management/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Configurazione e sicurezza
│   ├── models/       # Modelli database
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── tests/            # Test suite
├── alembic/          # Database migrations
└── pyproject.toml    # Poetry configuration
```
