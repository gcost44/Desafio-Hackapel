"""
🎮 PROTÓTIPO SIMULADO - Servidor Flask
Sistema de Agendamentos SUS com IA
Fluxo: Operador → Busca Excel → Envia WhatsApp → Lembretes Automáticos

Autor: Hackapel 2025
Versão: 2.0 - Fluxo Operador
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
import random
from datetime import datetime, timedelta
import os
from threading import Thread
import time
import google.generativeai as genai
from gtts import gTTS
import uuid
from whatsapp_integration import whatsapp_client

app = Flask(__name__)
CORS(app)

# Configurar API do Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyAC68hEyU437imZXY7CsCn0Jp41cygRvPc')
genai.configure(api_key=GEMINI_API_KEY)
modelo_gemini = genai.GenerativeModel('gemini-2.5-flash')

# Caminhos (funciona local e Railway)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, 'agenda_clinicas.xlsx')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
AUDIO_PATH = os.path.join(STATIC_DIR, 'audios')

# Criar pastas se não existirem
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(AUDIO_PATH, exist_ok=True)

# Dados simulados em memória
dados_sistema = {
    "metricas": {
        "agendados": 0,
        "confirmados": 0,
        "cancelados": 0,
        "lembretes_enviados": 0,
        "taxa_confirmacao": 0
    },
    "agendamentos": [],  # Agendamentos confirmados
    "notificacoes": [],  # Notificações para o operador
    "excel_carregado": False  # Status do Excel
}

# Carregar/Criar Excel de agendamentos
def carregar_excel():
    """Carrega Excel se existir"""
    if os.path.exists(EXCEL_PATH):
        dados_sistema["excel_carregado"] = True
        return pd.read_excel(EXCEL_PATH)
    else:
        dados_sistema["excel_carregado"] = False
        return None

def salvar_excel(df):
    """Salva DataFrame no Excel"""
    # Substituir NaN por string vazia antes de salvar
    df = df.fillna('')
    df.to_excel(EXCEL_PATH, index=False)
    dados_sistema["excel_carregado"] = True

# Educação em Saúde - Orientações por especialidade usando Gemini
def gerar_orientacoes_educativas(exame):
    """Gera orientações preventivas e educativas por tipo de exame usando IA Gemini"""
    
    print(f"\n🤖 Gerando orientação via Gemini para: {exame}")
    
    try:
        prompt = f"""Você é um médico especialista em {exame} trabalhando no SUS.

Crie orientações ESPECÍFICAS E DETALHADAS para um paciente que vai fazer consulta de {exame}.

IMPORTANTE: As dicas preventivas devem ser EXCLUSIVAS da área de {exame}. 
Por exemplo:
- Se for Cardiologista: fale de pressão arterial, colesterol, dor no peito
- Se for Dermatologista: fale de protetor solar, câncer de pele, manchas
- Se for Nutricionista: fale de alimentação balanceada, dieta, controle de peso
- Se for Oftalmologista: fale de saúde dos olhos, fadiga visual, uso de óculos

NÃO use dicas genéricas como "beba água" ou "pratique exercícios" que servem para tudo.

Formato EXATO (copie e preencha):

💙 ORIENTAÇÕES - {exame.upper()}

📋 O que levar:
• [Item 1 específico de {exame}]
• [Item 2 específico de {exame}]
• [Item 3 específico de {exame}]

⚠️ Jejum: [Sim/Não e detalhes]
🏃 Chegue [X] minutos antes

💡 DICAS PREVENTIVAS - {exame.upper()}:
• [Dica preventiva específica 1 de {exame}]
• [Dica preventiva específica 2 de {exame}]
• [Dica preventiva específica 3 de {exame}]
• [Dica preventiva específica 4 de {exame}]

Seja específico, use linguagem simples, máximo 120 palavras."""

        print(f"📤 Enviando prompt para Gemini...")
        resposta = modelo_gemini.generate_content(prompt)
        texto = resposta.text.strip()
        print(f"✅ Resposta recebida: {len(texto)} caracteres")
        return texto
        
    except Exception as e:
        print(f"❌ ERRO ao chamar Gemini API: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        
        # Retorna erro visível
        return f"""
❌ ERRO - Não foi possível gerar orientação com IA

Tipo de erro: {type(e).__name__}
Detalhes: {str(e)[:100]}

Para consulta de {exame}, consulte a unidade de saúde.
"""

# Gerar áudio para idosos
def gerar_audio_idoso(nome, idade, exame, data, horario, clinica):
    """Gera áudio explicativo para pacientes idosos usando Google TTS"""
    try:
        # Texto do áudio (sem emojis, formatado para fala)
        texto_audio = f"""
