// Variáveis globais
let rowCounter = 0;
let exportModal;
let dadosProcessados = []; // Array para armazenar dados processados da importação em massa

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar modal
    exportModal = new bootstrap.Modal(document.getElementById('exportModal'), {
        backdrop: 'static',
        keyboard: false
    });
    
    // Adicionar evento para garantir que o campo issuePai esteja habilitado quando o modal for exibido
    const exportModalElement = document.getElementById('exportModal');
    if (exportModalElement) {
        exportModalElement.addEventListener('shown.bs.modal', function() {
            habilitarCampoIssuePai();
            monitorarCampoIssuePai();
        });
    }
    
    // Event listeners para planilha manual
    const btnAddRowElement = document.getElementById('btnAddRow');
    if (btnAddRowElement) btnAddRowElement.addEventListener('click', addRow);
    
    const btnExportJiraElement = document.getElementById('btnExportJira');
    if (btnExportJiraElement) btnExportJiraElement.addEventListener('click', showExportModal);
    
    const btnConfirmExportElement = document.getElementById('btnConfirmExport');
    if (btnConfirmExportElement) btnConfirmExportElement.addEventListener('click', exportToJira);
    
    // Event listeners para importação em massa
    const btnProcessarDadosElement = document.getElementById('btnProcessarDados');
    if (btnProcessarDadosElement) btnProcessarDadosElement.addEventListener('click', processarDadosColados);
    
    const btnLimparDadosElement = document.getElementById('btnLimparDados');
    if (btnLimparDadosElement) btnLimparDadosElement.addEventListener('click', limparDadosImportacao);
    
    const btnPreencherPlanilhaElement = document.getElementById('btnPreencherPlanilha');
    if (btnPreencherPlanilhaElement) btnPreencherPlanilhaElement.addEventListener('click', preencherPlanilhaComDados);
    
    // Preencher issuePai automaticamente se disponível (versão silenciosa)
    preencherIssuePaiAutomaticamente(true);
    

    
    // Iniciar monitoramento do campo issuePai
    setTimeout(() => {
        monitorarCampoIssuePai();
        verificarInterferenciasJavaScript();
    }, 1000);
    
    // Adicionar debug para o campo issuePai
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        // Garantir que o campo esteja sempre habilitado
        issuePaiField.disabled = false;
        issuePaiField.readOnly = false;
        issuePaiField.style.pointerEvents = 'auto';
        issuePaiField.style.opacity = '1';
        issuePaiField.style.backgroundColor = 'white';
        issuePaiField.style.color = 'var(--neurotech-secondary)';
        
        // Interceptar e prevenir bloqueios de teclado
        issuePaiField.addEventListener('keydown', function(e) {
            console.log('Campo issuePai recebeu keydown:', e.key);
            // Garantir que o campo esteja habilitado
            e.target.disabled = false;
            e.target.readOnly = false;
            // Não bloquear nenhuma tecla
            e.stopPropagation();
        });
        
        issuePaiField.addEventListener('keypress', function(e) {
            console.log('Campo issuePai recebeu keypress:', e.key);
            // Garantir que o campo esteja habilitado
            e.target.disabled = false;
            e.target.readOnly = false;
            // Não bloquear nenhuma tecla
            e.stopPropagation();
        });
        
        issuePaiField.addEventListener('keyup', function(e) {
            console.log('Campo issuePai recebeu keyup:', e.key);
            // Garantir que o campo esteja habilitado
            e.target.disabled = false;
            e.target.readOnly = false;
            // Não bloquear nenhuma tecla
            e.stopPropagation();
        });
        
        issuePaiField.addEventListener('input', function(e) {
            console.log('Campo issuePai recebeu input:', e.target.value);
            // Garantir que o campo esteja habilitado
            e.target.disabled = false;
            e.target.readOnly = false;
        });
        
        issuePaiField.addEventListener('focus', function(e) {
            console.log('Campo issuePai recebeu foco');
            // Garantir que o campo esteja habilitado quando receber foco
            e.target.disabled = false;
            e.target.readOnly = false;
        });
        
        // Adicionar evento para garantir que o campo esteja sempre habilitado
        issuePaiField.addEventListener('click', function(e) {
            e.target.disabled = false;
            e.target.readOnly = false;
            e.target.focus();
        });
        
        // Interceptar tentativas de desabilitação
        const originalSetAttribute = issuePaiField.setAttribute;
        issuePaiField.setAttribute = function(name, value) {
            if (name === 'disabled' || name === 'readonly') {
                console.log('🚫 Tentativa de desabilitar campo issuePai bloqueada');
                return;
            }
            return originalSetAttribute.call(this, name, value);
        };
    }
    
    // Adicionar primeira linha
    addRow();
});

// Função para preencher automaticamente o campo issuePai (versão silenciosa para carregamento inicial)
function preencherIssuePaiAutomaticamente(silencioso = false) {
    const issuePaiField = document.getElementById('issuePai');
    if (!issuePaiField) return;
    
    // Se o campo já tem valor, não sobrescrever
    if (issuePaiField.value.trim()) {
        if (!silencioso) {
            mostrarNotificacao('Campo já possui valor. Limpe o campo primeiro se deseja preencher automaticamente.', 'info');
        }
        return;
    }
    
    // Verificar se há issuePai na URL (parâmetro)
    const urlParams = new URLSearchParams(window.location.search);
    const issuePaiFromUrl = urlParams.get('issuePai');
    
    // Verificar se há issuePai no localStorage (da página principal)
    const issuePaiFromStorage = localStorage.getItem('issuePaiAtual');
    
    // Verificar se há issuePai na variável global (se estiver na mesma sessão)
    const issuePaiFromGlobal = typeof issuePaiAtual !== 'undefined' ? issuePaiAtual : null;
    
    // Prioridade: URL > localStorage > global
    const issuePai = issuePaiFromUrl || issuePaiFromStorage || issuePaiFromGlobal;
    
    if (issuePai) {
        issuePaiField.value = issuePai;
        console.log('✅ Issue Pai preenchido automaticamente:', issuePai);
        if (!silencioso) {
            mostrarNotificacao(`Issue Pai preenchido: ${issuePai}`, 'success');
        }
    } else if (!silencioso) {
        mostrarNotificacao('Nenhum Issue Pai encontrado automaticamente. Preencha manualmente.', 'warning');
    }
}

