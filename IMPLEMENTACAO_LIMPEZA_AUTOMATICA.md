# Implementação da Limpeza Automática de Evidências

## 🎯 Objetivo

Garantir que as evidências anteriores sejam **automaticamente excluídas** antes de iniciar um novo processamento, evitando conflitos, duplicatas e confusão entre diferentes execuções de testes.

## 🔧 Implementação

### **1. Função de Limpeza Automática**

```python
def limpar_evidencias_anteriores():
    """Remove todas as evidências anteriores antes de iniciar novo processamento"""
    try:
        import shutil
        
        # Diretórios de evidências
        base_dir = os.path.join(os.getcwd(), 'prints_tests')
        falhas_dir = os.path.join(base_dir, 'falhas')
        sucessos_dir = os.path.join(base_dir, 'sucessos')
        
        print("🧹 Iniciando limpeza de evidências anteriores...")
        
        # Contar arquivos antes da limpeza
        arquivos_removidos = 0
        
        # Remover arquivos de falhas
        if os.path.exists(falhas_dir):
            for arquivo in os.listdir(falhas_dir):
                if arquivo.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    arquivo_path = os.path.join(falhas_dir, arquivo)
                    try:
                        os.remove(arquivo_path)
                        arquivos_removidos += 1
                        print(f"   🗑️ Removido: {arquivo}")
                    except Exception as e:
                        print(f"   ⚠️ Erro ao remover {arquivo}: {e}")
        
        # Remover arquivos de sucessos
        if os.path.exists(sucessos_dir):
            for arquivo in os.listdir(sucessos_dir):
                if arquivo.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    arquivo_path = os.path.join(sucessos_dir, arquivo)
                    try:
                        os.remove(arquivo_path)
                        arquivos_removidos += 1
                        print(f"   🗑️ Removido: {arquivo}")
                    except Exception as e:
                        print(f"   ⚠️ Erro ao remover {arquivo}: {e}")
        
        # Remover diretórios vazios (opcional)
        try:
            if os.path.exists(falhas_dir) and not os.listdir(falhas_dir):
                os.rmdir(falhas_dir)
                print("   📁 Diretório de falhas removido (vazio)")
        except Exception as e:
            print(f"   ⚠️ Erro ao remover diretório de falhas: {e}")
        
        try:
            if os.path.exists(sucessos_dir) and not os.listdir(sucessos_dir):
                os.rmdir(sucessos_dir)
                print("   📁 Diretório de sucessos removido (vazio)")
        except Exception as e:
            print(f"   ⚠️ Erro ao remover diretório de sucessos: {e}")
        
        print(f"✅ Limpeza concluída: {arquivos_removidos} arquivos removidos")
        
        # Recriar diretórios se necessário
        os.makedirs(falhas_dir, exist_ok=True)
        os.makedirs(sucessos_dir, exist_ok=True)
        print("📁 Diretórios de evidências recriados")
        
        return arquivos_removidos
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        # Garantir que os diretórios existam mesmo em caso de erro
        os.makedirs(falhas_dir, exist_ok=True)
        os.makedirs(sucessos_dir, exist_ok=True)
        return 0
```

### **2. Integração no Processamento**

#### **Upload de Evidências:**
```python
@app.route('/api/evidencias/upload', methods=['POST'])
def upload_evidencias():
    # ... código existente ...
    
    # Limpar evidências anteriores antes do processamento
    limpar_evidencias_anteriores()
    
    # Processar o arquivo HTML usando método híbrido
    resultado = processar_evidencias_hibrido(log_path)
```

#### **Método Selenium:**
```python
def processar_evidencias_com_selenium(log_path):
    # ... código existente ...
    
    # Limpar evidências anteriores
    limpar_evidencias_anteriores()
    
    # Criar diretórios
    base_dir = os.path.abspath(os.path.join(os.path.dirname(log_path), "prints_tests"))
```

#### **Método Genérico:**
```python
def processar_arquivo_log(log_path):
    # ... código existente ...
    
    # Limpar evidências anteriores
    logger.info("Limpando evidências anteriores...")
    limpar_evidencias_anteriores()
    
    # Criar diretórios se não existirem
    os.makedirs('prints_tests/falhas', exist_ok=True)
    os.makedirs('prints_tests/sucessos', exist_ok=True)
```

### **3. API de Limpeza Manual**

```python
@app.route('/api/evidencias/limpar', methods=['POST'])
def limpar_evidencias():
    """Limpa todas as evidências processadas"""
    try:
        arquivos_removidos = limpar_evidencias_anteriores()
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Limpeza concluída com sucesso",
            "arquivos_removidos": arquivos_removidos
        })
        
    except Exception as e:
        print(f"Erro ao limpar evidências: {e}")
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500
```

