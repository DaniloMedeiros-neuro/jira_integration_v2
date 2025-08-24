# Instruções para Planilhas de Organização

## Problema Específico

Quando a planilha está em uma organização do Google Workspace (Google Workspace for Business/Education), mesmo compartilhando com "Qualquer pessoa na organização com o link", o sistema pode não conseguir acessar automaticamente as abas devido a restrições de segurança.

## Solução Recomendada: Adição Manual de Abas

### Passo a Passo:

1. **Cole a URL da planilha** no campo "URL da Planilha"
2. **Clique em "Extrair ID"** (ou aguarde a extração automática)
3. **Clique no botão "+"** ao lado do campo "Nome da Aba"
4. **Digite o nome exato da aba** da sua planilha
5. **Clique em "OK"**
6. **Repita o processo** para todas as abas que deseja usar

### Exemplos de Nomes de Abas Comuns:

- `Sheet1` (padrão do Google Sheets)
- `Planilha1`
- `Dados`
- `Casos de Teste`
- `Test Cases`
- `Casos`
- `Tests`
- `Teste`
- `Planilha`
- `Sheet`
- `Aba1`
- `Primeira`
- `Principal`
- `Main`
- `Data`

### Como Descobrir o Nome da Aba:

1. **Abra a planilha** no Google Sheets
2. **Observe as abas** na parte inferior da tela
3. **Copie o nome exato** da aba (incluindo maiúsculas/minúsculas)
4. **Cole no sistema** usando o botão "+"

## Alternativa: Configurar API do Google Sheets

Se você tem acesso administrativo à organização, pode configurar a API do Google Sheets:

### 1. Configurar no Google Cloud Console
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou use um existente
3. Ative a API do Google Sheets
4. Crie credenciais (Service Account ou API Key)

### 2. Configurar no Sistema
1. Adicione ao arquivo `.env`:
   ```
   GOOGLE_SHEETS_API_KEY=sua_chave_aqui
   ```
2. Reinicie a aplicação

## Verificação

Para verificar se a planilha está acessível:

```bash
# Teste 1: URL pública
curl "https://docs.google.com/spreadsheets/d/1SW3-UseON1ZSKftz8Vb5Cmn47DUeat87/gviz/tq?tqx=out:csv&sheet=Sheet1"

# Teste 2: Formato de organização
curl "https://docs.google.com/spreadsheets/d/1SW3-UseON1ZSKftz8Vb5Cmn47DUeat87/export?format=csv&gid=0"
```

Se ambos retornarem HTML (página de login), a planilha não está acessível via URL pública.

## Dicas Importantes

### Para Administradores de Organização:
- Configure políticas de compartilhamento adequadas
- Considere usar a API do Google Sheets para acesso programático
- Configure domínios permitidos se necessário

### Para Usuários:
- Use nomes de abas simples e sem caracteres especiais
- Evite espaços no início ou fim dos nomes
- Teste com uma aba de exemplo primeiro
- Se não funcionar, use a adição manual

## Suporte

Se ainda tiver problemas:
1. Verifique se o nome da aba está correto
2. Confirme que a planilha tem dados
3. Teste com uma planilha de exemplo
4. Entre em contato com o administrador da organização
