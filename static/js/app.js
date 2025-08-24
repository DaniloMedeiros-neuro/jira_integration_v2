// Variáveis globais
let issuePaiAtual = '';
let casoTesteEditando = null;

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== APLICAÇÃO INICIADA ===');
    
    // Verificar se o Bootstrap está disponível
    if (typeof bootstrap !== 'undefined') {
        console.log('✅ Bootstrap carregado com sucesso');
    } else {
        console.error('❌ Bootstrap não encontrado!');
        alert('Erro: Bootstrap não foi carregado!');
        return;
    }
    
    // Permitir busca com Enter
    document.getElementById('requisitoPai').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            buscarRequisito();
        }
    });
    
    // Verificar se há um requisito na URL ao carregar a página
    verificarRequisitoNaURL();
    
    // Listener para mudanças na URL (navegação com botões voltar/avançar)
    window.addEventListener('popstate', function(event) {
        verificarRequisitoNaURL();
    });
    
    console.log('✅ Aplicação inicializada com sucesso');
});

// Função para buscar requisitos e seus casos de teste
async function buscarRequisito() {
    const requisitoPai = document.getElementById('requisitoPai').value.trim();
    
    if (!requisitoPai) {
        mostrarNotificacao('Por favor, digite o ID do requisito', 'warning');
        return;
    }
    
    // Atualizar URL com o ID do requisito
    const url = new URL(window.location);
    url.pathname = `/${requisitoPai}`;
    window.history.pushState({ requisito: requisitoPai }, '', url);
    
    await carregarCasosTeste(requisitoPai);
}

