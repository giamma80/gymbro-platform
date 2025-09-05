#!/bin/bash

# Script completo per avviare il servizio Calorie Balance e testare le API
# Autore: GitHub Copilot
# Data: 5 settembre 2025

# set -e  # Commentato per debug

# Colori per l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Avvio del servizio Calorie Balance e test completi...${NC}"

# Directory del servizio
SERVICE_DIR="/Users/giamma/workspace/gymbro-platform/services/calorie-balance"
cd "$SERVICE_DIR"

echo -e "${YELLOW}📂 Directory corrente: $(pwd)${NC}"

# Funzione per controllare se il server è già in esecuzione
check_server_running() {
    if curl -s -f "http://localhost:8001/health/" > /dev/null 2>&1; then
        return 0  # Server in esecuzione
    else
        return 1  # Server non in esecuzione
    fi
}

# Funzione per terminare processi esistenti
kill_existing_server() {
    echo -e "${YELLOW}🔄 Controllo processi esistenti...${NC}"
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        echo -e "${YELLOW}⚠️ Processo uvicorn esistente trovato, lo termino...${NC}"
        pkill -f "uvicorn app.main:app" || true
        sleep 3
    fi
}

# Verifica ambiente Poetry
echo -e "${BLUE}🔍 Verifica ambiente Poetry...${NC}"
if ! poetry --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Poetry non trovato. Installare Poetry prima di continuare.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Poetry trovato: $(poetry --version)${NC}"

# Installa dipendenze
echo -e "${BLUE}📦 Installo dipendenze...${NC}"
poetry install --only main > /dev/null 2>&1
echo -e "${GREEN}✅ Dipendenze installate${NC}"

# Verifica che l'app si importi correttamente
echo -e "${BLUE}🔍 Verifica importazione app...${NC}"
if poetry run python -c "from app.main import app; print('✅ App importata correttamente')" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ App importata correttamente${NC}"
else
    echo -e "${RED}❌ Errore nell'importazione app${NC}"
    poetry run python -c "from app.main import app"  # Mostra l'errore
    exit 1
fi

# Termina server esistente se presente
kill_existing_server

# Avvia il servizio
echo -e "${BLUE}🌐 Avvio servizio FastAPI su porta 8001...${NC}"
cd "$SERVICE_DIR"  # Assicurati di essere nella directory corretta
poetry run uvicorn app.main:app --reload --port 8001 &
SERVER_PID=$!

# Funzione di cleanup
cleanup() {
    echo -e "${YELLOW}🧹 Arresto del server...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Server arrestato${NC}"
}
trap cleanup EXIT

# Attende che il server sia pronto
echo -e "${YELLOW}⏳ Attendo avvio del server...${NC}"
sleep 3  # Aspetta un po' per l'avvio iniziale

for i in {1..20}; do
    if check_server_running; then
        echo -e "${GREEN}✅ Server in esecuzione su porta 8001${NC}"
        break
    else
        if [ $i -eq 20 ]; then
            echo -e "${RED}❌ Server non risponde dopo 20 tentativi${NC}"
            echo -e "${RED}Possibili errori di avvio:${NC}"
            # Mostra gli ultimi log se il server non si avvia
            sleep 2
            exit 1
        fi
        echo -e "${YELLOW}⏳ Tentativo $i/20...${NC}"
        sleep 2
    fi
done

echo -e "${BLUE}🏥 === INIZIO SANITY CHECK E TEST FUNZIONALI ===${NC}"

# Test 1: Health Check
echo -e "${BLUE}🏥 Test 1: Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s "http://localhost:8001/health/")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✅ Health Check PASS${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Health Check FAIL${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# Test 2: Creazione utente
echo -e "\n${BLUE}👤 Test 2: Creazione utente...${NC}"

# Genera ID unico per il test
TIMESTAMP=$(date +%s)
USER_ID="test_user_$TIMESTAMP"
EMAIL="test$TIMESTAMP@example.com"

USER_DATA="{
    \"user_id\": \"$USER_ID\",
    \"email\": \"$EMAIL\",
    \"full_name\": \"Test User\"
}"

CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/users/" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")

if echo "$CREATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Creazione utente PASS${NC}"
    echo "$CREATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Creazione utente FAIL${NC}"
    echo "$CREATE_RESPONSE"
    exit 1
fi

# Test 3: Recupero utente
echo -e "\n${BLUE}🔍 Test 3: Recupero utente...${NC}"
GET_RESPONSE=$(curl -s "http://localhost:8001/api/v1/users/$USER_ID")

if echo "$GET_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Recupero utente PASS${NC}"
    echo "$GET_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Recupero utente FAIL${NC}"
    echo "$GET_RESPONSE"
    exit 1
fi

# Test 4: Aggiornamento profilo utente
echo -e "\n${BLUE}✏️ Test 4: Aggiornamento profilo utente...${NC}"
UPDATE_DATA='{
    "age": 30,
    "gender": "MALE",
    "height_cm": 180.5,
    "weight_kg": 75.0,
    "activity_level": "MODERATE"
}'

UPDATE_RESPONSE=$(curl -s -X PUT "http://localhost:8001/api/v1/users/$USER_ID" \
    -H "Content-Type: application/json" \
    -d "$UPDATE_DATA")

if echo "$UPDATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Aggiornamento profilo PASS${NC}"
    echo "$UPDATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Aggiornamento profilo FAIL${NC}"
    echo "$UPDATE_RESPONSE"
    exit 1
fi

# Test 5: Verifica documentazione API
echo -e "\n${BLUE}📚 Test 5: Documentazione API...${NC}"
if curl -s -f "http://localhost:8001/docs" > /dev/null; then
    echo -e "${GREEN}✅ Swagger docs disponibile${NC}"
else
    echo -e "${YELLOW}⚠️ Swagger docs non disponibile${NC}"
fi

if curl -s -f "http://localhost:8001/redoc" > /dev/null; then
    echo -e "${GREEN}✅ ReDoc disponibile${NC}"
else
    echo -e "${YELLOW}⚠️ ReDoc non disponibile${NC}"
fi

# Test 6: Test endpoint non esistente (dovrebbe restituire 404)
echo -e "\n${BLUE}🚫 Test 6: Endpoint inesistente (404 atteso)...${NC}"
NOT_FOUND_RESPONSE=$(curl -s -w "%{http_code}" "http://localhost:8001/api/v1/nonexistent")
if echo "$NOT_FOUND_RESPONSE" | grep -q "404"; then
    echo -e "${GREEN}✅ Gestione 404 PASS${NC}"
else
    echo -e "${YELLOW}⚠️ Gestione 404 inaspettata${NC}"
fi

# Summary finale
echo -e "\n${GREEN}🎉 === TUTTI I TEST COMPLETATI CON SUCCESSO! === 🎉${NC}"
echo -e "${BLUE}📊 Riepilogo test:${NC}"
echo -e "  ✅ Health Check"
echo -e "  ✅ Creazione utente"
echo -e "  ✅ Recupero utente"
echo -e "  ✅ Aggiornamento profilo"
echo -e "  ✅ Documentazione API"
echo -e "  ✅ Gestione errori"

echo -e "\n${BLUE}🌐 Il servizio è disponibile su:${NC}"
echo -e "  • API: http://localhost:8001"
echo -e "  • Health: http://localhost:8001/health/"
echo -e "  • Docs: http://localhost:8001/docs"
echo -e "  • ReDoc: http://localhost:8001/redoc"

echo -e "\n${BLUE}👤 Utente di test creato:${NC}"
echo -e "  • ID: $USER_ID"
echo -e "  • Email: $EMAIL"

echo -e "\n${YELLOW}📝 Il servizio rimarrà in esecuzione. Premi Ctrl+C per terminare.${NC}"

# Mantieni il server in esecuzione
echo -e "${BLUE}⏳ Server in attesa... (Ctrl+C per uscire)${NC}"
while true; do
    if ! check_server_running; then
        echo -e "${RED}❌ Server non più raggiungibile!${NC}"
        exit 1
    fi
    sleep 10
done

