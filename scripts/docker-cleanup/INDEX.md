# 📁 Docker Cleanup - Struttura Files

## 🗂️ Files in questa directory

### 📄 `docker-cleanup.sh`
**Pulizia intelligente Docker** - Script principale per la pulizia sicura

**Cosa fa:**
- ✅ Rimuove container fermati  
- ✅ Rimuove immagini dangling (`<none>`)
- ✅ Rimuove vecchie versioni servizi GymBro
- ✅ Rimuove volumi non utilizzati
- ✅ Pulisce build cache
- ✅ **PRESERVA** immagini essenziali

**Uso:**
```bash
./docker-cleanup.sh
# oppure
make clean-docker
```

### 📄 `docker-nuclear-cleanup.sh`  
**Pulizia aggressiva Docker** - Per liberare il massimo spazio possibile

**⚠️ ATTENZIONE:** Rimuove tutto tranne container attivi e relative immagini!

**Uso:**
```bash
./docker-nuclear-cleanup.sh
# oppure  
make clean-nuclear
```

### 📄 `README.md`
**Documentazione completa** con:
- Guide dettagliate per ogni script
- Esempi d'uso avanzati
- Suggerimenti automazione
- Monitoraggio spazio disco

---

## 🎯 Raccomandazioni d'uso

- **Uso regolare**: `./docker-cleanup.sh` (settimanale)
- **Prima deploy**: `./docker-cleanup.sh` 
- **Emergenza spazio**: `./docker-nuclear-cleanup.sh`

💡 **Tip**: Leggi sempre il README.md per la documentazione completa!
