

## Schema SQL

```sql
CREATE TABLE meal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    meal_time TIMESTAMP NOT NULL,
    description TEXT,
    calories INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE meal_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_id UUID NOT NULL,
    food_name TEXT NOT NULL,
    quantity FLOAT,
    calories INTEGER,
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
SELECT * FROM meal WHERE user_id = '<USER_ID>';
```

---

**Ultimo aggiornamento:** 6 settembre 2025
