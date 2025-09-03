# 🏋️ Web Dashboard - Simple Testing Interface

Super simple web interface per testare l'integrazione Analytics + User Management.

## 🚀 Quick Start

```bash
# Avvia i servizi (se non già running)
make start

# Avvia la web dashboard
cd services/web-dashboard
python3 server.py
```

Dashboard disponibile su: **http://localhost:3000**

## 📋 Features

### 📝 **Data Input**
- Form per inserire dati fitness giornalieri
- Quick activity logger  
- Generazione automatica di dati mock per una settimana

### 📊 **Analytics View**
- Real-time analytics dal tuo Analytics Service
- Metriche basic: steps, calorie, sleep, attività
- Simple chart con Chart.js
- Status check dei servizi

### ⚡ **Quick Actions**
- **Generate Mock Week**: Crea 7 giorni di dati realistici
- **Check Services**: Verifica che User Management e Analytics siano online
- **Refresh Analytics**: Ricarica i dati elaborati

## 🛠️ Come Funziona

1. **Data Flow**: Web Dashboard → User Management API → Database
2. **Analytics Flow**: Web Dashboard → Analytics Service → User Management API
3. **Visualization**: Chart.js per grafici semplici

## 📊 Test Scenarios

### Scenario 1: Basic Data Entry
1. Inserisci dati fitness nel form
2. Clicca "Add Fitness Data"  
3. Clicca "Refresh Analytics"
4. Vedi risultati + grafico

### Scenario 2: Mock Data Generation  
1. Clicca "Generate Mock Week"
2. Aspetta 4-5 secondi
3. Clicca "Refresh Analytics"
4. Vedi trend dei dati generati

### Scenario 3: Activity Tracking
1. Seleziona tipo attività
2. Inserisci durata
3. Clicca "Add Activity"
4. Refresh per vedere impatto su analytics

## 🔧 Configuration

La dashboard usa questi endpoint:
- **User Management**: `http://localhost:8001`
- **Analytics**: `http://localhost:8003`

Se i servizi sono su porte diverse, modifica le variabili in `index.html`:
```javascript
const USER_MANAGEMENT_URL = 'http://localhost:8001';
const ANALYTICS_URL = 'http://localhost:8003';
```

## ⚠️ Troubleshooting

**Services not responding?**
```bash
make health-check
docker ps  # verifica container attivi
```

**Port 3000 already in use?**
```bash
lsof -ti:3000 | xargs kill
```

**CORS errors?**
Il server include headers CORS automatici.

---

💡 **Tip**: Questa è una implementazione **super semplice** fatta apposta per testing rapido!
