# Schema Management Pattern per Microservizi Python

## Overview
Questo documento descrive il pattern di gestione degli schemi SQL implementato per i microservizi Python della piattaforma GymBro. La soluzione consente l'isolamento dei dati per microservizio tramite schemi SQL dedicati configurabili via ambiente.

## Architettura della Soluzione

### 1. SchemaManager Class
**Posizione**: `app/core/schema_tables.py`

```python
from app.core.config import get_settings

class SchemaManager:
    def __init__(self):
        self.schema = get_settings().database_schema
    
    @property
    def auth_profiles(self):
        return f"{self.schema}.auth_profiles"
    
    @property
    def auth_sessions(self):
        return f"{self.schema}.auth_sessions"
    
    @property
    def auth_permissions(self):
        return f"{self.schema}.auth_permissions"
    
    # Aggiungi altre tabelle specifiche del microservizio

# Istanza globale
schema_manager = SchemaManager()

# Funzioni helper per backward compatibility
def get_auth_profiles_table(supabase_client):
    return supabase_client.table(schema_manager.auth_profiles)

def get_auth_sessions_table(supabase_client):
    return supabase_client.table(schema_manager.auth_sessions)
```

### 2. Configurazione Schema
**Posizione**: `app/core/config.py`

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... altre configurazioni
    database_schema: str = Field(default="public", env="DATABASE_SCHEMA")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### 3. File .env Template
```bash
# Database Configuration
DATABASE_SCHEMA=nome_schema_microservizio
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Implementazione nei Repository

### Pattern Standard per Repository
```python
from app.core.schema_tables import get_auth_profiles_table

class AuthRepository:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.table = get_auth_profiles_table(supabase_client)
    
    async def create_profile(self, profile_data):
        result = self.table.insert(profile_data).execute()
        return result.data[0] if result.data else None
```

## Vantaggi della Soluzione

1. **Isolamento dei Dati**: Ogni microservizio opera su schema dedicato
2. **Configurabilità**: Schema definito via variabile ambiente
3. **Backward Compatibility**: Funzioni helper mantengono compatibilità codice esistente
4. **Centralizzazione**: Unico punto di controllo per nomi tabelle
5. **Type Safety**: Proprietà Python per accesso type-safe alle tabelle

## Best Practices

### Per Nuovi Microservizi:
1. Definire lo schema specifico nel file `.env`
2. Estendere la classe `SchemaManager` con le tabelle del microservizio
3. Utilizzare sempre le funzioni helper nei repository
4. Testare con schema dedicato prima del deploy

### Per Microservizi Esistenti:
1. Creare migrazione dello schema esistente
2. Implementare `SchemaManager` con tabelle attuali
3. Aggiornare repository per utilizzare helper functions
4. Configurare `DATABASE_SCHEMA` nell'ambiente di produzione

## Struttura Files Template

```
app/
├── core/
│   ├── config.py          # Configurazione con database_schema
│   ├── database.py        # Connessione database
│   └── schema_tables.py   # SchemaManager e helper functions
├── infrastructure/
│   └── repositories/      # Repository che usano schema_tables
└── api/
    └── routers/          # Router che usano repository
```

## Deployment e Testing

### Setup Ambiente di Sviluppo:
```bash
# 1. Configurare schema nel .env
echo "DATABASE_SCHEMA=dev_microservice_name" >> .env

# 2. Avviare servizio
./start-dev.sh

# 3. Testare con suite completa
python comprehensive_test_suite.py
```

### Verifica Schema Management:
- Tutti i repository devono utilizzare `schema_manager`
- Nessun hardcoded schema name nel codice
- Test di connessione con schema configurato
- Health check endpoint funzionante

Questo pattern garantisce scalabilità, manutenibilità e isolamento dei dati per l'architettura a microservizi.
