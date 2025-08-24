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
    
    // Carregar preferência de visualização
    carregarPreferenciaVisualizacao();
    
    // Inicializar editor BDD
    initBDDEditorTela();
    
    // Listener para mudanças na URL (navegação com botões voltar/avançar)
    window.addEventListener('popstate', function(event) {
        verificarRequisitoNaURL();
    });
    
    // Listener para fechar edição em tela com Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const edicaoTela = document.getElementById('edicaoTela');
            if (edicaoTela && edicaoTela.style.display === 'flex') {
                fecharEdicaoTela();
            }
        }
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
    const cardsCasos = document.getElementById('cardsCasos');
    const totalCasos = document.getElementById('totalCasos');
    const btnPlanilha = document.getElementById('btnPlanilha');
    
    // Exibir informações do requisito pai
    if (data.requisito) {
        const requisitoInfo = data.requisito;
        const requisitoHTML = `
            <div class="requisito-info">
                <div class="requisito-header">
                    <h4 class="requisito-titulo">
                        <i class="fas fa-file-alt me-2"></i>
                        ${requisitoInfo.titulo}
                    </h4>
                    <span class="requisito-id">${requisitoInfo.id}</span>
                </div>
                <div class="requisito-meta">
                    <span class="requisito-meta-item">
                        <i class="fas fa-tag"></i>
                        ${requisitoInfo.tipo}
                    </span>
                    <span class="requisito-meta-item">
                        <i class="fas fa-project-diagram"></i>
                        ${requisitoInfo.projeto}
                    </span>
                    <span class="requisito-meta-item">
                        <i class="fas fa-info-circle"></i>
                        ${requisitoInfo.status}
                    </span>
                    <span class="requisito-meta-item">
                        <i class="fas fa-calendar-plus"></i>
                        ${formatarData(requisitoInfo.criado_em)}
                    </span>
                </div>
                ${requisitoInfo.descricao ? `
                    <div class="requisito-descricao">
                        <strong><i class="fas fa-align-left me-1"></i>Descrição:</strong><br>
                        <div class="requisito-descricao-texto">${requisitoInfo.descricao.replace(/\n/g, '<br>')}</div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Inserir informações do requisito antes da lista de casos
        const resultadosDiv = document.getElementById('resultados');
        const requisitoContainer = document.createElement('div');
        requisitoContainer.innerHTML = requisitoHTML;
        requisitoContainer.className = 'mb-4';
        
        // Remover informações do requisito anteriores se existirem
        const requisitoAnterior = resultadosDiv.querySelector('.requisito-info');
        if (requisitoAnterior) {
            requisitoAnterior.remove();
        }
        
        // Inserir no início da seção de resultados
        resultadosDiv.insertBefore(requisitoContainer, resultadosDiv.firstChild);
    }
    
    totalCasos.textContent = `${data.total_casos} caso(s) de teste`;
    
    if (data.casos_teste.length === 0) {
        btnPlanilha.style.display = 'none';
        document.getElementById('btnNovoCaso').style.display = 'inline-block'; // Mostrar botão para criar primeiro caso
        const emptyStateHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h4>Nenhum caso de teste encontrado</h4>
                <p>Não foram encontrados casos de teste para o requisito ${data.issue_pai}</p>
                <button class="btn btn-primary" onclick="abrirEdicaoTela()">
                    <i class="fas fa-plus me-1"></i>
                    Criar Primeiro Caso de Teste
                </button>
            </div>
        `;
        listaCasos.innerHTML = emptyStateHTML;
        cardsCasos.innerHTML = emptyStateHTML;
        return;
    }
    
    // Mostrar botões quando há casos de teste
    btnPlanilha.style.display = 'inline-block';
    
    // Renderizar em ambos os formatos
    const casosListaHTML = data.casos_teste.map(caso => criarHTMLCasoTesteLista(caso)).join('');
    const casosCardsHTML = data.casos_teste.map(caso => criarHTMLCasoTesteCard(caso)).join('');
    
    listaCasos.innerHTML = casosListaHTML;
    cardsCasos.innerHTML = casosCardsHTML;
}

// Função para criar HTML de um caso de teste em formato de lista
function criarHTMLCasoTesteLista(caso) {
    const statusClass = getStatusClass(caso.status);
    const dataCriacao = formatarData(caso.criado_em);
    const dataAtualizacao = formatarData(caso.atualizado_em);
    const componentes = caso.componentes.join(', ') || 'N/A';
    
    return `
        <div class="case-list-item" onclick="editarCasoTeste('${caso.id}')">
            <div class="case-list-main">
                <h5 class="case-list-title">${caso.titulo}</h5>
                <div class="case-list-meta">
                    <span class="case-list-meta-item">
                        <i class="fas fa-hashtag"></i>
                        ${caso.id}
                    </span>
                    <span class="case-list-meta-item">
                        <i class="fas fa-calendar-plus"></i>
                        ${dataCriacao}
                    </span>
                    <span class="case-list-meta-item">
                        <i class="fas fa-play"></i>
                        ${caso.tipo_execucao}
                    </span>
                    <span class="case-list-meta-item">
                        <i class="fas fa-tag"></i>
                        ${caso.tipo_teste}
                    </span>
                    <span class="case-list-meta-item">
                        <i class="fas fa-puzzle-piece"></i>
                        ${componentes}
                    </span>
                    <span class="case-list-meta-item case-status ${statusClass}">
                        <i class="fas fa-info-circle"></i>
                        ${caso.status}
                    </span>
                    <span class="case-list-meta-item case-action">
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); excluirCasoTeste('${caso.id}', '${caso.titulo}')" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </span>
                </div>

                ${caso.descricao ? `
                    <div class="case-list-description">
                        <strong><i class="fas fa-file-text"></i> Descrição:</strong><br>
                        <div class="case-description-texto">${caso.descricao.replace(/\n/g, '<br>')}</div>
                    </div>
                ` : ''}
            </div>
            <div class="case-list-actions">
                <span class="case-status ${statusClass}">${caso.status}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); excluirCasoTeste('${caso.id}', '${caso.titulo}')" title="Excluir">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