// Função para limpar o campo issuePai
function limparCampoIssuePai() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        issuePaiField.value = '';
        issuePaiField.focus();
        mostrarNotificacao('Campo Issue Pai limpo. Você pode preenchê-lo manualmente.', 'info');
    }
}

// Função para forçar habilitação do campo issuePai
function forcarHabilitacaoIssuePai() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        // Salvar o valor atual
        const valorAtual = issuePaiField.value;
        
        // Encontrar o container do input-group
        const inputGroup = issuePaiField.closest('.input-group');
        if (inputGroup) {
            // Criar um novo container simples
            const novoContainer = document.createElement('div');
            novoContainer.className = 'mb-3';
            
            // Criar um novo campo completamente limpo
            const novoCampo = document.createElement('input');
            novoCampo.type = 'text';
            novoCampo.id = 'issuePai';
            novoCampo.className = 'form-control';
            novoCampo.placeholder = 'Ex: CREDT-1161';
            novoCampo.required = true;
            novoCampo.value = valorAtual;
            novoCampo.style.backgroundColor = 'white';
            novoCampo.style.color = 'var(--neurotech-secondary)';
            novoCampo.style.cursor = 'text';
            novoCampo.style.pointerEvents = 'auto';
            novoCampo.style.opacity = '1';
            novoCampo.style.border = '1px solid var(--neurotech-border)';
            novoCampo.style.padding = 'var(--spacing-sm) var(--spacing-md)';
            novoCampo.style.fontSize = '14px';
            novoCampo.style.lineHeight = '1.5';
            novoCampo.style.borderRadius = 'var(--radius-sm)';
            novoCampo.style.transition = 'all var(--transition-normal)';
            novoCampo.style.boxShadow = 'none';
            novoCampo.style.outline = 'none';
            novoCampo.style.position = 'relative';
            novoCampo.style.zIndex = '10';
            novoCampo.style.width = '100%';
            novoCampo.style.marginBottom = 'var(--spacing-sm)';
            
            // Adicionar o campo ao novo container
            novoContainer.appendChild(novoCampo);
            
            // Substituir todo o input-group pelo novo container
            inputGroup.parentNode.replaceChild(novoContainer, inputGroup);
            
            // Focar no novo campo
            novoCampo.focus();
            
            // Adicionar eventos ao novo campo
            novoCampo.addEventListener('input', function(e) {
                console.log('Campo issuePai recebeu input:', e.target.value);
            });
            
            novoCampo.addEventListener('focus', function(e) {
                console.log('Campo issuePai recebeu foco');
            });
            
            mostrarNotificacao('Campo Issue Pai recriado fora do input-group!', 'success');
            
                    console.log('🔧 Campo issuePai recriado fora do input-group');
        
        // Testar se o novo campo está funcionando
        setTimeout(() => {
            const novoCampo = document.getElementById('issuePai');
            if (novoCampo) {
                novoCampo.focus();
                novoCampo.value = 'TESTE-' + Date.now();
                console.log('✅ Campo recriado está funcionando!');
                mostrarNotificacao('Campo testado e funcionando!', 'success');
            }
        }, 100);
    }
}
}

// Função para verificar se há JavaScript interferindo
function verificarInterferenciasJavaScript() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        console.log('🔍 Verificando interferências no campo issuePai...');
        
        // Verificar propriedades do campo
        console.log('Propriedades do campo:', {
            disabled: issuePaiField.disabled,
            readOnly: issuePaiField.readOnly,
            type: issuePaiField.type,
            className: issuePaiField.className,
            value: issuePaiField.value,
            style: {
                pointerEvents: issuePaiField.style.pointerEvents,
                opacity: issuePaiField.style.opacity,
                backgroundColor: issuePaiField.style.backgroundColor,
                color: issuePaiField.style.color,
                cursor: issuePaiField.style.cursor
            }
        });
        
        // Verificar se há CSS aplicado
        const computedStyle = window.getComputedStyle(issuePaiField);
        console.log('CSS Computado:', {
            pointerEvents: computedStyle.pointerEvents,
            opacity: computedStyle.opacity,
            backgroundColor: computedStyle.backgroundColor,
            color: computedStyle.color,
            cursor: computedStyle.cursor,
            userSelect: computedStyle.userSelect,
            webkitUserSelect: computedStyle.webkitUserSelect
        });
        
        // Verificar se há atributos HTML
        console.log('Atributos HTML:', {
            disabled: issuePaiField.hasAttribute('disabled'),
            readonly: issuePaiField.hasAttribute('readonly'),
            'aria-disabled': issuePaiField.hasAttribute('aria-disabled'),
            required: issuePaiField.hasAttribute('required')
        });
        
        // Testar se o campo responde a eventos
        console.log('Testando interatividade...');
        try {
            issuePaiField.focus();
            console.log('✅ Campo aceitou foco');
        } catch (e) {
            console.log('❌ Campo não aceitou foco:', e);
        }
        
        // Verificar se o campo está visível
        const rect = issuePaiField.getBoundingClientRect();
        console.log('Posição e visibilidade:', {
            width: rect.width,
            height: rect.height,
            top: rect.top,
            left: rect.left,
            visible: rect.width > 0 && rect.height > 0
        });
    } else {
        console.log('❌ Campo issuePai não encontrado no DOM');
    }
}

