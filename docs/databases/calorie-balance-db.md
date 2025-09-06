# Calorie Balance - Database Model

Questo documento descrive la struttura del database dedicato al microservizio Calorie Balance.

## Schema SQL

```sql
CREATE TABLE calorie_goal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    goal INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE metabolic_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    bmr FLOAT NOT NULL,
    calories_burned_bmr FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Altre tabelle secondo necessità
```

## Policy di Sicurezza
- Row Level Security abilitata
- Accesso solo tramite credenziali microservizio

## Strategie di Migrazione
- Utilizzare Supabase migration tool
- Versionamento schema tramite changelog

## Esempi di Query
```sql
SELECT * FROM calorie_goal WHERE user_id = '<USER_ID>';
```

---

**Ultimo aggiornamento:** 6 settembre 2025
