# Sistema de Evidências de Testes - Versão Melhorada

## 📋 Visão Geral

O Sistema de Evidências de Testes foi completamente reformulado com melhorias significativas em funcionalidade, robustez e experiência do usuário. Este sistema permite extrair automaticamente evidências visuais de logs de testes HTML e enviá-las para o Jira.

## ✨ Principais Melhorias Implementadas

### 🔧 **1. Screenshots Reais com Selenium**
- **Implementação completa** de captura de screenshots reais usando Selenium WebDriver
- **Configuração otimizada** do Chrome em modo headless
- **Fallback inteligente** para screenshots simulados quando Selenium não está disponível
- **Templates HTML profissionais** para evidências visuais
- **Configuração via variável de ambiente**: `CAPTURE_REAL_SCREENSHOTS=true`

### 🔗 **2. Integração Real com Jira**
- **Upload real de arquivos** para issues do Jira
- **Validação de issues** antes do envio
- **Comentários automáticos** com resumo das evidências
- **Tratamento de erros** robusto
- **Limite de tamanho** de arquivo (10MB por arquivo)
- **Suporte a múltiplos tipos** de anexo

### 📊 **3. Sistema de Logs Detalhados**
- **Logging estruturado** com diferentes níveis (DEBUG, INFO, WARNING, ERROR)
- **Rotação automática** de arquivos de log
- **Logs específicos** para cada operação
- **Rastreamento completo** do processamento
- **Diretório de logs**: `logs/evidencias_YYYYMMDD.log`

### 🔍 **4. Validação Robusta de Formatos**
- **Algoritmo inteligente** para detectar diferentes formatos de log
- **Suporte a múltiplos frameworks**: Robot Framework, Selenium, JUnit, Cucumber, etc.
- **Sistema de pontuação** para validar logs
- **Detecção automática** de frameworks de teste
- **Fallback graceful** para formatos não reconhecidos

### 🎨 **5. Interface Melhorada**
- **Drag & Drop** para upload de arquivos
- **Steps visuais** com animações
- **Feedback em tempo real** do processamento
- **Design responsivo** para mobile
- **Animações suaves** e transições
- **Estados de loading** melhorados

### ⚙️ **6. Sistema de Configuração Centralizado**
- **Arquivo de configuração** dedicado (`config_evidencias.py`)
- **Configurações por ambiente** via variáveis de ambiente
- **Validação automática** de configurações
- **Flexibilidade total** para personalização

### 🛡️ **7. Segurança e Validação**
- **Validação de arquivos** rigorosa
- **Sanitização de HTML** para segurança
- **Limites de tamanho** configuráveis
- **Bloqueio de arquivos executáveis**
- **Logs de segurança** para auditoria

## 🚀 Como Usar

### **1. Configuração Inicial**

```bash
# Habilitar screenshots reais (opcional)
export CAPTURE_REAL_SCREENSHOTS=true

# Configurar Jira (obrigatório para envio)
export JIRA_URL=https://seu-jira.atlassian.net
export JIRA_EMAIL=seu-email@empresa.com
export JIRA_API_TOKEN=seu-token-api

# Configurações opcionais
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
export MAX_CONCURRENT_SCREENSHOTS=5
```

### **2. Upload de Log de Testes**

1. **Acesse a página de evidências**: `/evidencias`
2. **Arraste e solte** ou **clique para selecionar** um arquivo HTML
3. **Aguarde a validação** automática do formato
4. **Clique em "Processar Evidências"**

### **3. Processamento Automático**

O sistema irá:
- ✅ **Validar** o formato do arquivo
- 📸 **Extrair** elementos de teste
- 🎯 **Classificar** por sucesso/falha
- 📱 **Gerar** screenshots profissionais
- 📁 **Organizar** em diretórios

### **4. Envio para Jira**

1. **Clique em "Enviar para Jira"**
2. **Digite a chave da issue** (ex: BC-123)
3. **Aguarde o upload** automático
4. **Verifique o comentário** criado na issue

## 📁 Estrutura de Arquivos

```
projeto/
├── prints_tests/
│   ├── sucessos/
│   │   ├── BC-123_sucesso.png
│   │   └── PROJ-456_sucesso.png
│   └── falhas/
│       ├── TEST-789_falha.png
│       └── BUG-101_falha.png
├── logs/
│   └── evidencias_20250101.log
├── config_evidencias.py
├── app.py
└── static/
    ├── css/style.css
    └── js/app.js
```

