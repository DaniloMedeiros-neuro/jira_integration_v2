# Análise Detalhada de Épicos - Neurotech Jira Integration

## 📊 Visão Geral

A nova funcionalidade de **Análise Detalhada de Épicos** oferece métricas avançadas e insights profundos sobre o progresso e performance dos épicos no Jira. Esta ferramenta permite aos gestores e equipes acompanhar de forma detalhada o desenvolvimento dos projetos.

## 🚀 Funcionalidades Principais

### 1. **Visão Geral**
- **Número total de issues** no épico (histórias, tarefas, bugs)
- **Breakdown por tipo** de issue
- **Progresso geral** com percentuais de conclusão
- **Story Points** totais e percentual de conclusão

### 2. **Breakdown por Status**
- **Distribuição detalhada** por status (Done, In Progress, To Do, Blocked, etc.)
- **Percentuais** de cada status
- **Story Points** por status
- **Tempo médio** de permanência em cada status

### 3. **Casos de Teste**
- **Resumo dos casos de teste** relacionados ao épico
- **Status de execução** (Passed, Failed, Not Executed)
- **Detalhamento** de cada caso de teste
- **Responsáveis** pelos testes

### 4. **Evolução do Escopo**
- **Itens adicionados** vs **itens removidos** durante a execução
- **Variação líquida** do escopo
- **Timeline** de mudanças por sprint
- **Gráfico de evolução** do escopo

### 5. **Velocidade e Tempo**
- **Lead Time médio** (tempo total desde criação até conclusão)
- **Cycle Time médio** (tempo em desenvolvimento)
- **Velocidade da equipe** (Story Points por sprint)
- **Throughput** (issues por sprint)
- **Distribuição de tempos** de conclusão

## 🎯 Como Usar

### Acesso à Funcionalidade
1. Acesse a página de **Métricas**: `http://localhost:5000/metricas`
2. Clique na aba **"Análise Detalhada de Épicos"**
3. Digite o **ID do Épico** (ex: TLD-100)
4. Clique em **"Analisar Épico"**

### Navegação pelas Sub-abas
A análise detalhada é organizada em 5 sub-abas:

1. **👁️ Visão Geral** - Resumo executivo do épico
2. **📊 Breakdown por Status** - Análise detalhada por status
3. **🧪 Casos de Teste** - Status e detalhes dos testes
4. **📈 Evolução do Escopo** - Mudanças no escopo ao longo do tempo
5. **⚡ Velocidade e Tempo** - Métricas de performance da equipe

## 📈 Métricas Calculadas

### Progresso
- **Total de Issues**: Soma de todas as issues do épico
- **Percentual de Conclusão**: Issues concluídas / Total de issues
- **Story Points Concluídos**: SP das issues em status final
- **Progresso por Status**: Distribuição percentual por status

### Tempo
- **Lead Time**: Tempo desde criação até resolução
- **Cycle Time**: Tempo em desenvolvimento ativo
- **Velocidade**: Story Points entregues por sprint
- **Throughput**: Issues entregues por sprint

### Qualidade
- **Casos de Teste**: Quantidade e status de execução
- **Bugs**: Quantidade de bugs no épico
- **Dependências**: Issues com bloqueios

## 🔧 Configuração Técnica

### APIs Utilizadas
- **`/api/analise-epico-detalhada/<epic_key>`** - Análise completa do épico
- **`/api/metricas-epico/<epic_key>`** - Métricas básicas do épico

### Dados Coletados
- Informações do épico (key, summary, status)
- Issues relacionadas (histórias, tarefas, bugs)
- Casos de teste vinculados
- Worklogs e comentários
- Histórico de mudanças

### Campos Jira Utilizados
- `issuetype` - Tipo da issue
- `status` - Status atual
- `storypoints` - Pontos de história
- `timespent` - Tempo gasto
- `timeestimate` - Tempo estimado
- `assignee` - Responsável
- `created` - Data de criação
- `resolutiondate` - Data de resolução

## 🎨 Interface

### Design Responsivo
- **Desktop**: Layout em grid com múltiplas colunas
- **Tablet**: Layout adaptativo
- **Mobile**: Layout em coluna única

### Componentes Visuais
- **Cards informativos** com métricas principais
- **Gráficos interativos** usando Chart.js
- **Tabelas detalhadas** com dados específicos
- **Barras de progresso** visuais
- **Badges de status** coloridos

### Cores e Temas
- **Verde**: Status concluído/sucesso
- **Amarelo**: Status em progresso
- **Vermelho**: Status bloqueado/erro
- **Azul**: Status pendente
- **Cinza**: Status neutro

## 🧪 Testes

### Script de Teste
Execute o script de teste para verificar a funcionalidade:

```bash
python teste_metricas_epico.py
```

### Dados de Teste
O script gera dados mock para demonstração:
- 25 issues totais
- 15 histórias, 8 tarefas, 2 bugs
- 48% de conclusão
- 85 Story Points totais
- 3 casos de teste

## 📊 Exemplos de Uso

### Cenário 1: Análise de Progresso
1. Digite o ID do épico
2. Vá para "Visão Geral"
3. Analise o percentual de conclusão
4. Verifique os Story Points pendentes

### Cenário 2: Identificação de Bloqueios
1. Acesse "Breakdown por Status"
2. Identifique issues em "Blocked"
3. Analise o tempo médio em impedimento
4. Tome ações para desbloquear

### Cenário 3: Análise de Qualidade
1. Vá para "Casos de Teste"
2. Verifique quantos testes falharam
3. Identifique responsáveis pelos testes
4. Planeje correções necessárias

### Cenário 4: Otimização de Velocidade
1. Acesse "Velocidade e Tempo"
2. Analise o Lead Time médio
3. Compare com sprints anteriores
4. Identifique oportunidades de melhoria

## 🔄 Atualizações Futuras

### Funcionalidades Planejadas
- **Comparação entre épicos** similares
- **Previsões** baseadas em dados históricos
- **Alertas automáticos** para métricas críticas
- **Exportação** para Excel/PDF
- **Integração** com ferramentas de BI

### Melhorias Técnicas
- **Cache** de dados para performance
- **Filtros avançados** por período
- **Dashboards personalizáveis**
- **APIs** para integração externa

## 🐛 Troubleshooting

### Problemas Comuns

**Erro: "Épico não encontrado"**
- Verifique se o ID do épico está correto
- Confirme se o épico existe no Jira
- Verifique as permissões de acesso

**Erro: "Configurações do Jira incompletas"**
- Verifique o arquivo `.env`
- Confirme as credenciais do Jira
- Teste a conexão com a API

**Dados não carregam**
- Verifique a conexão com a internet
- Confirme se o servidor está rodando
- Verifique os logs do console

### Logs Úteis
```bash
# Verificar logs do Flask
tail -f app.log

# Testar conexão com Jira
curl -u email:token https://neurotech.atlassian.net/rest/api/3/myself
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Execute os testes
3. Consulte os logs
4. Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido por:** Equipe Neurotech  
**Versão:** 2.0  
**Data:** Janeiro 2024