Olá {nome}! 
Este é um áudio especial do sistema de agendamentos do SUS.

Sua consulta de {exame} foi confirmada com sucesso.

A consulta será no dia {data}, às {horario}, no local {clinica}.

Como você tem {idade} anos, você tem direito a atendimento prioritário.

Anote o que você deve levar:
- Documento de identidade RG ou CPF
- Cartão do SUS
- Exames anteriores, se tiver
- Lista de remédios que você toma

Importante: chegue 15 minutos antes do horário.

Você vai receber lembretes automáticos:
- 7 dias antes
- 5 dias antes  
- 3 dias antes
- e 24 horas antes da consulta

Se tiver alguma dúvida, ligue para o telefone (11) 3000-0000.

Até logo e cuide bem da sua saúde!
"""
        
        # Gerar áudio com Google TTS (português Brasil)
        print(f"🎤 Gerando áudio para {nome} ({idade} anos)...")
        tts = gTTS(text=texto_audio, lang='pt', slow=False)
        
        # Salvar com nome único
        audio_filename = f"audio_idoso_{uuid.uuid4().hex[:8]}.mp3"
        audio_path = os.path.join(AUDIO_PATH, audio_filename)
        tts.save(audio_path)
        
        print(f"✅ Áudio gerado: {audio_filename}")
        return audio_filename
        
    except Exception as e:
        print(f"❌ Erro ao gerar áudio: {e}")
        return None

# Sistema de lembretes automáticos
def verificar_lembretes():
    """Thread que verifica e envia lembretes programados"""
    while True:
        agora = datetime.now()
        
        for agendamento in dados_sistema["agendamentos"]:
            if agendamento["status"] != "confirmado":
                continue
            
            # Converter data do agendamento
            data_agendamento = datetime.strptime(agendamento["data"], "%d/%m/%Y")
            dias_faltando = (data_agendamento - agora).days
            
            # Verificar se precisa enviar lembrete
            if dias_faltando in [7, 5, 3, 1]:  # 7, 5, 3 dias e 24h antes
                # Verificar se já enviou esse lembrete
                chave_lembrete = f"{agendamento['id']}_D{dias_faltando}"
                if chave_lembrete not in agendamento.get("lembretes_enviados", []):
                    enviar_lembrete_automatico(agendamento, dias_faltando)
                    
                    if "lembretes_enviados" not in agendamento:
                        agendamento["lembretes_enviados"] = []
                    agendamento["lembretes_enviados"].append(chave_lembrete)
                    
                    dados_sistema["metricas"]["lembretes_enviados"] += 1
        
        # Verificar a cada 1 hora (em produção seria menor)
        time.sleep(3600)

def enviar_lembrete_automatico(agendamento, dias_faltando):
    """Envia lembrete automático para o paciente com orientações educativas"""
    if dias_faltando == 1:
        periodo = "24 horas"
        dica_extra = """
⚠️ LEMBRE-SE DE LEVAR:
• Cartão SUS
• Documento com foto
• Exames anteriores
• Lista de medicamentos

Chegue 15 minutos antes!"""
    elif dias_faltando == 3:
        periodo = f"{dias_faltando} dias"
        dica_extra = """
💡 PREPARE-SE:
• Organize seus documentos
• Separe exames anteriores
• Anote suas dúvidas para o médico"""
    else:
        periodo = f"{dias_faltando} dias"
        dica_extra = ""
    
    mensagem = f"""🔔 LEMBRETE AUTOMÁTICO

Olá, {agendamento['paciente']}!

Faltam {periodo} para sua consulta:
📅 Data: {agendamento['data']}
⏰ Horário: {agendamento['horario']}
🏥 Local: {agendamento['clinica']}
👨‍⚕️ Especialidade: {agendamento['exame']}{dica_extra}

