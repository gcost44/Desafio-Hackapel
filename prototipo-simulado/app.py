"""
🏥 SISTEMA DE AGENDAMENTOS SUS - Hackapel 2025
Versão 4.0 - Google Sheets + WhatsApp + TTS
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from threading import Thread
import time
import google.generativeai as genai
from gtts import gTTS
import uuid
from whatsapp_integration import whatsapp_client, MensagensSUS
from google_sheets import sheets_client
import requests

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURAÇÃO ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_PATH = os.path.join(BASE_DIR, 'static', 'audios')
os.makedirs(AUDIO_PATH, exist_ok=True)

# Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    modelo_gemini = genai.GenerativeModel('gemini-2.5-flash')
else:
    modelo_gemini = None

# Controle de mensagens processadas
mensagens_processadas = set()

# ==================== IA GEMINI ====================

def gerar_orientacoes(exame):
    """Gera orientações educativas com IA"""
    if not modelo_gemini:
        return ""
    
    try:
        prompt = f"""Você é um médico do SUS. Crie orientações CURTAS para consulta de {exame}.
Formato:
📋 O que levar: [3 itens]
⚠️ Jejum: [Sim/Não]
💡 Dica preventiva específica de {exame}

Máximo 50 palavras."""
        
        resposta = modelo_gemini.generate_content(prompt)
        return resposta.text.strip()
    except:
        return ""

# ==================== ÁUDIO IDOSOS ====================

def gerar_audio_idoso(nome, idade, exame, data, horario, clinica):
    """Gera áudio especial para idosos (60+)"""
    try:
        texto = f"""Olá {nome}! Sua consulta de {exame} foi confirmada para {data} às {horario} 
