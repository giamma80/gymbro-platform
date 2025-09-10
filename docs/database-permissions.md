# Database Permissions Management

Questo documento descrive come gestire i permessi database per i microservizi in modo versionato e riproducibile.

## Problema

I permessi SQL applicati direttamente in Supabase non sono versionati e devono essere ripetuti manualmente per ogni nuovo microservizio.

## Soluzione

### 1. Template Versionato

File: `config/supabase/grants_template.sql`
- Template riutilizzabile per tutti i microservizi
- Placeholder `{{SCHEMA_NAME}}` sostituito automaticamente
- Include permessi per anon, authenticated, postgres, public
- Gestisce tabelle, view, sequenze e permessi futuri
- **⚠️ IMPORTANTE**: Contiene DDL SQL da eseguire nel portale Supabase, non come script shell

### 2. Script di Generazione (Locale)

File: `scripts/generate-grants-script.sh`
- **Funzione**: Genera automaticamente il file grants per un microservizio (solo locale)
- Numera sequenzialmente i file SQL  
- Fornisce istruzioni per l'applicazione manuale su Supabase
- **Non esegue** le operazioni DDL (che devono essere fatte nel portale)

### 3. Workflow per Nuovi Microservizi

```bash
# 1. Genera lo script grants per un nuovo microservizio (locale)
./scripts/generate-grants-script.sh my-new-service

# 2. Lo script crea: services/my-new-service/sql/XXX_grants.sql
```

**IMPORTANTE**: I passi successivi devono essere eseguiti manualmente nel portale Supabase:

3. **Apri Supabase Dashboard** → SQL Editor  
4. **Copia il contenuto** del file generato (es: `services/my-new-service/sql/XXX_grants.sql`)
5. **Incolla nel SQL Editor** di Supabase
6. **Esegui lo script DDL** cliccando "Run"
7. **Testa il microservizio** per verificare che si avvii correttamente

```bash
# Esempio con schema personalizzato:
./scripts/generate-grants-script.sh workout-tracking workout_tracking
# Poi eseguire manualmente il contenuto del file generato su Supabase
```

## Esempi di Utilizzo

### User Management Service
```bash
./scripts/generate-grants-script.sh user-management
# Genera: services/user-management/sql/004_grants.sql
# Schema: user_management
```

### Calorie Balance Service  
```bash
./scripts/generate-grants-script.sh calorie-balance
# Genera: services/calorie-balance/sql/001_grants.sql  
# Schema: calorie_balance
```

## Struttura File Generati

Ogni file grants generato include:
- CREATE SCHEMA IF NOT EXISTS
- GRANT USAGE ON SCHEMA
- GRANT SELECT ON ALL TABLES/VIEWS
- GRANT USAGE, SELECT ON SEQUENCES  
- ALTER DEFAULT PRIVILEGES per oggetti futuri
- Sezione commentata per permessi di scrittura (dev)
- Query di verifica permessi

## Best Practices

### Sviluppo
- Usa il template standard con permessi di lettura
- Decommentare permessi di scrittura se necessari per il dev
- Testare sempre l'avvio del microservizio dopo l'applicazione

### Produzione
- Rivedere i permessi per limitare ai ruoli necessari
- Evitare permessi a PUBLIC se possibile
- Documentare eventuali permessi aggiuntivi specifici

## Troubleshooting

### Microservizio non si avvia (403 Forbidden)
1. Verificare che lo script grants sia stato eseguito
2. Controllare che il nome schema corrisponda alla config del servizio
3. Verificare i permessi con la query inclusa nel file grants

### Permessi Insufficienti  
1. Verificare che tutti i ruoli necessari abbiano USAGE sullo schema
2. Aggiungere permessi DML se il servizio deve scrivere in dev
3. Controllare Row Level Security (RLS) se attiva

## File di Riferimento

- `config/supabase/grants_template.sql` - Template base
- `scripts/generate-grants-script.sh` - Generatore automatico
- `services/*/sql/*_grants.sql` - File generati per servizio
