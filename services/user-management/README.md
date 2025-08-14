# GymBro User Management Service

Servizio di gestione utenti per la piattaforma GymBro.

## Caratteristiche

- Registrazione e autenticazione utenti
- Gestione profili utente
- Sistema di ruoli e permessi
- Integrazione con JWT per l'autenticazione
- Cache Redis per performance ottimali

## Sviluppo

### Prerequisiti

- Python 3.11+
- Poetry
- PostgreSQL
- Redis

### Installazione

```bash
poetry install
```

### Avvio del servizio

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Test

```bash
poetry run pytest
```

### Linting e formattazione

```bash
poetry run black .
poetry run flake8 .
poetry run mypy .
```

## API Documentation

Una volta avviato il servizio, la documentazione è disponibile su:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

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
