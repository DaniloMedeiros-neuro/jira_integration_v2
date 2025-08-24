# Importação de Planilha do Google Drive

## Visão Geral

Esta funcionalidade permite importar casos de teste diretamente de uma planilha do Google Sheets para o Jira, criando automaticamente os casos de teste vinculados a uma issue pai (requisito).

## Como Usar

### 1. Acessar a Página de Importação

- Clique no botão "Importar" no cabeçalho da aplicação
- Ou acesse diretamente: `http://localhost:8081/importar-planilha`

### 2. Configurar a Importação

#### 2.1. URL da Planilha
- Cole a URL completa da planilha do Google Drive
- Exemplo: `https://docs.google.com/spreadsheets/d/1SW3-UseON1ZSKftz8Vb5Cmn47DUeat87/edit?usp=sharing`
- Clique em "Extrair ID" ou cole a URL (extração automática)

#### 2.2. Seleção da Aba
- O sistema carregará automaticamente as abas disponíveis na planilha
- Selecione a aba que contém os dados dos casos de teste
- Se a API do Google Sheets não estiver configurada, serão mostradas abas padrão

#### 2.3. Issue Pai
- Digite o ID da issue pai (requisito) onde os casos de teste serão criados
- Exemplo: `CREDT-1161`

### 3. Visualizar Dados

- Clique em "Visualizar Dados" para ver uma prévia dos casos que serão importados
- Verifique se os dados estão corretos antes de prosseguir

### 4. Importar para Jira

- Clique em "Importar para Jira"
- Confirme a importação
- Aguarde o processamento
- Visualize os resultados da importação

## Formato da Planilha

### Estrutura Recomendada

A planilha deve ter as seguintes colunas (na primeira linha):

| Coluna | Descrição | Obrigatório |
|--------|-----------|-------------|
| Título | Título do caso de teste | Sim |
| Descrição | Descrição em formato Gherkin | Sim |
| Objetivo | Objetivo do teste | Não |
| Pré-condição | Pré-condições do teste | Não |
| Tipo Execução | Automatizado/Manual | Não |
| Tipo Teste | Funcional/Integração/Unitário | Não |
| Componente | Componentes afetados | Não |
| Status | Status inicial | Não |

### Exemplo de Dados

```
Título | Descrição | Objetivo | Pré-condição | Tipo Execução | Tipo Teste | Componente | Status
Validar Login | Dado que o usuário está na tela de login\nQuando inserir credenciais válidas\nEntão deve ser redirecionado | Verificar login válido | Usuário cadastrado | Automatizado | Funcional | Frontend,Backend | To Do
```

## Configuração da API do Google Sheets

### Para Acesso Completo (Opcional)

Para acessar planilhas privadas ou obter dados reais:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Sheets
4. Crie credenciais (API Key)
5. Configure a variável de ambiente:
   ```bash
   GOOGLE_SHEETS_API_KEY=sua_api_key_aqui
   ```

### Modo Demo (Padrão)

Se a API não estiver configurada, o sistema usará dados de demonstração para mostrar como a funcionalidade funciona.

## Funcionalidades

### ✅ Implementadas

- [x] Extração automática do ID da planilha da URL
- [x] Carregamento dinâmico de abas da planilha
- [x] Visualização prévia dos dados
- [x] Importação para o Jira
- [x] Criação automática de casos de teste
- [x] Vinculação com issue pai
- [x] Atribuição automática de responsável
- [x] Tratamento de erros
- [x] Interface responsiva
- [x] Notificações em tempo real

### 🔄 Processo de Importação

1. **Validação**: Verifica se a issue pai existe
2. **Leitura**: Lê os dados da planilha
3. **Processamento**: Converte dados para formato do Jira
4. **Criação**: Cria casos de teste no Jira
5. **Vinculação**: Cria links entre casos e issue pai
6. **Atribuição**: Atribui responsável automaticamente
7. **Relatório**: Gera relatório de sucessos e erros

## Tratamento de Erros

### Erros Comuns

- **URL inválida**: Verifique se a URL da planilha está correta
- **Issue pai não encontrada**: Verifique se o ID da issue está correto
- **Planilha vazia**: Verifique se a aba selecionada contém dados
- **Permissões**: Verifique se a planilha está pública ou acessível

### Logs

Os logs detalhados são exibidos no console do navegador (F12) para facilitar o debug.

## Exemplo de Uso

### URL da Planilha Fornecida

```
https://docs.google.com/spreadsheets/d/1SW3-UseON1ZSKftz8Vb5Cmn47DUeat87/edit?usp=sharing&ouid=103666922741189875508&rtpof=true&sd=true
```

### ID Extraído

```
1SW3-UseON1ZSKftz8Vb5Cmn47DUeat87
```

### Processo

1. Cole a URL no campo "URL da Planilha"
2. Clique em "Extrair ID" (ou aguarde a extração automática)
3. Selecione a aba desejada
4. Digite o ID da issue pai (ex: CREDT-1161)
5. Visualize os dados
6. Importe para o Jira

## Suporte

Para dúvidas ou problemas:

1. Verifique os logs no console do navegador
2. Confirme se as configurações do Jira estão corretas
3. Verifique se a planilha está acessível
4. Teste com dados de demonstração primeiro