Responda:
1 - Confirmar presença
2 - Preciso cancelar"""
    
    print(f"📱 [LEMBRETE {periodo.upper()}] {agendamento['paciente']} - {agendamento['telefone']}")
    print(f"   Mensagem: {mensagem[:50]}...")
    
    # Em produção, aqui integraria com API WhatsApp

# ==================== ROTAS ====================

@app.route('/')
def index():
    """Painel do operador"""
    return render_template('index.html', 
                         metricas=dados_sistema["metricas"],
                         notificacoes=dados_sistema["notificacoes"][-5:])  # Últimas 5

@app.route('/api/agendar', methods=['POST'])
def agendar_paciente():
    """
    FLUXO PRINCIPAL: Operador envia nome + exame
    Sistema busca vaga no Excel e envia WhatsApp automaticamente
    """
    data = request.json
    nome = data.get("nome", "").strip()
    telefone = data.get("telefone", "").strip()
    data_nascimento = data.get("data_nascimento", "").strip()
    exame = data.get("exame", "").strip()
    
    if not nome or not telefone or not exame or not data_nascimento:
        return jsonify({"erro": "Preencha todos os campos"}), 400
    
    # Calcular idade
    try:
        nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d")
        hoje = datetime.now()
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
    except:
        return jsonify({"erro": "Data de nascimento inválida"}), 400
    
    # Verificar se tem Excel carregado
    if not dados_sistema["excel_carregado"]:
        return jsonify({"erro": "Carregue a planilha de horários primeiro!"}), 400
    
    # Carregar Excel
    df = carregar_excel()
    
    if df is None:
        return jsonify({"erro": "Erro ao carregar planilha"}), 500
    
    # Buscar primeira vaga disponível para esse exame
    vaga = df[(df["exame"] == exame) & (df["disponivel"] == "SIM")]
    
    if vaga.empty:
        return jsonify({
            "sucesso": False,
            "erro": f"Sem vagas disponíveis para {exame} no momento."
        }), 404
    
    # Pegar primeira vaga
    idx = vaga.index[0]
    vaga_info = vaga.iloc[0]
    
    # Marcar como ocupada no Excel (converter tipos explicitamente)
    df.at[idx, "disponivel"] = str("NAO")
    df.at[idx, "paciente"] = str(nome)
    df.at[idx, "telefone"] = str(telefone)
    
    # Salvar com tratamento de erro
    try:
        salvar_excel(df)
    except PermissionError:
        return jsonify({
            "erro": "Erro ao salvar planilha. Feche o arquivo Excel e tente novamente."
        }), 500
    
    # Criar agendamento
    agendamento = {
        "id": len(dados_sistema["agendamentos"]) + 1,
        "paciente": nome,
        "telefone": telefone,
        "idade": idade,
        "data_nascimento": data_nascimento,
        "exame": exame,
        "clinica": vaga_info["clinica"],
        "data": vaga_info["data"],
        "horario": vaga_info["horario"],
        "status": "pendente",
        "data_agendamento": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "lembretes_enviados": [],
        "audio_url": None
    }
    
    dados_sistema["agendamentos"].append(agendamento)
    dados_sistema["metricas"]["agendados"] += 1
    
    # Gerar orientações educativas por especialidade
    orientacoes = gerar_orientacoes_educativas(exame)
    
    # Verificar se é idoso (60+) para enviar áudio
    audio_idoso = ""
    audio_filename = None
    if idade >= 60:
        # Gerar áudio real
        audio_filename = gerar_audio_idoso(nome, idade, exame, vaga_info['data'], vaga_info['horario'], vaga_info['clinica'])
        
        if audio_filename:
            agendamento["audio_url"] = f"/static/audios/{audio_filename}"
            audio_idoso = f"""

🔊 ÁUDIO ESPECIAL PARA VOCÊ

Olá {nome}! Como você tem {idade} anos, preparamos um áudio explicativo sobre sua consulta de {exame}.

🎧 [CLIQUE AQUI PARA OUVIR O ÁUDIO]
http://localhost:5000/static/audios/{audio_filename}

📝 RESUMO DO ÁUDIO:
• Sua consulta está confirmada para {vaga_info['data']} às {vaga_info['horario']}
• Local: {vaga_info['clinica']}
• O que levar e como se preparar está descrito abaixo
• Qualquer dúvida, ligue para (11) 3000-0000

👵👴 Atendimento preferencial garantido!"""
    
    # Enviar mensagem WhatsApp REAL via Evolution API
    mensagem = f"""✅ AGENDAMENTO CONFIRMADO

Olá, {nome}!

Sua consulta foi agendada:
📅 Data: {vaga_info['data']}
⏰ Horário: {vaga_info['horario']}
🏥 Local: {vaga_info['clinica']}
👨‍⚕️ Especialidade: {exame}
{'👵 Idade: ' + str(idade) + ' anos (Atendimento Prioritário)' if idade >= 60 else ''}

{orientacoes}

📌 Lembretes automáticos:
   • 7, 5, 3 dias e 24h antes