no local {clinica}. Como você tem {idade} anos, tem direito a atendimento prioritário. 
Leve RG, Cartão SUS e exames anteriores. Chegue 15 minutos antes."""
        
        filename = f"idoso_{uuid.uuid4().hex[:8]}.mp3"
        tts = gTTS(text=texto, lang='pt', slow=False)
        tts.save(os.path.join(AUDIO_PATH, filename))
        return filename
    except:
        return None

# ==================== ROTAS PRINCIPAIS ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/agendar', methods=['POST'])
def agendar():
    """Cadastra paciente e envia WhatsApp + Áudio"""
    data = request.json
    nome = data.get("nome", "").strip()
    telefone = data.get("telefone", "").strip()
    data_nascimento = data.get("data_nascimento", "").strip()
    exame = data.get("exame", "").strip()
    
    if not all([nome, telefone, exame, data_nascimento]):
        return jsonify({"erro": "Preencha todos os campos"}), 400
    
    # Verificar conexão com Google Sheets
    if not sheets_client.conectado:
        return jsonify({"erro": "Google Sheets não conectado. Configure as credenciais."}), 400
    
    # Calcular idade
    try:
        nasc = datetime.strptime(data_nascimento, "%Y-%m-%d")
        hoje = datetime.now()
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except:
        return jsonify({"erro": "Data inválida"}), 400
    
    # Buscar vaga no Google Sheets
    linha, info = sheets_client.buscar_vaga(exame)
    if linha is None:
        return jsonify({"erro": f"Sem vagas para {exame}"}), 404
    
    # Reservar vaga
    sucesso = sheets_client.reservar_vaga(linha, nome, telefone)
    if not sucesso:
        return jsonify({"erro": "Erro ao reservar vaga"}), 500
    
    # Criar resposta
    agendamento = {
        "id": linha,
        "paciente": nome, 
        "telefone": telefone, 
        "idade": idade,
        "exame": exame, 
        "clinica": info.get("clinica", ""),
        "data": info.get("data", ""), 
        "horario": info.get("horario", ""),
        "status": "pendente"
    }
    
    # Criar mensagem
    orientacoes = gerar_orientacoes(exame)
    mensagem = MensagensSUS.agendamento_confirmado(
        nome, exame, info.get('data', ''), info.get('horario', ''), info.get('clinica', ''),
        idade if idade >= 60 else None
    )
    if orientacoes:
        mensagem += f"\n\n{orientacoes}"
    
    # Enviar WhatsApp + TTS
    whatsapp_client.enviar_mensagem_completa(telefone, mensagem, com_audio=True)
    
    # Áudio extra para idosos
    if idade >= 60:
        audio = gerar_audio_idoso(nome, idade, exame, info.get('data', ''), info.get('horario', ''), info.get('clinica', ''))
        if audio:
            url = f"{request.host_url}static/audios/{audio}"
            whatsapp_client.enviar_audio(telefone, url)
    
    return jsonify({
        "sucesso": True, 
        "agendamento": agendamento,
        "mensagem": mensagem
    })

@app.route('/api/status-excel')
def status_excel():
    """Status da planilha Google Sheets"""
    return jsonify(sheets_client.status_planilha())

@app.route('/api/metricas')
def metricas():
    """Retorna métricas do Google Sheets"""
    return jsonify(sheets_client.contar_metricas())

@app.route('/api/agendamentos')
def agendamentos():
    """Retorna lista de agendamentos"""
    return jsonify(sheets_client.listar_agendamentos()[-20:])

# ==================== WHATSAPP ====================

@app.route('/api/whatsapp/status')
def whatsapp_status():
    return jsonify(whatsapp_client.verificar_conexao())

@app.route('/api/whatsapp/qrcode')
def whatsapp_qrcode():
    return jsonify(whatsapp_client.obter_qrcode())

@app.route('/whatsapp-config')
def whatsapp_config():
    return render_template('whatsapp_config.html')

# ==================== WEBHOOK EVOLUTION API ====================

@app.route('/webhook/evolution', methods=['POST'])
def webhook_evolution():
    """Recebe mensagens da Evolution API via Webhook"""
    try:
        data = request.json
        print(f"📩 Webhook recebido: {data}")
        
        event = data.get('event', '')
        
        if event == 'messages.upsert':
            messages = data.get('data', [])
            if not isinstance(messages, list):
                messages = [messages]
            
            for msg in messages:
                key = msg.get('key', {})
                
                if key.get('fromMe'):
                    continue
                
                msg_id = key.get('id', '')
                if msg_id in mensagens_processadas:
                    continue
                
                mensagens_processadas.add(msg_id)
                
                numero = key.get('remoteJid', '').replace('@s.whatsapp.net', '')
                
                message_content = msg.get('message', {})
                texto = (
                    message_content.get('conversation') or
                    message_content.get('extendedTextMessage', {}).get('text') or
                    ''
                ).strip()
                
                print(f"📱 Mensagem de {numero}: '{texto}'")
                
                if texto in ['1', '2']:
                    print(f"✅ Processando resposta {texto} de {numero}")
                    Thread(target=processar_resposta, args=(numero, texto)).start()
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"❌ Erro webhook: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/webhook/evolution', methods=['GET'])
def webhook_evolution_verify():
    """Verificação do webhook"""
    return jsonify({"status": "webhook ativo", "sistema": "SUS Hackapel 2025"})

@app.route('/simulador')
def simulador():
    return render_template('simulador.html')

@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')

# ==================== PROCESSAMENTO DE RESPOSTAS ====================

def processar_resposta(telefone, resposta):
    """Processa resposta 1=Confirmar ou 2=Cancelar"""
    print(f"🔄 Processando resposta: telefone={telefone}, resposta={resposta}")
    
    try:
        if not sheets_client.conectado:
            print("❌ Google Sheets não conectado")
            return
        
        # Buscar paciente por telefone
        linha, dados = sheets_client.buscar_por_telefone(telefone)
        
        if linha is None:
            print(f"❌ Telefone {telefone} não encontrado")
            return
        
        paciente = dados.get('paciente', '')
        telefone_original = dados.get('telefone', telefone)
        print(f"✅ Paciente encontrado: {paciente} (linha {linha})")
        
        if resposta == '1':
            # Confirmar
            sheets_client.atualizar_status(linha, 'CONFIRMADO')
            
            msg = MensagensSUS.consulta_confirmada(paciente)
            print(f"📤 Enviando confirmação para {telefone_original}")
            whatsapp_client.enviar_mensagem_completa(telefone_original, msg, com_audio=True)
            print(f"✅ CONFIRMADO: {paciente}")
            
        elif resposta == '2':
            # Cancelar e liberar vaga
            sheets_client.liberar_vaga(linha)
            
            msg = MensagensSUS.consulta_cancelada(paciente)
            print(f"📤 Enviando cancelamento para {telefone_original}")
            whatsapp_client.enviar_mensagem_completa(telefone_original, msg, com_audio=True)
            print(f"❌ CANCELADO: {paciente}")
            
    except Exception as e:
        print(f"❌ Erro ao processar resposta: {e}")
        import traceback
        traceback.print_exc()

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 SISTEMA SUS - Hackapel 2025 v4.0")
    print("📊 Google Sheets + WhatsApp + TTS")
    print("="*60)
    
    # Detectar Railway
    railway = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
    if railway:
        os.environ['PUBLIC_URL'] = railway
        print(f"🌐 URL: https://{railway}")
    
    # Status Google Sheets
    if sheets_client.conectado:
        status = sheets_client.status_planilha()
        print(f"✅ Google Sheets: {status.get('total_horarios', 0)} horários")
    else:
        print("⚠️ Google Sheets: Não conectado")
    
    print("🔊 TTS ativo em todas mensagens")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"📱 http://localhost:{port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
