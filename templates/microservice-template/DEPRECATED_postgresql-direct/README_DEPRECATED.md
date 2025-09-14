# ⚠️ DEPRECATED: PostgreSQL Direct Template

## Status: DEPRECATED

Questo template è stato **deprecato** a partire da gennaio 2025.

### 🚫 Motivo della Deprecazione

La strategia "database ibrida" (Supabase Client + PostgreSQL Direct) è stata abbandonata in favore di un approccio unificato per:

1. **Semplicità**: Un solo pattern di connessione database per tutti i servizi
2. **Consistency**: Evitare complessità operativa con due strategie diverse  
3. **Maintenance**: Ridurre superficie di manutenzione e debugging
4. **Performance**: Supabase Client è adequato per tutti i use case attuali

### ✅ Soluzione Attuale

**TUTTI i microservizi** utilizzano ora **Supabase Client** con **schema-based isolation**:

- ✅ `user-management` → Supabase Client + `user_management` schema
- ✅ `calorie-balance` → Supabase Client + `calorie_balance` schema  
- ✅ `meal-tracking` → Supabase Client + `meal_tracking` schema
- ✅ `health-monitor` → Supabase Client + `health_monitor` schema
- ✅ `notifications` → Supabase Client + `notifications` schema
- ✅ `ai-coach` → Supabase Client + `ai_coach` schema

### 🛠️ Template da Utilizzare

Per **qualsiasi nuovo microservizio**, utilizza:

**[`../supabase-client-template/COMPLETE_TEMPLATE.md`](../supabase-client-template/COMPLETE_TEMPLATE.md)**

### 📋 Migration Guide

Se hai servizi esistenti basati su questo template deprecato:

1. **Sostituisci le dipendenze** asyncpg + SQLAlchemy con Supabase Client
2. **Aggiorna database.py** per utilizzare Supabase Client
3. **Configura schema isolation** via environment variable
4. **Testa la migrazione** in ambiente development
5. **Deploy gradualmente** in production

### 🔗 Riferimenti

- [Microservizi Python Documentation](../../docs/microservizi_python.md)
- [Template Unificato](../supabase-client-template/COMPLETE_TEMPLATE.md)
- [Supabase Client Pattern](../supabase-client-template/)

---

**Deprecato**: Gennaio 2025  
**Alternativa**: Template Supabase Client Unificato  
**Migration**: Possibile ma non necessaria per servizi funzionanti