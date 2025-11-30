"""
🏥 SISTEMA DE AGENDAMENTOS SUS - Hackapel 2025
Versão 3.0 - WhatsApp com TTS (Text-to-Speech)
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from datetime import datetime
import os
from threading import Thread
import time
import google.generativeai as genai
from gtts import gTTS
import uuid
from whatsapp_integration import whatsapp_client, MensagensSUS
import requests

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURAÇÃO ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, 'agenda_clinicas.xlsx')
AUDIO_PATH = os.path.join(BASE_DIR, 'static', 'audios')

os.makedirs(AUDIO_PATH, exist_ok=True)

# Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    modelo_gemini = genai.GenerativeModel('gemini-2.5-flash')
else:
    modelo_gemini = None

# Controle
mensagens_processadas = set()
dados_sistema = {
    "metricas": {"agendados": 0, "confirmados": 0, "cancelados": 0},
    "agendamentos": [],
    "excel_carregado": False
}

# ==================== EXCEL ====================

def carregar_excel():
    """Carrega planilha de horários"""
    if not os.path.exists(EXCEL_PATH):
        dados_sistema["excel_carregado"] = False
        return None
    
    df = pd.read_excel(EXCEL_PATH, dtype={'telefone': str})
    if 'telefone' in df.columns:
        df['telefone'] = df['telefone'].apply(
            lambda x: str(x).replace('.0', '').replace("'", '').strip() 
            if pd.notna(x) and str(x) != 'nan' else ''
        )
    dados_sistema["excel_carregado"] = True
    return df

def salvar_excel(df):
    """Salva planilha com telefones em formato texto"""
    df = df.fillna('')
    if 'telefone' in df.columns:
        df['telefone'] = df['telefone'].apply(
            lambda x: str(x).replace('.0', '').replace("'", '').strip() 
            if x and str(x) not in ['', 'nan'] else ''
        )
    
    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        ws = writer.sheets['Sheet1']
        if 'telefone' in df.columns:
            col = df.columns.get_loc('telefone') + 1
            for row in range(2, len(df) + 2):
                cell = ws.cell(row=row, column=col)
                cell.number_format = '@'
                if cell.value:
                    cell.value = str(cell.value)
    
    dados_sistema["excel_carregado"] = True

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
    return render_template('index.html', metricas=dados_sistema["metricas"])

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
    
    # Calcular idade
    try:
        nasc = datetime.strptime(data_nascimento, "%Y-%m-%d")
        hoje = datetime.now()
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except:
        return jsonify({"erro": "Data inválida"}), 400
    
    # Carregar Excel
    df = carregar_excel()
    if df is None:
        return jsonify({"erro": "Carregue a planilha primeiro"}), 400
    
    # Buscar vaga
    vaga = df[(df["exame"] == exame) & (df["disponivel"] == "SIM")]
    if vaga.empty:
        return jsonify({"erro": f"Sem vagas para {exame}"}), 404
    
    # Reservar vaga
    idx = vaga.index[0]
    info = vaga.iloc[0]
    
    # Converter colunas para object/string para evitar warnings do pandas
    for col in ['disponivel', 'paciente', 'telefone']:
        df[col] = df[col].astype(str)
    if 'status_confirmacao' not in df.columns:
        df['status_confirmacao'] = ''
    df['status_confirmacao'] = df['status_confirmacao'].astype(str)
    
    df.at[idx, "disponivel"] = "NAO"
    df.at[idx, "paciente"] = str(nome)
    df.at[idx, "telefone"] = str(telefone)
    df.at[idx, "status_confirmacao"] = "PENDENTE"
    
    salvar_excel(df)
    
    # Criar agendamento
    agendamento = {
        "id": len(dados_sistema["agendamentos"]) + 1,
        "paciente": nome, "telefone": telefone, "idade": idade,
        "exame": exame, "clinica": info["clinica"],
        "data": info["data"], "horario": info["horario"],
        "status": "pendente"
    }
    dados_sistema["agendamentos"].append(agendamento)
    dados_sistema["metricas"]["agendados"] += 1
    
    # Criar mensagem
    orientacoes = gerar_orientacoes(exame)
    mensagem = MensagensSUS.agendamento_confirmado(
        nome, exame, info['data'], info['horario'], info['clinica'],
        idade if idade >= 60 else None
    )
    if orientacoes:
        mensagem += f"\n\n{orientacoes}"
    
    # Enviar WhatsApp + TTS
    resultado = whatsapp_client.enviar_mensagem_completa(telefone, mensagem, com_audio=True)
    
    # Áudio extra para idosos
    if idade >= 60:
        audio = gerar_audio_idoso(nome, idade, exame, info['data'], info['horario'], info['clinica'])
        if audio:
            url = f"{request.host_url}static/audios/{audio}"
            whatsapp_client.enviar_audio(telefone, url)
    
    return jsonify({
        "sucesso": True, 
        "agendamento": agendamento,
        "mensagem": mensagem
    })

@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    """Upload de planilha"""
    if 'file' not in request.files:
        return jsonify({"erro": "Nenhum arquivo"}), 400
    
    file = request.files['file']
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"erro": "Arquivo deve ser Excel"}), 400
    
    try:
        df_novo = pd.read_excel(file)
        colunas = ["clinica", "exame", "data", "horario", "disponivel"]
        if not all(c in df_novo.columns for c in colunas):
            return jsonify({"erro": f"Faltam colunas: {colunas}"}), 400
        
        for col in ["paciente", "telefone", "status_confirmacao"]:
            if col not in df_novo.columns:
                df_novo[col] = ""
        
        # Juntar com existente se houver
        df_existente = carregar_excel()
        if df_existente is not None:
            df_existente['_key'] = df_existente.apply(
                lambda r: f"{r['clinica']}|{r['exame']}|{r['data']}|{r['horario']}", axis=1)
            df_novo['_key'] = df_novo.apply(
                lambda r: f"{r['clinica']}|{r['exame']}|{r['data']}|{r['horario']}", axis=1)
            
            novos = df_novo[~df_novo['_key'].isin(df_existente['_key'])]
            df_final = pd.concat([
                df_existente.drop(columns=['_key']), 
                novos.drop(columns=['_key'])
            ], ignore_index=True)
        else:
            df_final = df_novo
        
        salvar_excel(df_final)
        vagas = len(df_final[df_final["disponivel"] == "SIM"])
        
        return jsonify({
            "sucesso": True,
            "total_horarios": len(df_final),
            "vagas_disponiveis": vagas
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/status-excel')
def status_excel():
    """Status da planilha"""
    df = carregar_excel()
    if df is None:
        return jsonify({"carregado": False})
    
    return jsonify({
        "carregado": True,
        "total_horarios": len(df),
        "vagas_disponiveis": len(df[df["disponivel"] == "SIM"]),
        "vagas_ocupadas": len(df[df["disponivel"] != "SIM"])
    })

@app.route('/api/metricas')
def metricas():
    return jsonify(dados_sistema["metricas"])

@app.route('/api/agendamentos')
def agendamentos():
    return jsonify(dados_sistema["agendamentos"][-20:])

@app.route('/api/download-excel')
def download_excel():
    """Download da planilha"""
    if not os.path.exists(EXCEL_PATH):
        return jsonify({"erro": "Nenhuma planilha"}), 404
    return send_file(EXCEL_PATH, as_attachment=True, 
                    download_name=f'agendamentos_{datetime.now().strftime("%Y%m%d")}.xlsx')

@app.route('/api/limpar-excel', methods=['POST'])
def limpar_excel():
    """Remove planilha"""
    if os.path.exists(EXCEL_PATH):
        os.remove(EXCEL_PATH)
    dados_sistema["excel_carregado"] = False
    return jsonify({"sucesso": True})

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

@app.route('/simulador')
def simulador():
    return render_template('simulador.html')

@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')

# ==================== PROCESSAMENTO DE RESPOSTAS ====================

def processar_resposta(telefone, resposta):
    """Processa resposta 1=Confirmar ou 2=Cancelar"""
    try:
        df = carregar_excel()
        if df is None:
            return
        
        # Normalizar telefone
        tel = ''.join(c for c in str(telefone) if c.isdigit())
        if tel.startswith('55') and len(tel) > 11:
            tel = tel[2:]
        
        # Buscar paciente
        df['_tel'] = df['telefone'].apply(lambda x: ''.join(c for c in str(x) if c.isdigit()))
        mask = df['_tel'].str.contains(tel[-9:], na=False)
        
        if not mask.any():
            print(f"❌ Telefone {tel} não encontrado")
            return
        
        idx = df[mask].index[0]
        paciente = df.at[idx, 'paciente']
        
        if resposta == '1':
            # Confirmar
            df.at[idx, 'status_confirmacao'] = 'CONFIRMADO'
            salvar_excel(df)
            dados_sistema['metricas']['confirmados'] += 1
            
            msg = MensagensSUS.consulta_confirmada(paciente)
            whatsapp_client.enviar_mensagem_completa(telefone, msg, com_audio=True)
            print(f"✅ CONFIRMADO: {paciente}")
            
        elif resposta == '2':
            # Cancelar e liberar vaga
            df.at[idx, 'disponivel'] = 'SIM'
            df.at[idx, 'paciente'] = ''
            df.at[idx, 'telefone'] = ''
            df.at[idx, 'status_confirmacao'] = 'CANCELADO'
            salvar_excel(df)
            dados_sistema['metricas']['cancelados'] += 1
            
            msg = MensagensSUS.consulta_cancelada(paciente)
            whatsapp_client.enviar_mensagem_completa(telefone, msg, com_audio=True)
            print(f"❌ CANCELADO: {paciente}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

# ==================== POLLING ====================

def polling_whatsapp():
    """Verifica mensagens a cada 15 segundos"""
    print("🔄 Polling iniciado")
    
    while True:
        try:
            time.sleep(15)
            
            url = os.environ.get('EVOLUTION_API_URL', '')
            key = os.environ.get('EVOLUTION_API_KEY', '')
            instance = os.environ.get('EVOLUTION_INSTANCE', 'sus-agendamentos')
            
            if not url or not key:
                continue
            
            if not url.startswith('http'):
                url = f'https://{url}'
            
            resp = requests.post(
                f"{url}/chat/findMessages/{instance}",
                headers={'apikey': key, 'Content-Type': 'application/json'},
                json={'where': {'key': {'fromMe': False}}, 'limit': 3},
                timeout=10
            )
            
            if resp.status_code != 200:
                continue
            
            dados = resp.json()
            msgs = dados if isinstance(dados, list) else dados.get('messages', [])
            
            for msg in msgs:
                key_data = msg.get('key', {})
                msg_id = key_data.get('id')
                
                if msg_id in mensagens_processadas or key_data.get('fromMe'):
                    continue
                
                mensagens_processadas.add(msg_id)
                
                numero = key_data.get('remoteJid', '').replace('@s.whatsapp.net', '')
                texto = msg.get('message', {}).get('conversation', '').strip()
                
                if texto in ['1', '2']:
                    print(f"📱 {numero}: '{texto}'")
                    Thread(target=processar_resposta, args=(numero, texto)).start()
            
            # Limpar cache
            if len(mensagens_processadas) > 100:
                mensagens_processadas.clear()
                
        except Exception as e:
            print(f"⚠️ Polling erro: {e}")
            time.sleep(30)

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 SISTEMA SUS - Hackapel 2025 v3.0")
    print("="*60)
    
    # Detectar Railway
    railway = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
    if railway:
        os.environ['PUBLIC_URL'] = railway
        print(f"🌐 URL: https://{railway}")
    
    # Verificar Excel
    df = carregar_excel()
    if df is not None:
        print(f"✅ Excel: {len(df)} horários")
    
    # Iniciar polling
    Thread(target=polling_whatsapp, daemon=True).start()
    print("✅ Polling WhatsApp ativo (15s)")
    print("🔊 TTS ativo em todas mensagens")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"📱 http://localhost:{port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
