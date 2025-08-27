# 📸 Sistema de Evidências de Testes

Este sistema permite extrair automaticamente evidências visuais de testes do arquivo `log.html` e enviá-las como comentários aos casos de teste no Jira.

## 🚀 Funcionalidades

- **Extração automática de screenshots** de testes passados e falhados
- **Organização por status**: separação automática entre sucessos e falhas
- **Nomenclatura inteligente**: uso do ID do caso de teste como nome do arquivo
- **Integração com Jira**: anexo automático de evidências aos casos de teste
- **Comentários formatados**: painéis visuais com status de aprovação/reprovação

## 📁 Estrutura de Arquivos

```
jira_integration_v2/
├── extrair_prints.py          # Script de extração de screenshots
├── adicionar_evidencias.py    # Script de envio para o Jira
├── gerar_evidencias.py        # Script principal integrado
├── prints_tests/              # Diretório de evidências geradas
│   ├── falhas/               # Screenshots de testes que falharam
│   └── sucessos/             # Screenshots de testes que passaram
└── log.html                  # Arquivo de log dos testes (entrada)
```

## 🛠️ Pré-requisitos

1. **Arquivo log.html** no diretório raiz do projeto
2. **Variáveis de ambiente** configuradas no arquivo `.env`:
   ```env
   JIRA_URL=https://neurotech.atlassian.net
   JIRA_EMAIL=seu.email@neurotech.com
   JIRA_API_TOKEN=sua_api_token
   PROJECT_KEY=CREDT
   ```
3. **Chrome/Chromium** instalado no sistema
4. **Dependências Python** instaladas:
   ```bash
   pip install selenium webdriver-manager
   ```

## 📖 Como Usar

### 1. Processo Completo (Recomendado)

```bash
python gerar_evidencias.py
```

Este comando:
1. Extrai screenshots do arquivo `log.html`
2. Organiza por status (sucessos/falhas)
3. Pergunta se deseja enviar ao Jira
4. Envia evidências automaticamente

### 2. Extração Apenas de Prints

```bash
python extrair_prints.py
```

Gera apenas os screenshots sem enviar ao Jira.

### 3. Envio de Evidência Específica

```bash
python gerar_evidencias.py CREDT-1343 sucessos
python gerar_evidencias.py CREDT-1343 falhas
```

### 4. Processamento Manual

```bash
# Extrair prints
python extrair_prints.py

# Enviar evidências
python adicionar_evidencias.py
```

## 🎯 Funcionamento

### Extração de Prints (`extrair_prints.py`)

1. **Carrega o arquivo log.html** no Chrome headless
2. **Identifica elementos de teste** usando seletores CSS
3. **Determina status** (sucesso/falha) baseado nas classes CSS
4. **Extrai código do teste** (ex: CREDT-1343) do nome
5. **Captura screenshot** de cada teste
6. **Organiza em pastas** por status

### Envio de Evidências (`adicionar_evidencias.py`)

1. **Lê arquivos PNG** das pastas de sucessos e falhas
2. **Anexa arquivo** ao caso de teste correspondente no Jira
3. **Cria comentário formatado** com painel visual
4. **Inclui imagem** no comentário usando mediaSingle

### Formato dos Comentários

**Teste Aprovado:**
```
[PAINEL VERDE] TESTE AUTOMAÇÃO APROVADO
[IMAGEM DO SCREENSHOT]
```

**Teste Reprovado:**
```
[PAINEL VERMELHO] TESTE AUTOMAÇÃO REPROVADO
[IMAGEM DO SCREENSHOT]
```

## 🔧 Configurações

### Seletores CSS Personalizados

Se o formato do `log.html` for diferente, ajuste os seletores em `extrair_prints.py`:

```python
# Buscar elementos de teste
test_divs = driver.find_elements(By.CSS_SELECTOR, ".children.populated > div.test")

# Buscar label de status
label = test_div.find_element(By.CSS_SELECTOR, ".element-header-left .label")

# Buscar nome do teste
name_span = test_div.find_element(By.CSS_SELECTOR, ".element-header-left .name")
```

### Padrão de Nomenclatura

O sistema extrai códigos de teste usando regex:
```python
match = re.search(r'[A-Z]+-\d+', test_name)  # CREDT-1343, BC-236, etc.
```

### Configurações do Chrome

```python
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,3000")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
```

## 📊 Exemplos de Uso

### Cenário 1: Execução Completa
```bash
$ python gerar_evidencias.py
🎯 SISTEMA DE EVIDÊNCIAS DE TESTES
==================================================
📋 Iniciando processo completo de evidências...

🔍 PASSO 1: Extraindo prints de evidências...
🚀 Iniciando extração de prints de evidências...
📄 Carregando arquivo: /path/to/log.html
🧪 Total de testes encontrados: 20
✅ Screenshot sucesso salvo: CREDT-1343.png
❌ Screenshot falha salvo: CREDT-1342.png
...
📊 Prints gerados: 3 falhas, 17 sucessos

❓ Deseja enviar as evidências para o Jira? (s/n): s

📤 PASSO 2: Enviando evidências para o Jira...
[ANEXO] 📎 Enviado para CREDT-1343: CREDT-1343.png
[COMENTÁRIO] 💬 Adicionado em CREDT-1343
✅ Evidência adicionada com sucesso para CREDT-1343
...
```

### Cenário 2: Evidência Específica
```bash
$ python gerar_evidencias.py CREDT-1343 sucessos
🎯 Processando evidência específica para CREDT-1343...
[ANEXO] 📎 Enviado para CREDT-1343: CREDT-1343.png
[COMENTÁRIO] 💬 Adicionado em CREDT-1343
✅ Evidência adicionada com sucesso para CREDT-1343
```

## 🚨 Troubleshooting

### Erro: "Arquivo log.html não encontrado"
- Verifique se o arquivo `log.html` está no diretório raiz
- Confirme se o arquivo contém dados de teste válidos

### Erro: "Nenhum teste encontrado"
- Verifique se o arquivo `log.html` tem a estrutura esperada
- Ajuste os seletores CSS se necessário

### Erro: "Chrome não encontrado"
- Instale o Chrome/Chromium no sistema
- O webdriver-manager baixará automaticamente o driver

### Erro: "Erro ao anexar arquivo"
- Verifique as credenciais do Jira no arquivo `.env`
- Confirme se o caso de teste existe no Jira
- Verifique permissões de anexo no Jira

## 📝 Logs e Debug

O sistema gera logs detalhados durante a execução:

- **Progresso de extração**: número de testes encontrados e processados
- **Status de cada arquivo**: sucesso ou falha na captura
- **Estatísticas finais**: total de evidências processadas
- **Erros detalhados**: informações para troubleshooting

## 🔄 Integração com CI/CD

Para integração com pipelines de CI/CD:

```bash
# Extrair prints sem interação
python extrair_prints.py

# Enviar evidências automaticamente
python adicionar_evidencias.py
```

## 📈 Próximas Melhorias

- [ ] Suporte a múltiplos formatos de log
- [ ] Configuração via arquivo YAML
- [ ] Integração com relatórios de teste automatizados
- [ ] Suporte a vídeos de evidência
- [ ] Dashboard de estatísticas de evidências