Responda:
1 - Confirmar
2 - Cancelar"""
    
    # Enviar via Evolution API
    resultado_envio = whatsapp_client.enviar_mensagem_texto(telefone, mensagem)
    
    # Se for idoso, enviar áudio separado
    if idade >= 60 and audio_filename:
        # URL pública do áudio (ajustar conforme domínio)
        audio_url_publico = f"{request.host_url}static/audios/{audio_filename}"
        whatsapp_client.enviar_audio(telefone, audio_url_publico)
        print(f"   👴👵 IDOSO ({idade} anos) - ÁUDIO ENVIADO")
    
    print(f"\n🟢 [WhatsApp REAL] Enviado para {telefone}")
    
    return jsonify({
        "sucesso": True,
        "agendamento": agendamento,
        "mensagem": mensagem,
        "idoso": idade >= 60,
        "idade": idade,
        "audio_url": agendamento["audio_url"]
    })

@app.route('/api/resposta-paciente', methods=['POST'])
def resposta_paciente():
    """Processa resposta do paciente via WhatsApp"""
    data = request.json
    telefone = data.get("telefone")
    resposta = data.get("resposta", "").lower().strip()
    
    # Buscar agendamento
    agendamento = next((a for a in dados_sistema["agendamentos"] 
                       if a["telefone"] == telefone and a["status"] in ["pendente", "confirmado"]), None)
    
    if not agendamento:
        return jsonify({"erro": "Agendamento não encontrado"}), 404
    
    # Processar resposta
    if "1" in resposta or "sim" in resposta or "confirmo" in resposta:
        agendamento["status"] = "confirmado"
        dados_sistema["metricas"]["confirmados"] += 1
        
        mensagem_resposta = """✅ Obrigado! Presença confirmada.

Lembre-se de trazer:
• Cartão SUS
• Documento com foto
• Pedido médico

Até lá! 😊"""
        
        return jsonify({
            "sucesso": True,
            "acao": "CONFIRMADO",
            "mensagem": mensagem_resposta
        })
    
    elif "2" in resposta or "não" in resposta or "cancelo" in resposta:
        # CANCELAMENTO - Liberar vaga e notificar operador
        agendamento["status"] = "cancelado"
        dados_sistema["metricas"]["cancelados"] += 1
        
        # Liberar horário no Excel
        df = carregar_excel()
        mask = (df["paciente"] == agendamento["paciente"]) & \
               (df["data"] == agendamento["data"]) & \
               (df["horario"] == agendamento["horario"])
        
        df.loc[mask, "disponivel"] = str("SIM")
        df.loc[mask, "paciente"] = str("")
        df.loc[mask, "telefone"] = str("")
        
        try:
            salvar_excel(df)
        except PermissionError:
            pass  # Não bloquear cancelamento por erro de Excel
        
        # NOTIFICAR OPERADOR
        notificacao = {
            "id": len(dados_sistema["notificacoes"]) + 1,
            "tipo": "CANCELAMENTO",
            "mensagem": f"🚨 {agendamento['paciente']} CANCELOU {agendamento['exame']} em {agendamento['data']} às {agendamento['horario']} - Horário liberado!",
            "horario": datetime.now().strftime("%H:%M:%S"),
            "data": agendamento['data'],
            "horario_vaga": agendamento['horario'],
            "exame": agendamento['exame'],
            "clinica": agendamento['clinica']
        }
        dados_sistema["notificacoes"].append(notificacao)
        
        mensagem_resposta = """❌ Consulta cancelada com sucesso.

O horário foi liberado para outro paciente.

Para reagendar: (11) 3000-0000"""
        
        return jsonify({
            "sucesso": True,
            "acao": "CANCELADO",
            "mensagem": mensagem_resposta
        })
    
    else:
        return jsonify({
            "mensagem": """🤔 Não entendi. Responda:
