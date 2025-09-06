# AI Coach - Database Model

Questo documento descrive la struttura del database dedicato al microservizio AI Coach.

## Schema SQL

```sql
CREATE TABLE ai_coach_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_start TIMESTAMP NOT NULL,
    session_end TIMESTAMP,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Policy di Sicurezza
- Row Level Security abilitata
- Accesso solo tramite credenziali microservizio

## Strategie di Migrazione
- Utilizzare Supabase migration tool
- Versionamento schema tramite changelog

## Esempi di Query
```sql
SELECT * FROM ai_coach_session WHERE user_id = '<USER_ID>';
```

---

**Ultimo aggiornamento:** 6 settembre 2025
