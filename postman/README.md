# 🏋️ GymBro Platform - Postman Collection

Progetto Postman completo per testare il **User Management Service** della GymBro Platform.

## 📦 **Contenuto del Progetto**

### 📂 Files Inclusi
- `GymBro-Platform.postman_collection.json` - Collection principale
- `environments/GymBro-Development.postman_environment.json` - Environment Development
- `environments/GymBro-Production.postman_environment.json` - Environment Production

### 🌐 **Environments Disponibili**

#### **Development Environment**
- **Base URL**: `http://localhost:8000`
- **Uso**: Testing locale durante sviluppo
- **Dati Test**: User predefiniti per test rapidi

#### **Production Environment**
- **Base URL**: `https://gymbro-user-service.onrender.com`
- **Uso**: Testing del servizio live in produzione
- **Dati Test**: User reali per validazione production

## 🚀 **Setup Rapido**

### 1. **Import in Postman**
```bash
# Opzione 1: Import manuale
1. Apri Postman
2. Click "Import"
3. Drag & drop GymBro-Platform.postman_collection.json
4. Import anche i 2 environment files

# Opzione 2: Import da file
File → Import → Upload Files → Seleziona tutti i .json files
```

### 2. **Seleziona Environment**
```
1. Click dropdown "No Environment" in alto a destra
2. Seleziona "GymBro Production" per test live
3. Oppure "GymBro Development" per test locali
```

### 3. **Test Immediato**
```
1. Apri folder "🏥 Health & Status"
2. Clicca "Health Check"
3. Click "Send"
4. ✅ Dovresti vedere status: "healthy"
```

## 🎯 **Workflow di Testing Consigliato**

### **Scenario 1: Test Completo Nuovo Utente**
```
1. 🏥 Health Check                    → Verifica servizio attivo
2. 🔐 Register User                   → Crea nuovo account
3. 🔐 Login                          → Ottieni JWT tokens
4. 👤 Get Profile                    → Verifica profilo
5. 👤 Update Profile                 → Modifica dati
6. 👤 Get Profile Stats              → Controlla BMI/stats
7. ⚙️ Get Preferences               → Vedi impostazioni
8. ⚙️ Update Preferences            → Cambia preferenze
```

### **Scenario 2: Test Authentication Flow**
```
1. 🔐 Register User                   → Crea account
2. 🔐 Login                          → Login normale
3. 🔐 Change Password                → Cambia password
4. 🔐 Login (con nuova password)     → Verifica cambio
```

### **Scenario 3: Test Admin Operations**
```
1. Registra user con role "admin"
2. 🔐 Login come admin
3. 👑 List All Users                 → Visualizza tutti gli utenti
```

## 🔧 **Configurazione Avanzata**

### **Custom Test Data**
Modifica le variabili negli environments per usare i tuoi dati:

```json
{
  "test_email": "il-tuo-email@test.com",
  "test_password": "TuaPasswordSicura123!",
  "test_full_name": "Il Tuo Nome Completo"
}
```

### **JWT Token Management**
I token JWT vengono gestiti automaticamente:
- ✅ **Auto-store**: Login salva automaticamente access_token
- ✅ **Auto-use**: Tutte le requests autenticate usano il token
- ✅ **Auto-refresh**: Logica per refresh token inclusa

### **Test Automation**
Ogni request include test automatici:
```javascript
pm.test("User registration successful", function () {
    pm.response.to.have.status(201);
    const response = pm.response.json();
    pm.expect(response).to.have.property("user_id");
});
```

## 📊 **Collections Organizzate**

### 🏥 **Health & Status**
- `Health Check` - Basic health endpoint
- `Ping` - Connectivity test
- `Detailed Health Check` - Database + system status

### 🔐 **Authentication**
- `Register User` - Create new account with full profile
- `Login` - Get JWT access & refresh tokens
- `Change Password` - Update user password

### 👤 **Profile Management**
- `Get Profile` - Retrieve user profile
- `Update Profile` - Modify user information
- `Get Profile Stats` - BMI and activity metrics

### ⚙️ **Preferences**
- `Get Preferences` - User settings and preferences
- `Update Preferences` - Modify notifications, privacy, units

### 👑 **Admin Operations**
- `List All Users` - Admin-only user management

### 🗑️ **Account Management**
- `Delete Account` - GDPR-compliant account deletion

## 🎨 **Features Avanzate**

### **Pre-request Scripts**
Auto-generazione dati test se non configurati:
```javascript
// Auto-generate unique email for testing
const timestamp = Date.now();
pm.environment.set("test_email", `testuser${timestamp}@gymbro.test`);
```

### **Response Tests**
Validazione automatica di ogni response:
```javascript
pm.test("Service is healthy", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    pm.expect(response.status).to.eql("healthy");
});
```

### **Environment Variables**
Gestione dinamica di:
- 🔑 **Auth Tokens**: access_token, refresh_token
- 👤 **User Data**: user_id, profile info
- 🌐 **URLs**: base_url per dev/prod switching
- 🧪 **Test Data**: email, password, profile fields

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **401 Unauthorized**
```
❌ Problema: Token JWT scaduto o mancante
✅ Soluzione: Run "Login" request per ottenere nuovo token
```

#### **404 Not Found**
```
❌ Problema: Environment sbagliato o servizio down
✅ Soluzione: 
   1. Verifica environment selezionato
   2. Run "Health Check" per verificare servizio
```

#### **500 Server Error**
```
❌ Problema: Errore lato server
✅ Soluzione:
   1. Check "Detailed Health Check" per status database
   2. Verifica logs del servizio
```

### **Debug Tips**
```
1. 🔍 Console Tab: Vedi logs dettagliati
2. 📊 Test Results: Verifica tutti i test passati
3. 🌐 Network: Analizza request/response headers
4. ⚙️ Environment: Controlla variabili settate
```

## 🎯 **Production Testing Checklist**

### **Pre-Deployment Validation**
- [ ] Health endpoints rispondono
- [ ] User registration funziona
- [ ] Authentication flow completo
- [ ] JWT tokens valid
- [ ] Database connectivity OK
- [ ] Error handling corretto
- [ ] Response times acceptable (<550ms)

### **Post-Deployment Verification**
- [ ] Production URLs aggiornati
- [ ] SSL/HTTPS working
- [ ] CORS configuration OK
- [ ] Rate limiting active
- [ ] Security headers present

## 📈 **Metriche & Monitoring**

### **Performance Targets**
- **Response Time**: <550ms (production)
- **Success Rate**: >99%
- **Error Rate**: <1%

### **Test Coverage**
- ✅ All endpoints tested
- ✅ Authentication flows
- ✅ Error scenarios
- ✅ Input validation
- ✅ Security checks

---

## 🔗 **Links Utili**

- **🌐 Production Service**: https://gymbro-user-service.onrender.com
- **📚 API Documentation**: https://gymbro-user-service.onrender.com/docs
- **🐳 Docker Images**: https://github.com/giamma80/gymbro-platform/pkgs/container/gymbro-user-management
- **📖 Project Repository**: https://github.com/giamma80/gymbro-platform

---

**Created by**: GymBro Platform Team  
**Last Updated**: 15 Agosto 2025  
**Version**: 1.0.0
