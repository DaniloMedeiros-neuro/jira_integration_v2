# Gerenciador de Casos de Teste - Jira Integration v2

Sistema web para gerenciar casos de teste do Jira com integração completa à API do Atlassian Jira.

## 🚀 Funcionalidades

### ✅ Funcionalidades Principais
- **Busca de Casos de Teste**: Busca todos os casos de teste relacionados a uma issue pai
- **Criação de Casos de Teste**: Interface para criar novos casos de teste no Jira
- **Edição de Casos de Teste**: Modificar casos de teste existentes
- **Exclusão de Casos de Teste**: Remover casos de teste do Jira
- **Visualização em Cards**: Interface moderna com cards para visualizar casos de teste

### 🆕 Novas Funcionalidades
- **Visualização em Planilha**: Nova interface para visualizar casos de teste em formato de tabela
- **Exportação para Excel**: Exportar casos de teste para arquivo Excel (.xlsx) com formatação profissional
- **Navegação entre Visualizações**: Alternar entre visualização em cards e planilha
- **Edição Inline na Planilha**: Editar campos diretamente na tabela sem sair da visualização
- **Salvamento Individual**: Salvar alterações de cada campo individualmente
- **Salvamento em Lote**: Salvar todas as alterações de uma vez
- **Feedback Visual**: Indicadores visuais para campos modificados, salvando e com erro

## 📋 Pré-requisitos

- Python 3.8+
- Acesso ao Jira com credenciais de API
- Ambiente virtual (recomendado)

## 🛠️ Instalação

1. **Clone o repositório**:
```bash
git clone <url-do-repositorio>
cd jira_integration_v2
```

2. **Crie e ative o ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**:
```bash
cp env.example .env
```

Edite o arquivo `.env` com suas credenciais do Jira:
```env
JIRA_URL=https://seu-dominio.atlassian.net
JIRA_EMAIL=seu-email@empresa.com
JIRA_API_TOKEN=seu-token-api
PROJECT_KEY=SEU_PROJETO
JIRA_AUTH=base64(email:token)
```

5. **Execute a aplicação**:
```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:8080`

## 🎯 Como Usar

### 1. Buscar Casos de Teste
1. Acesse a página principal
2. Digite o ID da issue pai (ex: BC-126)
3. Clique em "Buscar"
4. Visualize os casos de teste em formato de cards

### 2. Visualizar Casos de Teste
1. Digite o ID da issue pai (ex: BC-126, CREDT-1161)
2. Clique em "Buscar Casos de Teste"
3. Os casos de teste serão exibidos em ordem decrescente por ID (mais recentes primeiro)
4. Clique em "Ver como Planilha" para visualizar em formato de tabela editável

### 3. Editar Casos de Teste na Planilha
1. Na visualização em planilha, clique em qualquer campo editável
2. Faça as alterações desejadas
3. **Opção 1 - Salvar Individualmente**: 
   - Passe o mouse sobre o campo alterado
   - Clique no botão de salvar que aparece no canto superior direito
4. **Opção 2 - Salvar em Lote**:
   - Faça todas as alterações desejadas
   - Clique no botão "Salvar Todas as Alterações" no cabeçalho
5. **Indicadores Visuais**:
   - 🟡 **Amarelo**: Campo modificado (não salvo)
   - 🟢 **Verde**: Salvando
   - 🔴 **Vermelho**: Erro ao salvar
   - ✅ **Verde**: Salvo com sucesso

**⚠️ Nota**: Apenas o campo Status pode retornar erro devido a restrições de permissão no Jira. Todos os outros campos (Título, Tipo de Execução, Tipo de Teste, Componentes, Objetivo, Pré-condições, Descrição) são editáveis e funcionam corretamente.

### 4. Exportar para Excel
1. Na visualização em planilha
2. Clique no botão "Exportar Excel"
3. O arquivo será baixado automaticamente com formatação profissional

