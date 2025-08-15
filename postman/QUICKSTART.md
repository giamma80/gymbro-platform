# 🚀 Quick Start Guide - Postman Collection

## ⚡ **Setup in 2 Minuti**

### 1. **Import Collection**
```
1. Apri Postman
2. Click "Import" 
3. Drag & drop tutti i file .json dalla cartella postman/
4. ✅ Done!
```

### 2. **Test Immediato Production**
```
1. Seleziona environment "GymBro Production"
2. Folder "🏥 Health & Status" → "Health Check"
3. Click "Send"
4. ✅ Dovresti vedere: {"status": "healthy"}
```

## 🎯 **Test Scenarios Pronti**

### **Scenario A: Nuovo Utente Completo**
**Tempo stimato: 3 minuti**

```
Step 1: 🔐 Register User
→ Body pre-compilato, click "Send"
→ ✅ Status 201, user creato

Step 2: 🔐 Login  
→ Credenziali auto-caricate, click "Send"
→ ✅ Status 200, JWT token salvato automaticamente

Step 3: 👤 Get Profile
→ Authorization header auto-aggiunto, click "Send"  
→ ✅ Status 200, profilo utente completo

Step 4: 👤 Get Profile Stats
→ Click "Send"
→ ✅ Status 200, BMI e statistiche calcolate
```

### **Scenario B: Test Authentication Flow**
**Tempo stimato: 2 minuti**

```
Step 1: 🔐 Register User → Status 201
Step 2: 🔐 Login → Status 200, tokens saved
Step 3: 🔐 Change Password → Status 200  
Step 4: 🔐 Login (new password) → Status 200
```

### **Scenario C: Profile Management**
**Tempo stimato: 2 minuti**

```
Step 1: 👤 Get Profile → Status 200
Step 2: 👤 Update Profile → Status 200, modifica peso/altezza
Step 3: 👤 Get Profile Stats → Status 200, nuovo BMI calcolato
Step 4: ⚙️ Update Preferences → Status 200, cambia notifiche
```

## 🔧 **Customizzazione Rapida**

### **Cambia Dati Test**
Environment → Variables:
```
test_email: "tuo-email@test.com"
test_password: "TuaPassword123!"
test_full_name: "Il Tuo Nome"
```

### **Usa Dati Reali**
```
1. Modifica le variabili nell'environment
2. Run "Register User" con i tuoi dati
3. Tutti gli altri test useranno i tuoi dati
```

## ⚡ **Newman CLI (Automazione)**

### **Install Newman**
```bash
npm install -g newman
```

### **Run Tests**
```bash
# Quick production test
cd postman/
./run-tests.sh prod

# Test both environments  
./run-tests.sh both

# Development only
./run-tests.sh dev
```

### **CI/CD Integration**
```bash
# In GitHub Actions / Jenkins
newman run GymBro-Platform.postman_collection.json \
  -e environments/GymBro-Production.postman_environment.json \
  --reporters cli,json
```

## 🎨 **Pro Tips**

### **Auto-Variables**
- ✅ **Email**: Auto-genera con timestamp per evitare duplicati
- ✅ **Tokens**: Salvati automaticamente dopo login
- ✅ **User ID**: Estratto automaticamente dalla registrazione

### **Error Testing**
```
1. Modifica email per duplicare → 400 Bad Request
2. Password sbagliata → 401 Unauthorized  
3. Token scaduto → 401 Unauthorized
4. Endpoint inesistente → 404 Not Found
```

### **Performance Testing**
Tutti i requests includono test di performance:
```javascript
pm.test("Response time < 1000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});
```

## 🚨 **Troubleshooting Veloce**

### **Token Scaduto**
```
❌ 401 Unauthorized
✅ Run "Login" per nuovo token
```

### **Environment Sbagliato** 
```
❌ Connection refused
✅ Switch a "GymBro Production"
```

### **Dati Duplicati**
```
❌ Email already exists  
✅ Cambia test_email nell'environment
```

## 📊 **Test Results**

### **Success Indicators**
```
✅ Status 200/201 per tutti i requests
✅ Response time < 550ms  
✅ Tutti i test automatici passano
✅ JWT tokens validi e funzionanti
```

### **What to Expect**
```
Health Check: ~100ms
Register User: ~300ms  
Login: ~200ms
Profile Operations: ~150ms
```

---

**🎯 Ready to test? Import i files e inizia con "Health Check"!**