## ⚙️ Configurações Avançadas

### **Variáveis de Ambiente**

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CAPTURE_REAL_SCREENSHOTS` | `false` | Habilitar screenshots reais |
| `JIRA_URL` | - | URL do Jira |
| `JIRA_EMAIL` | - | Email do usuário |
| `JIRA_API_TOKEN` | - | Token de API do Jira |
| `DEBUG_MODE` | `false` | Modo debug |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `MAX_CONCURRENT_SCREENSHOTS` | `3` | Screenshots simultâneos |
| `SCREENSHOT_TIMEOUT` | `30` | Timeout em segundos |

### **Configurações de Processamento**

```python
# config_evidencias.py
PROCESSING_CONFIG = {
    'max_file_size_mb': 10,
    'supported_formats': ['.html', '.htm'],
    'temp_dir': 'temp_evidence',
    'output_dir': 'prints_tests',
    'log_dir': 'logs'
}
```

## 🔧 Frameworks Suportados

O sistema detecta automaticamente e suporta:

- **🤖 Robot Framework**
- **🌐 Selenium WebDriver**
- **☕ JUnit/TestNG**
- **🥒 Cucumber/BDD**
- **🐍 PyTest**
- **📱 Jest/Mocha**
- **📋 Formatos customizados**

## 📊 Relatórios e Estatísticas

### **Estatísticas de Processamento**
- Total de testes encontrados
- Sucessos vs falhas
- Tempo de processamento
- Taxa de sucesso

### **Logs Detalhados**
- Processamento por elemento
- Erros e warnings
- Performance metrics
- Validação de formato

## 🛠️ Troubleshooting

### **Problemas Comuns**

1. **Screenshots não são gerados**
   ```bash
   # Verificar se Selenium está instalado
   pip install selenium webdriver-manager
   
   # Habilitar screenshots reais
   export CAPTURE_REAL_SCREENSHOTS=true
   ```

2. **Erro no upload para Jira**
   ```bash
   # Verificar configurações do Jira
   export JIRA_URL=https://seu-jira.atlassian.net
   export JIRA_EMAIL=seu-email@empresa.com
   export JIRA_API_TOKEN=seu-token-api
   ```

3. **Arquivo não reconhecido**
   - Verificar se é um arquivo HTML válido
   - Verificar se contém elementos de teste
   - Consultar logs para detalhes

### **Logs de Debug**

```bash
# Habilitar logs detalhados
export LOG_LEVEL=DEBUG
export DEBUG_MODE=true

# Verificar logs
tail -f logs/evidencias_$(date +%Y%m%d).log
```

## 🔄 API Endpoints

### **Upload de Arquivo**
```http
POST /api/evidencias/upload
Content-Type: multipart/form-data

{
  "sucesso": true,
  "estatisticas": {
    "sucessos": 5,
    "falhas": 2,
    "total": 7
  },
  "nomes_evidencias": [...]
}
```

### **Envio para Jira**
```http
POST /api/evidencias/enviar
Content-Type: application/json

{
  "issue_key": "BC-123"
}
```

### **Status das Evidências**
```http
GET /api/evidencias/status

{
  "sucessos": 5,
  "falhas": 2,
  "total": 7,
  "processado": true
}
```

## 🎯 Próximas Melhorias

- [ ] **Suporte a múltiplos formatos** de log
- [ ] **Integração com CI/CD** (Jenkins, GitLab CI)
- [ ] **Dashboard de métricas** em tempo real
- [ ] **Notificações push** para falhas críticas
- [ ] **Backup automático** para nuvem
- [ ] **API REST completa** para integração
- [ ] **Suporte a vídeos** de execução
- [ ] **Análise de performance** dos testes

## 📞 Suporte

Para dúvidas ou problemas:

1. **Verifique os logs** em `logs/evidencias_*.log`
2. **Consulte a documentação** de configuração
3. **Teste com arquivos de exemplo** fornecidos
4. **Habilite o modo debug** para mais detalhes

---

**🎉 Sistema de Evidências Melhorado - Versão 2.0**  
*Transformando logs de teste em evidências visuais profissionais*
