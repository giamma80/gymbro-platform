# > **Status del mi| **📈 Timeline Analytics (NEW)** | 0 | 12 | 🔴 0% |
| **🗓️ Temporal Views (DB Ready)** | 5 | 5 | 🟢 100% |
| **Analytics & Trends** | 0 | 4 | 🔴 0% |
| **Metabolic Profiles** | 0 | 3 | 🔴 0% |
| **Advanced Features** | 0 | 3 | 🔴 0% |
| **TOTALE** | **17** | **54** | **🟡 31%** |rvizio**: ✅ **Event-Driven Ready** - Database migrato con successo!  
> **Versione attuale**: v1.2.0 (Multi-Level Temporal Analytics)  
> **Ultimo aggiornamento**: 5 settembre 2025  
> **🎉 MAJOR UPDATE**: 5-Level Temporal Views implementate (hourly → monthly)Roadmap - Calorie Balance Service

> **Status del microservizio**: � **Major Refactoring** - Ristrutturazione per supporto eventi ad alta frequenza  
> **Versione attuale**: v1.1.0 (Event-Driven Architecture)  
> **Ultimo aggiornamento**: 5 settembre 2025  
> **🚨 BREAKING CHANGE**: Nuova architettura bi-livello per campionamento smartphone (2-minuti)

## 📊 Overview dello Stato

| Categoria | Implementate | Totali | Completamento |
|-----------|--------------|--------|---------------|
| **Health & Status** | 3 | 3 | 🟢 100% |
| **User Management** | 3 | 5 | 🟡 60% |
| **Calorie Goals** | 2 | 6 | 🟡 33% |
| **🔥 Calorie Events (NEW)** | 0 | 6 | 🔴 0% |
| **Daily Balance (Legacy)** | 4 | 7 | 🟡 57% |
| **📈 Timeline Analytics (NEW)** | 0 | 8 | 🔴 0% |
| **Analytics & Trends** | 0 | 4 | 🔴 0% |
| **Metabolic Profiles** | 0 | 3 | 🔴 0% |
| **Advanced Features** | 0 | 3 | 🔴 0% |
| **TOTALE** | **12** | **45** | **� 27%** |

---

## 🔗 API Endpoints Roadmap

### 🏥 Health & Status
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/health/` | GET | ✅ **FATTO** | P0 | Basic health check |
| `/health/ready` | GET | ✅ **FATTO** | P0 | Kubernetes readiness |
| `/health/live` | GET | ✅ **FATTO** | P0 | Kubernetes liveness |

### 👤 User Management
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/` | POST | ✅ **FATTO** | P0 | Create user profile |
| `/api/v1/users/{user_id}` | GET | ✅ **FATTO** | P0 | Get user profile |
| `/api/v1/users/{user_id}` | PUT | ✅ **FATTO** | P0 | Update user profile |
| `/api/v1/users/{user_id}` | DELETE | ❌ **TODO** | P2 | Delete user profile |
| `/api/v1/users/` | GET | ❌ **TODO** | P3 | List users (admin) |

### 🎯 Calorie Goals
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/goals/users/{user_id}` | POST | ✅ **FATTO** | P0 | Create calorie goal |
| `/api/v1/goals/users/{user_id}/active` | GET | ✅ **FATTO** | P0 | Get active goal |
| `/api/v1/goals/users/{user_id}/goals/{goal_id}` | PUT | ❌ **TODO** | P1 | Update specific goal |
| `/api/v1/goals/users/{user_id}/goals/{goal_id}` | DELETE | ❌ **TODO** | P1 | Delete goal |
| `/api/v1/goals/users/{user_id}/history` | GET | ❌ **TODO** | P2 | Goals history |
| `/api/v1/goals/users/{user_id}/goals` | GET | ❌ **TODO** | P2 | List all user goals |

### 🔥 Calorie Events (High-Frequency Data)
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/events/users/{user_id}/calorie-consumed` | POST | ❌ **TODO** | P0 | Log calorie consumption event |
| `/api/v1/events/users/{user_id}/calorie-burned` | POST | ❌ **TODO** | P0 | Log exercise calorie burn |
| `/api/v1/events/users/{user_id}/weight` | POST | ❌ **TODO** | P0 | Log weight measurement |
| `/api/v1/events/users/{user_id}/batch` | POST | ❌ **TODO** | P0 | Batch events from mobile |
| `/api/v1/events/users/{user_id}/timeline` | GET | ❌ **TODO** | P1 | Get events timeline |
| `/api/v1/events/users/{user_id}/latest` | GET | ❌ **TODO** | P2 | Get latest events |

