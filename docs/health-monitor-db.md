

## Schema SQL

```sql
CREATE TABLE health_metric (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    metric_type TEXT NOT NULL,
    value FLOAT NOT NULL,
    measured_at TIMESTAMP NOT NULL,
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
SELECT * FROM health_metric WHERE user_id = '<USER_ID>';
```

---

**Ultimo aggiornamento:** 6 settembre 2025
