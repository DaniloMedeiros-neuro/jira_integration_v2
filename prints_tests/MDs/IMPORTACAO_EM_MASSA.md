# Importação em Massa - Planilha Manual

## Visão Geral

A funcionalidade de **Importação em Massa** permite copiar e colar dados de uma tabela (Excel, Google Sheets, etc.) diretamente na planilha manual, preenchendo automaticamente todos os campos de uma só vez.

## Como Usar

### 1. Acessar a Funcionalidade

1. Acesse: `http://localhost:8081/planilha-manual`
2. Na seção **"Importação em Massa"** no topo da página, você verá uma área para colar dados

### 2. Preparar os Dados

#### Formato Esperado
Os dados devem estar organizados em colunas separadas por **tabulação (Tab)** ou **vírgula**, com uma linha por caso de teste:

```
Título | Status | Tipo Execução | Tipo Teste | Componentes | Objetivo | Pré-condições | Descrição
```

#### Exemplo de Dados
```
Teste de Login	To Do	Manual	Functional	Frontend	Verificar autenticação de usuário	Usuário cadastrado no sistema	Dado que o usuário está na tela de login
Quando inserir credenciais válidas
Então deve ser redirecionado para o dashboard
Teste de Cadastro	In Progress	Automated	Functional	Backend	Validar criação de conta	Servidor funcionando	Dado que o usuário está na tela de cadastro
Quando preencher todos os campos obrigatórios
Então deve criar a conta com sucesso
```

### 3. Processo de Importação

#### Passo 1: Colar Dados
1. Copie os dados da sua tabela (Excel, Google Sheets, etc.)
2. Cole no campo **"Dados da Tabela"**
3. Clique em **"Processar Dados"**

#### Passo 2: Revisar Preview
- O sistema mostrará um preview dos dados processados
- Verifique se os campos foram mapeados corretamente
- Se necessário, ajuste os dados originais e processe novamente

#### Passo 3: Preencher Planilha
- Clique em **"Preencher Planilha"** para transferir os dados para a planilha
- Todos os casos de teste serão adicionados automaticamente

### 4. Mapeamento Automático

O sistema mapeia automaticamente os seguintes campos:

#### Status
- `To Do`, `Todo`, `Pendente` → **To Do**
- `In Progress`, `Em Andamento`, `Progresso` → **In Progress**
- `Done`, `Concluído`, `Concluido`, `Finalizado` → **Done**

#### Tipo de Execução
- `Automated`, `Automatizado`, `Automático`, `Automatizável`, `Automatizavel` → **Automated**
- Outros → **Manual** (padrão)

#### Tipo de Teste
- `Functional`, `Funcional` → **Functional**
- `Non-Functional`, `Não Funcional` → **Non-Functional**
- `Integration`, `Integração` → **Integration**
- `Unit`, `Unitário` → **Unit**

## Formatos Suportados

### 1. Dados com Cabeçalho
```
Título	Status	Tipo Execução	Tipo Teste	Componentes	Objetivo	Pré-condições	Descrição
Teste de Login	To Do	Manual	Functional	Frontend	Verificar login	Usuário cadastrado	Realizar login
```

### 2. Dados sem Cabeçalho
```
Teste de Login	To Do	Manual	Functional	Frontend	Verificar login	Usuário cadastrado	Realizar login
Teste de Cadastro	In Progress	Automated	Functional	Backend	Validar conta	Servidor ativo	Criar conta
```

### 3. Dados Separados por Vírgula
```
Teste de Login,To Do,Manual,Functional,Frontend,Verificar login,Usuário cadastrado,Realizar login
Teste de Cadastro,In Progress,Automated,Functional,Backend,Validar conta,Servidor ativo,Criar conta
```

### 4. Dados com Quebras de Linha nos Campos
Para campos que contêm quebras de linha (como descrições longas), use aspas duplas para delimitar o campo:

```
Título	Status	Tipo Execução	Tipo Teste	Componentes	Objetivo	Pré-condições	Descrição
"Teste com Descrição Longa"	To Do	Manual	Functional	Frontend	"Objetivo com
múltiplas linhas"	"Pré-condições
em várias linhas"	"Descrição detalhada
com quebras de linha
e formatação"
```