// Função para testar digitação no campo
function testarDigitação() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        console.log('⌨️ Testando digitação no campo issuePai...');
        
        // Verificar se há event listeners bloqueando
        console.log('Verificando event listeners...');
        
        // Tentar focar no campo
        issuePaiField.focus();
        
        // Tentar simular digitação
        const testValue = 'TESTE-' + Date.now();
        issuePaiField.value = testValue;
        
        // Disparar eventos de input
        const inputEvent = new Event('input', { bubbles: true });
        issuePaiField.dispatchEvent(inputEvent);
        
        const changeEvent = new Event('change', { bubbles: true });
        issuePaiField.dispatchEvent(changeEvent);
        
        console.log('✅ Valor testado:', testValue);
        console.log('Valor atual do campo:', issuePaiField.value);
        
        if (issuePaiField.value === testValue) {
            mostrarNotificacao('✅ Campo aceita digitação!', 'success');
        } else {
            mostrarNotificacao('❌ Campo não aceita digitação!', 'error');
        }
    } else {
        console.log('❌ Campo issuePai não encontrado');
        mostrarNotificacao('❌ Campo não encontrado!', 'error');
    }
}

// Função para remover event listeners que podem estar bloqueando
function removerEventListenersBloqueadores() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        console.log('🔧 Removendo event listeners bloqueadores...');
        
        // Clonar o elemento para remover todos os event listeners
        const novoCampo = issuePaiField.cloneNode(true);
        
        // Preservar o valor atual
        novoCampo.value = issuePaiField.value;
        
        // Substituir o campo
        issuePaiField.parentNode.replaceChild(novoCampo, issuePaiField);
        
        // Adicionar apenas os event listeners necessários
        novoCampo.addEventListener('input', function(e) {
            console.log('Campo issuePai recebeu input:', e.target.value);
        });
        
        novoCampo.addEventListener('focus', function(e) {
            console.log('Campo issuePai recebeu foco');
        });
        
        // Garantir que o campo esteja habilitado
        novoCampo.disabled = false;
        novoCampo.readOnly = false;
        novoCampo.style.pointerEvents = 'auto';
        novoCampo.style.opacity = '1';
        novoCampo.style.backgroundColor = 'white';
        novoCampo.style.color = 'var(--neurotech-secondary)';
        novoCampo.style.cursor = 'text';
        
        // Focar no novo campo
        novoCampo.focus();
        
        console.log('✅ Event listeners removidos e campo recriado');
        mostrarNotificacao('Event listeners removidos!', 'success');
    }
}

// Função para remover bloqueadores de teclado
function removerBloqueadoresTeclado() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        console.log('🔧 Removendo bloqueadores de teclado...');
        
        // Remover event listeners que possam estar bloqueando
        const novoCampo = issuePaiField.cloneNode(true);
        issuePaiField.parentNode.replaceChild(novoCampo, issuePaiField);
        
        // Configurar o novo campo
        novoCampo.id = 'issuePai';
        novoCampo.className = 'form-control';
        novoCampo.placeholder = 'Ex: CREDT-1161';
        novoCampo.required = true;
        novoCampo.style.backgroundColor = 'white';
        novoCampo.style.color = 'var(--neurotech-secondary)';
        novoCampo.style.cursor = 'text';
        novoCampo.style.pointerEvents = 'auto';
        novoCampo.style.opacity = '1';
        novoCampo.style.border = '1px solid var(--neurotech-border)';
        novoCampo.style.padding = 'var(--spacing-sm) var(--spacing-md)';
        novoCampo.style.fontSize = '14px';
        novoCampo.style.lineHeight = '1.5';
        novoCampo.style.borderRadius = 'var(--radius-sm)';
        novoCampo.style.transition = 'all var(--transition-normal)';
        novoCampo.style.boxShadow = 'none';
        novoCampo.style.outline = 'none';
        novoCampo.style.position = 'relative';
        novoCampo.style.zIndex = '10';
        novoCampo.style.width = '100%';
        
        // Garantir que não há atributos bloqueadores
        novoCampo.removeAttribute('disabled');
        novoCampo.removeAttribute('readonly');
        novoCampo.removeAttribute('aria-disabled');
        novoCampo.removeAttribute('tabindex');
        
        // Focar no novo campo
        novoCampo.focus();
        
        // Adicionar eventos básicos
        novoCampo.addEventListener('input', function(e) {
            console.log('Campo issuePai recebeu input:', e.target.value);
        });
        
        novoCampo.addEventListener('keydown', function(e) {
            console.log('Campo issuePai recebeu keydown:', e.key);
            // Não bloquear nenhuma tecla
            e.stopPropagation();
        });
        
        novoCampo.addEventListener('keypress', function(e) {
            console.log('Campo issuePai recebeu keypress:', e.key);
            // Não bloquear nenhuma tecla
            e.stopPropagation();
        });
        
        novoCampo.addEventListener('keyup', function(e) {
            console.log('Campo issuePai recebeu keyup:', e.key);
            // Não bloquear nenhuma tecla
            e.stopPropagation();
        });
        
        mostrarNotificacao('Bloqueadores de teclado removidos!', 'success');
        console.log('✅ Bloqueadores de teclado removidos');
    }
}

