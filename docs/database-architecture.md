# Database Architecture - Microservizi

Questo documento descrive la strategia di segregazione dei database per la piattaforma NutriFit. Ogni microservizio avrà un database dedicato su Supabase, con schema e policy indipendenti.

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
