# Correção: Validação de Projeto Válido

## Problema Identificado

Após a correção anterior do prefixo do projeto, surgiu um erro:

```
Erro ao criar caso de teste: 400 - {"errorMessages":[],"errors":{"project":"valid project is required"}}
```

### Causa do Problema
A correção anterior extraía o prefixo diretamente da string da issue pai (`issue_pai.split('-')[0]`), mas não validava se esse projeto realmente existe no Jira.

**Exemplo:**
- Issue Pai: `CREDT-1161`
- Prefixo Extraído: `CREDT`
- Problema: Projeto `CREDT` pode não existir no Jira

## Solução Implementada

### Modificação na Função `criar_caso_teste_planilha_manual()`

**Antes (Problemático):**
```python
# Extrair o prefixo do projeto da issue pai (método antigo)
project_key = issue_pai.split('-')[0] if '-' in issue_pai else "FALLBACK"
```

**Depois (Correto):**
```python
# Obter informações da issue pai (incluindo project_key válido)
project_key, issue_type_pai = obter_informacoes_issue(issue_pai)
if not project_key:
    return {
        'sucesso': False,
        'erro': f'Issue pai {issue_pai} não encontrada ou inválida'
    }
```

### Como Funciona a Validação

1. **Chamada à API**: `obter_informacoes_issue(issue_pai)` faz uma requisição GET para `/rest/api/3/issue/{issue_key}`
2. **Validação Real**: Verifica se a issue existe e obtém o `project_key` real do Jira
3. **Fallback Seguro**: Se a issue não existir, retorna erro em vez de tentar criar com projeto inválido

## Benefícios da Correção

### ✅ Validação Real
- Verifica se a issue pai realmente existe no Jira
- Obtém o `project_key` correto diretamente da API
- Evita erros de projeto inválido

### ✅ Tratamento de Erro
- Retorna erro claro se a issue pai não existir
- Não tenta criar casos de teste com projeto inválido
- Feedback mais útil para o usuário

### ✅ Consistência
- Usa a mesma lógica das outras funções que já funcionam
- Mantém padrão de validação em todo o sistema

## Exemplos de Comportamento

### Caso 1: Issue Pai Válida
```
Issue Pai: CREDT-1161 (existe no Jira)
Resultado: project_key = "CREDT" (obtido da API)
Status: ✅ Sucesso
```

### Caso 2: Issue Pai Inválida
```
Issue Pai: INVALID-999 (não existe no Jira)
Resultado: project_key = None
Status: ❌ Erro com mensagem clara
```

### Caso 3: Issue Pai com Projeto Diferente
```
Issue Pai: BC-123 (existe no Jira, projeto BC)
Resultado: project_key = "BC" (obtido da API)
Status: ✅ Sucesso
```

## Funcionalidades Afetadas

### ✅ Corrigidas
- **Planilha Manual**: Agora valida projeto antes de criar casos
- **Importação em Massa**: Validação de projeto implementada

### ✅ Já Funcionavam
- **Criação Individual**: Já usava `obter_informacoes_issue()`
- **Importação de Planilha**: Já usava validação de projeto

## Teste da Correção

Para testar se a correção está funcionando:

1. **Teste com Issue Válida:**
   - Use uma issue pai que existe no Jira (ex: `CREDT-1161`)
   - Deve criar casos de teste com sucesso

2. **Teste com Issue Inválida:**
   - Use uma issue pai que não existe (ex: `INVALID-999`)
   - Deve retornar erro claro sobre issue não encontrada

## Arquivos Modificados

- `app.py`: Função `criar_caso_teste_planilha_manual()` atualizada para usar validação real

## Status

✅ **Correção Implementada**
- Validação real de projeto implementada
- Tratamento de erro melhorado
- Consistência com outras funções mantida
- Testes recomendados para verificar funcionamento