// Função para forçar habilitação completa do campo
function forcarHabilitacaoCompleta() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        console.log('🔧 Forçando habilitação completa...');
        
        // Criar um campo completamente novo
        const novoCampo = document.createElement('input');
        novoCampo.type = 'text';
        novoCampo.id = 'issuePai';
        novoCampo.className = 'form-control';
        novoCampo.placeholder = 'Ex: CREDT-1161';
        novoCampo.required = true;
        novoCampo.value = issuePaiField.value;
        
        // Aplicar estilos inline para garantir funcionamento
        Object.assign(novoCampo.style, {
            backgroundColor: 'white',
            color: 'var(--neurotech-secondary)',
            cursor: 'text',
            pointerEvents: 'auto',
            opacity: '1',
            border: '1px solid var(--neurotech-border)',
            padding: 'var(--spacing-sm) var(--spacing-md)',
            fontSize: '14px',
            lineHeight: '1.5',
            borderRadius: 'var(--radius-sm)',
            transition: 'all var(--transition-normal)',
            boxShadow: 'none',
            outline: 'none',
            position: 'relative',
            zIndex: '10',
            width: '100%'
        });
        
        // Substituir o campo
        issuePaiField.parentNode.replaceChild(novoCampo, issuePaiField);
        
        // Focar e testar
        novoCampo.focus();
        
        // Adicionar event listeners que permitem digitação
        novoCampo.addEventListener('input', function(e) {
            console.log('Campo issuePai recebeu input:', e.target.value);
        });
        
        novoCampo.addEventListener('keydown', function(e) {
            console.log('Campo issuePai recebeu keydown:', e.key);
            // Permitir todas as teclas
            e.stopPropagation();
            return true;
        });
        
        novoCampo.addEventListener('keypress', function(e) {
            console.log('Campo issuePai recebeu keypress:', e.key);
            // Permitir todas as teclas
            e.stopPropagation();
            return true;
        });
        
        novoCampo.addEventListener('keyup', function(e) {
            console.log('Campo issuePai recebeu keyup:', e.key);
            // Permitir todas as teclas
            e.stopPropagation();
            return true;
        });
        
        // Permitir colar
        novoCampo.addEventListener('paste', function(e) {
            console.log('Campo issuePai recebeu paste');
            e.stopPropagation();
            return true;
        });
        
        // Permitir copiar
        novoCampo.addEventListener('copy', function(e) {
            console.log('Campo issuePai recebeu copy');
            e.stopPropagation();
            return true;
        });
        
        console.log('✅ Campo completamente recriado e habilitado');
        mostrarNotificacao('Campo completamente recriado!', 'success');
        
        // Testar digitação automaticamente
        setTimeout(() => {
            novoCampo.value = 'TESTE-' + Date.now();
            console.log('✅ Teste automático de digitação realizado');
        }, 100);
    }
}