// Função para criar HTML de um caso de teste em formato de card
function criarHTMLCasoTesteCard(caso) {
    const statusClass = getStatusClass(caso.status);
    const dataCriacao = formatarData(caso.criado_em);
    const dataAtualizacao = formatarData(caso.atualizado_em);
    const componentes = caso.componentes.join(', ') || 'N/A';
    
    return `
        <div class="case-card" onclick="editarCasoTeste('${caso.id}')">
            <div class="case-header">
                <h5 class="case-title">${caso.titulo}</h5>
                <span class="case-status ${statusClass}">${caso.status}</span>
            </div>
            
            <div class="case-meta">
                <div class="case-meta-item">
                    <i class="fas fa-hashtag"></i>
                    <span>${caso.id}</span>
                </div>
                <div class="case-meta-item">
                    <i class="fas fa-calendar-plus"></i>
                    <span>${dataCriacao}</span>
                </div>
                <div class="case-meta-item">
                    <i class="fas fa-play"></i>
                    <span>${caso.tipo_execucao}</span>
                </div>
                <div class="case-meta-item">
                    <i class="fas fa-tag"></i>
                    <span>${caso.tipo_teste}</span>
                </div>
                <div class="case-meta-item">
                    <i class="fas fa-puzzle-piece"></i>
                    <span>${componentes}</span>
                </div>
                <div class="case-meta-item case-status ${statusClass}">
                    <i class="fas fa-info-circle"></i>
                    <span>${caso.status}</span>
                </div>
                <div class="case-meta-item case-action">
                    <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); excluirCasoTeste('${caso.id}', '${caso.titulo}')" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            

            ${caso.descricao ? `
                <div class="case-description">
                    <strong><i class="fas fa-file-text"></i> Descrição:</strong><br>
                    <div class="case-description-texto">${caso.descricao.replace(/\n/g, '<br>')}</div>
                </div>
            ` : ''}
            
            <div class="case-actions">
                <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); excluirCasoTeste('${caso.id}', '${caso.titulo}')" title="Excluir">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

// Função para criar HTML de um caso de teste (mantida para compatibilidade)
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
                        <button class="btn btn-sm btn-outline-danger" onclick="excluirCasoTeste('${caso.id}', '${caso.titulo.replace(/'/g, "\\'")}')" title="Excluir">
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

// NOVA FUNÇÃO PARA ABRIR EDIÇÃO EM TELA
function abrirEdicaoTela() {
    console.log('=== ABRINDO EDIÇÃO EM TELA ===');
    
    if (!issuePaiAtual) {
        mostrarNotificacao('Primeiro busque uma issue pai para criar casos de teste', 'warning');
        return;
    }
    
    console.log('Issue pai atual:', issuePaiAtual);
    
    // Limpar formulário
    casoTesteEditando = null;
    document.getElementById('edicaoTelaTitle').innerHTML = '<i class="fas fa-plus me-2"></i>Novo Caso de Teste';
    document.getElementById('formCasoTesteTela').reset();
    document.getElementById('issuePaiFormTela').value = issuePaiAtual;
    document.getElementById('issueKeyTela').value = '';
    

    
    // Mostrar edição em tela
    const edicaoTela = document.getElementById('edicaoTela');
    if (edicaoTela) {
        edicaoTela.style.display = 'flex';
        document.body.classList.add('edicao-ativa');
        console.log('✅ Edição em tela aberta com sucesso');
        
        // Focar no primeiro campo e inicializar editor BDD
        setTimeout(() => {
            const tituloField = document.getElementById('tituloTela');
            if (tituloField) {
                tituloField.focus();
                console.log('✅ Campo título focado');
            }
            
            // Inicializar editor BDD
            initBDDEditorTela();
            updateBDDPreviewTela();
        }, 100);
    } else {
        console.error('❌ Seção de edição em tela não encontrada');
    }
}

// Função para fechar edição em tela
function fecharEdicaoTela() {
    const edicaoTela = document.getElementById('edicaoTela');
    if (edicaoTela) {
        edicaoTela.classList.add('slide-out');
        setTimeout(() => {
            edicaoTela.style.display = 'none';
            edicaoTela.classList.remove('slide-out');
            document.body.classList.remove('edicao-ativa');
            console.log('✅ Edição em tela fechada');
        }, 300);
    }
}

// Função para editar caso de teste
async function editarCasoTeste(issueKey) {
    console.log('🚀 Função editarCasoTeste chamada com issueKey:', issueKey);
    try {
        console.log('Editando caso de teste:', issueKey);
        
        // Buscar o caso de teste no servidor para obter todos os dados
        const response = await fetch(`http://127.0.0.1:8081/api/caso-teste/${issueKey}`);
        const caso = await response.json();
        
        console.log('Resposta da API:', caso);
        console.log('Status da resposta:', response.status);
        
        if (!response.ok) {
            throw new Error(caso.erro || 'Erro ao carregar dados do caso de teste');
        }
        
        casoTesteEditando = issueKey;
        document.getElementById('edicaoTelaTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Caso de Teste';
        document.getElementById('issueKeyTela').value = issueKey;
        document.getElementById('issuePaiFormTela').value = issuePaiAtual;
        
        console.log('Preenchendo formulário com dados:', {
            titulo: caso.titulo,
            status: caso.status,
            descricao: caso.descricao,
            objetivo: caso.objetivo,
            pre_condicoes: caso.pre_condicoes,
            tipo_execucao: caso.tipo_execucao,
            tipo_teste: caso.tipo_teste,
            componentes: caso.componentes
        });
        
        // Preencher formulário com dados do servidor
        // Preencher campos com logs detalhados
        const tituloElement = document.getElementById('tituloTela');
        tituloElement.value = caso.titulo || '';
        console.log('✅ Título definido:', tituloElement.value);
        
        // Mapear status do Jira para o formulário
        let statusMapeado = 'To Do';
        if (caso.status) {
            switch (caso.status.toLowerCase()) {
                case 'para ajustar':
                case 'to do':
                case 'open':
                    statusMapeado = 'To Do';
                    break;
                case 'em progresso':
                case 'in progress':
                case 'em desenvolvimento':
                    statusMapeado = 'In Progress';
                    break;
                case 'concluído':
                case 'done':
                case 'resolved':
                    statusMapeado = 'Done';
                    break;
                default:
                    statusMapeado = 'To Do';
            }
        }
        const statusElement = document.getElementById('statusTela');
        statusElement.value = statusMapeado;
        console.log('✅ Status mapeado:', statusMapeado, 'para status original:', caso.status);
        
        const descricaoElement = document.getElementById('descricaoTela');
        descricaoElement.value = caso.descricao || '';
        console.log('✅ Descrição definida:', descricaoElement.value ? 'com conteúdo' : 'vazia');
        
        const objetivoElement = document.getElementById('objetivoTela');
        objetivoElement.value = caso.objetivo || '';
        console.log('✅ Objetivo definido:', objetivoElement.value ? 'com conteúdo' : 'vazio');
        
        const preCondicoesElement = document.getElementById('preCondicoesTela');
        preCondicoesElement.value = caso.pre_condicoes || '';
        console.log('✅ Pré-condições definidas:', preCondicoesElement.value ? 'com conteúdo' : 'vazias');
        
        const tipoExecucaoElement = document.getElementById('tipoExecucaoTela');
        tipoExecucaoElement.value = caso.tipo_execucao || 'Manual';
        console.log('✅ Tipo execução definido:', tipoExecucaoElement.value);
        
        const tipoTesteElement = document.getElementById('tipoTesteTela');
        tipoTesteElement.value = caso.tipo_teste || 'Funcional';
        console.log('✅ Tipo teste definido:', tipoTesteElement.value);
        
        const componentesElement = document.getElementById('componentesTela');
        componentesElement.value = caso.componentes?.[0] || 'API';
        console.log('✅ Componentes definidos:', componentesElement.value);
        
        console.log('Formulário preenchido com sucesso');
        

        
        // Mostrar edição em tela
        const edicaoTela = document.getElementById('edicaoTela');
        if (edicaoTela) {
            edicaoTela.style.display = 'flex';
            document.body.classList.add('edicao-ativa');
            console.log('✅ Edição em tela exibida com sucesso');
            
            // Verificar se os campos foram preenchidos
            setTimeout(() => {
                const titulo = document.getElementById('tituloTela').value;
                const descricao = document.getElementById('descricaoTela').value;
                console.log('✅ Verificação dos campos:');
                console.log('  - Título:', titulo);
                console.log('  - Descrição:', descricao ? descricao.substring(0, 50) + '...' : 'vazia');
            }, 200);
        } else {
            console.error('❌ Seção de edição em tela não encontrada');
        }
        
        // Inicializar editor BDD e atualizar preview
        setTimeout(() => {
            try {
                initBDDEditorTela();
                updateBDDPreviewTela();
                console.log('✅ Editor BDD inicializado com sucesso');
            } catch (error) {
                console.error('❌ Erro ao inicializar editor BDD:', error);
            }
        }, 100);
        
    } catch (error) {
        console.error('Erro ao editar:', error);
        mostrarNotificacao('Erro ao carregar dados para edição: ' + error.message, 'error');
    }
}

