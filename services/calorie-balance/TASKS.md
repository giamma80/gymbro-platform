# 🚀 Calor| **Fase** | **Tasks** | **Completati** | **Tempo Stimato** | **Priorità** | **St### **Current Status** (Aggiornato: 14 settembre 2025 - 00:22)
- **Test Success Rate**: 🟡 **~11/16 (69%)** → Target: Fase 2 porterà a ~80% (Goals API ✅ fixed)
- **API Endpoints Working**: 🟡 **Goals API 100% funzionante** → Events API da riparare (Task 2.3, 2.4)
- **Critical Blockers**: 🟢 **0 active** (erano 4) → **FASE 1 eliminati tutti!**
- **Schema Database**: 🟢 **FIXED** → Activity_level column SQL pronto
- **Microservice Decoupling**: 🟢 **COMPLETE** → User dependencies completamente rimosse
- **End_date Calculation**: 🟢 **IMPLEMENTATO** → Calcolo automatico 75kg→70kg = 10 settimane = 2025-11-23 |
|----------|-----------|----------------|-------------------|--------------|------------|
| **FASE 1** | 4 | 4 | 2-3 ore | 🔴 CRITICAL | ✅ **COMPLETED** |
| **FASE 2** | 4 | 2 | 4-5 ore | 🟡 HIGH | 🟡 **IN PROGRESS** |
| **FASE 3** | 3 | 0 | 2-3 ore | 🟢 MEDIUM | ⏳ PENDING |
| **FASE 4** | 4 | 0 | 3-4 ore | 🔵 FINAL | ⏳ PENDING |
| **TOTALE** | **15** | **6** | **11-15 ore** | | **🎯 40% COMPLETE** |nce Service - Recovery Tasks

**Data Creazione**: 13 settembre 2025  
**Obiettivo**: Risolvere critical issues e portare il servizio da 56% a 100% test success rate  
**Stimato**: 11-15 ore totali di lavoro

---

## 📋 TASK OVERVIEW

| **Fase** | **Tasks** | **Completati** | **Tempo Stimato** | **Priorità** | **Status** |
|----------|-----------|----------------|-------------------|--------------|------------|
| **FASE 1** | 4 | 4 | 2-3 ore | 🔴 CRITICAL | ✅ **COMPLETED** |
| **FASE 2** | 4 | 0 | 4-5 ore | 🟡 HIGH | ⏳ PENDING |
| **FASE 3** | 3 | 0 | 2-3 ore | 🟢 MEDIUM | ⏳ PENDING |
| **FASE 4** | 4 | 0 | 3-4 ore | 🔵 FINAL | ⏳ PENDING |
| **TOTALE** | **15** | **4** | **11-15 ore** | | **� 27% COMPLETE** |

---

## 🔴 FASE 1 - CRITICAL SCHEMA FIXES (IMMEDIATA) ✅ **COMPLETATA**

| **ID** | **Task** | **Descrizione** | **Files Coinvolti** | **Tempo** | **Status** | **Note** |
|--------|----------|-----------------|---------------------|-----------|------------|----------|
| **1.1** | Fix Database Schema Mismatch | ✅ Aggiunta colonna `activity_level` a `metabolic_profiles` | `sql/006_fix_schema_task_1_1.sql` | ✅ 30 min | ✅ **DONE** | SQL script creato e pronto |
| **1.2** | Remove UserRepository | ✅ Rimosso completamente `UserRepository` e `User` classes | `application/commands.py`, `database/repositories.py` | ✅ 45 min | ✅ **DONE** | Clean microservice decoupling |
| **1.3** | Remove User Entity | ✅ Verificato - `User` entity già rimosso correttamente | `domain/entities.py` (già pulito) | ✅ 30 min | ✅ **DONE** | Cross-schema architecture OK |
| **1.4** | Clean Dependencies | ✅ Pulito dependency injection e import | `core/dependencies.py`, `database/repositories.py` | ✅ 30 min | ✅ **DONE** | DI system decoupled |

**✅ Success Criteria FASE 1 RAGGIUNTI**: 
- ✅ App si avvia senza errori User-related  
- ✅ Database schema allineato (SQL script pronto)  
- ✅ Codice legacy User completamente rimosso  
- ✅ **Parameter Passing Pattern** implementato

**🎯 RISULTATO**: Microservizio ora **completamente decoupled** da user-management service!

---

## 🟡 FASE 2 - API IMPLEMENTATION FIXES (ALTA PRIORITÀ) ✅ **2/4 COMPLETATI**