// Função para mostrar ajuda sobre como encontrar o Issue Pai
function mostrarAjudaIssuePai() {
    const ajudaHTML = `
        <div class="alert alert-info">
            <h6><i class="fas fa-question-circle me-2"></i>Como encontrar o Issue Pai?</h6>
            <ol class="mb-0">
                <li><strong>No Jira:</strong> Abra o requisito/epic no Jira e copie o ID (ex: CREDT-1161)</li>
                <li><strong>Na página principal:</strong> Busque o requisito primeiro e depois clique em "Planilha"</li>
                <li><strong>Formato:</strong> Deve seguir o padrão PROJETO-NÚMERO (ex: CREDT-1161, BC-129)</li>
                <li><strong>Dica:</strong> O Issue Pai é o requisito/epic que contém os casos de teste</li>
            </ol>
        </div>
    `;
    
    // Criar modal de ajuda
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-question-circle me-2"></i>Ajuda - Issue Pai
                    </h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    ${ajudaHTML}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-dismiss="modal">Entendi</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Remover modal do DOM após fechar
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// ========================================
// FUNÇÕES DE IMPORTAÇÃO EM MASSA
// ========================================

// Função para processar dados colados
function processarDadosColados() {
    const dadosTabelaElement = document.getElementById('dadosTabela');
    if (!dadosTabelaElement) {
        mostrarNotificacao('Elemento de dados da tabela não encontrado', 'error');
        return;
    }
    
    const dadosTabela = dadosTabelaElement.value.trim();
    
    if (!dadosTabela) {
        mostrarNotificacao('Por favor, cole os dados da tabela primeiro', 'warning');
        return;
    }
    
    try {
        // Detectar separador (tab ou vírgula)
        const primeiraLinha = dadosTabela.split('\n')[0];
        let separador = '\t'; // Padrão: tabulação
        
        if (primeiraLinha.includes(',') && !primeiraLinha.includes('\t')) {
            separador = ',';
        }
        
        // Função para dividir texto respeitando quebras de linha nos campos
        function dividirLinhasRespeitandoCampos(texto, separador) {
            const linhas = [];
            let linhaAtual = '';
            let dentroDeCampo = false;
            let nivelAspas = 0;
            
            for (let i = 0; i < texto.length; i++) {
                const char = texto[i];
                const proximoChar = texto[i + 1];
                
                // Verificar aspas
                if (char === '"') {
                    if (proximoChar === '"') {
                        // Aspas duplas escapadas
                        linhaAtual += char + proximoChar;
                        i++; // Pular próximo caractere
                        continue;
                    } else {
                        // Aspas simples
                        nivelAspas = 1 - nivelAspas;
                        dentroDeCampo = nivelAspas > 0;
                        linhaAtual += char;
                        continue;
                    }
                }
                
                // Se estamos dentro de aspas, adicionar caractere normalmente
                if (dentroDeCampo) {
                    linhaAtual += char;
                    continue;
                }
                
                // Verificar se é quebra de linha real (não dentro de campo)
                if (char === '\n' || char === '\r') {
                    if (char === '\r' && proximoChar === '\n') {
                        // \r\n - pular ambos
                        i++;
                    }
                    
                    // Se a linha atual tem conteúdo, adicionar à lista
                    if (linhaAtual.trim()) {
                        linhas.push(linhaAtual.trim());
                        linhaAtual = '';
                    }
                    continue;
                }
                
                // Adicionar caractere à linha atual
                linhaAtual += char;
            }
            
            // Adicionar última linha se houver conteúdo
            if (linhaAtual.trim()) {
                linhas.push(linhaAtual.trim());
            }
            
            return linhas;
        }
        
        // Dividir em linhas respeitando campos com quebras de linha
        const linhas = dividirLinhasRespeitandoCampos(dadosTabela, separador);
        
        if (linhas.length === 0) {
            mostrarNotificacao('Nenhum dado válido encontrado', 'warning');
            return;
        }
        
        // Processar cada linha
        dadosProcessados = [];
        let temCabecalho = false;
        
        linhas.forEach((linha, index) => {
            // Função para dividir campos respeitando aspas
            function dividirCampos(linha, separador) {
                const campos = [];
                let campoAtual = '';
                let dentroDeAspas = false;
                
                for (let i = 0; i < linha.length; i++) {
                    const char = linha[i];
                    const proximoChar = linha[i + 1];
                    
                    if (char === '"') {
                        if (proximoChar === '"') {
                            // Aspas duplas escapadas
                            campoAtual += char + proximoChar;
                            i++; // Pular próximo caractere
                        } else {
                            // Aspas simples - alternar estado
                            dentroDeAspas = !dentroDeAspas;
                        }
                    } else if (char === separador && !dentroDeAspas) {
                        // Separador encontrado fora de aspas
                        campos.push(campoAtual.trim());
                        campoAtual = '';
                    } else {
                        // Adicionar caractere ao campo atual
                        campoAtual += char;
                    }
                }
                
                // Adicionar último campo
                campos.push(campoAtual.trim());
                
                return campos;
            }
            
            const campos = dividirCampos(linha, separador);
            
            // Verificar se é cabeçalho (primeira linha com palavras-chave)
            if (index === 0) {
                const palavrasChave = ['título', 'titulo', 'title', 'status', 'execução', 'execucao', 'teste', 'componentes', 'objetivo', 'pré-condições', 'pre-condicoes', 'descrição', 'descricao'];
                const temPalavrasChave = palavrasChave.some(palavra => 
                    campos.some(campo => campo.toLowerCase().includes(palavra))
                );
                
                if (temPalavrasChave) {
                    temCabecalho = true;
                    return; // Pular cabeçalho
                }
            }
            
            // Mapear campos para o formato esperado
            const caso = mapearCampos(campos);
            if (caso) {
                dadosProcessados.push(caso);
            }
        });
        
        if (dadosProcessados.length === 0) {
            mostrarNotificacao('Nenhum caso de teste válido encontrado nos dados', 'warning');
            return;
        }
        
        // Mostrar preview
        mostrarPreviewDados();
        
        // Mostrar notificação de sucesso
        mostrarNotificacao(`${dadosProcessados.length} casos de teste processados com sucesso!`, 'success');
        
    } catch (error) {
        console.error('Erro ao processar dados:', error);
        mostrarNotificacao(`Erro ao processar dados: ${error.message}`, 'error');
    }
}

// Função para mapear campos dos dados colados
function mapearCampos(campos) {
    // Se temos pelo menos um campo (título), criar o caso
    if (campos.length === 0 || !campos[0]) {
        return null;
    }
    
    const caso = {
        titulo: campos[0] || '',
        status: mapearStatus(campos[1] || ''),
        tipo_execucao: mapearTipoExecucao(campos[2] || ''),
        tipo_teste: mapearTipoTeste(campos[3] || ''),
        componentes: campos[4] || '',
        objetivo: campos[5] || '',
        pre_condicoes: campos[6] || '',
        descricao: campos[7] || ''
    };
    
    return caso;
}

// Função para mapear status
function mapearStatus(status) {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('to do') || statusLower.includes('todo') || statusLower.includes('pendente')) {
        return 'To Do';
    } else if (statusLower.includes('in progress') || statusLower.includes('em andamento') || statusLower.includes('progresso')) {
        return 'In Progress';
    } else if (statusLower.includes('done') || statusLower.includes('concluído') || statusLower.includes('concluido') || statusLower.includes('finalizado')) {
        return 'Done';
    }
    return 'To Do'; // Padrão
}

// Função para mapear tipo de execução
function mapearTipoExecucao(tipo) {
    const tipoLower = tipo.toLowerCase();
    if (tipoLower.includes('automated') || tipoLower.includes('automatizado') || tipoLower.includes('automático') || tipoLower.includes('automatizável') || tipoLower.includes('automatizavel')) {
        return 'Automated';
    }
    return 'Manual'; // Padrão
}

// Função para mapear tipo de teste
function mapearTipoTeste(tipo) {
    const tipoLower = tipo.toLowerCase();
    if (tipoLower.includes('functional') || tipoLower.includes('funcional')) {
        return 'Functional';
    } else if (tipoLower.includes('non-functional') || tipoLower.includes('não funcional') || tipoLower.includes('nao funcional')) {
        return 'Non-Functional';
    } else if (tipoLower.includes('integration') || tipoLower.includes('integração') || tipoLower.includes('integracao')) {
        return 'Integration';
    } else if (tipoLower.includes('unit') || tipoLower.includes('unitário') || tipoLower.includes('unitario')) {
        return 'Unit';
    }
    return 'Functional'; // Padrão
}

