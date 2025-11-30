"""
🟢 WhatsApp Integration - Evolution API v2
Sistema SUS Hackapel 2025
"""

import requests
import os
import uuid
from gtts import gTTS

# ==================== CONFIGURAÇÃO ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, 'static', 'audios')
os.makedirs(AUDIO_DIR, exist_ok=True)

def get_public_url():
    """Retorna URL pública para áudios"""
    domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
    if domain:
        return f"https://{domain}"
    return f"http://localhost:{os.environ.get('PORT', 5000)}"

# ==================== TEXT-TO-SPEECH ====================

class TTS:
    """Gerador de áudio"""
    
    @staticmethod
    def gerar(texto):
        """Gera MP3 a partir de texto"""
        try:
            # Limpar emojis
            for emoji in ['✅', '❌', '📅', '⏰', '🏥', '👨‍⚕️', '👴', '👵', '📲', '1️⃣', '2️⃣', '🔔', '⚠️', '📞', '💡', '📋']:
                texto = texto.replace(emoji, '')
            texto = texto.replace('\n', '. ')
            
            filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            path = os.path.join(AUDIO_DIR, filename)
            
            tts = gTTS(text=texto, lang='pt-br', slow=False)
            tts.save(path)
            
            return {"sucesso": True, "url": f"{get_public_url()}/static/audios/{filename}"}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

# ==================== CLIENTE WHATSAPP ====================

