# GymBro Platform - Quality Assurance (QA)

Questa cartella contiene la suite completa di test End-to-End per la piattaforma GymBro, progettata per validare l'integrazione completa tra tutti i microservizi e garantire la coerenza funzionale dell'intera piattaforma.

## 📋 Contenuto della Cartella

### Documentazione
- **`E2E_TEST_CHOREOGRAPHY.md`** - Specifica completa della coreografia di test, definisce scenari, fasi di validazione e criteri di successo
- **`README.md`** - Questa documentazione

### Script di Test
- **`e2e_test_choreography.py`** - Script Python principale che implementa tutti i test end-to-end
- **`run_e2e_tests.sh`** - Script bash per eseguire facilmente i test con controlli preliminari

## 🎯 Obiettivi del Test Suite

Il sistema di testing è progettato per validare:

1. **Lifecycle Completo Utente** - Creazione, verifica e gestione utenti
2. **Integrazione Cross-Service** - Comunicazione tra user-management e calorie-balance
3. **GraphQL Federation** - Funzionamento corretto del gateway Apollo
4. **Coerenza Dati** - Integrità dei dati tra REST e GraphQL APIs
5. **Analytics Timeline** - Aggregazioni temporali e pattern detection
6. **Performance** - Tempi di risposta accettabili
7. **Robustezza** - Gestione errori e scenari edge

## 🚀 Esecuzione dei Test

### Prerequisiti
1. Tutti i servizi devono essere attivi:
   - User Management service su porta 8001
   - Calorie Balance service su porta 8002
   - Apollo Gateway su porta 4000

2. Python 3.x installato con il pacchetto `requests`

### Metodo Rapido (Raccomandato)
```bash
cd QA
./run_e2e_tests.sh
```

### Metodo Manuale
```bash
cd QA
python3 e2e_test_choreography.py
```

## 📊 Fasi di Test

### Phase 1: User Lifecycle Management
- Creazione utente di test
- Verifica dati utente via REST
- Validazione via GraphQL Federation

### Phase 2: Metabolic Profile Setup
- Calcolo profilo metabolico
- Validazione BMR/TDEE
- Verifica persistenza dati

### Phase 3: Calorie Goal Configuration
- Creazione obiettivi calorici
- Validazione logica business (deficit, target)
- Controllo date e attivazione

### Phase 4: Multi-Day Calorie Event Simulation
- **Day 1**: Scenario baseline (8 eventi, 1650 cal consumate, 500 bruciate)
- **Day 2**: Scenario alta attività (8 eventi, 2550 cal consumate, 950 bruciate)  
- **Day 3**: Scenario parziale giorno corrente (3 eventi)

### Phase 5: Daily Balance Validation
- Verifica aggregazioni giornaliere
- Controllo calcoli net calories
- Validazione data completeness score

### Phase 6: Timeline Analytics Validation
- Analytics orarie (24 data points)
- Comparazione analytics giornaliere
- Validazione analytics settimanali
- Detection pattern comportamentali

### Phase 7: GraphQL Federation End-to-End
- Query cross-service federate
- Analytics via GraphQL
- Performance testing

### Phase 8: Data Consistency Cross-Validation
- Confronto REST vs GraphQL
- Consistenza aggregazioni hourly→daily
- Validazione aggiornamenti real-time

## 📈 Interpretazione Risultati

### Criteri di Successo
- **HTTP Level**: Status codes corretti, tempi < 1000ms
- **Functional Level**: Calcoli matematicamente corretti, regole business rispettate
- **Integration Level**: Federation GraphQL funzionante, consistenza dati

### Output del Test
```
✅ Test passato - Funzionalità validata correttamente
❌ Test fallito - Problemi rilevati (dettagli nell'errore)
⚠️  Warning - Test parzialmente riuscito o non critico
```

### Metriche Finali
- Total Tests: Numero totale test eseguiti
- Success Rate: Percentuale di successo
- Execution Time: Tempo totale di esecuzione
- Failed Tests: Lista dettagliata errori

## 🧹 Gestione Dati di Test

Il sistema include:
- **Cleanup Automatico**: Rimozione dati di test alla fine
- **Timestamps Unici**: Evita conflitti tra esecuzioni parallele
- **Rollback**: Gestione errori con cleanup parziale
- **Isolamento**: Ogni esecuzione usa dati separati

## 🔧 Configurazione Avanzata

### Modifica Endpoints
Editare le costanti in `e2e_test_choreography.py`:
```python
USER_MANAGEMENT_URL = "http://localhost:8001"
CALORIE_BALANCE_URL = "http://localhost:8002"
APOLLO_GATEWAY_URL = "http://localhost:4000"
```

### Personalizzazione Scenari
I dati di test sono configurabili nella classe `GymBroE2ETest`:
- Profili metabolici
- Obiettivi calorici
- Eventi calorie multi-day
- Soglie di validazione

### Debug Mode
Per debugging dettagliato, modificare il livello di output nei print statements.

## 🔄 Integrazione CI/CD

Lo script è progettato per integrazione in pipeline CI/CD:
- Exit code 0 per successo, 1 per fallimenti
- Output formattato per parsing automatico
- Timeouts configurabili
- Cleanup garantito

## 📝 Manutenzione

### Aggiornamento Test
1. Modificare `E2E_TEST_CHOREOGRAPHY.md` per nuove specifiche
2. Implementare nuove fasi in `e2e_test_choreography.py`
3. Testare localmente prima del deploy
4. Aggiornare questa documentazione

### Troubleshooting Comuni
- **Service non risponde**: Verificare che tutti i servizi siano avviati
- **Database errori**: Controllare connessioni Supabase
- **GraphQL errors**: Verificare schema federation Apollo Gateway
- **Timeout errors**: Aumentare timeouts per ambienti lenti

## 🎯 Prossimi Sviluppi

- [ ] Test di carico e stress
- [ ] Test di sicurezza e autenticazione
- [ ] Test di performance analytics
- [ ] Test di recovery da errori
- [ ] Integrazione con altri microservizi (meal-tracking, health-monitor)

---

**Contatto**: Utilizzare questo sistema per validare ogni release della piattaforma GymBro prima del deployment in produzione.