### ⚖️ Daily Balance (Legacy Support)
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/balance/users/{user_id}` | PUT | ✅ **FATTO** | P0 | Update daily balance (legacy) |
| `/api/v1/balance/users/{user_id}/date/{date}` | GET | ✅ **FATTO** | P0 | Get balance for date |
| `/api/v1/balance/users/{user_id}/today` | GET | ✅ **FATTO** | P0 | Get today's balance |
| `/api/v1/balance/users/{user_id}/progress` | POST | ✅ **FATTO** | P0 | Get progress data |
| `/api/v1/balance/users/{user_id}/summary/weekly` | GET | ❌ **TODO** | P1 | Weekly summary |
| `/api/v1/balance/users/{user_id}/summary/monthly` | GET | ❌ **TODO** | P1 | Monthly summary |
| `/api/v1/balance/users/{user_id}/range` | GET | ❌ **TODO** | P2 | Custom date range |

### 📈 Timeline Analytics (Real-Time Insights)
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/timeline/users/{user_id}/hourly` | GET | ❌ **TODO** | P1 | Hourly aggregations from view |
| `/api/v1/timeline/users/{user_id}/daily` | GET | ❌ **TODO** | P1 | Daily aggregations from view |
| `/api/v1/timeline/users/{user_id}/weekly` | GET | ❌ **TODO** | P1 | Weekly patterns & trends |
| `/api/v1/timeline/users/{user_id}/monthly` | GET | ❌ **TODO** | P1 | Monthly progress analytics |
| `/api/v1/timeline/users/{user_id}/balance` | GET | ❌ **TODO** | P1 | Net balance calculations |
| `/api/v1/timeline/users/{user_id}/intraday` | GET | ❌ **TODO** | P1 | Detailed intra-day view |
| `/api/v1/timeline/users/{user_id}/patterns` | GET | ❌ **TODO** | P1 | Behavioral patterns |
| `/api/v1/timeline/users/{user_id}/real-time` | GET | ❌ **TODO** | P2 | Real-time current status |
| `/api/v1/timeline/users/{user_id}/export` | GET | ❌ **TODO** | P2 | Export timeline data |
| `/api/v1/timeline/users/{user_id}/compare` | GET | ❌ **TODO** | P2 | Compare time periods |
| `/api/v1/timeline/users/{user_id}/alerts` | GET | ❌ **TODO** | P3 | Timeline-based alerts |
| `/api/v1/timeline/users/{user_id}/predictions` | GET | ❌ **TODO** | P3 | AI-based predictions |

### 🗓️ Temporal Views (Database Ready)
| Vista Database | Status | Aggregazione | Funzionalità | Performance |
|----------------|--------|--------------|--------------|-------------|
| `hourly_calorie_summary` | ✅ **READY** | Per ora | Real-time intraday trends | Sub-second |
| `daily_calorie_summary` | ✅ **READY** | Per giorno | Day-over-day comparisons | Sub-second |
| `weekly_calorie_summary` | ✅ **READY** | Per settimana | Weekly patterns, habit formation | Sub-second |
| `monthly_calorie_summary` | ✅ **READY** | Per mese | Long-term trends, monthly reports | Sub-second |
| `daily_balance_summary` | ✅ **READY** | Bilanci netti | Net calories, weight correlation | Sub-second |

### 📊 Analytics & Trends
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/{user_id}/trends` | GET | ❌ **TODO** | P1 | Weekly/monthly trends |
| `/api/v1/users/{user_id}/insights` | GET | ❌ **TODO** | P1 | AI-powered insights |
| `/api/v1/users/{user_id}/analytics/weight` | GET | ❌ **TODO** | P2 | Weight trend analysis |
| `/api/v1/users/{user_id}/analytics/performance` | GET | ❌ **TODO** | P2 | Goal performance metrics |

### 🧬 Metabolic Profiles
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/{user_id}/profile/metabolic` | GET | ❌ **TODO** | P1 | Get metabolic profile |
| `/api/v1/users/{user_id}/profile/metabolic` | PUT | ❌ **TODO** | P1 | Update metabolic profile |
| `/api/v1/users/{user_id}/profile/metabolic/calculate` | POST | ❌ **TODO** | P2 | Recalculate BMR/TDEE |