class WhatsAppClient:
    """Cliente Evolution API"""
    
    def __init__(self):
        url = os.environ.get('EVOLUTION_API_URL', '')
        # Garantir que tem protocolo https
        if url and not url.startswith('http'):
            url = f"https://{url}"
        self.base_url = url.rstrip('/') if url else ''
        self.api_key = os.environ.get('EVOLUTION_API_KEY', '')
        self.instance = os.environ.get('EVOLUTION_INSTANCE', 'sus-agendamentos')
        self.headers = {'Content-Type': 'application/json', 'apikey': self.api_key}
        self.modo_simulacao = not self.api_key or not self.base_url
        
        print(f"🔧 WhatsApp Config:")
        print(f"   URL: {self.base_url}")
        print(f"   Instance: {self.instance}")
        print(f"   API Key: {'✅ Configurada' if self.api_key else '❌ Não configurada'}")
        print(f"   Modo: {'⚠️ SIMULAÇÃO' if self.modo_simulacao else '✅ PRODUÇÃO'}")
    
    def _formatar(self, tel):
        """Formata telefone para Evolution API (com código 55 do Brasil)"""
        num = ''.join(c for c in str(tel) if c.isdigit())
        
        # Garantir que tem código do Brasil (55)
        if not num.startswith('55'):
            num = '55' + num
        
        print(f"📞 Telefone formatado: {tel} -> {num}")
        return num
    
    def enviar_texto(self, telefone, msg):
        """Envia texto"""
        if self.modo_simulacao:
            print(f"📱 [SIMULAÇÃO] {telefone}: {msg[:50]}...")
            return {"sucesso": True, "simulado": True}
        
        try:
            numero = self._formatar(telefone)
            url = f"{self.base_url}/message/sendText/{self.instance}"
            payload = {"number": numero, "textMessage": {"text": msg}}
            
            print(f"📤 Enviando para: {url}")
            print(f"📦 Payload: number={numero}, msg={msg[:50]}...")
            
            resp = requests.post(url, headers=self.headers, json=payload, timeout=15)
            
            print(f"📡 Status: {resp.status_code}")
            print(f"📡 Resposta: {resp.text[:200] if resp.text else 'vazio'}")
            
            sucesso = resp.status_code in [200, 201]
            return {"sucesso": sucesso, "status": resp.status_code, "resposta": resp.text[:200]}
        except Exception as e:
            print(f"❌ Erro ao enviar: {e}")
            return {"sucesso": False, "erro": str(e)}
    
    def enviar_audio(self, telefone, url):
        """Envia áudio"""
        if self.modo_simulacao:
            return {"sucesso": True}
        
        try:
            resp = requests.post(
                f"{self.base_url}/message/sendMedia/{self.instance}",
                headers=self.headers,
                json={"number": self._formatar(telefone), "mediaMessage": {"mediatype": "audio", "media": url}},
                timeout=15
            )
            return {"sucesso": resp.status_code in [200, 201]}
        except:
            return {"sucesso": False}
    
    def enviar_mensagem_completa(self, telefone, msg, com_audio=True):
        """Envia texto + áudio TTS"""
        resultado = {"sucesso": False, "texto_enviado": False, "audio_enviado": False}
        
        # Texto
        res = self.enviar_texto(telefone, msg)
        resultado["texto_enviado"] = res.get("sucesso", False)
        resultado["sucesso"] = resultado["texto_enviado"]
        
        # Áudio TTS
        if com_audio:
            audio = TTS.gerar(msg)
            if audio.get("sucesso"):
                res = self.enviar_audio(telefone, audio["url"])
                resultado["audio_enviado"] = res.get("sucesso", False)
        
        return resultado
    
    def verificar_conexao(self):
        """Verifica status"""
        if self.modo_simulacao:
            return {"conectado": False, "simulacao": True}
        
        try:
            resp = requests.get(
                f"{self.base_url}/instance/connectionState/{self.instance}",
                headers=self.headers, timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                state = data.get('state') or data.get('instance', {}).get('state')
                return {"conectado": state == 'open', "status": state}
            return {"conectado": False}
        except:
            return {"conectado": False}
    
    def obter_qrcode(self):
        """Obtém QR Code"""
        if self.modo_simulacao:
            return {"sucesso": False, "erro": "API não configurada"}
        
        try:
            resp = requests.get(
                f"{self.base_url}/instance/connect/{self.instance}",
                headers=self.headers, timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return {"sucesso": True, "qrcode": data.get('base64')}
            elif resp.status_code == 404:
                # Criar instância
                resp = requests.post(
                    f"{self.base_url}/instance/create",
                    headers=self.headers,
                    json={"instanceName": self.instance, "qrcode": True},
                    timeout=10
                )
                if resp.status_code == 201:
                    return {"sucesso": True, "qrcode": resp.json().get('qrcode', {}).get('base64')}
            return {"sucesso": False}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    # Aliases para compatibilidade
    def verificar_status_instancia(self):
        return self.verificar_conexao()
    
    def criar_instancia(self):
        return self.obter_qrcode()

# ==================== TEMPLATES DE MENSAGENS ====================

class MensagensSUS:
    """Templates de mensagens"""
    
    @staticmethod
    def agendamento_confirmado(nome, exame, data, horario, clinica, idade=None):
        prioridade = f"\n👴 Idade: {idade} anos - ATENDIMENTO PRIORITÁRIO" if idade else ""
        return f"""✅ AGENDAMENTO CONFIRMADO

Olá, {nome}!

📅 Data: {data}
⏰ Horário: {horario}
🏥 Local: {clinica}
👨‍⚕️ Especialidade: {exame}{prioridade}

📲 Responda:
1️⃣ - CONFIRMAR presença
2️⃣ - CANCELAR consulta

Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def consulta_confirmada(nome):
        return f"""✅ CONSULTA CONFIRMADA!

Olá, {nome}!

Sua presença está confirmada.
Compareça no dia e horário agendados.

Leve: RG, Cartão SUS, exames anteriores.

Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def consulta_cancelada(nome):
        return f"""❌ CONSULTA CANCELADA

Olá, {nome}!

Sua consulta foi cancelada.
O horário foi liberado.

Para reagendar: (53) 3000-0000

Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def lembrete_7_dias(nome, exame, data, horario, clinica):
        return f"""🔔 LEMBRETE - 7 DIAS

Olá, {nome}!

Sua consulta está chegando!

📅 Data: {data}
⏰ Horário: {horario}
🏥 Local: {clinica}
👨‍⚕️ Especialidade: {exame}

Faltam 7 dias para sua consulta.

📲 Responda:
2️⃣ - Para CANCELAR

Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def lembrete_5_dias(nome, exame, data, horario, clinica):
        return f"""🔔 LEMBRETE - 5 DIAS

Olá, {nome}!

Sua consulta está se aproximando!

📅 Data: {data}
⏰ Horário: {horario}
🏥 Local: {clinica}
👨‍⚕️ Especialidade: {exame}

Faltam 5 dias para sua consulta.
Separe seus documentos: RG e Cartão SUS.

📲 Responda:
2️⃣ - Para CANCELAR

Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def lembrete_3_dias(nome, exame, data, horario, clinica):
        return f"""🔔 LEMBRETE - 3 DIAS

Olá, {nome}!

Sua consulta é em 3 dias!

📅 Data: {data}
⏰ Horário: {horario}
🏥 Local: {clinica}
👨‍⚕️ Especialidade: {exame}

⚠️ Prepare-se:
- RG e Cartão SUS
- Exames anteriores
- Lista de medicamentos

📲 Responda:
2️⃣ - Para CANCELAR

Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def lembrete_24h(nome, exame, data, horario, clinica):
        return f"""🔔 LEMBRETE URGENTE - AMANHÃ!

Olá, {nome}!

Sua consulta é AMANHÃ!

📅 Data: {data}
⏰ Horário: {horario}
🏥 Local: {clinica}
👨‍⚕️ Especialidade: {exame}

⚠️ IMPORTANTE:
- Chegue 15 minutos antes
- Leve RG e Cartão SUS
- Leve exames anteriores

📲 Responda:
2️⃣ - Para CANCELAR (urgente)

Sistema SUS - Hackapel 2025"""

# ==================== INSTÂNCIA GLOBAL ====================

whatsapp_client = WhatsAppClient()
