# 🚀 GitHub Actions Workflows

## Active Workflows

### `simple-ci.yml` ✅ **ATTIVO**
- **Scopo**: CI/CD semplificato per repository-based deployment
- **Strategia**: Test + Validazione + Render auto-deploy 
- **Features**:
  - Change detection per ottimizzazione build
  - Test automatici per user-management e calorie-balance  
  - Docker build testing
  - Release GitHub automatiche
  - Compatibile con Render repository sync

**Workflow Steps:**
1. 🔍 Detect changes nei servizi
2. 🧪 Test servizi modificati (pytest + Docker build)
3. 📦 Release automatica su main branch
4. 🚀 Render auto-deploy da repository

## Archived Workflows

### `platform-deployment.yml` ❌ **ARCHIVIATO**
- **Ubicazione**: `.github/old_workflow_CICD/platform-deployment.yml`
- **Scopo**: Deployment complesso con container registry
- **Motivo Disattivazione**: Troppo complesso per la strategia repository-based di Render

## Deployment Strategy

**Attuale (Repository-Based):**
```
GitHub Push → simple-ci.yml (test) → Render Auto-Deploy
```

**Precedente (Container Registry):**
```
GitHub Push → Build Docker → Push GHCR → Deploy (COMPLESSO)
```

## Configuration

### Environment Variables
I servizi ricevono environment variables da:
- **Render Dashboard**: Configurazione production
- **GitHub Secrets**: Per testing in CI/CD
- **Local .env**: Per sviluppo locale

### Render Auto-Deploy
- **User Management**: Auto-deploy attivato su `services/user-management/**`
- **Calorie Balance**: Auto-deploy attivato su `services/calorie-balance/**`
- **Branch**: `main` (auto-deploy immediato)

## Usage

### Trigger Workflow
```bash
# Push automatico (main/develop)
git push origin main

# Pull Request
git push origin feature/branch
```

### Check Status  
- **GitHub**: [Actions tab](https://github.com/giamma80/gymbro-platform/actions)
- **Render**: [Dashboard](https://dashboard.render.com)

### Debug
```bash
# Test locale prima del push
cd services/user-management && poetry run pytest
cd services/calorie-balance && poetry run pytest

# Test Docker build
docker build --target production .
```

---
**🎯 Status**: Workflow ottimizzato per repository-based deployment con Render