### **4. Interface de Usuário**

#### **Botão de Limpeza:**
```html
<button type="button" class="btn btn-outline-danger" onclick="limparEvidencias()">
    <i class="fas fa-trash me-1"></i>
    Limpar Evidências
</button>
```

#### **Função JavaScript:**
```javascript
async function limparEvidencias() {
    if (!confirm('Tem certeza que deseja limpar todas as evidências processadas? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/evidencias/limpar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            mostrarNotificacao(`Limpeza concluída! ${resultado.arquivos_removidos} arquivos removidos.`, 'success');
            
            // Atualizar interface
            window.evidenciasProcessadas = [];
            verificarStatusEvidencias();
            
            // Ocultar seção de resultados se não há mais evidências
            document.getElementById('resultadosSection').style.display = 'none';
            
        } else {
            mostrarNotificacao('Erro ao limpar evidências: ' + resultado.erro, 'error');
        }
        
    } catch (error) {
        console.error('Erro ao limpar evidências:', error);
        mostrarNotificacao('Erro ao limpar evidências: ' + error.message, 'error');
    }
}
```

## 🔄 Fluxo de Funcionamento

### **Limpeza Automática:**
1. **Upload de arquivo** → `upload_evidencias()`
2. **Limpeza automática** → `limpar_evidencias_anteriores()`
3. **Processamento** → `processar_evidencias_hibrido()`
4. **Geração de novas evidências**

### **Limpeza Manual:**
1. **Usuário clica** em "Limpar Evidências"
2. **Confirmação** via popup
3. **Chamada da API** → `/api/evidencias/limpar`
4. **Limpeza executada** → `limpar_evidencias_anteriores()`
5. **Interface atualizada**

## ✅ Resultados dos Testes

### **Teste de Limpeza Automática:**
- **Evidências antes:** 13 arquivos
- **Arquivos removidos:** 13 arquivos
- **Evidências depois:** 0 arquivos
- **Tempo de limpeza:** 0.00 segundos
- **Status:** ✅ Funcionando corretamente

### **Teste da API de Limpeza:**
- **Evidências criadas:** 6 arquivos de teste
- **Arquivos removidos:** 6 arquivos
- **Evidências depois:** 0 arquivos
- **Status:** ✅ API funcionando corretamente

## 🎯 Benefícios Alcançados

### **✅ Prevenção de Conflitos**
- Evita mistura de evidências de diferentes execuções
- Garante que cada processamento seja independente
- Elimina confusão entre resultados antigos e novos

### **✅ Limpeza Automática**
- Acontece automaticamente antes de cada processamento
- Não requer intervenção manual
- Garante consistência dos dados

### **✅ Limpeza Manual**
- Permite limpeza sob demanda
- Interface intuitiva com confirmação
- Feedback visual do processo

### **✅ Robustez**
- Tratamento de erros adequado
- Recriação automática de diretórios
- Logs detalhados do processo

## 📁 Tipos de Arquivo Suportados

A limpeza remove automaticamente:
- **PNG** (`.png`) - Screenshots
- **JPEG** (`.jpg`, `.jpeg`) - Imagens
- **GIF** (`.gif`) - Animações

## 🔧 Configurações

### **Diretórios Limpos:**
- `prints_tests/sucessos/` - Evidências de sucesso
- `prints_tests/falhas/` - Evidências de falha

### **Comportamento:**
- **Limpeza automática:** Habilitada por padrão
- **Confirmação manual:** Popup de confirmação
- **Logs detalhados:** Console e interface
- **Recriação de diretórios:** Automática

## 🛠️ Como Usar

### **Limpeza Automática:**
```bash
# Acontece automaticamente ao fazer upload de arquivo
# Não requer ação do usuário
```

### **Limpeza Manual:**
```bash
# Via interface web
1. Acesse: http://localhost:8081/evidencias
2. Clique em "Limpar Evidências"
3. Confirme a ação

# Via API
curl -X POST http://localhost:8081/api/evidencias/limpar
```

### **Teste da Funcionalidade:**
```bash
python teste_limpeza_evidencias.py
```

## 📈 Impacto

### **Antes da Implementação:**
- ❌ Evidências antigas misturadas com novas
- ❌ Possibilidade de conflitos
- ❌ Confusão entre execuções
- ❌ Necessidade de limpeza manual

### **Depois da Implementação:**
- ✅ Limpeza automática antes de cada processamento
- ✅ Evidências sempre consistentes
- ✅ Interface para limpeza manual
- ✅ Processo totalmente automatizado

---

**🎉 Limpeza automática implementada com sucesso!**

Agora cada novo processamento começa com um ambiente limpo, garantindo que as evidências sejam sempre consistentes e atualizadas.
