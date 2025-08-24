# Configuração da Planilha do Google Drive

## Problema Identificado

A planilha fornecida não está acessível publicamente, por isso o sistema não consegue carregar as abas reais. Aqui estão as soluções:

## Solução 1: Configurar Permissões da Planilha (Recomendado)

### Para Planilhas Públicas:

1. **Abra a planilha** no Google Drive
2. **Clique em "Compartilhar"** (canto superior direito)
3. **Clique em "Alterar para qualquer pessoa com o link"**
4. **Selecione "Visualizador"** nas permissões
5. **Clique em "Concluído"**

### Para Planilhas de Organização:

1. **Abra a planilha** no Google Drive
2. **Clique em "Compartilhar"** (canto superior direito)
3. **Clique em "Alterar para qualquer pessoa com o link"**
4. **Selecione "Qualquer pessoa na [sua organização] com o link"**
5. **Selecione "Visualizador"** nas permissões
6. **Clique em "Concluído"**

**Nota**: Para planilhas de organização, o sistema tentará acessar usando formatos específicos, mas pode ser necessário adicionar as abas manualmente.

### Resultado:
- A planilha ficará acessível via URL pública
- O sistema conseguirá carregar as abas reais automaticamente
- Não será necessário configurar API do Google Sheets

## Solução 2: Adicionar Abas Manualmente

Se não quiser tornar a planilha pública, você pode:

1. **Clique no botão "+"** ao lado do campo "Nome da Aba"
2. **Digite o nome exato da aba** da sua planilha
3. **Clique em "OK"**
4. **A aba será adicionada à lista**

### Exemplos de nomes comuns:
- `Sheet1`
- `Planilha1`
- `Dados`
- `Casos de Teste`
- `Test Cases`
- `Casos`
- `Tests`

## Solução 3: Configurar API do Google Sheets (Avançado)

Para acesso completo sem tornar a planilha pública:

### 1. Criar Projeto no Google Cloud Console
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a API do Google Sheets

### 2. Criar Credenciais
1. Vá em "APIs e Serviços" > "Credenciais"
2. Clique em "Criar Credenciais" > "Chave de API"
3. Copie a chave gerada

### 3. Configurar no Sistema
1. Adicione ao arquivo `.env`:
   ```
   GOOGLE_SHEETS_API_KEY=sua_chave_aqui
   ```
2. Reinicie a aplicação

## Verificação

Para verificar se a planilha está acessível:

```bash
curl "https://docs.google.com/spreadsheets/d/1SW3-UseON1ZSKftz8Vb5Cmn47DUeat87/gviz/tq?tqx=out:csv&sheet=Sheet1"
```

Se retornar dados CSV, a planilha está acessível.
Se retornar HTML (página de login), a planilha não está pública.

## Recomendação

**Use a Solução 1** (configurar permissões) - é a mais simples e não requer configuração técnica adicional.

## Suporte

Se ainda tiver problemas:
1. Verifique se o nome da aba está correto
2. Confirme que a planilha tem dados
3. Teste com uma planilha de exemplo primeiro
