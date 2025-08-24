# Remoção da Dependência do PROJECT_KEY

## Objetivo

Remover completamente a dependência da variável de ambiente `PROJECT_KEY` para tornar o sistema totalmente adaptável a qualquer projeto do Jira.

## Problema Anterior

O sistema estava configurado com um projeto específico (`PROJECT_KEY=BC`) no arquivo `.env`, o que limitava sua flexibilidade para trabalhar com diferentes projetos.

### Limitações do Sistema Anterior
- **Projeto Fixo**: Sistema configurado para um projeto específico
- **Configuração Manual**: Necessidade de alterar `.env` para cada projeto
- **Falta de Flexibilidade**: Não conseguia trabalhar automaticamente com múltiplos projetos

## Solução Implementada

### 1. Remoção da Variável PROJECT_KEY

**Antes:**
```python
PROJECT_KEY = os.getenv("PROJECT_KEY", "TEST")
```

**Depois:**
```python
# Variável removida - sistema agora é totalmente dinâmico
```

### 2. Detecção Automática de Projeto

O sistema agora detecta automaticamente o projeto através da issue pai:

```python
# Obter informações da issue pai (incluindo project_key válido)
project_key, issue_type_pai = obter_informacoes_issue(issue_pai)
if not project_key:
    return {
        'sucesso': False,
        'erro': f'Issue pai {issue_pai} não encontrada ou inválida'
    }
```

### 3. Validação Dinâmica

- **Chamada à API**: Verifica se a issue pai existe no Jira
- **Detecção de Projeto**: Obtém o `project_key` real da API
- **Validação de Tipos**: Verifica se "Caso de Teste" está disponível no projeto

## Benefícios da Remoção

### ✅ Flexibilidade Total
- **Qualquer Projeto**: Funciona com qualquer projeto do Jira
- **Sem Configuração**: Não precisa alterar `.env` para cada projeto
- **Detecção Automática**: Identifica o projeto automaticamente

### ✅ Simplicidade de Configuração
- **Menos Variáveis**: Redução de configurações necessárias
- **Menos Erros**: Elimina erros de configuração de projeto
- **Deploy Mais Fácil**: Menos variáveis para configurar

### ✅ Adaptabilidade
- **Múltiplos Projetos**: Pode trabalhar com vários projetos simultaneamente
- **Migração Fácil**: Funciona imediatamente em novos projetos
- **Sem Limitações**: Não há restrições de projeto

## Configuração Atual

### Arquivo `.env` Simplificado
```env
# Configurações do Jira
JIRA_URL=https://seu-dominio.atlassian.net
JIRA_EMAIL=seu-email@empresa.com
JIRA_API_TOKEN=seu-token-api
JIRA_AUTH=base64(email:token)
```

### Variáveis Removidas
- ❌ `PROJECT_KEY=BC` (removido)

## Funcionalidades Afetadas

### ✅ Todas as Funcionalidades Mantidas
- **Criação Individual**: Funciona com qualquer projeto
- **Planilha Manual**: Adapta-se automaticamente ao projeto da issue pai
- **Importação de Planilha**: Detecta projeto automaticamente
- **Importação em Massa**: Funciona com qualquer projeto

### ✅ Melhorias Implementadas
- **Validação Real**: Verifica se projeto existe antes de criar casos
- **Detecção Automática**: Identifica projeto através da issue pai
- **Tratamento de Erro**: Mensagens claras para projetos inválidos

## Exemplos de Uso

### Caso 1: Projeto CREDT
```
Issue Pai: CREDT-1161
Sistema Detecta: Projeto CREDT
Casos Criados: CREDT-124, CREDT-125, CREDT-126
```

### Caso 2: Projeto BC
```
Issue Pai: BC-123
Sistema Detecta: Projeto BC
Casos Criados: BC-124, BC-125, BC-126
```

### Caso 3: Projeto QUALQUER
```
Issue Pai: QUALQUER-456
Sistema Detecta: Projeto QUALQUER
Casos Criados: QUALQUER-457, QUALQUER-458, QUALQUER-459
```

## Migração

### Para Usuários Existentes
1. **Remover PROJECT_KEY**: Remover a linha `PROJECT_KEY=BC` do arquivo `.env`
2. **Manter Outras Configurações**: Manter JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
3. **Testar**: O sistema funcionará automaticamente com qualquer projeto

### Para Novos Usuários
1. **Configurar Credenciais**: Apenas JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
2. **Usar Diretamente**: Sistema funciona com qualquer projeto sem configuração adicional

## Arquivos Modificados

- `app.py`: Removida variável `PROJECT_KEY` e referências
- `env.example`: Removida linha `PROJECT_KEY=BC`
- `README.md`: Atualizada documentação de configuração
- `REMOCAO_PROJECT_KEY.md`: Este arquivo de documentação

## Status

✅ **Implementação Concluída**
- Sistema totalmente adaptável a qualquer projeto
- Configuração simplificada
- Flexibilidade máxima mantida
- Compatibilidade com todos os projetos do Jira
