// Variáveis globais
let rowCounter = 0;
let exportModal;
let dadosProcessados = []; // Array para armazenar dados processados da importação em massa

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar modal
    exportModal = new bootstrap.Modal(document.getElementById('exportModal'));
    
    // Event listeners para planilha manual
    document.getElementById('btnAddRow').addEventListener('click', addRow);
    document.getElementById('btnExportJira').addEventListener('click', showExportModal);
    document.getElementById('btnConfirmExport').addEventListener('click', exportToJira);
    
    // Event listeners para importação em massa
    document.getElementById('btnProcessarDados').addEventListener('click', processarDadosColados);
    document.getElementById('btnLimparDados').addEventListener('click', limparDadosImportacao);
    document.getElementById('btnPreencherPlanilha').addEventListener('click', preencherPlanilhaComDados);
    
    // Adicionar primeira linha
    addRow();
});

// ========================================
// FUNÇÕES DE IMPORTAÇÃO EM MASSA
// ========================================

// Função para processar dados colados
function processarDadosColados() {
    const dadosTabela = document.getElementById('dadosTabela').value.trim();
    
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
    document.getElementById('dadosTabela').value = '';
    document.getElementById('previewContainer').style.display = 'none';
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
    
    document.getElementById('totalCasos').textContent = validRows.length;
    exportModal.show();
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
    const issuePai = document.getElementById('issuePai').value.trim();
    
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
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
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
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
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
    
    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}
