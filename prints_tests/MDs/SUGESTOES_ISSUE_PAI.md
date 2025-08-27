# Sugestões de Issue Pai - Correção de Digitação

## Problema Identificado

Usuários frequentemente cometem erros de digitação ao informar a issue pai, como:
- `CREDIT-1161` em vez de `CREDT-1161`
- `BC-12` em vez de `BC-123`
- `PROJ-456` em vez de `PROJ-4567`

Isso resultava em erros genéricos sem orientação sobre como corrigir.

## Solução Implementada

### Funcionalidade de Sugestões Automáticas

Quando uma issue pai não é encontrada, o sistema agora:

1. **Analisa o erro**: Identifica que a issue não existe
2. **Busca similares**: Procura issues com o mesmo prefixo de projeto
3. **Sugere alternativas**: Apresenta até 5 issues similares como sugestões
4. **Guia o usuário**: Fornece orientação clara sobre possíveis correções

### Exemplo de Funcionamento

**Erro Anterior:**
```
Issue pai CREDIT-1161 não encontrada ou inválida
```

**Erro Atual (com Sugestões):**
```
Issue pai CREDIT-1161 não encontrada ou inválida. Sugestões: CREDT-1161, CREDT-1160, CREDT-1162, CREDT-1159, CREDT-1163
```

## Implementação Técnica

### Função `buscar_issues_similares()`

```python
def buscar_issues_similares(issue_key):
    """Busca issues similares para sugerir correção de digitação"""
    try:
        # Extrair prefixo e número da issue
        if '-' in issue_key:
            prefixo, numero = issue_key.split('-', 1)
        else:
            return []
        
        # Buscar issues com o mesmo prefixo
        jql = f'project = {prefixo} AND issuekey LIKE "{prefixo}-%" ORDER BY created DESC'
        url = f"{JIRA_BASE_URL}/rest/api/3/search"
        
        payload = {
            "jql": jql,
            "maxResults": 10,
            "fields": ["key", "summary"]
        }
        
        response = requests.post(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            
            # Filtrar issues mais similares
            sugestoes = []
            for issue in issues:
                issue_key_found = issue['key']
                if issue_key_found != issue_key:  # Não sugerir a mesma issue
                    sugestoes.append(issue_key_found)
            
            return sugestoes[:5]  # Retornar até 5 sugestões
        
        return []
        
    except Exception as e:
        print(f"Erro ao buscar issues similares: {e}")
        return []
```

### Integração nas Funções

A funcionalidade foi integrada em todas as funções que validam issues pai:

1. **`criar_caso_teste()`** - Criação individual de casos de teste
2. **`criar_caso_teste_planilha_manual()`** - Planilha manual
3. **`importar_planilha_api()`** - Importação de planilha

## Benefícios

### ✅ Experiência do Usuário Melhorada
- **Feedback Útil**: Erros mais informativos
- **Correção Rápida**: Sugestões imediatas
- **Menos Tentativas**: Reduz tentativas de adivinhação

### ✅ Redução de Erros
- **Prevenção**: Orienta sobre possíveis correções
- **Aprendizado**: Usuário aprende o formato correto
- **Eficiência**: Menos tempo perdido com erros

### ✅ Flexibilidade
- **Qualquer Projeto**: Funciona com todos os projetos
- **Busca Inteligente**: Encontra issues similares automaticamente
- **Limite de Sugestões**: Máximo de 5 sugestões para não sobrecarregar

## Exemplos de Uso

### Caso 1: Erro de Digitação Simples
```
Input: CREDIT-1161
Erro: Issue pai CREDIT-1161 não encontrada ou inválida. Sugestões: CREDT-1161, CREDT-1160, CREDT-1162
Ação: Usuário corrige para CREDT-1161
```

### Caso 2: Número Incorreto
```
Input: BC-12
Erro: Issue pai BC-12 não encontrada ou inválida. Sugestões: BC-123, BC-124, BC-125
Ação: Usuário corrige para BC-123
```

### Caso 3: Prefixo Incorreto
```
Input: PROJ-456
Erro: Issue pai PROJ-456 não encontrada ou inválida. Sugestões: PROJ-4567, PROJ-4568, PROJ-4569
Ação: Usuário corrige para PROJ-4567
```

## Casos Especiais

### Quando Não Há Sugestões
Se não existirem issues similares no projeto, o sistema retorna o erro padrão:
```
Issue pai INVALID-999 não encontrada ou inválida
```

### Quando o Projeto Não Existe
Se o prefixo do projeto não existir, não há sugestões:
```
Issue pai FANTASMA-123 não encontrada ou inválida
```

## Configuração

### Parâmetros Ajustáveis
- **Máximo de Sugestões**: 5 (configurável)
- **Busca por Projeto**: Mesmo prefixo de projeto
- **Ordenação**: Por data de criação (mais recentes primeiro)

### Performance
- **Cache**: Não implementado (busca em tempo real)
- **Timeout**: Usa timeout padrão do requests
- **Limite**: Máximo 10 issues buscadas, 5 retornadas

## Teste da Funcionalidade

Para testar as sugestões:

1. **Acesse**: `http://localhost:8081/planilha-manual`
2. **Digite uma issue inválida**: Ex: `CREDIT-1161`
3. **Tente exportar**: Clique em "Exportar para Jira"
4. **Verifique as sugestões**: Deve aparecer `CREDT-1161` nas sugestões

## Arquivos Modificados

- `app.py`: 
  - Nova função `buscar_issues_similares()`
  - Integração em `criar_caso_teste()`
  - Integração em `criar_caso_teste_planilha_manual()`
  - Integração em `importar_planilha_api()`

## Status

✅ **Funcionalidade Implementada**
- Sugestões automáticas para issues pai inválidas
- Integração em todas as funções relevantes
- Feedback melhorado para o usuário
- Testes recomendados para verificar funcionamento
