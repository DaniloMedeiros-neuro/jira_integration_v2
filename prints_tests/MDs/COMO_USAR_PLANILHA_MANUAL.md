# 📋 Como Usar a Planilha Manual

## 🎯 **O que é a Planilha Manual**

A Planilha Manual é uma interface editável diretamente na tela que permite criar casos de teste com todos os campos do Jira, sem depender de planilhas externas.

## 🚀 **Como Acessar**

1. **URL**: http://localhost:8081/planilha-manual
2. **Menu**: Clique em "Planilha Manual" no header da aplicação

## 📊 **Campos Disponíveis**

### **Campos Editáveis:**

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| **Título** | Texto | Nome do caso de teste | "Validar Login com Credenciais Válidas" |
| **Status** | Select | Status do caso | To Do, In Progress, Done |
| **Tipo de Execução** | Select | Como será executado | Manual, Automated |
| **Tipo de Teste** | Select | Categoria do teste | Functional, Non-Functional, Integration, Unit |
| **Componentes** | Texto | Componentes afetados | "Frontend, Backend" |
| **Objetivo** | Textarea | Objetivo do teste | "Verificar se o sistema permite login com credenciais corretas" |
| **Pré-condições** | Textarea | Condições necessárias | "Usuário cadastrado no sistema" |
| **Descrição** | Textarea | Descrição detalhada | "Dado que o usuário está na tela de login..." |

### **Campos Automáticos:**

| Campo | Descrição |
|-------|-----------|
| **ID** | Gerado automaticamente pelo Jira após exportação |
| **Criado em** | Data/hora de criação no Jira |
| **Atualizado em** | Data/hora da última atualização |

## 🔧 **Como Usar**

### **Passo a Passo:**

1. **Acesse a página** da planilha manual
2. **Preencha os dados** diretamente nas células editáveis
3. **Adicione mais linhas** usando o botão "Adicionar Linha"
4. **Remova linhas** usando o botão "X" em cada linha
5. **Clique em "Exportar para Jira"**
6. **Digite a Issue Pai** (ex: CREDT-1161)
7. **Confirme a exportação**
8. **Veja os IDs e datas** preenchidos automaticamente

### **Exemplo de Preenchimento:**

```
Título: Validar Login com Credenciais Válidas
Status: To Do
Tipo de Execução: Manual
Tipo de Teste: Functional
Componentes: Frontend, Backend
Objetivo: Verificar se o sistema permite login com credenciais corretas
Pré-condições: Usuário cadastrado no sistema
Descrição: Dado que o usuário está na tela de login, quando inserir credenciais válidas, então deve ser redirecionado para o dashboard
```

## 🎨 **Interface**

### **Design Features:**
- ✅ **Planilha responsiva** com scroll horizontal e vertical
- ✅ **Cabeçalhos fixos** durante scroll
- ✅ **Cores diferenciadas** para linhas pares/ímpares
- ✅ **Hover effects** nas linhas
- ✅ **Campos readonly** destacados em cinza
- ✅ **Botões de ação** intuitivos

### **Funcionalidades:**
- ✅ **Adicionar linhas** ilimitadas
- ✅ **Remover linhas** individualmente
- ✅ **Validação** de campos obrigatórios
- ✅ **Feedback visual** de modificações
- ✅ **Modal de confirmação** para exportação
- ✅ **Resultados detalhados** após exportação

## 📤 **Exportação para Jira**

### **Processo:**
1. **Clique** em "Exportar para Jira"
2. **Digite** a Issue Pai (obrigatório)
3. **Confirme** a exportação
4. **Aguarde** o processamento
5. **Veja** os resultados

### **Resultados:**
- ✅ **IDs do Jira** preenchidos automaticamente
- ✅ **Datas** de criação e atualização
- ✅ **Status** de sucesso/erro para cada caso
- ✅ **Relatório** detalhado da exportação

## 🔍 **Validações**

### **Campos Obrigatórios:**
- **Título**: Deve ser preenchido
- **Issue Pai**: Deve ser informada na exportação

### **Valores Aceitos:**
- **Status**: To Do, In Progress, Done
- **Tipo de Execução**: Manual, Automated
- **Tipo de Teste**: Functional, Non-Functional, Integration, Unit

## 🎉 **Vantagens**

### **✅ Simplicidade:**
- Não precisa de planilhas externas
- Interface intuitiva e direta
- Sem dependências de APIs externas

### **✅ Controle Total:**
- Edição direta na tela
- Validação em tempo real
- Feedback imediato

### **✅ Integração Completa:**
- Exportação direta para Jira
- IDs e datas automáticos
- Resultados detalhados

### **✅ Flexibilidade:**
- Adicionar/remover linhas
- Editar qualquer campo
- Exportar quando quiser

## 🚀 **Teste Agora**

1. **Acesse**: http://localhost:8081/planilha-manual
2. **Preencha** alguns casos de teste
3. **Adicione** mais linhas se necessário
4. **Exporte** para o Jira
5. **Veja** os IDs e datas preenchidos

**A planilha manual oferece controle total sobre seus casos de teste!** 🎉
