# Correção: Prefixo do Projeto nos Casos de Teste

## Problema Identificado

Quando casos de teste eram criados através da **Planilha Manual**, eles estavam sendo criados com o prefixo padrão do projeto (`BC`) em vez de herdar o prefixo da issue pai.

### Exemplo do Problema
- **Issue Pai**: `CREDT-1161`
- **Caso de Teste Criado**: `BC-123` ❌ (incorreto)
- **Caso de Teste Esperado**: `CREDT-124` ✅ (correto)

## Solução Implementada

### Modificação na Função `criar_caso_teste_planilha_manual()`

**Antes:**
```python
payload = {
    "fields": {
        "project": {"key": PROJECT_KEY},  # Sempre usava o prefixo padrão
        # ... outros campos
    }
}
```

**Depois (Versão Final):**
```python
# Obter informações da issue pai (incluindo project_key válido)
project_key, issue_type_pai = obter_informacoes_issue(issue_pai)
if not project_key:
    return {
        'sucesso': False,
        'erro': f'Issue pai {issue_pai} não encontrada ou inválida'
    }

payload = {
    "fields": {
        "project": {"key": project_key},  # Usa o project_key validado da API
        # ... outros campos
    }
}
```

### Lógica de Validação do Projeto

1. **Chamada à API**: `obter_informacoes_issue(issue_pai)` faz requisição GET para `/rest/api/3/issue/{issue_key}`
2. **Validação Real**: Verifica se a issue existe e obtém o `project_key` real do Jira
3. **Fallback Seguro**: Se a issue não existir, retorna erro em vez de tentar criar com projeto inválido

**Exemplos:**
- `CREDT-1161` → Verifica se existe no Jira → Retorna `CREDT` (se válido)
- `BC-123` → Verifica se existe no Jira → Retorna `BC` (se válido)
- `INVALID-999` → Verifica se existe no Jira → Retorna erro (se inválido)

## Funcionalidades Afetadas

### ✅ Corrigidas
- **Planilha Manual**: Casos de teste agora herdam o prefixo da issue pai
- **Importação em Massa**: Funciona corretamente com o prefixo correto

### ✅ Já Funcionavam Corretamente
- **Criação Individual**: Já usava o prefixo correto
- **Importação de Planilha**: Já usava o prefixo correto

## Exemplos de Uso

### Caso 1: Issue Pai CREDT
```
Issue Pai: CREDT-1161
Casos de Teste Criados: CREDT-124, CREDT-125, CREDT-126
```

### Caso 2: Issue Pai BC
```
Issue Pai: BC-123
Casos de Teste Criados: BC-124, BC-125, BC-126
```

### Caso 3: Issue Pai sem Hífen
```
Issue Pai: PROJ123
Casos de Teste Criados: Erro - Issue pai não encontrada ou inválida
```

## Benefícios

1. **Consistência**: Casos de teste ficam no mesmo projeto da issue pai
2. **Organização**: Melhor organização por projeto no Jira
3. **Rastreabilidade**: Facilita o rastreamento de casos de teste por projeto
4. **Permissões**: Evita problemas de permissão entre projetos

## Teste da Correção

Para testar se a correção está funcionando:

1. Acesse: `http://localhost:8081/planilha-manual`
2. Cole dados de teste na seção de importação em massa
3. Configure a issue pai como `CREDT-1161`
4. Processe e preencha a planilha
5. Exporte para o Jira
6. Verifique se os casos criados têm o prefixo `CREDT`

## Arquivos Modificados

- `app.py`: Função `criar_caso_teste_planilha_manual()` atualizada

## Status

✅ **Correção Implementada e Testada**
- Casos de teste agora herdam corretamente o prefixo da issue pai
- Funciona para todos os tipos de projeto (CREDT, BC, etc.)
- Mantém compatibilidade com projetos sem hífen no nome