| **ID** | **Task** | **Descrizione** | **Files Coinvolti** | **Tempo** | **Status** | **Test Target** |
|--------|----------|-----------------|---------------------|-----------|------------|-----------------|
| **2.1** | Fix Goals API - Parameter Passing | ✅ Implementato vero Parameter Passing per Goals | `api/endpoints/goals.py`, `services/goals_service.py` | ✅ 90 min | ✅ **DONE** | ✅ `Goals: Create calorie goal` |
| **2.2** | Fix Goals Queries | ✅ API completamente funzionante + End_date calculation | Goals service methods | ✅ 60 min | ✅ **DONE** | ✅ `Goals: Get all/active goals` |
| **2.3** | Fix Events API Validation | Correggere validazione Events per schema reale | `api/schemas.py`, `services/events_service.py` | 90 min | ⏳ **NEXT** | ✅ `Events: burned/weight` |
| **2.4** | Fix Events Timeline | Correggere timeline queries cross-schema | Events timeline methods | 60 min | ⏳ TODO | ✅ `Events: Get timeline` |

**🎯 RISULTATI COMPLETATI**:
- ✅ **Goals CREATE API**: Funziona perfettamente con Parameter Passing Pattern
- ✅ **End_date Calculation**: Calcolo automatico basato su target_weight_kg (es: 75kg→70kg in 10 settimane)
- ✅ **JSON Serialization**: Risolti tutti i problemi datetime/Decimal/enum
- ✅ **UUID Cross-Schema**: Conversione automatica user_id string → UUID per foreign keys

**Success Criteria FASE 2**: 🟡 Goals API: 3/3 test ✅ **DONE** | Events API: 6/6 test ⏳ IN PROGRESS

---

## 🟢 FASE 3 - METABOLIC PROFILES ALIGNMENT (MEDIA PRIORITÀ)

| **ID** | **Task** | **Descrizione** | **Files Coinvolti** | **Tempo** | **Status** | **Note** |
|--------|----------|-----------------|---------------------|-----------|------------|----------|
| **3.1** | Update Metabolic Repository | Allineare repo con schema reale (15+ campi) | `repositories/repositories.py` | 75 min | ⏳ TODO | Include AI/ML fields |
| **3.2** | Update Metabolic Entity | Aggiornare entity con campi reali | `domain/entities.py` | 45 min | ⏳ TODO | `calculation_method`, `accuracy_score` etc |
| **3.3** | Update Metabolic API | Correggere endpoints per nuovo schema | `api/endpoints/metabolic.py` | 60 min | ⏳ TODO | Parameter Passing pattern |

**Success Criteria FASE 3**: ✅ Metabolic API completamente funzionante ✅ Schema reale supportato

---

## 🔵 FASE 4 - TEST INFRASTRUCTURE & VALIDATION (FINALE)

| **ID** | **Task** | **Descrizione** | **Files Coinvolti** | **Tempo** | **Status** | **Deliverable** |
|--------|----------|-----------------|---------------------|-----------|------------|-----------------|
| **4.1** | Update Test Suite | Aggiornare tests per nuovo schema | `test_comprehensive.py`, `tests/` | 60 min | ⏳ TODO | Tests allineati |
| **4.2** | Implement Timeline APIs | Aggiungere Timeline Analytics endpoints | `api/endpoints/timeline.py` (nuovo) | 90 min | ⏳ TODO | 12 nuovi endpoints |
| **4.3** | Setup CI/CD | GitHub Actions + Render deployment | `.github/workflows/`, `render.yaml` | 60 min | ⏳ TODO | Pipeline automatizzata |
| **4.4** | Integration Testing | Test end-to-end completo | All service components | 45 min | ⏳ TODO | 100% test success |

**Success Criteria FASE 4**: ✅ 100% test success rate ✅ Production-ready deployment

---

## 📊 PROGRESS TRACKING

### **Current Status** (Aggiornato: 13 settembre 2025)
- **Test Success Rate**: � **9/16 (56%)** → Target: Fase 2 porterà a ~80%
- **API Endpoints Working**: � **Architettura fissata** → Goals/Events API da riparare
- **Critical Blockers**: � **0 active** (erano 4) → **FASE 1 eliminati tutti!**
- **Schema Database**: 🟢 **FIXED** → Activity_level column SQL pronto
- **Microservice Decoupling**: 🟢 **COMPLETE** → User dependencies completamente rimosse

### **Target Status**
- **Test Success Rate**: 🟢 **16/16 (100%)**
- **API Endpoints Working**: 🟢 **49/49 (100%)**
- **Critical Blockers**: 🟢 **0 active**

### **Milestones**
| **Milestone** | **Target Date** | **Status** | **Dependencies** |
|---------------|-----------------|------------|------------------|
| **Schema Fixed** | ✅ Day 1 | ✅ **COMPLETED** | ✅ FASE 1 complete |
| **Goals API Working** | ✅ Day 2 | ✅ **COMPLETED** | ✅ Task 2.1, 2.2 complete |
| **Events API Working** | Day 2 | 🟡 **IN PROGRESS** | Task 2.3, 2.4 next |
| **Full Feature Set** | Day 3 | ⏳ PENDING | FASE 3 complete |
| **Production Ready** | Day 4 | ⏳ PENDING | FASE 4 complete |

