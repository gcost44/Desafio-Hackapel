// ========================================
// FILA DE ESPERA - Sistema SUS Automação
// ========================================

let filaPacientes = [];

// Carregar dados ao iniciar
document.addEventListener('DOMContentLoaded', function() {
    carregarEstatisticas();
    carregarFila();
});

// ========================================
// ESTATÍSTICAS
// ========================================

async function carregarEstatisticas() {
    try {
        const response = await fetch('/api/fila');
        const fila = await response.json();
        
        const altaPrioridade = fila.filter(p => p.score_fila >= 50).length;
        const tempoMedio = calcularTempoMedio(fila);
        
        document.getElementById('total-fila').textContent = fila.length;
        document.getElementById('alta-prioridade').textContent = altaPrioridade;
        document.getElementById('tempo-medio').textContent = tempoMedio;
        document.getElementById('convocacoes-hoje').textContent = Math.floor(Math.random() * 10) + 5; // Simulado
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

function calcularTempoMedio(fila) {
    if (fila.length === 0) return '0d';
    
    const hoje = new Date();
    const somaTempos = fila.reduce((soma, paciente) => {
        const dataInscricao = new Date(paciente.data_inscricao_fila);
        const dias = Math.floor((hoje - dataInscricao) / (1000 * 60 * 60 * 24));
        return soma + dias;
    }, 0);
    
    const media = Math.floor(somaTempos / fila.length);
    return `${media}d`;
}

// ========================================
// FILA
// ========================================

async function carregarFila() {
    document.getElementById('loading-spinner').style.display = 'flex';
    
    try {
        const response = await fetch('/api/fila');
        filaPacientes = await response.json();
        
        // Ordenar por score (maior para menor)
        filaPacientes.sort((a, b) => b.score_fila - a.score_fila);
        
        renderizarFila(filaPacientes);
    } catch (error) {
        console.error('Erro ao carregar fila:', error);
    } finally {
        document.getElementById('loading-spinner').style.display = 'none';
    }
}

function renderizarFila(lista) {
    const tbody = document.getElementById('fila-tbody');
    tbody.innerHTML = '';
    
    document.getElementById('fila-count').textContent = `${lista.length} pacientes`;
    
    lista.forEach((paciente, index) => {
        const tr = document.createElement('tr');
        
        // Determinar prioridade
        let prioridadeClass = 'priority-low';
        let prioridadeLabel = 'Baixa';
        
        if (paciente.score_fila >= 50) {
            prioridadeClass = 'priority-high';
            prioridadeLabel = 'Alta';
        } else if (paciente.score_fila >= 30) {
            prioridadeClass = 'priority-medium';
            prioridadeLabel = 'Média';
        }
        
        tr.className = prioridadeClass;
        
        // Calcular tempo de espera
        const tempoEspera = calcularTempoEspera(paciente.data_inscricao_fila);
        
        tr.innerHTML = `
            <td><strong>${index + 1}º</strong></td>
            <td><strong>${paciente.nome}</strong></td>
            <td>${paciente.idade} anos</td>
            <td>${paciente.especialidade}</td>
            <td>${tempoEspera}</td>
            <td>
                <strong style="font-size: 1.1rem;">${paciente.score_fila}</strong>
                <button class="btn btn-sm" onclick="verDetalhesScore(${paciente.id})" style="padding: 0.2rem 0.5rem; margin-left: 0.5rem;">
                    ℹ️
                </button>
            </td>
            <td><span class="badge badge-${getPrioridadeBadge(paciente.score_fila)}">${prioridadeLabel}</span></td>
            <td>
                <button class="btn btn-success btn-sm" onclick="convocarPaciente(${paciente.id})">
                    📞 Convocar
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// ========================================
// FILTROS
// ========================================

function filtrarFila() {
    const searchTerm = document.getElementById('search-fila').value.toLowerCase();
    const especialidadeFilter = document.getElementById('filter-especialidade').value;
    const prioridadeFilter = document.getElementById('filter-prioridade').value;
    
    const filtrados = filaPacientes.filter(paciente => {
        const matchSearch = paciente.nome.toLowerCase().includes(searchTerm);
        const matchEspecialidade = !especialidadeFilter || paciente.especialidade === especialidadeFilter;
        
        let matchPrioridade = true;
        if (prioridadeFilter === 'alta') {
            matchPrioridade = paciente.score_fila >= 50;
        } else if (prioridadeFilter === 'media') {
            matchPrioridade = paciente.score_fila >= 30 && paciente.score_fila < 50;
        } else if (prioridadeFilter === 'baixa') {
            matchPrioridade = paciente.score_fila < 30;
        }
        
        return matchSearch && matchEspecialidade && matchPrioridade;
    });
    
    renderizarFila(filtrados);
}

// ========================================
// AÇÕES
// ========================================

async function convocarPaciente(pacienteId) {
    const paciente = filaPacientes.find(p => p.id === pacienteId);
    
    if (!paciente) {
        alert('Paciente não encontrado!');
        return;
    }
    
    if (confirm(`Convocar ${paciente.nome} para consulta?`)) {
        try {
            const response = await fetch('/api/convocar-fila', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paciente_id: pacienteId })
            });
            
            const result = await response.json();
            
            if (result.sucesso) {
                alert(`✅ ${paciente.nome} foi convocado com sucesso!\n\nMensagem enviada via WhatsApp.`);
                carregarEstatisticas();
                carregarFila();
            } else {
                alert('❌ Erro ao convocar paciente.');
            }
        } catch (error) {
            console.error('Erro ao convocar paciente:', error);
            alert('❌ Erro ao convocar paciente.');
        }
    }
}

async function verDetalhesScore(pacienteId) {
    const paciente = filaPacientes.find(p => p.id === pacienteId);
    
    if (!paciente) return;
    
    try {
        const response = await fetch(`/api/calcular-score?paciente_id=${pacienteId}`);
        const detalhes = await response.json();
        
        const content = `
            <div style="padding: 1rem;">
                <h3 style="margin-bottom: 1rem;">📊 Detalhamento do Score</h3>
                
                <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <strong>Paciente:</strong> ${paciente.nome}<br>
                    <strong>Idade:</strong> ${paciente.idade} anos<br>
                    <strong>Especialidade:</strong> ${paciente.especialidade}
                </div>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #0066CC; color: white;">
                            <th style="padding: 0.75rem; text-align: left;">Critério</th>
                            <th style="padding: 0.75rem; text-align: right;">Pontos</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 0.75rem;">👴 Idade (${paciente.idade} anos)</td>
                            <td style="padding: 0.75rem; text-align: right;"><strong>${detalhes.pontos_idade || 0}</strong></td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 0.75rem;">🏥 Tipo de Exame</td>
                            <td style="padding: 0.75rem; text-align: right;"><strong>${detalhes.pontos_exame || 0}</strong></td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 0.75rem;">⏱️ Tempo de Espera</td>
                            <td style="padding: 0.75rem; text-align: right;"><strong>${detalhes.pontos_tempo || 0}</strong></td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 0.75rem;">🎯 Bônus Especiais</td>
                            <td style="padding: 0.75rem; text-align: right;"><strong>${detalhes.pontos_bonus || 0}</strong></td>
                        </tr>
                        <tr style="background: #f8fafc; font-weight: bold;">
                            <td style="padding: 0.75rem;">SCORE TOTAL</td>
                            <td style="padding: 0.75rem; text-align: right; font-size: 1.25rem; color: #0066CC;">
                                ${paciente.score_fila}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('detalhes-content').innerHTML = content;
        document.getElementById('detalhes-modal').classList.add('active');
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
    }
}

function fecharModalDetalhes() {
    document.getElementById('detalhes-modal').classList.remove('active');
}

// ========================================
// UTILITÁRIOS
// ========================================

function calcularTempoEspera(dataInscricao) {
    const hoje = new Date();
    const inscricao = new Date(dataInscricao);
    const dias = Math.floor((hoje - inscricao) / (1000 * 60 * 60 * 24));
    
    if (dias === 0) return 'Hoje';
    if (dias === 1) return '1 dia';
    if (dias < 30) return `${dias} dias`;
    if (dias < 60) return '1 mês';
    
    const meses = Math.floor(dias / 30);
    return `${meses} meses`;
}

function getPrioridadeBadge(score) {
    if (score >= 50) return 'danger';
    if (score >= 30) return 'warning';
    return 'success';
}

function atualizarFila() {
    carregarEstatisticas();
    carregarFila();
}

// Fechar modal ao clicar fora
window.addEventListener('click', function(event) {
    const modal = document.getElementById('detalhes-modal');
    if (event.target === modal) {
        fecharModalDetalhes();
    }
});