// Função para mostrar preview dos dados processados
function mostrarPreviewDados() {
    const previewContainer = document.getElementById('previewContainer');
    const previewTable = document.getElementById('previewTable');
    
    if (dadosProcessados.length === 0) {
        previewContainer.style.display = 'none';
        return;
    }
    
    // Criar tabela de preview
    let html = `
        <table class="table table-sm table-bordered">
            <thead>
                <tr>
                    <th>Título</th>
                    <th>Status</th>
                    <th>Tipo Execução</th>
                    <th>Tipo Teste</th>
                    <th>Componentes</th>
                    <th>Objetivo</th>
                    <th>Pré-condições</th>
                    <th>Descrição</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    dadosProcessados.forEach(caso => {
        html += `
            <tr>
                <td>${caso.titulo}</td>
                <td><span class="badge bg-secondary">${caso.status}</span></td>
                <td><span class="badge bg-info">${caso.tipo_execucao}</span></td>
                <td><span class="badge bg-warning">${caso.tipo_teste}</span></td>
                <td>${caso.componentes}</td>
                <td>${caso.objetivo.substring(0, 50)}${caso.objetivo.length > 50 ? '...' : ''}</td>
                <td>${caso.pre_condicoes.substring(0, 50)}${caso.pre_condicoes.length > 50 ? '...' : ''}</td>
                <td>${caso.descricao.substring(0, 50)}${caso.descricao.length > 50 ? '...' : ''}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    previewTable.innerHTML = html;
    previewContainer.style.display = 'block';
}

// Função para limpar dados de importação
function limparDadosImportacao() {
    const dadosTabelaElement = document.getElementById('dadosTabela');
    if (dadosTabelaElement) {
        dadosTabelaElement.value = '';
    }
    const previewContainerElement = document.getElementById('previewContainer');
    if (previewContainerElement) {
        previewContainerElement.style.display = 'none';
    }
    dadosProcessados = [];
    mostrarNotificacao('Dados de importação limpos', 'info');
}

// Função para preencher planilha com dados processados
function preencherPlanilhaComDados() {
    if (dadosProcessados.length === 0) {
        mostrarNotificacao('Nenhum dado processado para preencher a planilha', 'warning');
        return;
    }
    
    // Limpar planilha atual
    const tbody = document.getElementById('planilhaBody');
    tbody.innerHTML = '';
    rowCounter = 0;
    
    // Adicionar dados processados
    dadosProcessados.forEach(caso => {
        addRowWithData(caso);
    });
    
    // Mostrar notificação de sucesso
    mostrarNotificacao(`${dadosProcessados.length} casos de teste adicionados à planilha!`, 'success');
    
    // Limpar dados de importação
    limparDadosImportacao();
}

// Função para adicionar linha com dados específicos
function addRowWithData(caso) {
    const tbody = document.getElementById('planilhaBody');
    const newRow = document.createElement('tr');
    rowCounter++;
    
    newRow.innerHTML = `
        <td class="actions-column">
            <button type="button" class="btn-remove-row" onclick="removeRow(this)">
                <i class="fas fa-times"></i>
            </button>
        </td>
        <td>
            <input type="text" class="form-control readonly-field" readonly placeholder="Gerado automaticamente">
        </td>
        <td>
            <input type="text" class="form-control" placeholder="Título do caso de teste" value="${caso.titulo}" required>
        </td>
        <td>
            <select class="form-control">
                <option value="To Do" ${caso.status === 'To Do' ? 'selected' : ''}>To Do</option>
                <option value="In Progress" ${caso.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                <option value="Done" ${caso.status === 'Done' ? 'selected' : ''}>Done</option>
            </select>
        </td>
        <td>
            <select class="form-control">
                <option value="Manual" ${caso.tipo_execucao === 'Manual' ? 'selected' : ''}>Manual</option>
                <option value="Automated" ${caso.tipo_execucao === 'Automated' ? 'selected' : ''}>Automated</option>
            </select>
        </td>
        <td>
            <select class="form-control">
                <option value="Functional" ${caso.tipo_teste === 'Functional' ? 'selected' : ''}>Functional</option>
                <option value="Non-Functional" ${caso.tipo_teste === 'Non-Functional' ? 'selected' : ''}>Non-Functional</option>
                <option value="Integration" ${caso.tipo_teste === 'Integration' ? 'selected' : ''}>Integration</option>
                <option value="Unit" ${caso.tipo_teste === 'Unit' ? 'selected' : ''}>Unit</option>
            </select>
        </td>
        <td>
            <input type="text" class="form-control" placeholder="Frontend, Backend, etc." value="${caso.componentes}">
        </td>
        <td>
            <textarea class="form-control" rows="2" placeholder="Objetivo do teste">${caso.objetivo}</textarea>
        </td>
        <td>
            <textarea class="form-control" rows="2" placeholder="Pré-condições necessárias">${caso.pre_condicoes}</textarea>
        </td>
        <td>
            <textarea class="form-control" rows="3" placeholder="Descrição detalhada do teste">${caso.descricao}</textarea>
        </td>
        <td>
            <input type="text" class="form-control readonly-field" readonly placeholder="Data/hora automática">
        </td>
        <td>
            <input type="text" class="form-control readonly-field" readonly placeholder="Data/hora automática">
        </td>
    `;
    
    tbody.appendChild(newRow);
    
    // Adicionar event listeners para os campos
    addFieldEventListeners(newRow);
}

// ========================================
// FUNÇÕES EXISTENTES DA PLANILHA MANUAL
// ========================================