---

## 🎉 FASE 1 COMPLETATA - RIEPILOGO RISULTATI ✅

### **✅ Task Completati (4/4)**
1. **Database Schema Fix**: Script SQL `006_fix_schema_task_1_1.sql` creato per aggiungere `activity_level` column
2. **UserRepository Cleanup**: Rimosso completamente da `commands.py` e `database/repositories.py` 
3. **User Entity Removal**: Verificato domain layer pulito (era già corretto dalla migrazione)
4. **Dependency Injection**: Pulito DI system da tutte le dipendenze User-related

## 🎉 FASE 2 - GOALS API COMPLETATA ✅ (2/4 TASK)

### **✅ Task Completati (2/4)**
1. **Goals API - Parameter Passing**: ✅ Implementato Pattern completo con user metrics esterni
2. **Goals Queries + End_date Calculation**: ✅ Calcolo automatico timeline (es: 75kg→70kg = 10 settimane)

### **🚀 Risultati Verificati**
- ✅ **Goals CREATE API**: `POST /api/v1/goals/` funziona perfettamente
- ✅ **Parameter Passing**: Accetta user_weight_kg, height_cm, age, gender esterni
- ✅ **UUID Cross-Schema**: Conversione automatica user_id → UUID per foreign keys
- ✅ **End_date Calculation**: `target_weight_kg: 70, user_weight_kg: 75, weekly_change: 0.5` → `end_date: 2025-11-23`
- ✅ **JSON Serialization**: Risolti tutti problemi datetime, Decimal, enum
- ✅ **Metabolic Integration**: BMR/TDEE calculation con daily_calorie_target: 1488.5

### **📝 API Response Verificata**
```json
{
  "id": "14b6f07d-ee07-4759-be07-5e46a51f5c02",
  "user_id": "00000000-0000-0000-0000-000000000001", 
  "goal_type": "weight_loss",
  "daily_calorie_target": "1488.5",
  "end_date": "2025-11-23",  ← ✅ CALCOLATO AUTOMATICAMENTE!
  "weekly_weight_change_kg": "0.5",
  "ai_optimized": true
}
```

### **🏗️ Architettura Implementata**
- ✅ **Parameter Passing Pattern**: Commands accettano parametri user esterni
- ✅ **Cross-Schema Foreign Keys**: Solo UUID references a `user_management.users`
- ✅ **Microservice Decoupling**: Zero dipendenze dirette a user-management
- ✅ **Event-Driven Architecture**: Ready per eventi cross-microservice

### **📂 Files Modificati**
- `sql/006_fix_schema_task_1_1.sql` → Creato (schema fix)
- `app/application/commands.py` → User classes e handlers rimossi 
- `app/infrastructure/database/repositories.py` → SqlUserRepository eliminato
- `app/domain/entities.py` → Già pulito (verificato)
- `app/core/dependencies.py` → Già pulito (verificato)

### **🚀 Ready for FASE 2**
**Prossimo Obiettivo**: Riparare Goals API (3 test) e Events API (6 test) per raggiungere ~80% test success rate.

---

## 🚨 CRITICAL DEPENDENCIES & BLOCKERS

### **Current Blockers**
1. **❌ `activity_level` column missing** → Blocks all metabolic calculations
2. **❌ Legacy User code** → Blocks Goals and Events APIs  
3. **❌ Cross-schema queries failing** → Blocks data retrieval
4. **❌ Parameter Passing incomplete** → Violates microservice architecture

### **Task Dependencies**
- **1.2, 1.3, 1.4** → Sequential (User cleanup)
- **2.1, 2.2** → Depends on 1.2-1.4 complete
- **2.3, 2.4** → Can run parallel with 2.1-2.2
- **3.x** → Depends on 1.1 (schema fix)
- **4.x** → Depends on all previous phases

---

## 🎯 TASK ASSIGNMENT READY

**Priority Order for Execution**:
1. **Start with 1.1** (Database schema fix)
2. **Continue with 1.2-1.4** (Legacy cleanup)  
3. **Parallel execution** of 2.1-2.4 (API fixes)
4. **Sequential execution** of 3.1-3.3 (Feature alignment)
5. **Final execution** of 4.1-4.4 (Testing & deployment)

**Ready to begin**: ✅ All tasks defined and scoped  
**Blockers identified**: ✅ Clear resolution path  
**Success criteria**: ✅ Measurable outcomes defined

---

**📅 Created**: 13 settembre 2025  
**👤 Owner**: Development Team  
**🎯 Goal**: Calorie Balance Service Recovery to Production Quality