**Nota**: O sistema agora detecta automaticamente campos delimitados por aspas e trata quebras de linha dentro desses campos como parte do conteúdo, não como separadores de linha.

## Funcionalidades Adicionais

### Botões Disponíveis

- **🪄 Processar Dados**: Analisa e mapeia os dados colados
- **🧹 Limpar**: Remove todos os dados da área de importação
- **⬇️ Preencher Planilha**: Transfere dados processados para a planilha

### Preview Inteligente
- Mostra como os dados serão mapeados antes de preencher a planilha
- Permite revisar e corrigir problemas antes da importação
- Exibe badges coloridos para facilitar a visualização

### Detecção Automática
- **Separador**: Detecta automaticamente se os dados usam tabulação ou vírgula
- **Cabeçalho**: Identifica e ignora linhas de cabeçalho automaticamente
- **Mapeamento**: Converte valores para os formatos aceitos pelo Jira

## Dicas de Uso

### 1. Preparação dos Dados
- Certifique-se de que os dados estão organizados em colunas
- Use tabulação (Tab) para separar colunas (recomendado)
- Evite quebras de linha dentro dos campos

### 2. Validação
- Sempre revise o preview antes de preencher a planilha
- Verifique se os campos obrigatórios (título) estão preenchidos
- Confirme se os valores de status e tipos estão corretos

### 3. Correções
- Se o mapeamento estiver incorreto, ajuste os dados originais
- Use os valores exatos mencionados na seção de mapeamento
- Processe novamente após fazer correções

## Exemplo Completo

### Dados Originais (Excel/Google Sheets)
```
Título	Status	Tipo Execução	Tipo Teste	Componentes	Objetivo	Pré-condições	Descrição
Login Válido	To Do	Manual	Functional	Frontend	Testar login com credenciais corretas	Usuário cadastrado	1. Acessar página de login 2. Inserir email e senha válidos 3. Clicar em entrar 4. Verificar redirecionamento para dashboard
Login Inválido	In Progress	Automated	Functional	Backend	Testar validação de credenciais	API funcionando	1. Enviar requisição com dados inválidos 2. Verificar resposta de erro 3. Validar mensagem de erro
Performance	Done	Automated	Non-Functional	Frontend	Testar tempo de carregamento	Servidor configurado	1. Medir tempo de resposta 2. Verificar se está dentro do limite 3. Gerar relatório de performance
```

### Resultado na Planilha
Após processar e preencher, a planilha terá 3 linhas com todos os campos preenchidos automaticamente, prontos para exportação ao Jira.

## Benefícios

1. **Eficiência**: Importe dezenas de casos de teste de uma só vez
2. **Precisão**: Mapeamento automático reduz erros de digitação
3. **Flexibilidade**: Suporta diferentes formatos de dados
4. **Validação**: Preview permite revisar antes de importar
5. **Compatibilidade**: Funciona com Excel, Google Sheets e outras fontes

## Troubleshooting

### Problema: Dados não são processados
**Solução**: Verifique se os dados estão separados por tabulação ou vírgula

### Problema: Mapeamento incorreto
**Solução**: Use os valores exatos mencionados na documentação de mapeamento

### Problema: Preview não aparece
**Solução**: Certifique-se de que pelo menos um campo (título) está preenchido

### Problema: Campos vazios na planilha
**Solução**: Verifique se todos os campos necessários estão presentes nos dados originais

### Problema: Uma linha sendo importada como múltiplos casos de teste
**Solução**: Use aspas duplas para delimitar campos que contêm quebras de linha. Exemplo:
```
❌ Incorreto (gera múltiplos casos):
Título	Status	Descrição
Teste	To Do	Descrição com
quebra de linha

✅ Correto (gera um caso):
Título	Status	Descrição
"Teste"	To Do	"Descrição com
quebra de linha"
```

### Problema: Quebras de linha sendo interpretadas como novas linhas
**Solução**: O sistema agora detecta automaticamente campos delimitados por aspas. Se seus dados contêm quebras de linha nos campos, certifique-se de que estão entre aspas duplas.