// Função para salvar caso de teste (versão em tela)
async function salvarCasoTesteTela() {
    const form = document.getElementById('formCasoTesteTela');
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
            
            // Fechar edição em tela
            fecharEdicaoTela();
            
            // Recarregar lista
            carregarCasosTeste(issuePaiAtual);
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
            carregarCasosTeste(issuePaiAtual);
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

// Função para alternar entre visualização em lista e cards
function toggleView(viewType) {
    const btnListView = document.getElementById('btnListView');
    const btnCardView = document.getElementById('btnCardView');
    const listaCasos = document.getElementById('listaCasos');
    const cardsCasos = document.getElementById('cardsCasos');
    
    // Remover classe active de todos os botões
    btnListView.classList.remove('active');
    btnCardView.classList.remove('active');
    
    // Remover classe active de todos os containers
    listaCasos.classList.remove('active');
    cardsCasos.classList.remove('active');
    
    if (viewType === 'list') {
        // Ativar visualização em lista
        btnListView.classList.add('active');
        listaCasos.classList.add('active');
    } else {
        // Ativar visualização em cards
        btnCardView.classList.add('active');
        cardsCasos.classList.add('active');
    }
    
    // Salvar preferência no localStorage
    localStorage.setItem('viewPreference', viewType);
}

// Função para carregar preferência de visualização
function carregarPreferenciaVisualizacao() {
    const preferencia = localStorage.getItem('viewPreference') || 'list';
    toggleView(preferencia);
}

// Função para inserir palavra-chave BDD (versão em tela)
function insertBDDKeywordTela(keyword) {
    const textarea = document.getElementById('descricaoTela');
    const cursorPos = textarea.selectionStart;
    const textBefore = textarea.value.substring(0, cursorPos);
    const textAfter = textarea.value.substring(cursorPos);
    
    // Determinar se precisa adicionar quebra de linha
    const needsNewLine = textBefore.length > 0 && !textBefore.endsWith('\n');
    const insertion = (needsNewLine ? '\n' : '') + keyword + ' ';
    
    textarea.value = textBefore + insertion + textAfter;
    
    // Posicionar cursor após a palavra-chave
    const newCursorPos = cursorPos + insertion.length;
    textarea.setSelectionRange(newCursorPos, newCursorPos);
    textarea.focus();
    
    // Atualizar preview
    updateBDDPreviewTela();
}

// Função para formatar texto BDD (versão em tela)
function formatBDDTela() {
    const textarea = document.getElementById('descricaoTela');
    let text = textarea.value;
    
    // Dividir em linhas
    const lines = text.split('\n');
    const formattedLines = [];
    
    lines.forEach(line => {
        const trimmedLine = line.trim();
        if (trimmedLine) {
            // Verificar se a linha já começa com uma palavra-chave BDD
            const bddKeywords = ['Given', 'When', 'Then', 'And', 'But'];
            const startsWithKeyword = bddKeywords.some(keyword => 
                trimmedLine.toLowerCase().startsWith(keyword.toLowerCase())
            );
            
            if (startsWithKeyword) {
                // Capitalizar a primeira palavra se for uma palavra-chave
                const words = trimmedLine.split(' ');
                if (bddKeywords.includes(words[0])) {
                    words[0] = words[0].charAt(0).toUpperCase() + words[0].slice(1).toLowerCase();
                }
                formattedLines.push(words.join(' '));
            } else {
                // Se não começar com palavra-chave, adicionar "Given" se for a primeira linha
                if (formattedLines.length === 0) {
                    formattedLines.push('Given ' + trimmedLine);
                } else {
                    formattedLines.push(trimmedLine);
                }
            }
        }
    });
    
    textarea.value = formattedLines.join('\n');
    updateBDDPreviewTela();
}

// Função para atualizar preview BDD (versão em tela)
function updateBDDPreviewTela() {
    const textarea = document.getElementById('descricaoTela');
    const preview = document.getElementById('bddPreviewTela');
    const text = textarea.value;
    
    if (!text.trim()) {
        preview.classList.remove('show');
        return;
    }
    
    // Formatar o texto para preview
    const lines = text.split('\n');
    const formattedLines = lines.map(line => {
        const trimmedLine = line.trim();
        if (!trimmedLine) return '';
        
        const lowerLine = trimmedLine.toLowerCase();
        if (lowerLine.startsWith('given')) {
            return `<span class="given">${trimmedLine}</span>`;
        } else if (lowerLine.startsWith('when')) {
            return `<span class="when">${trimmedLine}</span>`;
        } else if (lowerLine.startsWith('then')) {
            return `<span class="then">${trimmedLine}</span>`;
        } else if (lowerLine.startsWith('and') || lowerLine.startsWith('but')) {
            return `<span class="and">${trimmedLine}</span>`;
        } else {
            return trimmedLine;
        }
    });
    
    preview.innerHTML = formattedLines.join('<br>');
    preview.classList.add('show');
}

// Função para inicializar editor BDD (versão em tela)
function initBDDEditorTela() {
    const textarea = document.getElementById('descricaoTela');
    if (textarea) {
        textarea.addEventListener('input', updateBDDPreviewTela);
        textarea.addEventListener('keydown', function(e) {
            // Auto-completar com Tab
            if (e.key === 'Tab') {
                e.preventDefault();
                const cursorPos = this.selectionStart;
                const textBefore = this.value.substring(0, cursorPos);
                const textAfter = this.value.substring(cursorPos);
                
                // Verificar se está no início da linha
                const lineStart = textBefore.lastIndexOf('\n') + 1;
                const currentLine = textBefore.substring(lineStart);
                
                if (currentLine.trim() === '') {
                    // Se a linha estiver vazia, inserir "Given"
                    this.value = textBefore + 'Given ' + textAfter;
                    this.setSelectionRange(cursorPos + 6, cursorPos + 6);
                } else {
                    // Se não estiver vazia, inserir tab normal
                    this.value = textBefore + '    ' + textAfter;
                    this.setSelectionRange(cursorPos + 4, cursorPos + 4);
                }
                updateBDDPreviewTela();
            }
        });
    }
}

// Função para visualizar em formato de planilha
function visualizarPlanilha() {
    if (!issuePaiAtual) {
        mostrarNotificacao('Nenhuma issue pai selecionada', 'warning');
        return;
    }
    
    // Navegar para a página de visualização em planilha
    window.open(`http://127.0.0.1:8081/planilha/${issuePaiAtual}`, '_blank');
}