### 🏆 Advanced Features
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/{user_id}/streaks` | GET | ❌ **TODO** | P2 | Calorie goal streaks |
| `/api/v1/users/{user_id}/challenges` | GET | ❌ **TODO** | P3 | User challenges |
| `/api/v1/users/{user_id}/badges` | GET | ❌ **TODO** | P3 | Achievement badges |

---

## 🎯 Priorità di Sviluppo

### **P0 - Critical (DATABASE READY ✅)**
Migrazione all'architettura event-driven completata:
- ✅ Health checks (completato)
- ✅ User CRUD base (completato)
- ✅ Goals creation/retrieval (completato)
- ✅ **Database Schema Migration** - **COMPLETED**
- ✅ **Temporal Views (5-Level)** - **READY FOR APIS**
- 🔄 **Calorie Events API** - **NEXT PRIORITY** per mobile app

### **P1 - High Priority (Ready to Implement)**
Funzionalità essenziali con database support completo:
1. **Calorie Events API** (batch, timeline, latest) - **Priority 1A**
2. **Timeline Analytics** (hourly → monthly via views) - **Priority 1B**
3. **Temporal Analytics** (weekly/monthly insights) - **Priority 1C**
4. **Metabolic Profiles** - **Priority 1D**
5. **Legacy Balance Support** (weekly/monthly summaries) - **Priority 1E**

### **P2 - Medium Priority**
Funzionalità per migliorare UX post-migrazione:
- Real-time timeline status
- Advanced timeline features (export, compare)
- Weight analytics con eventi
- Goal performance con eventi
- Custom date ranges

### **P3 - Low Priority**
Funzionalità avanzate per scaling:
- Timeline-based alerts e predictions
- Admin features
- Challenges system
- Achievement badges

---

## 🚀 Migration Roadmap

### **✅ Phase 1 - Database & Core Events (COMPLETED)**
- ✅ **CRITICAL: Created calorie_events table**
- ✅ **CRITICAL: Migrated daily_balances structure**
- ✅ **CRITICAL: 5-Level Temporal Views implemented**
  - `hourly_calorie_summary` - Real-time intraday analytics
  - `daily_calorie_summary` - Day-over-day comparisons
  - `weekly_calorie_summary` - Weekly patterns & habits
  - `monthly_calorie_summary` - Long-term trends
  - `daily_balance_summary` - Net calorie calculations
- ✅ **Performance indexes optimized for mobile queries**
- ✅ **Database structure validation completed**
- [ ] **CalorieEvent domain entity implementation**
- [ ] **Basic events API** (`/events/calorie-consumed`, `/calorie-burned`, `/weight`)

### **Phase 2 - Mobile Integration (Week 1-2)**
- [ ] **CalorieEvent domain entities & services**
- [ ] **Batch events API** (`/events/batch`)
- [ ] **Timeline APIs with temporal views** (`/timeline/hourly`, `/daily`, `/weekly`, `/monthly`)
- [ ] **Balance summary API** (`/timeline/balance`)
- [ ] **Mobile app integration testing**

### **Phase 3 - Analytics Enhancement (Week 3-4)**
- [ ] **Pattern analysis** (`/timeline/patterns`)
- [ ] **Advanced timeline features** (export, compare)
- [ ] **Real-time aggregation logic** (`/timeline/real-time`)
- [ ] **Performance optimization** (caching, indexing)
- [ ] **Legacy balance API migration**

### **Phase 4 - Production Ready (Week 5-6)**
- [ ] **AI predictions** (`/timeline/predictions`)
- [ ] **Timeline-based alerts** (`/timeline/alerts`)
- [ ] **Monitoring & observability**
- [ ] **Documentation completion**

---

## 🧪 Test Coverage Status

| Categoria | Unit Tests | Integration Tests | Status |
|-----------|------------|-------------------|--------|
| **Health** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Users** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Goals** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Balance** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Analytics** | ❌ 0% | ❌ 0% | 🔴 Missing |
| **Metabolic** | ❌ 0% | ❌ 0% | 🔴 Missing |

---

## 📝 Note Tecniche

### **Dipendenze per Sviluppo Futuro:**
- **Analytics**: Richiede aggregazione dati e possibile integrazione con AI Coach Service
- **Metabolic Profiles**: Necessita algoritmi di calcolo BMR/TDEE specifici per il mercato italiano
- **Advanced Features**: Dipendenti da Notifications Service per gamification

### **Considerazioni Architetturali:**
- Mantenere separazione Domain/Application/Infrastructure
- Utilizzare CQRS pattern per analytics read-heavy operations
- Implementare caching Redis per endpoints analytics
- Preparare integrazione con N8N workflows per AI insights

### **Performance Goals:**
- Response time < 200ms per tutti gli endpoint P0/P1
- Support fino a 1000 RPS per endpoint critici
- Cache hit ratio > 80% per analytics endpoints

---

## 🔄 Database Migration Strategy

### **Current Schema Issues**
- ❌ `daily_balances.UNIQUE(user_id, date)` blocks high-frequency data
- ❌ No timestamp precision for intra-day events
- ❌ No event sourcing capability

### **New Schema (Event-Driven)**
```sql
-- High-frequency events table
CREATE TABLE calorie_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    event_type VARCHAR(30) NOT NULL, -- 'consumed', 'burned_exercise', 'burned_bmr', 'weight'
    event_timestamp TIMESTAMPTZ NOT NULL, -- Precision to second
    value DECIMAL(6, 1) NOT NULL,
    source VARCHAR(50), -- 'healthkit', 'manual', 'app_tracking'  
    metadata JSONB, -- Additional data (confidence, device, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enhanced daily_balances for aggregations
ALTER TABLE daily_balances 
ADD COLUMN events_count INTEGER DEFAULT 0,
ADD COLUMN last_event_timestamp TIMESTAMPTZ;
```

### **Migration Steps**
1. ✅ **Backup existing data**
2. ✅ **Create calorie_events table**
3. ✅ **Migrate daily_balances structure**
4. ✅ **Implement dual-write pattern** (events + daily aggregation)
5. ✅ **Update APIs to use events**
6. ✅ **Remove old constraints**

---

## 📝 Technical Architecture Notes

### **Event-Driven Benefits:**
- ✅ **Smartphone Integration**: Support 2-minute sampling
- ✅ **Timeline Precision**: Second-level accuracy
- ✅ **Scalability**: Partitioning by user/date
- ✅ **Analytics**: Rich behavioral insights
- ✅ **Real-time**: Live dashboard capabilities
- ✅ **5-Level Temporal Views**: Hourly → Monthly analytics ready

### **🗓️ Multi-Level Temporal Analytics Capabilities:**
- **🕐 Hourly View**: Real-time intraday trends, meal timing analysis, exercise patterns
- **📅 Daily View**: Day-over-day comparisons, daily goal tracking, streak analysis
- **📆 Weekly View**: Weekly patterns, habit formation, consistency tracking (Mon-Sun)
- **🗓️ Monthly View**: Long-term trends, monthly progress reports, seasonal patterns
- **⚖️ Balance View**: Net calorie calculations, weight correlation, deficit/surplus analysis

### **📊 Advanced Aggregation Features:**
- **Active Days Tracking**: `active_days` count per period for engagement analysis
- **Multi-Level Averages**: `avg_daily_value`, `avg_weekly_value` for trend comparison
- **Event Density**: `event_count` per aggregation for data quality assessment
- **Time Range Precision**: `first_event`/`last_event` for accurate period analysis
- **Cross-Period Analysis**: Week numbers, month numbers for seasonal comparisons

### **Performance Considerations:**
- **Indexing Strategy**: user_id + event_timestamp compound indexes
- **Caching Layer**: Redis for hourly/daily aggregations
- **Partitioning**: Time-based partitioning for events table
- **Background Jobs**: Pre-calculation of common aggregations

### **Mobile App Integration:**
- **Batch API**: Send multiple events in single request
- **Offline Support**: Queue events when offline
- **Conflict Resolution**: Timestamp-based event ordering
- **Data Validation**: Client-side + server-side validation

---

**🔄 Migration Status**: ✅ **Database Phase Complete**  
**📊 New Completion**: 31% (17/54 endpoints)  
**🗓️ Temporal Views**: ✅ **All 5 levels ready**  
**🎯 Event-Driven APIs**: Week 2  
**🚀 Mobile-Ready**: Week 4  
**📈 Full Analytics**: Week 6