// Função para carregar casos de teste (separada da busca)
async function carregarCasosTeste(requisitoPai) {
    issuePaiAtual = requisitoPai;
    
    // Atualizar campo de busca
    document.getElementById('requisitoPai').value = requisitoPai;
    
    // Mostrar loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('listaCasos').innerHTML = '';
    document.getElementById('resultados').style.display = 'block';
    
    try {
        console.log('📡 Buscando requisito:', requisitoPai);
        
        const response = await fetch(`http://127.0.0.1:8081/api/casos-teste/${requisitoPai}`);
        console.log('📡 Resposta recebida:', response.status, response.statusText);
        
        const data = await response.json();
        console.log('📡 Dados recebidos:', data);
        
        if (response.ok) {
            console.log('✅ Requisito encontrado, exibindo casos de teste');
            exibirCasosTeste(data);
            // Mostrar botão de criar novo caso quando requisito é encontrado
            document.getElementById('btnNovoCaso').style.display = 'inline-block';
        } else {
            console.error('❌ Erro na resposta:', data);
            mostrarNotificacao(data.erro || 'Requisito não encontrado', 'error');
            document.getElementById('resultados').style.display = 'none';
            document.getElementById('btnNovoCaso').style.display = 'none';
        }
    } catch (error) {
        console.error('❌ Erro capturado:', error);
        mostrarNotificacao(`Erro de conexão: ${error.message}`, 'error');
        document.getElementById('resultados').style.display = 'none';
        document.getElementById('btnNovoCaso').style.display = 'none';
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// Função para verificar se há um requisito na URL
function verificarRequisitoNaURL() {
    const pathname = window.location.pathname;
    
    // Verificar se a URL tem um padrão de requisito (ex: /CREDT-1161)
    const requisitoMatch = pathname.match(/^\/([A-Z]+-\d+)$/);
    
    if (requisitoMatch) {
        const requisitoPai = requisitoMatch[1];
        console.log('🔍 Requisito encontrado na URL:', requisitoPai);
        carregarCasosTeste(requisitoPai);
    } else if (pathname === '/') {
        // Se estiver na home, limpar resultados
        document.getElementById('resultados').style.display = 'none';
        document.getElementById('requisitoPai').value = '';
        issuePaiAtual = '';
    }
}



// Função para exibir casos de teste
function exibirCasosTeste(data) {
    const listaCasos = document.getElementById('listaCasos');
    const totalCasos = document.getElementById('totalCasos');
    const btnPlanilha = document.getElementById('btnPlanilha');
    
    totalCasos.textContent = `${data.total_casos} caso(s) de teste`;
    
    if (data.casos_teste.length === 0) {
        btnPlanilha.style.display = 'none';
        document.getElementById('btnNovoCaso').style.display = 'inline-block'; // Mostrar botão para criar primeiro caso
        listaCasos.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h4>Nenhum caso de teste encontrado</h4>
                <p>Não foram encontrados casos de teste para o requisito ${data.issue_pai}</p>
                <button class="btn btn-primary" onclick="abrirModalCriar()">
                    <i class="fas fa-plus me-1"></i>
                    Criar Primeiro Caso de Teste
                </button>
            </div>
        `;
        return;
    }
    
    // Mostrar botões quando há casos de teste
    btnPlanilha.style.display = 'inline-block';
    
    const casosHTML = data.casos_teste.map(caso => criarHTMLCasoTeste(caso)).join('');
    listaCasos.innerHTML = casosHTML;
}

// Função para criar HTML de um caso de teste
function criarHTMLCasoTeste(caso) {
    const statusClass = getStatusClass(caso.status);
    const dataCriacao = formatarData(caso.criado_em);
    const dataAtualizacao = formatarData(caso.atualizado_em);
    const componentes = caso.componentes.join(', ') || 'N/A';
    
    return `
        <div class="caso-teste-item">
            <div class="caso-teste-header">
                <div>
                    <h5 class="caso-teste-titulo">${caso.titulo}</h5>
                    <span class="caso-teste-id">${caso.id}</span>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <span class="caso-teste-status ${statusClass}">${caso.status}</span>
                    <div class="caso-teste-acoes">
                        <button class="btn btn-sm btn-outline-primary" onclick="editarCasoTeste('${caso.id}')" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="excluirCasoTeste('${caso.id}', '${caso.titulo}')" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="caso-teste-meta">
                <span><i class="fas fa-calendar-plus"></i> Criado: ${dataCriacao}</span>
                <span><i class="fas fa-calendar-check"></i> Atualizado: ${dataAtualizacao}</span>
                <span><i class="fas fa-play"></i> Execução: ${caso.tipo_execucao}</span>
                <span><i class="fas fa-tag"></i> Tipo: ${caso.tipo_teste}</span>
                <span><i class="fas fa-puzzle-piece"></i> Componentes: ${componentes}</span>
            </div>
            
            ${caso.objetivo ? `<div><strong>Objetivo:</strong> ${caso.objetivo}</div>` : ''}
            ${caso.pre_condicoes ? `<div><strong>Pré-condições:</strong> ${caso.pre_condicoes}</div>` : ''}
            
            ${caso.descricao ? `
                <div class="caso-teste-descricao">
                    <strong>Descrição/Cenário:</strong><br>
                    ${caso.descricao}
                </div>
            ` : ''}
        </div>
    `;
}

// Função para obter classe CSS do status
function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'to do':
        case 'open':
            return 'status-todo';
        case 'in progress':
        case 'progress':
            return 'status-progress';
        case 'done':
        case 'closed':
        case 'resolved':
            return 'status-done';
        default:
            return 'status-todo';
    }
}

// Função para formatar data
function formatarData(dataString) {
    if (!dataString) return 'N/A';
    
    try {
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dataString;
    }
}

// NOVA FUNÇÃO SIMPLES PARA ABRIR MODAL CUSTOMIZADO
function abrirModalCriar() {
    console.log('=== ABRINDO MODAL CUSTOMIZADO ===');
    
    if (!issuePaiAtual) {
        mostrarNotificacao('Primeiro busque uma issue pai para criar casos de teste', 'warning');
        return;
    }
    
    console.log('Issue pai atual:', issuePaiAtual);
    
    // Limpar formulário
    casoTesteEditando = null;
    document.getElementById('modalTitleCustomizado').innerHTML = '<i class="fas fa-plus me-2"></i>Novo Caso de Teste';
    document.getElementById('formCasoTesteCustomizado').reset();
    document.getElementById('issuePaiFormCustomizado').value = issuePaiAtual;
    document.getElementById('issueKeyCustomizado').value = '';
    
    // Mostrar modal customizado
    const modalElement = document.getElementById('modalCustomizado');
    if (modalElement) {
        modalElement.style.display = 'flex';
        console.log('✅ Modal customizado aberto com sucesso');
        
        // Focar no primeiro campo
        setTimeout(() => {
            const tituloField = document.getElementById('tituloCustomizado');
            if (tituloField) {
                tituloField.focus();
                console.log('✅ Campo título focado');
            }
        }, 100);
    } else {
        console.error('❌ Modal customizado não encontrado');
    }
}

// Função para fechar modal customizado
function fecharModalCustomizado() {
    const modalElement = document.getElementById('modalCustomizado');
    if (modalElement) {
        modalElement.style.display = 'none';
        console.log('✅ Modal customizado fechado');
    }
}

// Fechar modal ao clicar fora dele
document.addEventListener('click', function(event) {
    const modalElement = document.getElementById('modalCustomizado');
    if (modalElement && event.target === modalElement) {
        fecharModalCustomizado();
    }
});

// Fechar modal ao pressionar Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modalElement = document.getElementById('modalCustomizado');
        if (modalElement && modalElement.style.display === 'flex') {
            fecharModalCustomizado();
        }
    }
});



// Função para editar caso de teste
async function editarCasoTeste(issueKey) {
    try {
        const casoElement = document.querySelector(`[onclick="editarCasoTeste('${issueKey}')"]`).closest('.caso-teste-item');
        
        casoTesteEditando = issueKey;
        document.getElementById('modalTitleCustomizado').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Caso de Teste';
        document.getElementById('issueKeyCustomizado').value = issueKey;
        document.getElementById('issuePaiFormCustomizado').value = issuePaiAtual;
        
        // Preencher formulário com dados existentes
        const titulo = casoElement.querySelector('.caso-teste-titulo').textContent;
        const status = casoElement.querySelector('.caso-teste-status').textContent;
        const descricao = casoElement.querySelector('.caso-teste-descricao')?.textContent.replace('Descrição/Cenário:', '').trim() || '';
        
        document.getElementById('tituloCustomizado').value = titulo;
        document.getElementById('statusCustomizado').value = status;
        document.getElementById('descricaoCustomizado').value = descricao;
        
        // Extrair outros campos dos meta dados
        const metaElements = casoElement.querySelectorAll('.caso-teste-meta span');
        metaElements.forEach(meta => {
            const text = meta.textContent;
            if (text.includes('Execução:')) {
                const tipoExecucao = text.split('Execução:')[1].trim();
                document.getElementById('tipoExecucaoCustomizado').value = tipoExecucao;
            } else if (text.includes('Tipo:')) {
                const tipoTeste = text.split('Tipo:')[1].trim();
                document.getElementById('tipoTesteCustomizado').value = tipoTeste;
            } else if (text.includes('Componentes:')) {
                const componentes = text.split('Componentes:')[1].trim();
                document.getElementById('componentesCustomizado').value = componentes;
            }
        });
        
        // Extrair objetivo e pré-condições
        const objetivoElement = casoElement.querySelector('div:contains("Objetivo:")');
        if (objetivoElement) {
            const objetivo = objetivoElement.textContent.replace('Objetivo:', '').trim();
            document.getElementById('objetivoCustomizado').value = objetivo;
        }
        
        const preCondicoesElement = casoElement.querySelector('div:contains("Pré-condições:")');
        if (preCondicoesElement) {
            const preCondicoes = preCondicoesElement.textContent.replace('Pré-condições:', '').trim();
            document.getElementById('preCondicoesCustomizado').value = preCondicoes;
        }
        
        // Mostrar modal customizado
        const modal = document.getElementById('modalCustomizado');
        modal.style.display = 'flex';
        
    } catch (error) {
        console.error('Erro ao editar:', error);
        mostrarNotificacao('Erro ao carregar dados para edição', 'error');
    }
}

// Função para salvar caso de teste (versão customizada)
async function salvarCasoTesteCustomizado() {
    const form = document.getElementById('formCasoTesteCustomizado');
    const formData = new FormData(form);
    
    // Validar campos obrigatórios
    const titulo = formData.get('titulo').trim();
    const descricao = formData.get('descricao').trim();
    
    if (!titulo || !descricao) {
        mostrarNotificacao('Título e descrição são obrigatórios', 'warning');
        return;
    }
    
    // Preparar dados
    const dados = {
        issue_pai: formData.get('issuePai'),
        titulo: titulo,
        descricao: descricao,
        objetivo: formData.get('objetivo').trim(),
        pre_condicoes: formData.get('preCondicoes').trim(),
        tipo_execucao: formData.get('tipoExecucao'),
        tipo_teste: formData.get('tipoTeste'),
        componentes: [formData.get('componentes')]
    };
    
    const issueKey = formData.get('issueKey');
    const url = issueKey ? `http://127.0.0.1:8081/api/caso-teste/${issueKey}` : 'http://127.0.0.1:8081/api/caso-teste';
    const method = issueKey ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            mostrarNotificacao(result.mensagem, 'success');
            
            // Fechar modal
            fecharModalCustomizado();
            
            // Recarregar lista
            buscarCasosTeste();
        } else {
            mostrarNotificacao(result.erro || 'Erro ao salvar caso de teste', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao('Erro de conexão. Verifique sua internet.', 'error');
    }
}

// Função para excluir caso de teste
function excluirCasoTeste(issueKey, titulo) {
    casoTesteEditando = issueKey;
    document.getElementById('confirmacaoTexto').textContent = `${issueKey} - ${titulo}`;
    
    const modal = new bootstrap.Modal(document.getElementById('modalConfirmacao'));
    modal.show();
}

// Função para confirmar exclusão
async function confirmarExclusao() {
    if (!casoTesteEditando) return;
    
    try {
        const response = await fetch(`http://127.0.0.1:8081/api/caso-teste/${casoTesteEditando}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            mostrarNotificacao(result.mensagem, 'success');
            
            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalConfirmacao'));
            modal.hide();
            
            // Recarregar lista
            buscarCasosTeste();
        } else {
            mostrarNotificacao(result.erro || 'Erro ao excluir caso de teste', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao('Erro de conexão. Verifique sua internet.', 'error');
    }
}

// Função para mostrar notificações
function mostrarNotificacao(mensagem, tipo = 'info') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    
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
            toastTitle.textContent = 'Atenção';
            break;
        default:
            toastIcon.className = 'fas fa-info-circle me-2 text-info';
            toastTitle.textContent = 'Informação';
    }
    
    toastBody.textContent = mensagem;
    
    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Função auxiliar para buscar elementos por texto
Element.prototype.contains = function(text) {
    return this.textContent.includes(text);
};

// Função para visualizar em formato de planilha
function visualizarPlanilha() {
    if (!issuePaiAtual) {
        mostrarNotificacao('Nenhuma issue pai selecionada', 'warning');
        return;
    }
    
    // Navegar para a página de visualização em planilha
    window.open(`http://127.0.0.1:8081/planilha/${issuePaiAtual}`, '_blank');
}