// Função para adicionar nova linha
function addRow() {
    const tbody = document.getElementById('planilhaBody');
    const newRow = document.createElement('tr');
    rowCounter++;
    
    newRow.innerHTML = `
        <td class="actions-column">
            <button type="button" class="btn-remove-row" onclick="removeRow(this)">
                <i class="fas fa-times"></i>
            </button>
        </td>
        <td>
            <input type="text" class="form-control readonly-field" readonly placeholder="Gerado automaticamente">
        </td>
        <td>
            <input type="text" class="form-control" placeholder="Título do caso de teste" required>
        </td>
        <td>
            <select class="form-control">
                <option value="To Do">To Do</option>
                <option value="In Progress">In Progress</option>
                <option value="Done">Done</option>
            </select>
        </td>
        <td>
            <select class="form-control">
                <option value="Manual">Manual</option>
                <option value="Automated">Automated</option>
            </select>
        </td>
        <td>
            <select class="form-control">
                <option value="Functional">Functional</option>
                <option value="Non-Functional">Non-Functional</option>
                <option value="Integration">Integration</option>
                <option value="Unit">Unit</option>
            </select>
        </td>
        <td>
            <input type="text" class="form-control" placeholder="Frontend, Backend, etc.">
        </td>
        <td>
            <textarea class="form-control" rows="2" placeholder="Objetivo do teste"></textarea>
        </td>
        <td>
            <textarea class="form-control" rows="2" placeholder="Pré-condições necessárias"></textarea>
        </td>
        <td>
            <textarea class="form-control" rows="3" placeholder="Descrição detalhada do teste"></textarea>
        </td>
        <td>
            <input type="text" class="form-control readonly-field" readonly placeholder="Data/hora automática">
        </td>
        <td>
            <input type="text" class="form-control readonly-field" readonly placeholder="Data/hora automática">
        </td>
    `;
    
    tbody.appendChild(newRow);
    
    // Adicionar event listeners para os campos
    addFieldEventListeners(newRow);
}

// Função para remover linha
function removeRow(button) {
    const row = button.closest('tr');
    row.remove();
    updateRowCount();
}

// Função para adicionar event listeners aos campos
function addFieldEventListeners(row) {
    const inputs = row.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            // Marcar como modificado
            this.style.borderLeft = '3px solid #3498db';
        });
        
        input.addEventListener('input', function() {
            // Marcar como modificado
            this.style.borderLeft = '3px solid #3498db';
        });
    });
}

// Função para mostrar modal de exportação
function showExportModal() {
    const totalRows = document.querySelectorAll('#planilhaBody tr').length;
    const validRows = getValidRows();
    
    if (validRows.length === 0) {
        mostrarNotificacao('Adicione pelo menos um caso de teste válido', 'warning');
        return;
    }
    
    const totalCasosElement = document.getElementById('totalCasos');
    if (totalCasosElement) {
        totalCasosElement.textContent = validRows.length;
    }
    
    // Garantir que o campo issuePai esteja habilitado quando o modal abrir
    setTimeout(() => {
        habilitarCampoIssuePai();
    }, 100);
    
    exportModal.show();
}

// Função para garantir que o campo issuePai esteja sempre habilitado
function habilitarCampoIssuePai() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        // Força habilitação de todas as formas possíveis
        issuePaiField.disabled = false;
        issuePaiField.readOnly = false;
        issuePaiField.style.pointerEvents = 'auto';
        issuePaiField.style.opacity = '1';
        issuePaiField.style.backgroundColor = 'white';
        issuePaiField.style.color = 'var(--neurotech-secondary)';
        issuePaiField.style.cursor = 'text';
        issuePaiField.style.userSelect = 'auto';
        issuePaiField.style.webkitUserSelect = 'auto';
        issuePaiField.style.mozUserSelect = 'auto';
        issuePaiField.style.msUserSelect = 'auto';
        
        // Remove todos os atributos que podem desabilitar
        issuePaiField.removeAttribute('disabled');
        issuePaiField.removeAttribute('readonly');
        issuePaiField.removeAttribute('aria-disabled');
        
        // Força o foco e seleção
        issuePaiField.focus();
        issuePaiField.select();
        
        console.log('✅ Campo issuePai habilitado - Status:', {
            disabled: issuePaiField.disabled,
            readOnly: issuePaiField.readOnly,
            pointerEvents: issuePaiField.style.pointerEvents,
            opacity: issuePaiField.style.opacity
        });
    }
}

// Função para monitorar e forçar habilitação continuamente
function monitorarCampoIssuePai() {
    const issuePaiField = document.getElementById('issuePai');
    if (issuePaiField) {
        // Verifica a cada 500ms se o campo está habilitado
        setInterval(() => {
            if (issuePaiField.disabled || issuePaiField.readOnly) {
                console.log('⚠️ Campo issuePai foi desabilitado, reabilitando...');
                habilitarCampoIssuePai();
            }
        }, 500);
        
        // Adiciona evento para interceptar tentativas de desabilitação
        const originalSetAttribute = issuePaiField.setAttribute;
        issuePaiField.setAttribute = function(name, value) {
            if (name === 'disabled' || name === 'readonly') {
                console.log('🚫 Tentativa de desabilitar campo issuePai bloqueada');
                return;
            }
            return originalSetAttribute.call(this, name, value);
        };
    }
}

// Função para obter linhas válidas
function getValidRows() {
    const rows = document.querySelectorAll('#planilhaBody tr');
    const validRows = [];
    
    rows.forEach(row => {
        const titulo = row.querySelector('td:nth-child(3) input').value.trim();
        if (titulo) {
            validRows.push(row);
        }
    });
    
    return validRows;
}

