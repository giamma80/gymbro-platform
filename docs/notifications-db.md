

## Schema SQL

```sql
CREATE TABLE notification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE
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
SELECT * FROM notification WHERE user_id = '<USER_ID>';
```

---

**Ultimo aggiornamento:** 6 settembre 2025
