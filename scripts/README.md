# 🛠️ GymBro Platform Scripts

Questa cartella contiene tutti gli script di utilità per la gestione e manutenzione della GymBro Platform.

## 📁 Struttura Scripts

```
scripts/
├── README.md                    # Questo file
├── docker-cleanup/              # 🧹 Script pulizia Docker
│   ├── README.md               # Documentazione dettagliata
│   ├── docker-cleanup.sh       # Pulizia intelligente
│   └── docker-nuclear-cleanup.sh # Pulizia aggressiva
├── health-check.sh             # 🏥 Health check servizi
└── test-api.py                 # 🧪 Test API endpoints
```

## 🚀 Script Disponibili

### 🧹 Docker Cleanup
Utilities per la pulizia e ottimizzazione di Docker:
- **Pulizia intelligente**: Mantiene solo immagini essenziali
- **Pulizia aggressiva**: Rimuove tutto il non utilizzato
- **Automazione**: Integrazione con Makefile

📂 **Percorso**: `docker-cleanup/`  
📖 **Documentazione**: [docker-cleanup/README.md](docker-cleanup/README.md)

```bash
# Comandi rapidi
make clean-docker   # Pulizia intelligente
make clean-nuclear  # Pulizia aggressiva
```

### 🏥 Health Check
Script per il monitoraggio della salute dei servizi:

```bash
./scripts/health-check.sh
# oppure
make health-check
```

### 🧪 API Testing
Script Python per testare tutti gli endpoint API:

```bash
python3 ./scripts/test-api.py
# oppure
make test-apis
```

## 🔧 Sviluppo Scripts

### Linee Guida

1. **Organizzazione**: Ogni categoria di script ha la sua cartella
2. **Documentazione**: Ogni script deve avere un README.md
3. **Integrazione**: Tutti gli script devono essere integrati nel Makefile
4. **Sicurezza**: Script distruttivi richiedono conferma utente
5. **Error Handling**: Gestione robusta degli errori

### Template Nuovo Script

```bash
#!/bin/bash
# 🏋️ GymBro Platform - [Nome Script]
# [Descrizione breve]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Script logic here...
```

## 📋 Makefile Integration

Tutti gli script sono integrati nel Makefile principale per facilità d'uso:

```bash
make help              # Mostra tutti i comandi disponibili
make clean-docker      # Pulizia Docker intelligente
make clean-nuclear     # Pulizia Docker aggressiva
make health-check      # Controllo salute servizi
make test-apis         # Test API endpoints
```

## 🤝 Contribuzioni

Per aggiungere nuovi script:

1. Crea una cartella dedicata se necessario
2. Includi un README.md dettagliato
3. Aggiungi il comando al Makefile principale
4. Testa su diversi scenari
5. Documenta esempi d'uso

---

💡 **Tip**: Usa sempre `make help` per vedere tutti i comandi disponibili!
