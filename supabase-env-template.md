# 🔐 Configurazione Environment Variables con Secret File

## ⚡ **Metodo .env File (RACCOMANDATO)**

### 📁 **Passo 1: Prepara il file .env**
Ho creato `config/environments/production.env` con tutte le variabili necessarie.

**Compila questi valori**:
1. **SUPABASE_URL** - Vai su [Supabase Dashboard](https://app.supabase.com) → Settings → API  
2. **SUPABASE_ANON_KEY** - Public anon key (sicuro)
3. **SUPABASE_SERVICE_ROLE_KEY** - Service role key (**SEGRETO**)
4. **JWT_SECRET** - Genera una chiave sicura di almeno 32 caratteri

### 🚀 **Passo 2: Carica su Render**

1. **Vai su [Render Dashboard](https://dashboard.render.com)**
2. **Seleziona `nutrifit-user-management`**  
3. **Vai su "Environment" tab**
4. **Clicca "Secret Files"**
5. **Add Secret File**:
   - **Filename**: `.env`
   - **Contents**: Copia tutto il contenuto di `config/environments/production.env` (compilato)

### ✅ **Passo 3: Deploy Automatico**
Il servizio si riavvierà automaticamente e leggerà il file `.env`!

## 🔄 **Vantaggi del Secret File**
- ✅ **Un solo file** invece di tante variabili
- ✅ **Più sicuro** - il contenuto non è visibile nei log
- ✅ **Facile da gestire** - puoi aggiornare tutto in una volta
- ✅ **Backup semplice** - salvi il file .env localmente

## ⚠️ **Importante**
- Non committare MAI il file production.env con i valori reali su Git
- Usa il template e compila i valori direttamente su Render
