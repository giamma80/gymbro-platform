# Migrazione da pip a Poetry - GymBro Platform

## Panoramica

Abbiamo migrato il sistema di gestione delle dipendenze da `pip + requirements.txt` a Poetry per migliorare:

- **Risoluzione delle dipendenze**: Poetry risolve automaticamente i conflitti di dipendenze
- **Lock file deterministico**: `poetry.lock` garantisce build riproducibili
- **Gestione ambienti virtuali**: Poetry gestiona automaticamente i virtual environments
- **Separazione dipendenze**: Separazione chiara tra dipendenze di produzione e sviluppo
- **Build e packaging**: Supporto nativo per build e distribuzione di pacchetti Python

## Cosa è cambiato

### File di configurazione

- ✅ **Nuovo**: `pyproject.toml` - Configurazione centralizzata di Poetry
- ✅ **Nuovo**: `poetry.lock` - Lock file per dipendenze deterministiche
- ❌ **Rimosso**: `requirements.txt` - Sostituito da pyproject.toml
- ❌ **Rimosso**: `requirements-dev.txt` - Dipendenze dev ora in pyproject.toml

### Comandi aggiornati

| Operazione | Vecchio comando | Nuovo comando |
|------------|----------------|---------------|
| **Installazione** | `pip install -r requirements.txt` | `poetry install` |
| **Aggiunta dipendenza** | `pip install package` | `poetry add package` |
| **Aggiunta dipendenza dev** | `pip install package` (manual req-dev.txt) | `poetry add --group dev package` |
| **Aggiornamento** | `pip install --upgrade -r requirements.txt` | `poetry update` |
| **Esecuzione script** | `python script.py` | `poetry run python script.py` |
| **Attivazione ambiente** | `source venv/bin/activate` | Automatico con `poetry run` |
| **Test** | `python -m pytest` | `poetry run pytest` |
| **Linting** | `flake8 .` | `poetry run flake8 .` |

### Makefile aggiornato

Tutti i comandi nel Makefile sono stati aggiornati per usare Poetry:

```makefile
# Prima
install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

# Ora
install:
	poetry install

test:
	poetry run pytest tests/ -v
```

### CI/CD Pipeline aggiornata

La pipeline GitHub Actions è stata aggiornata:

```yaml
# Prima
- run: pip install -r requirements.txt

# Ora
- run: poetry install --no-root
- run: poetry run pytest
- run: poetry run flake8 .
```

## Vantaggi della migrazione

### 1. Risoluzione dipendenze migliorata
Poetry risolve automaticamente i conflitti di versione e garantisce compatibilità.

### 2. Build riproducibili
Il file `poetry.lock` blocca le versioni esatte di tutte le dipendenze (incluse quelle transitive).

### 3. Gestione ambienti semplificata
Poetry crea e gestisce automaticamente virtual environments isolati.

### 4. Separazione chiara delle dipendenze
```toml
[tool.poetry.dependencies]  # Produzione
python = "^3.11"
fastapi = "^0.115.6"

[tool.poetry.group.dev.dependencies]  # Solo sviluppo
pytest = "^8.0.0"
black = "^24.0.0"
```

### 5. Configurazione centralizzata
Un singolo file `pyproject.toml` contiene:
- Dipendenze
- Metadati del progetto
- Configurazione strumenti (black, mypy, pytest, etc.)

## Prossimi passi

1. **✅ User Management**: Già migrato
2. **🔄 Altri servizi**: Da migrare gradualmente
3. **📚 Documentazione**: Aggiornare README di ogni servizio
4. **🔧 Script**: Aggiornare eventuali script di deployment

## Note per gli sviluppatori

### Installazione Poetry (se non presente)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Workflow quotidiano

```bash
# Clona il progetto
git clone <repo>
cd gymbro-platform/services/user-management

# Installa dipendenze (crea automaticamente venv)
poetry install

# Esegui comandi
poetry run uvicorn main:app --reload
poetry run pytest
poetry run black .

# Aggiungi nuove dipendenze
poetry add requests
poetry add --group dev pytest-cov
```

### Vantaggi per il team

- **Onboarding semplificato**: Un comando (`poetry install`) per setup completo
- **Ambienti consistenti**: Stesso `poetry.lock` = stesso ambiente per tutti
- **Meno conflitti**: Poetry previene dipendenze incompatibili
- **CI/CD più veloce**: Cache intelligente delle dipendenze

## Troubleshooting

### "Command not found: poetry"
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### "ModuleNotFoundError" durante i test
```bash
poetry run pytest  # Assicurati di usare 'poetry run'
```

### Problemi con il virtual environment
```bash
poetry env info  # Mostra info sull'ambiente attuale
poetry env remove python  # Rimuovi ambiente corrotto
poetry install  # Ricrea ambiente
```