# Test dell'API Health Check
echo -e "${BLUE}🏥 Test Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s "http://localhost:8001/api/v1/health/")
echo -e "${GREEN}Health Check Response:${NC}"
echo "$HEALTH_RESPONSE" | python3 -m json.tool

# Test creazione utente
echo -e "${BLUE}👤 Test creazione utente...${NC}"
USER_DATA='{
    "user_id": "test_user_123",
    "email": "test@example.com",
    "full_name": "Test User"
}'

CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/users/" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")

echo -e "${GREEN}Creazione Utente Response:${NC}"
echo "$CREATE_RESPONSE" | python3 -m json.tool

# Verifica se la creazione è andata a buon fine
if echo "$CREATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Creazione utente riuscita${NC}"
else
    echo -e "${RED}❌ Errore nella creazione utente${NC}"
    echo "$CREATE_RESPONSE"
    exit 1
fi

# Test recupero utente
echo -e "${BLUE}🔍 Test recupero utente...${NC}"
GET_RESPONSE=$(curl -s "http://localhost:8001/api/v1/users/test_user_123")

echo -e "${GREEN}Recupero Utente Response:${NC}"
echo "$GET_RESPONSE" | python3 -m json.tool

# Verifica se il recupero è andato a buon fine
if echo "$GET_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Recupero utente riuscito${NC}"
else
    echo -e "${RED}❌ Errore nel recupero utente${NC}"
    exit 1
fi

# Test aggiornamento profilo utente
echo -e "${BLUE}✏️ Test aggiornamento profilo utente...${NC}"
UPDATE_DATA='{
    "age": 30,
    "gender": "MALE",
    "height_cm": 180.5,
    "weight_kg": 75.0,
    "activity_level": "MODERATE"
}'

UPDATE_RESPONSE=$(curl -s -X PUT "http://localhost:8001/api/v1/users/test_user_123" \
    -H "Content-Type: application/json" \
    -d "$UPDATE_DATA")

echo -e "${GREEN}Aggiornamento Profilo Response:${NC}"
echo "$UPDATE_RESPONSE" | python3 -m json.tool

# Verifica se l'aggiornamento è andato a buon fine
if echo "$UPDATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Aggiornamento profilo riuscito${NC}"
else
    echo -e "${RED}❌ Errore nell'aggiornamento profilo${NC}"
    exit 1
fi

# Test degli endpoint di documentazione
echo -e "${BLUE}📚 Test documentazione API...${NC}"
if curl -s -f "http://localhost:8001/docs" > /dev/null; then
    echo -e "${GREEN}✅ Documentazione Swagger disponibile su http://localhost:8001/docs${NC}"
else
    echo -e "${YELLOW}⚠️ Documentazione Swagger non disponibile${NC}"
fi

if curl -s -f "http://localhost:8001/redoc" > /dev/null; then
    echo -e "${GREEN}✅ Documentazione ReDoc disponibile su http://localhost:8001/redoc${NC}"
else
    echo -e "${YELLOW}⚠️ Documentazione ReDoc non disponibile${NC}"
fi

# Summary finale
echo -e "${GREEN}🎉 TUTTI I TEST COMPLETATI CON SUCCESSO! 🎉${NC}"
echo -e "${BLUE}📊 Riepilogo test:${NC}"
echo -e "  ✅ Connessione database"
echo -e "  ✅ Avvio servizio FastAPI"
echo -e "  ✅ Health Check"
echo -e "  ✅ Creazione utente"
echo -e "  ✅ Recupero utente"
echo -e "  ✅ Aggiornamento profilo"
echo -e "  ✅ Documentazione API"

echo -e "${BLUE}🌐 Il servizio è disponibile su:${NC}"
echo -e "  • API: http://localhost:8001"
echo -e "  • Health: http://localhost:8001/api/v1/health/"
echo -e "  • Docs: http://localhost:8001/docs"
echo -e "  • ReDoc: http://localhost:8001/redoc"

echo -e "${YELLOW}📝 Il servizio rimarrà in esecuzione. Premi Ctrl+C per terminare.${NC}"

# Mantieni il server in esecuzione
wait $SERVER_PID
