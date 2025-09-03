---
name: 🚀 Pull Request
about: Template per contributi al NutriFit Platform
title: '[SERVICE] Brief description of changes'
labels: ''
assignees: ''
---

## 📝 Description

### Changes Made
<!-- Describe what changes you made and why -->

### Service Impacted
- [ ] 🔥 Calorie Balance Service
- [ ] 🍎 Meal Tracking Service  
- [ ] 📊 Health Monitor Service
- [ ] 🔔 Notifications Service
- [ ] 🤖 AI Nutrition Coach Service
- [ ] 📱 Flutter Mobile App
- [ ] 🔧 Infrastructure/DevOps

### Type of Change
- [ ] 🆕 New feature
- [ ] 🐛 Bug fix
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test improvements
- [ ] 🔒 Security enhancement

## 🔍 Testing

### Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated (if applicable)
- [ ] Performance tests updated (if applicable)

### Test Results
<!-- Paste test output or link to CI results -->
```
Coverage Report:
- Lines: XX% 
- Functions: XX%
- Branches: XX%
```

### Manual Testing
<!-- Describe manual testing performed -->
- [ ] Local testing completed
- [ ] API endpoints tested with Postman/Insomnia
- [ ] Database migrations tested
- [ ] External integrations verified

## 🏗️ Architecture Impact

### Domain-Driven Design
- [ ] Value Objects properly implemented
- [ ] Domain boundaries respected
- [ ] Aggregates correctly designed
- [ ] Repository patterns followed

### Data Quality & Precision
- [ ] ±20g accuracy maintained for food quantities
- [ ] Confidence scoring implemented
- [ ] Data source attribution maintained
- [ ] Fallback strategies implemented

### External Integrations
- [ ] OpenFoodFacts integration tested
- [ ] HealthKit/Health Connect compatibility verified
- [ ] OpenAI API usage optimized
- [ ] Supabase Auth integration maintained

## 🔒 Security Review

- [ ] Input validation implemented
- [ ] Authentication/authorization verified
- [ ] Sensitive data properly handled
- [ ] GDPR compliance maintained
- [ ] Health data privacy requirements met
- [ ] No secrets in code

## 📊 Performance Considerations

- [ ] API response times <200ms
- [ ] Database queries optimized
- [ ] Memory usage assessed
- [ ] Potential scaling issues addressed
- [ ] Caching strategies implemented (if applicable)

## 📚 Documentation

- [ ] Code properly documented (docstrings)
- [ ] README updated (if applicable)
- [ ] API documentation updated
- [ ] Architecture diagrams updated (if applicable)
- [ ] Migration scripts documented

## 🚀 Deployment

### Database Changes
- [ ] No breaking schema changes
- [ ] Migration scripts included
- [ ] Rollback strategy documented
- [ ] Data migration tested

### Configuration Changes
- [ ] Environment variables documented
- [ ] Docker configuration updated
- [ ] Health checks implemented
- [ ] Monitoring alerts configured

### Breaking Changes
- [ ] No breaking changes
- [ ] Breaking changes documented with migration guide
- [ ] Backward compatibility maintained
- [ ] API versioning implemented (if applicable)

## 📷 Screenshots/Demo

<!-- Add screenshots or demo GIFs if UI/UX changes -->

## 🔗 Related Issues

<!-- Link related issues using keywords like "closes", "fixes", "relates to" -->
- Closes #XXX
- Relates to #XXX

## ✅ Pre-merge Checklist

### Code Quality
- [ ] All linting checks pass (black, isort, flake8, mypy)
- [ ] All tests pass locally
- [ ] Code coverage ≥80%
- [ ] No TODO/FIXME comments left
- [ ] Type hints complete

### Review Requirements  
- [ ] Self-review completed
- [ ] Architecture review requested (if major changes)
- [ ] Security review completed (if security-related)
- [ ] Performance review completed (if performance-critical)

### CI/CD Pipeline
- [ ] All GitHub Actions pass
- [ ] Docker build successful
- [ ] No security vulnerabilities detected
- [ ] Documentation build successful

## 🎯 Post-merge Actions

- [ ] Monitor deployment in staging
- [ ] Verify health checks
- [ ] Update project documentation
- [ ] Close related issues
- [ ] Announce changes to team (if significant)

---

**Additional Notes:**
<!-- Any additional context, concerns, or information for reviewers -->

**Review Timeline:**
- Expected review completion: <!-- Date -->
- Target merge date: <!-- Date -->
- Deployment window: <!-- Date/Time -->