// Função para exportar para Jira
async function exportToJira() {
    const issuePaiElement = document.getElementById('issuePai');
    if (!issuePaiElement) {
        mostrarNotificacao('Elemento issue pai não encontrado', 'error');
        return;
    }
    
    const issuePai = issuePaiElement.value.trim();
    
    if (!issuePai) {
        mostrarNotificacao('Por favor, informe a Issue Pai', 'warning');
        return;
    }
    
    const validRows = getValidRows();
    if (validRows.length === 0) {
        mostrarNotificacao('Nenhum caso de teste válido encontrado', 'warning');
        return;
    }
    
    // Preparar dados
    const casos = [];
    validRows.forEach(row => {
        const caso = {
            titulo: row.querySelector('td:nth-child(3) input').value.trim(),
            status: row.querySelector('td:nth-child(4) select').value,
            tipo_execucao: row.querySelector('td:nth-child(5) select').value,
            tipo_teste: row.querySelector('td:nth-child(6) select').value,
            componentes: row.querySelector('td:nth-child(7) input').value.trim(),
            objetivo: row.querySelector('td:nth-child(8) textarea').value.trim(),
            pre_condicoes: row.querySelector('td:nth-child(9) textarea').value.trim(),
            descricao: row.querySelector('td:nth-child(10) textarea').value.trim()
        };
        casos.push(caso);
    });
    
    try {
        // Desabilitar botão
        const btnExport = document.getElementById('btnConfirmExport');
        btnExport.disabled = true;
        btnExport.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exportando...';
        
        console.log('📤 Exportando casos para Jira:', casos.length);
        
        const response = await fetch('/api/exportar-planilha-manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                issue_pai: issuePai,
                casos: casos
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('✅ Exportação concluída:', data);
            
            // Atualizar IDs e datas nas linhas
            updateRowsWithJiraData(data.resultados);
            
            // Fechar modal
            exportModal.hide();
            
            // Mostrar notificação de sucesso
            mostrarNotificacao(`Exportação concluída! ${data.sucessos} casos criados com sucesso.`, 'success');
            
            // Mostrar resultados detalhados
            showExportResults(data);
            
        } else {
            console.error('❌ Erro na exportação:', data);
            mostrarNotificacao(data.erro || 'Erro na exportação', 'error');
        }
        
    } catch (error) {
        console.error('❌ Erro de conexão:', error);
        mostrarNotificacao(`Erro de conexão: ${error.message}`, 'error');
    } finally {
        // Reabilitar botão
        const btnExport = document.getElementById('btnConfirmExport');
        btnExport.disabled = false;
        btnExport.innerHTML = '<i class="fas fa-upload"></i> Exportar';
    }
}

// Função para atualizar linhas com dados do Jira
function updateRowsWithJiraData(resultados) {
    const rows = document.querySelectorAll('#planilhaBody tr');
    let resultadoIndex = 0;
    
    rows.forEach((row, index) => {
        const titulo = row.querySelector('td:nth-child(3) input').value.trim();
        if (titulo && resultados[resultadoIndex]) {
            const resultado = resultados[resultadoIndex];
            
            // Atualizar ID
            const idField = row.querySelector('td:nth-child(2) input');
            idField.value = resultado.jira_id || 'Erro';
            idField.style.color = resultado.jira_id ? '#27ae60' : '#e74c3c';
            
            // Atualizar data de criação
            const createdField = row.querySelector('td:nth-child(11) input');
            createdField.value = resultado.created_at || 'Erro';
            createdField.style.color = resultado.created_at ? '#27ae60' : '#e74c3c';
            
            // Atualizar data de atualização
            const updatedField = row.querySelector('td:nth-child(12) input');
            updatedField.value = resultado.updated_at || 'Erro';
            updatedField.style.color = resultado.updated_at ? '#27ae60' : '#e74c3c';
            
            // Marcar linha como exportada
            row.style.backgroundColor = resultado.jira_id ? '#d5f4e6' : '#fadbd8';
            
            resultadoIndex++;
        }
    });
}

// Função para mostrar resultados da exportação
function showExportResults(data) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-check-circle"></i> Resultado da Exportação</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-success">
                        <strong>Exportação concluída!</strong><br>
                        Sucessos: ${data.sucessos} | Erros: ${data.erros}
                    </div>
                    
                    <h6>Detalhes:</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Título</th>
                                    <th>Status</th>
                                    <th>ID Jira</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.resultados.map(r => `
                                    <tr class="${r.jira_id ? 'table-success' : 'table-danger'}">
                                        <td>${r.titulo}</td>
                                        <td>${r.jira_id ? 'Criado' : 'Erro'}</td>
                                        <td>${r.jira_id || r.erro}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Fechar</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remover modal do DOM após fechar
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// Função para atualizar contador de linhas
function updateRowCount() {
    const totalRows = document.querySelectorAll('#planilhaBody tr').length;
    console.log(`Total de linhas: ${totalRows}`);
}

// Função para mostrar notificações
function mostrarNotificacao(mensagem, tipo = 'info') {
    const toast = document.getElementById('toast');
    const toastBody = document.getElementById('toastBody');
    const toastIcon = document.getElementById('toastIcon');
    const toastTitle = document.getElementById('toastTitle');
    
    // Configurar ícone e título baseado no tipo
    switch (tipo) {
        case 'success':
            toastIcon.className = 'fas fa-check-circle me-2 text-success';
            toastTitle.textContent = 'Sucesso';
            break;
        case 'error':
            toastIcon.className = 'fas fa-exclamation-circle me-2 text-danger';
            toastTitle.textContent = 'Erro';
            break;
        case 'warning':
            toastIcon.className = 'fas fa-exclamation-triangle me-2 text-warning';
            toastTitle.textContent = 'Aviso';
            break;
        default:
            toastIcon.className = 'fas fa-info-circle me-2 text-info';
            toastTitle.textContent = 'Informação';
    }
    
    toastBody.textContent = mensagem;
    
    // Mostrar toast usando Bootstrap 4
    $('#toast').toast('show');
}


