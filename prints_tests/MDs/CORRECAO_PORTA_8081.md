# Correção da Porta do Servidor

## Problema Identificado

O sistema estava apresentando erro de conexão ao tentar buscar requisitos:

```
Erro de conexão: Failed to fetch
```

### Causa do Problema
O JavaScript estava fazendo requisições para a porta `8080`, mas o servidor Flask está configurado para rodar na porta `8081`.

## Solução Implementada

### URLs Corrigidas no JavaScript

**Antes:**
```javascript
const response = await fetch(`http://127.0.0.1:8080/api/casos-teste/${requisitoPai}`);
const url = issueKey ? `http://127.0.0.1:8080/api/caso-teste/${issueKey}` : 'http://127.0.0.1:8080/api/caso-teste';
const response = await fetch(`http://127.0.0.1:8080/api/caso-teste/${casoTesteEditando}`, {
window.open(`http://127.0.0.1:8080/planilha/${issuePaiAtual}`, '_blank');
```

**Depois:**
```javascript
const response = await fetch(`http://127.0.0.1:8081/api/casos-teste/${requisitoPai}`);
const url = issueKey ? `http://127.0.0.1:8081/api/caso-teste/${issueKey}` : 'http://127.0.0.1:8081/api/caso-teste';
const response = await fetch(`http://127.0.0.1:8081/api/caso-teste/${casoTesteEditando}`, {
window.open(`http://127.0.0.1:8081/planilha/${issuePaiAtual}`, '_blank');
```

### Documentação Atualizada

**README.md:**
```diff
- A aplicação estará disponível em: `http://localhost:8080`
+ A aplicação estará disponível em: `http://localhost:8081`
```

**README_IMPORTACAO.md:**
```diff
- Ou acesse diretamente: `http://localhost:8080/importar-planilha`
+ Ou acesse diretamente: `http://localhost:8081/importar-planilha`
```

## Configuração do Servidor

### Porta Padrão
O servidor Flask está configurado para rodar na porta `8081`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
```

### URLs do Sistema
- **Página Principal**: `http://localhost:8081`
- **Planilha Manual**: `http://localhost:8081/planilha-manual`
- **Importar Planilha**: `http://localhost:8081/importar-planilha`
- **Visualizar Planilha**: `http://localhost:8081/planilha/{issue_pai}`

## Funcionalidades Afetadas

### ✅ Corrigidas
- **Busca de Requisitos**: Agora funciona corretamente
- **Criação de Casos**: URLs corrigidas
- **Edição de Casos**: URLs corrigidas
- **Exclusão de Casos**: URLs corrigidas
- **Visualização em Planilha**: URLs corrigidas

### ✅ Testadas
- Busca de requisitos por ID
- Criação de novos casos de teste
- Edição de casos existentes
- Exclusão de casos de teste
- Navegação para visualização em planilha

## Como Testar

### 1. Iniciar o Servidor
```bash
python app.py
```

### 2. Acessar a Aplicação
- Abrir: `http://localhost:8081`
- Verificar se a página carrega corretamente

### 3. Testar Busca de Requisito
- Digitar um ID de requisito (ex: `CREDT-1161`)
- Clicar em "Buscar"
- Verificar se os casos de teste são carregados

### 4. Testar Funcionalidades
- Criar novo caso de teste
- Editar caso existente
- Excluir caso de teste
- Visualizar em planilha

## Arquivos Modificados

- `static/js/app.js`: URLs corrigidas para porta 8081
- `README.md`: Documentação atualizada
- `README_IMPORTACAO.md`: Documentação atualizada
- `CORRECAO_PORTA_8081.md`: Este arquivo de documentação

## Status

✅ **Correção Implementada**
- Todas as URLs JavaScript corrigidas para porta 8081
- Documentação atualizada
- Funcionalidades testadas e funcionando
- Sistema operacional completo
