# 🔄 Instruções de Rollback - SB Admin 2

## 📋 **INFORMAÇÕES DA VERSÃO ATUAL**

### **Commit Hash**: `f6a4e7b`
### **Tag**: `v2.0.0-sb-admin-2`
### **Data**: 29/08/2025
### **Descrição**: Implementação completa do SB Admin 2 + Funcionalidades de Evidências

---

## 🚨 **COMO FAZER ROLLBACK**

### **Opção 1: Rollback Simples (Recomendado)**
```bash
# Voltar para o commit anterior
git reset --hard HEAD~1

# Verificar se voltou corretamente
git log --oneline -1
```

### **Opção 2: Rollback para Tag Específica**
```bash
# Listar todas as tags
git tag -l

# Voltar para uma tag específica (se existir)
git reset --hard <tag-name>
```

### **Opção 3: Rollback para Commit Específico**
```bash
# Encontrar o commit desejado
git log --oneline

# Voltar para um commit específico
git reset --hard <commit-hash>
```

---

## 📁 **ARQUIVOS PRINCIPAIS ALTERADOS**

### **Arquivos Novos (serão removidos no rollback)**:
- `templates/base_sb_admin.html` - Template SB Admin 2
- `static/css/sb-admin-2-*.css` - Estilos SB Admin 2
- `static/js/sb-admin-2-*.js` - Scripts SB Admin 2
- `FUNCIONALIDADES_EVIDENCIAS_IMPLEMENTADAS.md`
- `CORRECAO_TOAST_EVIDENCIAS.md`
- `PLANO_IMPLEMENTACAO_SB_ADMIN_2.md`

### **Arquivos Modificados (serão revertidos)**:
- `app.py` - APIs de evidências
- `static/js/app.js` - Funções de evidências
- `templates/evidencias.html` - Interface de evidências
- Outros templates atualizados para SB Admin 2

---

## 🔍 **VERIFICAÇÃO PÓS-ROLLBACK**

### **1. Verificar Status**
```bash
git status
```

### **2. Verificar Arquivos**
```bash
# Verificar se os arquivos SB Admin 2 foram removidos
ls templates/base_sb_admin.html
ls static/css/sb-admin-2-*.css
ls static/js/sb-admin-2-*.js
```

### **3. Testar Aplicação**
```bash
# Iniciar servidor
python app.py

# Acessar no navegador
# http://localhost:8081
```

---

## ⚠️ **IMPORTANTE**

### **Antes do Rollback**:
1. ✅ Fazer backup de qualquer configuração personalizada
2. ✅ Documentar mudanças específicas que você quer manter
3. ✅ Verificar se não há dados importantes não commitados

### **Após o Rollback**:
1. ✅ Testar todas as funcionalidades básicas
2. ✅ Verificar se o template anterior está funcionando
3. ✅ Confirmar que as APIs estão operacionais

---

## 📞 **SUPORTE**

### **Se algo der errado**:
```bash
# Ver histórico de commits
git log --oneline

# Ver diferenças entre commits
git diff HEAD~1 HEAD

# Recuperar arquivos específicos
git checkout HEAD~1 -- <arquivo>
```

### **Para restaurar a versão SB Admin 2**:
```bash
# Voltar para o commit SB Admin 2
git reset --hard f6a4e7b
```

---

## 🎯 **RESUMO**

- **Commit Atual**: `f6a4e7b` (SB Admin 2)
- **Rollback**: `git reset --hard HEAD~1`
- **Restaurar**: `git reset --hard f6a4e7b`
- **Tag**: `v2.0.0-sb-admin-2`

**Esta documentação garante que você pode voltar à versão anterior com segurança!** 🔄
