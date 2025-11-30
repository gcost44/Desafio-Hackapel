// ========================================
// DASHBOARD - Sistema SUS Automação
// ========================================

let pacientes = [];
let pacienteAtual = null;

// Carregar dados ao iniciar
document.addEventListener('DOMContentLoaded', function() {
    carregarMetricas();
    carregarPacientes();
});

// ========================================
// MÉTRICAS
// ========================================

async function carregarMetricas() {
    try {
        const response = await fetch('/api/metricas');
        const metricas = await response.json();
        
        document.getElementById('total-enviados').textContent = metricas.total_enviados;
        document.getElementById('total-confirmados').textContent = metricas.total_confirmados;
        document.getElementById('total-faltas').textContent = metricas.total_faltas;
        document.getElementById('taxa-confirmacao').textContent = metricas.taxa_confirmacao + '%';
    } catch (error) {
        console.error('Erro ao carregar métricas:', error);
    }
}

// ========================================
// PACIENTES
// ========================================

async function carregarPacientes() {
    document.getElementById('loading-spinner').style.display = 'flex';
    
    try {
        const response = await fetch('/api/pacientes');
        pacientes = await response.json();
        
        renderizarPacientes(pacientes);
    } catch (error) {
        console.error('Erro ao carregar pacientes:', error);
    } finally {
        document.getElementById('loading-spinner').style.display = 'none';
    }
}

function renderizarPacientes(lista) {
    const tbody = document.getElementById('pacientes-tbody');
    tbody.innerHTML = '';
    
    document.getElementById('pacientes-count').textContent = `${lista.length} pacientes`;
    
    lista.forEach(paciente => {
        const tr = document.createElement('tr');
        
        // Badge de status
        const statusColor = {
            'PENDENTE': 'secondary',
            'ENVIADO': 'info',
            'CONFIRMADO': 'success',
            'CANCELADO': 'warning',
            'FALTOU': 'danger'
        }[paciente.status] || 'secondary';
        
        tr.innerHTML = `
            <td><strong>${paciente.nome}</strong></td>
            <td>${formatarTelefone(paciente.telefone)}</td>
            <td>${formatarData(paciente.data_consulta)} às ${paciente.horario || 'N/A'}</td>
            <td>${paciente.especialidade}</td>
            <td><span class="badge badge-${statusColor}">${paciente.status}</span></td>
            <td><strong>${paciente.score_ia || 0}</strong></td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="abrirWhatsApp(${paciente.id})">
                    📱 Enviar
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// ========================================
// FILTROS
// ========================================

function filtrarPacientes() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const statusFilter = document.getElementById('filter-status').value;
    
    const filtrados = pacientes.filter(paciente => {
        const matchSearch = paciente.nome.toLowerCase().includes(searchTerm) || 
                          paciente.telefone.includes(searchTerm);
        const matchStatus = !statusFilter || paciente.status === statusFilter;
        
        return matchSearch && matchStatus;
    });
    
    renderizarPacientes(filtrados);
}

// ========================================
// WHATSAPP SIMULATOR
// ========================================

function abrirWhatsApp(pacienteId) {
    pacienteAtual = pacientes.find(p => p.id === pacienteId);
    
    if (!pacienteAtual) {
        alert('Paciente não encontrado!');
        return;
    }
    
    // Atualizar modal
    document.getElementById('modal-paciente-nome').textContent = pacienteAtual.nome;
    
    // Limpar mensagens
    const messagesDiv = document.getElementById('whatsapp-messages');
    messagesDiv.innerHTML = '';
    
    // Enviar lembrete automático
    enviarLembrete();
    
    // Mostrar modal
    document.getElementById('whatsapp-modal').classList.add('active');
}

function fecharModal() {
    document.getElementById('whatsapp-modal').classList.remove('active');
    pacienteAtual = null;
}

async function enviarLembrete() {
    if (!pacienteAtual) return;
    
    try {
        const response = await fetch('/api/enviar-lembrete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ paciente_id: pacienteAtual.id })
        });
        
        const result = await response.json();
        
        if (result.sucesso) {
            adicionarMensagem(result.mensagem, 'sent');
            
            // Atualizar status do paciente
            pacienteAtual.status = 'ENVIADO';
            carregarMetricas();
            carregarPacientes();
        }
    } catch (error) {
        console.error('Erro ao enviar lembrete:', error);
    }
}

async function simularResposta() {
    const input = document.getElementById('whatsapp-input-text');
    const resposta = input.value.trim();
    
    if (!resposta || !pacienteAtual) return;
    
    // Mostrar mensagem do paciente
    adicionarMensagem(resposta, 'received');
    input.value = '';
    
    try {
        const response = await fetch('/api/processar-resposta', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                paciente_id: pacienteAtual.id,
                resposta: resposta
            })
        });
        
        const result = await response.json();
        
        // Resposta automática após 1 segundo
        setTimeout(() => {
            adicionarMensagem(result.resposta_automatica, 'sent');
            
            // Atualizar dados
            carregarMetricas();
            carregarPacientes();
            
            // Se foi cancelamento, convocar fila
            if (result.intencao === 'CANCELAR') {
                setTimeout(() => {
                    adicionarMensagem('🔄 Processando fila de espera...', 'sent');
                    convocarFila();
                }, 1500);
            }
        }, 1000);
    } catch (error) {
        console.error('Erro ao processar resposta:', error);
    }
}

function adicionarMensagem(texto, tipo) {
    const messagesDiv = document.getElementById('whatsapp-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `whatsapp-message ${tipo}`;
    messageDiv.textContent = texto;
    messagesDiv.appendChild(messageDiv);
    
    // Scroll para o final
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function convocarFila() {
    try {
        const response = await fetch('/api/convocar-fila', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.sucesso && result.paciente_convocado) {
            setTimeout(() => {
                adicionarMensagem(
                    `✅ ${result.paciente_convocado.nome} foi convocado da fila automaticamente!`,
                    'sent'
                );
            }, 1000);
        }
    } catch (error) {
        console.error('Erro ao convocar fila:', error);
    }
}

// ========================================
// UTILITÁRIOS
// ========================================

function formatarTelefone(telefone) {
    const cleaned = telefone.replace(/\D/g, '');
    if (cleaned.length === 11) {
        return `(${cleaned.slice(0,2)}) ${cleaned.slice(2,7)}-${cleaned.slice(7)}`;
    }
    return telefone;
}

function formatarData(data) {
    if (data.includes('/')) return data;
    
    const [ano, mes, dia] = data.split('-');
    return `${dia}/${mes}/${ano}`;
}

function atualizarDados() {
    carregarMetricas();
    carregarPacientes();
}

// Event listener para Enter no input do WhatsApp
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('whatsapp-input-text');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                simularResposta();
            }
        });
    }
});

// Fechar modal ao clicar fora
window.addEventListener('click', function(event) {
    const modal = document.getElementById('whatsapp-modal');
    if (event.target === modal) {
        fecharModal();
    }
});