1 - Confirmar
2 - Cancelar"""
        })

@app.route('/api/notificacoes')
def api_notificacoes():
    """Retorna notificações para o operador"""
    return jsonify(dados_sistema["notificacoes"][-10:])  # Últimas 10

@app.route('/api/metricas')
def api_metricas():
    """Retorna métricas do sistema"""
    # Calcular taxa de confirmação
    if dados_sistema["metricas"]["agendados"] > 0:
        taxa = dados_sistema["metricas"]["confirmados"] / dados_sistema["metricas"]["agendados"]
        dados_sistema["metricas"]["taxa_confirmacao"] = round(taxa * 100, 1)
    
    return jsonify(dados_sistema["metricas"])

@app.route('/api/agendamentos')
def api_agendamentos():
    """Lista agendamentos recentes"""
    return jsonify(dados_sistema["agendamentos"][-20:])  # Últimos 20

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    """Upload da planilha de horários pelo operador - Junta com planilhas anteriores"""
    if 'file' not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"erro": "Arquivo vazio"}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"erro": "Arquivo deve ser Excel (.xlsx ou .xls)"}), 400
    
    try:
        # Ler nova planilha
        df_novo = pd.read_excel(file)
        
        # Validar estrutura
        colunas_necessarias = ["clinica", "exame", "data", "horario", "disponivel"]
        
        if not all(col in df_novo.columns for col in colunas_necessarias):
            return jsonify({
                "erro": f"Planilha deve ter as colunas: {', '.join(colunas_necessarias)}"
            }), 400
        
        # Adicionar colunas se não existirem
        if "paciente" not in df_novo.columns:
            df_novo["paciente"] = ""
        if "telefone" not in df_novo.columns:
            df_novo["telefone"] = ""
        
        # Garantir que colunas sejam string
        df_novo["paciente"] = df_novo["paciente"].astype(str)
        df_novo["telefone"] = df_novo["telefone"].astype(str)
        df_novo["disponivel"] = df_novo["disponivel"].astype(str)
        
        # Remover duplicatas INTERNAS da nova planilha primeiro
        df_novo_limpo = df_novo.drop_duplicates(subset=['clinica', 'exame', 'data', 'horario'], keep='first')
        duplicatas_internas = len(df_novo) - len(df_novo_limpo)
        
        # Verificar se já existe planilha anterior
        df_existente = carregar_excel()
        
        if df_existente is not None and len(df_existente) > 0:
            # JUNTAR com planilha existente
            # Criar chaves únicas para comparação
            df_existente['_chave'] = (df_existente['clinica'].astype(str) + '|' + 
                                     df_existente['exame'].astype(str) + '|' + 
                                     df_existente['data'].astype(str) + '|' + 
                                     df_existente['horario'].astype(str))
            
            df_novo_limpo['_chave'] = (df_novo_limpo['clinica'].astype(str) + '|' + 
                                       df_novo_limpo['exame'].astype(str) + '|' + 
                                       df_novo_limpo['data'].astype(str) + '|' + 
                                       df_novo_limpo['horario'].astype(str))
            
            # Adicionar apenas horários novos (que não existem)
            chaves_existentes = set(df_existente['_chave'].values)
            mask_novos = ~df_novo_limpo['_chave'].isin(chaves_existentes)
            df_adicionar = df_novo_limpo[mask_novos].copy()
            
            # Remover coluna auxiliar
            df_existente = df_existente.drop(columns=['_chave'])
            df_adicionar = df_adicionar.drop(columns=['_chave'])
            
            # Concatenar
            df_final = pd.concat([df_existente, df_adicionar], ignore_index=True)
            
            horarios_adicionados = len(df_adicionar)
            horarios_duplicados = len(df_novo_limpo) - len(df_adicionar) + duplicatas_internas
        else:
            # Primeira planilha
            df_final = df_novo_limpo
            horarios_adicionados = len(df_novo_limpo)
            horarios_duplicados = duplicatas_internas
        
        # Salvar planilha consolidada
        salvar_excel(df_final)
        
        total_vagas = len(df_final[df_final["disponivel"] == "SIM"])
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"✅ Planilha adicionada com sucesso!",
            "total_horarios": len(df_final),
            "vagas_disponiveis": total_vagas,
            "horarios_adicionados": horarios_adicionados,
            "horarios_duplicados": horarios_duplicados
        })
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar planilha: {str(e)}"}), 500

@app.route('/api/status-excel')
def status_excel():
    """Verifica se Excel está carregado"""
    if dados_sistema["excel_carregado"]:
        df = carregar_excel()
        total = len(df)
        disponiveis = len(df[df["disponivel"] == "SIM"])
        ocupadas = len(df[df["disponivel"] != "SIM"])
        
        return jsonify({
            "carregado": True,
            "total_horarios": total,
            "vagas_disponiveis": disponiveis,
            "vagas_ocupadas": ocupadas
        })
    else:
        return jsonify({
            "carregado": False,
            "mensagem": "Nenhuma planilha carregada"
        })

@app.route('/api/limpar-excel', methods=['POST'])
def limpar_excel():
    """Remove toda a planilha do sistema"""
    try:
        if os.path.exists(EXCEL_PATH):
            os.remove(EXCEL_PATH)
        dados_sistema["excel_carregado"] = False
        return jsonify({
            "sucesso": True,
            "mensagem": "Planilha removida com sucesso"
        })
    except Exception as e:
        return jsonify({"erro": f"Erro ao remover planilha: {str(e)}"}), 500

@app.route('/simulador')
def simulador():
    """Interface de simulação de conversa WhatsApp"""
    return render_template('simulador.html')

@app.route('/api/simulador/conversas')
def listar_conversas():
    """Lista todos os agendamentos para simulação"""
    conversas = []
    for ag in dados_sistema["agendamentos"]:
        conversas.append({
            "id": ag["id"],
            "paciente": ag["paciente"],
            "telefone": ag["telefone"],
            "exame": ag["exame"],
            "data": ag["data"],
            "horario": ag["horario"],
            "status": ag["status"]
        })
    return jsonify(conversas)

@app.route('/api/simulador/mensagem/<int:agendamento_id>')
def obter_mensagem(agendamento_id):
    """Obtém a mensagem inicial de agendamento"""
    agendamento = next((a for a in dados_sistema["agendamentos"] if a["id"] == agendamento_id), None)
    
    if not agendamento:
        return jsonify({"erro": "Agendamento não encontrado"}), 404
    
    # Regenerar orientações
    orientacoes = gerar_orientacoes_educativas(agendamento["exame"])
    
    mensagem = f"""✅ AGENDAMENTO CONFIRMADO

