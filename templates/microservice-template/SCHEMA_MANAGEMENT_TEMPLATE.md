# Template Schema Management - app/core/schema_tables.py

Questo template implementa il pattern di gestione schema SQL dedicato per microservizio.

## Codice Template da Copiare

```python
# app/core/schema_tables.py
"""
Schema Management Pattern per {SERVICE_NAME}
Gestisce l'accesso alle tabelle tramite schema configurabile via environment.
"""

from app.core.config import get_settings

class SchemaManager:
    """
    Gestisce l'accesso alle tabelle tramite schema configurabile.
    Ogni microservizio utilizza uno schema SQL dedicato per isolamento dati.
    """
    
    def __init__(self):
        self.schema = get_settings().database_schema
    
    # ===============================================
    # SOSTITUIRE CON LE TABELLE DEL TUO MICROSERVIZIO
    # ===============================================
    
    @property
    def example_table(self):
        """Esempio: tabella principale del microservizio"""
        return f"{self.schema}.example_table"
    
    @property 
    def example_relations(self):
        """Esempio: tabelle di relazione/associazione"""
        return f"{self.schema}.example_relations"
    
    @property
    def example_metadata(self):
        """Esempio: tabelle di metadati/configurazione"""
        return f"{self.schema}.example_metadata"
    
    # ===============================================
    # AGGIUNGI QUI LE PROPRIETÀ PER LE TUE TABELLE
    # ===============================================
    
    # @property
    # def your_table_name(self):
    #     """Descrizione della tabella"""
    #     return f"{self.schema}.your_table_name"

# Istanza globale riutilizzabile in tutto il microservizio
schema_manager = SchemaManager()

# ===============================================
# HELPER FUNCTIONS PER BACKWARD COMPATIBILITY
# ===============================================

def get_example_table(supabase_client):
    """
    Ottiene la tabella example_table con schema configurato.
    Utilizzare nei repository invece di supabase.table("example_table")
    """
    return supabase_client.table(schema_manager.example_table)

def get_example_relations_table(supabase_client):
    """
    Ottiene la tabella example_relations con schema configurato.
    Utilizzare nei repository invece di supabase.table("example_relations")
    """
    return supabase_client.table(schema_manager.example_relations)

def get_example_metadata_table(supabase_client):
    """
    Ottiene la tabella example_metadata con schema configurato.
    Utilizzare nei repository invece di supabase.table("example_metadata")
    """
    return supabase_client.table(schema_manager.example_metadata)

# ===============================================
# AGGIUNGI QUI LE HELPER FUNCTIONS PER LE TUE TABELLE  
# ===============================================

# def get_your_table_name_table(supabase_client):
#     """Ottiene la tabella your_table_name con schema configurato"""
#     return supabase_client.table(schema_manager.your_table_name)
```

## Configurazione Required - app/core/config.py

Aggiungi al tuo file di configurazione:

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... altre configurazioni esistenti
    
    # Schema Management Configuration
    database_schema: str = Field(
        default="public", 
        env="DATABASE_SCHEMA",
        description="Schema SQL dedicato per questo microservizio"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

## File Environment - .env

Aggiungi al tuo file `.env`:

```bash
# Database Schema Configuration
DATABASE_SCHEMA={service_schema_name}    # es. user_management, calorie_balance, etc.

# Altre configurazioni database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Esempio Repository Implementation

```python
# app/infrastructure/repositories/example_repository.py
"""
Repository example che utilizza il Schema Management Pattern
"""

from typing import List, Optional
from app.core.schema_tables import (
    get_example_table,
    get_example_relations_table,
    get_example_metadata_table
)

class ExampleRepository:
    """Repository per operazioni su tabelle example"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        
        # Utilizzare SEMPRE helper functions, mai hardcoded table names
        self.main_table = get_example_table(supabase_client)
        self.relations_table = get_example_relations_table(supabase_client)
        self.metadata_table = get_example_metadata_table(supabase_client)
    
    async def create_item(self, item_data: dict) -> Optional[dict]:
        """Crea nuovo item nella tabella principale"""
        result = self.main_table.insert(item_data).execute()
        return result.data[0] if result.data else None
    
    async def get_item_by_id(self, item_id: str) -> Optional[dict]:
        """Recupera item per ID"""
        result = self.main_table.select("*").eq("id", item_id).execute()
        return result.data[0] if result.data else None
    
    async def list_items(self, limit: int = 100) -> List[dict]:
        """Lista tutti gli items con limite"""
        result = self.main_table.select("*").limit(limit).execute()
        return result.data or []
    
    async def update_item(self, item_id: str, update_data: dict) -> Optional[dict]:
        """Aggiorna item esistente"""
        result = self.main_table.update(update_data).eq("id", item_id).execute()
        return result.data[0] if result.data else None
    
    async def delete_item(self, item_id: str) -> bool:
        """Elimina item per ID"""
        result = self.main_table.delete().eq("id", item_id).execute()
        return len(result.data) > 0
```

## Checklist per Implementazione

- [ ] Copiare template `schema_tables.py` nella cartella `app/core/`
- [ ] Sostituire `{SERVICE_NAME}` con il nome del tuo microservizio
- [ ] Sostituire `example_table`, `example_relations`, `example_metadata` con le tue tabelle reali
- [ ] Aggiungere proprietà `@property` per ogni tabella del microservizio
- [ ] Creare helper function per ogni tabella utilizzata
- [ ] Aggiornare `app/core/config.py` con il campo `database_schema`
- [ ] Configurare `DATABASE_SCHEMA` nel file `.env`
- [ ] Aggiornare tutti i repository per utilizzare helper functions
- [ ] Testare con `python -m pytest` per verificare che tutto funzioni
- [ ] Rimuovere eventuali hardcoded table names dal codice

## Vantaggi del Pattern

✅ **Isolamento Dati**: Ogni microservizio opera su schema dedicato  
✅ **Configurabilità**: Schema definito tramite environment variable  
✅ **Backward Compatibility**: Helper functions mantengono compatibilità  
✅ **Centralizzazione**: Unico punto di controllo per nomi tabelle  
✅ **Type Safety**: Proprietà Python per accesso type-safe  
✅ **Testabilità**: Facile switch tra schema test/dev/prod  
