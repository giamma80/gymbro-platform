# Database Architecture - Microservizi

> Appendice Stato Reale (18-09-2025): Attualmente sono operativi solo gli schemi `user_management` e `calorie_balance` in un **unico cluster Supabase condiviso**. La strategia "1 database per microservizio" è parte della visione evolutiva, ma nella fase corrente viene applicato un approccio schema-based multi-tenant controllato per ridurre complessità iniziale e costi.

Questo documento descrive la strategia di segregazione dei dati per la piattaforma NutriFit. Visione target: database (o cluster) dedicato per microservizio; stato corrente: schemi isolati nello stesso database con policy specifiche.

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

## Microservizi e Segmentazione Dati (Visione vs Stato Reale)

| Microservizio | Visione (DB dedicato) | Stato Reale (Schema) | Note |
|---------------|-----------------------|----------------------|------|
| User Management | user_management_db | `user_management` | ATTIVO |
| Calorie Balance | calorie_balance_db | `calorie_balance` | ATTIVO (parziale) |
| Meal Tracking | meal_tracking_db | `meal_tracking` | NON ANCORA |
| Health Monitor | health_monitor_db | `health_monitor` | NON ANCORA |
| Notifications | notifications_db | `notifications` | NON ANCORA |
| AI Coach | ai_coach_db | `ai_coach` | NON ANCORA |

Ogni database è isolato e gestito tramite Supabase, con policy di sicurezza e accesso dedicate.

## Policy di Segregazione (Applicate Oggi)
- Nessuna duplicazione tabella utenti: `user_management.users` è SSoT
- Foreign key cross-schema dove richiesto (referenze utenti)
- Row Level Security abilitata sugli schemi attivi
- Principle of Least Privilege: credenziali limitate per servizio (in roadmap l'estrazione per schemi futuri)
- Migrazione graduale prevista verso separazione fisica (quando volumi / requisiti compliance lo richiederanno)

## Dettagli
Per ogni microservizio, consultare il documento specifico collegato nella tabella sopra per:
- Schema SQL
- Policy di sicurezza
- Strategie di migrazione
- Esempi di query

---

**Ultimo aggiornamento:** 18 settembre 2025 (allineato stato reale schema-based)
