# 📂 Postman Collection - File Structure

```
postman/
├── 📋 GymBro-Platform.postman_collection.json     # Main collection
├── 📁 environments/
│   ├── 🔧 GymBro-Development.postman_environment.json
│   └── 🌐 GymBro-Production.postman_environment.json
├── 📖 README.md                                   # Complete documentation
├── 🚀 QUICKSTART.md                              # Quick start guide
├── 🧪 run-tests.sh                               # Automated test runner
├── 📦 package.json                               # Newman dependencies
└── 📄 INDEX.md                                   # This file
```

## 🎯 **Quick Actions**

| Action | File | Description |
|--------|------|-------------|
| **Import Collection** | `GymBro-Platform.postman_collection.json` | Main API collection |
| **Setup Environments** | `environments/*.json` | Development & Production configs |
| **Read Documentation** | `README.md` | Complete setup guide |
| **Quick Start** | `QUICKSTART.md` | 2-minute setup |
| **Run Automated Tests** | `./run-tests.sh` | CLI testing |

## 📊 **Collection Stats**

- **Total Requests**: 14
- **Folders**: 6 organized categories
- **Environments**: 2 (Development + Production)
- **Auto Tests**: ✅ All requests include validation
- **Auth Management**: ✅ JWT tokens auto-handled
- **Test Data**: ✅ Pre-configured sample data

## 🏗️ **Architecture**

### **Request Organization**
```
🏥 Health & Status (3 requests)
├── Health Check
├── Ping  
└── Detailed Health Check

🔐 Authentication (3 requests)
├── Register User
├── Login
└── Change Password

👤 Profile Management (3 requests)
├── Get Profile
├── Update Profile
└── Get Profile Stats

⚙️ Preferences (2 requests)
├── Get Preferences
└── Update Preferences

👑 Admin Operations (1 request)
└── List All Users

🗑️ Account Management (1 request)
└── Delete Account
```

### **Environment Variables**
```
🌐 URLs:
- base_url: Service endpoint
- environment: dev/prod identifier

🧪 Test Data:
- test_email, test_password, test_full_name
- test_age, test_gender, test_height, test_weight
- test_activity_level, test_goal

🔑 Authentication:
- access_token, refresh_token (auto-managed)
- user_id (auto-extracted)
- admin_token (for admin operations)
```

## ✅ **Ready to Use!**

1. **Import**: Drag & drop JSON files into Postman
2. **Environment**: Select "GymBro Production"  
3. **Test**: Run "Health Check" first
4. **Explore**: Follow QUICKSTART.md for guided testing

---

**🏋️ Happy Testing!**
