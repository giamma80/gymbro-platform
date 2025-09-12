# Database Architecture - Microservizi

Questo documento descrive la strategia di segregazione dei database per la piattaforma NutriFit. Ogni microservizio avrà un database dedicato su Supabase, con schema e policy indipendenti.

## ⚠️ CONFIGURAZIONE CRITICA - Esposizione Schema in Supabase

**IMPORTANTE**: Dopo aver creato gli schemi personalizzati, devono essere esposti tramite PostgREST nella dashboard di Supabase.

### Passi Obbligatori per Ogni Schema

1. **Accedere alla Dashboard Supabase**: `https://supabase.com/dashboard/project/{project-id}/settings/api`

2. **Configurare API Settings**:
   - Sezione: `API Settings` 
   - Campo: `Exposed schemas`
   - **Aggiungere gli schemi custom** (es. `calorie_balance, user_management`)
   
3. **Schema da Esporre per Servizio**:
   ```
   user_management      # Per user-management service
   calorie_balance      # Per calorie-balance service  
   meal_tracking        # Per meal-tracking service
   health_monitor       # Per health-monitor service
   notifications        # Per notifications service
   ai_coach            # Per ai-coach service
   ```

4. **Verificare Esposizione**: Gli schemi devono apparire nella lista `The schema must be one of the following` negli errori PostgREST

⚠️ **Senza questa configurazione**: I microservizi non possono accedere ai propri schemi e restituiscono errori `PGRST106`.

## Microservizi e Database dedicati

| Microservizio         | Database dedicato         | Documentazione Datamodel |
|----------------------|--------------------------|-------------------------|
| Calorie Balance      | calorie_balance_db       | [Calorie Balance DB](databases/calorie-balance-db.md) |
| Meal Tracking        | meal_tracking_db         | [Meal Tracking DB](databases/meal-tracking-db.md) |
| Health Monitor       | health_monitor_db        | [Health Monitor DB](databases/health-monitor-db.md) |
| Notifications        | notifications_db         | [Notifications DB](databases/notifications-db.md) |
| AI Coach             | ai_coach_db              | [AI Coach DB](databases/ai-coach-db.md) |

Ogni database è isolato e gestito tramite Supabase, con policy di sicurezza e accesso dedicate.

## Policy di Segregazione
- Nessun dato condiviso tra database
- Accesso tramite credenziali dedicate per ogni microservizio
- Row Level Security abilitata su tutti i database

## Dettagli
Per ogni microservizio, consultare il documento specifico collegato nella tabella sopra per:
- Schema SQL
- Policy di sicurezza
- Strategie di migrazione
- Esempi di query

---

**Ultimo aggiornamento:** 6 settembre 2025