Olá, {agendamento['paciente']}!

Sua consulta foi agendada:
📅 Data: {agendamento['data']}
⏰ Horário: {agendamento['horario']}
🏥 Local: {agendamento['clinica']}
👨‍⚕️ Especialidade: {agendamento['exame']}

{orientacoes}

📌 Lembretes automáticos:
   • 7, 5, 3 dias e 24h antes

Responda:
1 - Confirmar
2 - Cancelar"""
    
    return jsonify({
        "mensagem": mensagem,
        "paciente": agendamento['paciente'],
        "telefone": agendamento['telefone'],
        "status": agendamento['status'],
        "audio_url": agendamento.get('audio_url'),
        "idade": agendamento.get('idade')
    })

@app.route('/api/simulador/responder/<int:agendamento_id>', methods=['POST'])
def responder_simulador(agendamento_id):
    """Processa resposta do paciente no simulador"""
    data = request.json
    resposta = data.get("resposta", "").strip()
    
    agendamento = next((a for a in dados_sistema["agendamentos"] if a["id"] == agendamento_id), None)
    
    if not agendamento:
        return jsonify({"erro": "Agendamento não encontrado"}), 404
    
    if resposta == "1" or "confirmar" in resposta.lower():
        # Confirmar consulta
        agendamento["status"] = "confirmado"
        dados_sistema["metricas"]["confirmados"] += 1
        
        mensagem_resposta = '✅ Consulta confirmada com sucesso!\n\nVocê receberá lembretes automáticos:\n• 7 dias antes\n• 5 dias antes\n• 3 dias antes\n• 24 horas antes\n\nNos vemos em breve! 😊'
        
    elif resposta == "2" or "cancelar" in resposta.lower():
        # Cancelar consulta
        agendamento["status"] = "cancelado"
        dados_sistema["metricas"]["cancelados"] += 1
        
        # Liberar vaga no Excel
        try:
            df = carregar_excel()
            if df is not None:
                # Encontrar a vaga
                mask = (df["paciente"] == agendamento["paciente"]) & \
                       (df["telefone"] == agendamento["telefone"]) & \
                       (df["data"] == agendamento["data"]) & \
                       (df["horario"] == agendamento["horario"])
                
                if mask.any():
                    idx = df[mask].index[0]
                    df.at[idx, "disponivel"] = str("SIM")
                    df.at[idx, "paciente"] = str("")
                    df.at[idx, "telefone"] = str("")
                    salvar_excel(df)
        except Exception as e:
            print(f"Erro ao liberar vaga: {e}")
        
        # Notificar operador
        dados_sistema["notificacoes"].append({
            "tipo": "CANCELAMENTO",
            "mensagem": f"❌ {agendamento['paciente']} cancelou {agendamento['exame']}",
            "horario": datetime.now().strftime("%H:%M")
        })
        
        mensagem_resposta = '❌ Consulta cancelada.\n\nSua vaga foi liberada para outro paciente.\n\nPrecisa reagendar? Entre em contato com a unidade de saúde.\n\n📞 Telefone: (11) 3000-0000'
        
    else:
        mensagem_resposta = '😊 Por nada!\n\nQualquer dúvida, estamos à disposição.\n\nAté logo! 👋'
    
    return jsonify({
        "sucesso": True,
        "mensagem": mensagem_resposta,
        "status": agendamento["status"]
    })

@app.route('/api/download-excel')
def download_excel():
    """Download da planilha consolidada"""
    if not os.path.exists(EXCEL_PATH):
        return jsonify({"erro": "Nenhuma planilha disponível para download"}), 404
    
    try:
        # Carregar, limpar NaN e salvar temporariamente
        df = pd.read_excel(EXCEL_PATH)
        df = df.fillna('')  # Substitui NaN por string vazia
        
        # Salvar versão limpa
        temp_path = EXCEL_PATH.replace('.xlsx', '_temp.xlsx')
        df.to_excel(temp_path, index=False)
        
        # Enviar arquivo
        response = send_file(
            temp_path,
            as_attachment=True,
            download_name=f'planilha_consolidada_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Remover arquivo temporário após envio
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
        
        return response
    except Exception as e:
        return jsonify({"erro": f"Erro ao baixar planilha: {str(e)}"}), 500

@app.route('/relatorios')
def relatorios():
    """Página de relatórios"""
    return render_template('relatorios.html')

# ==================== ROTAS WHATSAPP EVOLUTION API ====================

@app.route('/api/whatsapp/status')
def whatsapp_status():
    """Verifica status da conexão WhatsApp"""
    status = whatsapp_client.verificar_status_instancia()
    return jsonify(status)

@app.route('/api/whatsapp/qrcode')
def whatsapp_qrcode():
    """Obtém QR Code para conectar WhatsApp"""
    resultado = whatsapp_client.obter_qrcode()
    return jsonify(resultado)

@app.route('/api/whatsapp/criar-instancia', methods=['POST'])
def whatsapp_criar_instancia():
    """Cria nova instância WhatsApp"""
    resultado = whatsapp_client.criar_instancia()
    return jsonify(resultado)

@app.route('/api/whatsapp/config')
def whatsapp_config():
    """Retorna configurações atuais"""
    return jsonify({
        "base_url": whatsapp_client.base_url,
        "instance_name": whatsapp_client.instance_name,
        "modo_simulacao": whatsapp_client.modo_simulacao,
        "api_configurada": not whatsapp_client.modo_simulacao
    })

@app.route('/whatsapp-config')
def whatsapp_config_page():
    """Página de configuração WhatsApp"""
    return render_template('whatsapp_config.html')

@app.route('/api/whatsapp/configurar-webhook', methods=['POST'])
def whatsapp_configurar_webhook():
    """Configura webhook na Evolution API"""
    try:
        data = request.get_json() or {}
        webhook_url = data.get('webhook_url') or f"{request.host_url}webhook/whatsapp"
        resultado = whatsapp_client.configurar_webhook(webhook_url)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500

@app.route('/webhook/whatsapp', methods=['POST', 'GET'])
def webhook_whatsapp():
    """Recebe mensagens do WhatsApp"""
    if request.method == 'GET':
        return jsonify({"status": "webhook ativo", "url": request.url}), 200
    
    try:
        dados = request.get_json()
        print(f"\n{'='*60}")
        print(f"📨 WEBHOOK RECEBIDO!")
        print(f"{'='*60}")
        print(f"Dados completos: {json.dumps(dados, indent=2)}")
        
        # Verificar tipo de evento
        evento = dados.get('event') if dados else None
        print(f"🔍 Evento: {evento}")
        
        if not dados or evento != 'messages.upsert':
            print(f"⏭️ Ignorando evento: {evento}")
            return jsonify({"status": "ignored", "evento": evento}), 200
        
        # Extrair dados
        mensagem_data = dados.get('data', {})
        key_info = mensagem_data.get('key', {})
        mensagem_info = mensagem_data.get('message', {})
        
        print(f"🔍 Key info: {key_info}")
        print(f"🔍 Message info: {mensagem_info}")
        
        # Ignorar mensagens enviadas por nós
        if key_info.get('fromMe'):
            print("⏭️ Mensagem enviada por nós, ignorando")
            return jsonify({"status": "ignored", "motivo": "fromMe"}), 200
        
        # Número do remetente
        numero_completo = key_info.get('remoteJid', '')
        numero = numero_completo.replace('@s.whatsapp.net', '')
        
        # Texto da mensagem
        texto = mensagem_info.get('conversation') or mensagem_info.get('extendedTextMessage', {}).get('text', '')
        texto = texto.strip()
        
        print(f"📱 Número: {numero}")
        print(f"💬 Mensagem: '{texto}'")
        print(f"{'='*60}\n")
        
        # Processar resposta
        if texto in ['1', '2']:
            print(f"✅ Iniciando processamento da resposta '{texto}'")
            Thread(target=processar_resposta_paciente, args=(numero, texto)).start()
        else:
            print(f"⏭️ Mensagem '{texto}' não é 1 ou 2, ignorando")
        
        return jsonify({"status": "ok", "numero": numero, "texto": texto}), 200
        
    except Exception as e:
        print(f"❌ ERRO NO WEBHOOK: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "erro": str(e)}), 500

def processar_resposta_paciente(telefone, resposta):
    """Processa resposta 1=Confirmar ou 2=Cancelar"""
    try:
        print(f"\n{'='*60}")
        print(f"🔄 PROCESSANDO RESPOSTA")
        print(f"{'='*60}")
        print(f"Telefone recebido: {telefone}")
        print(f"Resposta: {resposta}")
        
        df = carregar_excel()
        if df is None:
            print("❌ Planilha não encontrada")
            return
        
        # Buscar pelo telefone (remover 55 se tiver)
        tel_busca = telefone[2:] if telefone.startswith('55') else telefone
        print(f"🔍 Buscando por: {tel_busca}")
        
        df['telefone'] = df['telefone'].astype(str)
        
        # Debug: mostrar todos os telefones na planilha
        print(f"📋 Telefones na planilha: {df['telefone'].tolist()}")
        
        agendamento = df[df['telefone'].str.contains(tel_busca, na=False)]
        
        if agendamento.empty:
            print(f"⚠️ Nenhum agendamento encontrado para: {tel_busca}")
            print(f"Tentando buscar sem os dois primeiros dígitos...")
            # Tentar sem DDD também
            tel_sem_ddd = tel_busca[2:] if len(tel_busca) > 9 else tel_busca
            agendamento = df[df['telefone'].str.contains(tel_sem_ddd, na=False)]
            
        if agendamento.empty:
            print(f"❌ Definitivamente não encontrado")
            return
        
        print(f"✅ Agendamento encontrado!")
        
        idx = agendamento.index[0]
        paciente = df.at[idx, 'paciente']
        
        if resposta == '1':
            # CONFIRMAR
            if 'status_confirmacao' not in df.columns:
                df['status_confirmacao'] = ''
            df.at[idx, 'status_confirmacao'] = 'CONFIRMADO'
            salvar_excel(df)
            
            dados_sistema['metricas']['confirmados'] += 1
            
            msg = f"""✅ *Consulta Confirmada!*

