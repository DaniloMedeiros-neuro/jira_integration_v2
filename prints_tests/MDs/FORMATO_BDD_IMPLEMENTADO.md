# Formato BDD Implementado

## Visão Geral

O sistema agora formata automaticamente o campo **Descrição** dos casos de teste em formato BDD (Behavior Driven Development) usando a sintaxe Gherkin, conforme padrão do projeto de referência.

## Formato BDD Aplicado

### Estrutura da Descrição no Jira

A descrição é formatada com a seguinte estrutura:

1. **Objetivo** (em negrito)
2. **Pré Condição** (em negrito)
3. **Cenário BDD** (em bloco de código Gherkin)

### Exemplo de Formatação

```json
{
  "description": {
    "type": "doc",
    "version": 1,
    "content": [
      {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
      {"type": "paragraph", "content": [{"type": "text", "text": "Objetivo:", "marks": [{"type": "strong"}]}]},
      {"type": "paragraph", "content": [{"type": "text", "text": "Verificar se o sistema permite login com credenciais corretas"}]},
      {"type": "paragraph", "content": [{"type": "text", "text": "Pré Condição:", "marks": [{"type": "strong"}]}]},
      {"type": "paragraph", "content": [{"type": "text", "text": "Usuário cadastrado no sistema"}]},
      {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
      {
        "type": "codeBlock",
        "attrs": {"language": "gherkin"},
        "content": [{"type": "text", "text": "Dado que o usuário está na tela de login\nQuando inserir credenciais válidas\nEntão deve ser redirecionado para o dashboard"}]
      }
    ]
  }
}
```

### Resultado Visual no Jira

**Objetivo:** Verificar se o sistema permite login com credenciais corretas

**Pré Condição:** Usuário cadastrado no sistema

```gherkin
Dado que o usuário está na tela de login
Quando inserir credenciais válidas
Então deve ser redirecionado para o dashboard
```

## Sintaxe BDD (Gherkin)

### Palavras-Chave Utilizadas

- **Dado que**: Define o contexto/estado inicial
- **Quando**: Define a ação/evento
- **Então**: Define o resultado esperado

### Exemplos de Cenários BDD

#### Exemplo 1: Login Válido
```gherkin
Dado que o usuário está na tela de login
Quando inserir credenciais válidas
Então deve ser redirecionado para o dashboard
```

#### Exemplo 2: Login Inválido
```gherkin
Dado que o usuário está na tela de login
Quando inserir credenciais inválidas
Então deve exibir mensagem de erro
```

#### Exemplo 3: Validação de Campos
```gherkin
Dado que o usuário está na tela de cadastro
Quando tentar salvar sem preencher campos obrigatórios
Então deve exibir validações
```

#### Exemplo 4: API Test
```gherkin
Dado que estou autenticado com perfil gerencial
Quando envio uma requisição GET para "/api/v1/records/{SCHEMA_NAME}?NUMERO_DOCUMENTO={VALOR_INEXISTENTE}"
Então o sistema retorna 404 NOT_FOUND
E valido o retorno da API
{
  "statusCode": "404 - NOT_FOUND",
  "message": "Não existem registros com esta chave!"
}
```

## Funcionalidades Afetadas

### ✅ Todas as Funções Atualizadas

1. **`criar_caso_teste()`** - Criação individual de casos de teste
2. **`criar_caso_teste_planilha_manual()`** - Planilha manual
3. **`criar_caso_teste_planilha()`** - Importação de planilha

### ✅ Formatação Consistente

Todas as funções agora usam o mesmo formato:
- **Objetivo** em negrito
- **Pré Condição** em negrito
- **Cenário BDD** em bloco de código Gherkin

## Benefícios da Implementação

### ✅ Padrão BDD
- **Clareza**: Cenários claros e legíveis
- **Colaboração**: Facilita comunicação entre equipes
- **Testes**: Base para automação de testes

### ✅ Formatação Visual
- **Destaque**: Objetivo e pré-condições em negrito
- **Sintaxe**: Bloco de código com syntax highlighting
- **Organização**: Estrutura clara e organizada

### ✅ Compatibilidade
- **Jira**: Formatação nativa do Jira
- **Gherkin**: Sintaxe padrão para BDD
- **Automação**: Compatível com ferramentas de teste

## Como Usar

### 1. Criação Individual
Ao criar um caso de teste individual, a descrição será automaticamente formatada em BDD.

### 2. Planilha Manual
Na planilha manual, o campo "Descrição" deve conter o cenário BDD:
```
Dado que o usuário está na tela de login
Quando inserir credenciais válidas
Então deve ser redirecionado para o dashboard
```

### 3. Importação em Massa
Ao importar dados em massa, o campo descrição será formatado automaticamente.

### 4. Importação de Planilha
Ao importar de planilhas, o formato BDD será aplicado automaticamente.

## Exemplos de Dados

### Dados de Exemplo (gerar_dados_demo)

```python
{
    'id': 'CT-001',
    'titulo': 'Validar Login com Credenciais Válidas',
    'descricao': 'Dado que o usuário está na tela de login\nQuando inserir credenciais válidas\nEntão deve ser redirecionado para o dashboard',
    'objetivo': 'Verificar se o sistema permite login com credenciais corretas',
    'pre_condicoes': 'Usuário cadastrado no sistema',
    'tipo_execucao': 'Automatizado',
    'tipo_teste': 'Funcional',
    'componentes': ['Frontend', 'Backend'],
    'status': 'To Do'
}
```

### Formato para Importação em Massa

```
Título	Status	Tipo Execução	Tipo Teste	Componentes	Objetivo	Pré-condições	Descrição
"Validar Login"	To Do	Manual	Functional	Frontend	"Verificar login"	"Usuário cadastrado"	"Dado que o usuário está na tela de login
Quando inserir credenciais válidas
Então deve ser redirecionado para o dashboard"
```

## Configuração

### Parâmetros da Formatação
- **Linguagem**: `gherkin` (para syntax highlighting)
- **Estrutura**: Objetivo → Pré Condição → Cenário BDD
- **Formatação**: Negrito para títulos, código para cenário

### Personalização
O formato pode ser facilmente personalizado modificando a estrutura do payload nas funções de criação.

## Status

✅ **Implementação Concluída**
- Formato BDD aplicado em todas as funções
- Sintaxe Gherkin implementada
- Formatação visual consistente
- Compatibilidade com automação de testes