### 5. Criar Novo Caso de Teste
1. Clique em "Criar Novo Caso"
2. Preencha os campos obrigatórios
3. Clique em "Salvar"

### 6. Editar Caso de Teste
1. Na lista de casos de teste
2. Clique no ícone de edição (lápis)
3. Modifique os campos desejados
4. Clique em "Salvar"

### 7. Excluir Caso de Teste
1. Na lista de casos de teste
2. Clique no ícone de exclusão (lixeira)
3. Confirme a exclusão

## 📊 Estrutura do Projeto

```
jira_integration_v2/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── .env                  # Variáveis de ambiente (não versionado)
├── env.example           # Exemplo de variáveis de ambiente
├── templates/
│   ├── index.html        # Página principal
│   └── planilha.html     # Página de visualização em planilha
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS
│   └── js/
│       └── app.js        # JavaScript da aplicação
└── README.md             # Este arquivo
```

## 🔧 API Endpoints

### GET `/api/casos-teste/<issue_pai>`
Busca todos os casos de teste relacionados a uma issue pai.

### POST `/api/caso-teste`
Cria um novo caso de teste.

### PUT `/api/caso-teste/<issue_key>`
Atualiza um caso de teste existente.

### PUT `/api/casos-teste/batch-update`
Atualiza múltiplos casos de teste de uma vez (para edição inline na planilha).

### DELETE `/api/caso-teste/<issue_key>`
Exclui um caso de teste.

### GET `/api/casos-teste/<issue_pai>/exportar-excel`
Exporta os casos de teste para arquivo Excel.

### GET `/planilha/<issue_pai>`
Página de visualização em formato de planilha.

## 🎨 Interface

### Visualização em Cards
- Layout moderno com cards
- Informações organizadas e fáceis de ler
- Botões de ação para cada caso de teste

### Visualização em Planilha
- Tabela responsiva com todas as informações
- Cabeçalho fixo durante a rolagem
- Formatação de status com cores
- Scroll horizontal para colunas adicionais
- **Campos editáveis inline**: Clique para editar diretamente na tabela
- **Botões de salvar individuais**: Aparecem ao passar o mouse sobre campos modificados
- **Botão de salvar em lote**: Salva todas as alterações de uma vez
- **Indicadores visuais**: Cores diferentes para campos modificados, salvando e com erro

### Exportação Excel
- Arquivo Excel com formatação profissional
- Cabeçalho com cores e fonte em negrito
- Largura das colunas ajustada automaticamente
- Nome do arquivo com timestamp

## 🔒 Segurança

- Credenciais armazenadas em variáveis de ambiente
- Autenticação via API Token do Jira
- Validação de entrada em todos os formulários

## 🐛 Solução de Problemas

### Erro 500 - Variáveis de ambiente não carregadas
- Verifique se o arquivo `.env` existe
- Confirme se o ambiente virtual está ativado
- Reinicie a aplicação após alterações no `.env`

### Erro de autenticação no Jira
- Verifique se o token API está correto
- Confirme se o email está correto
- Teste a autenticação diretamente na API do Jira

### Casos de teste não encontrados
- Verifique se a issue pai existe
- Confirme se há casos de teste relacionados via issue links
- Verifique as permissões do usuário no Jira

## 📝 Changelog

### v2.0.0
- ✅ Adicionada visualização em formato de planilha
- ✅ Implementada exportação para Excel
- ✅ Melhorada a interface de usuário
- ✅ Corrigidos problemas de autenticação
- ✅ Adicionadas novas dependências (pandas, openpyxl)
- ✅ **Implementada edição inline na planilha**
- ✅ **Adicionado salvamento individual e em lote**
- ✅ **Criados indicadores visuais para feedback**
- ✅ **Nova API endpoint para atualização em lote**

### v1.0.0
- ✅ Funcionalidades básicas de CRUD
- ✅ Integração com API do Jira
- ✅ Interface web responsiva

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte, entre em contato através de:
- Email: [seu-email@empresa.com]
- Issues do GitHub: [link-do-repositorio/issues]