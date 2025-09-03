# 🧹 Docker Cleanup Scripts

Questa cartella contiene script per automatizzare la pulizia di Docker e liberare spazio disco nella GymBro Platform.

## 📁 Script Disponibili

### 1. `docker-cleanup.sh` - Pulizia Intelligente ⭐️ **CONSIGLIATO**

Pulizia sicura e intelligente che mantiene solo le immagini essenziali:

```bash
# Esecuzione diretta
./scripts/docker-cleanup/docker-cleanup.sh

# Oppure tramite Makefile
make clean-docker
```

**Cosa fa:**
- ✅ Rimuove container fermati
- ✅ Rimuove immagini dangling (`<none>`)
- ✅ Rimuove vecchie versioni dei servizi GymBro
- ✅ Rimuove volumi non utilizzati
- ✅ Pulisce la build cache
- ✅ **MANTIENE** le immagini essenziali in uso

**Immagini preservate:**
- `analytics-service-enhanced`
- `user-management-enhanced` 
- `postgres:15-alpine`
- `n8nio/n8n`
- `python:3.11-slim`
- `traefik:v3.0`

### 2. `docker-nuclear-cleanup.sh` - Pulizia Aggressiva ⚠️

Pulizia completa di tutto il non utilizzato (con conferma utente):

```bash
# Esecuzione diretta
./scripts/docker-cleanup/docker-nuclear-cleanup.sh

# Oppure tramite Makefile
make clean-nuclear
```

**⚠️ ATTENZIONE:** Rimuove tutto tranne container in esecuzione e relative immagini!

## 🚀 Utilizzo Consigliato

### Pulizia Regolare (Settimanale)
```bash
make clean-docker
```

### Pulizia Prima di Deploy
```bash
make clean-docker
```

### Pulizia Completa (Solo se necessario)
```bash
make clean-nuclear
```

## 📊 Monitoraggio Spazio

Per controllare l'utilizzo dello spazio Docker:

```bash
# Panoramica generale
docker system df

# Dettagli volumi
docker system df -v

# Lista immagini con dimensioni
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
```

## 🔧 Personalizzazione

Gli script possono essere modificati per adattarsi a esigenze specifiche:

1. **Aggiungere immagini da preservare:** Modifica l'array `essential_images` in `docker-cleanup/docker-cleanup.sh`
2. **Modificare comportamento:** Gli script sono completamente commentati e modulari

## ⚡️ Automazione

Puoi aggiungere la pulizia automatica alla tua routine:

```bash
# Crontab per pulizia settimanale (Domenica alle 2:00)
0 2 * * 0 /path/to/gymbro-platform/scripts/docker-cleanup/docker-cleanup.sh

# Pre-commit hook per pulizia automatica
echo "make clean-docker" >> .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

## 📈 Risultati Tipici

- **Prima della pulizia:** ~15GB di immagini Docker
- **Dopo pulizia intelligente:** ~3.4GB (solo essenziali) 
- **Spazio recuperato:** ~11-12GB tipici

---

💡 **Tip:** Esegui `make clean-docker` regolarmente per mantenere ottimale l'utilizzo dello spazio disco!