Olá, {paciente}!

Sua consulta foi confirmada com sucesso.

📅 Compareça no dia e horário agendados
📋 Leve documentos e exames anteriores
⏰ Chegue 15 minutos antes

Obrigado! 🏥"""
            
            whatsapp_client.enviar_mensagem_texto(telefone, msg)
            print(f"✅ Confirmação enviada: {paciente}")
            
        elif resposta == '2':
            # CANCELAR
            df.at[idx, 'disponivel'] = 'SIM'
            df.at[idx, 'paciente'] = ''
            df.at[idx, 'telefone'] = ''
            if 'status_confirmacao' in df.columns:
                df.at[idx, 'status_confirmacao'] = ''
            salvar_excel(df)
            
            dados_sistema['metricas']['cancelados'] += 1
            
            msg = f"""❌ *Consulta Cancelada*

Olá, {paciente}.

Sua consulta foi cancelada.
O horário está disponível novamente.

Para reagendar, entre em contato com a UBS.

Obrigado! 🏥"""
            
            whatsapp_client.enviar_mensagem_texto(telefone, msg)
            print(f"❌ Cancelamento processado: {paciente}")
            
    except Exception as e:
        print(f"❌ Erro ao processar resposta: {e}")

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏥 SISTEMA DE AGENDAMENTOS SUS v2.0 - Fluxo Operador")
    print("="*70)
    print("\n🚀 Inicializando sistema...")
    
    # Verificar Excel
    df = carregar_excel()
    if df is not None:
        print(f"✅ Excel encontrado: {len(df)} horários")
    else:
        print("⚠️  Nenhuma planilha carregada - faça upload no sistema")
    
    print("\n" + "="*70)
    print("📋 FLUXO DO SISTEMA:")
    print("="*70)
    print("1️⃣  Operador faz UPLOAD da planilha Excel de horários")
    print("2️⃣  Operador cadastra: Nome + Telefone + Exame")
    print("3️⃣  Sistema BUSCA AUTOMATICAMENTE vaga na planilha")
    print("4️⃣  WhatsApp enviado INSTANTANEAMENTE para o paciente")
    print("5️⃣  Lembretes automáticos: 7, 5, 3 dias e 24h antes")
    print("6️⃣  Se cancelar: Operador é notificado + Horário liberado")
    print("="*70)
    print("\n📱 Abra no navegador: http://localhost:5000")
    print("="*70 + "\n")
    
    # Porta dinâmica para Railway, 5000 para local
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
