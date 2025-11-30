"""
🟢 INTEGRAÇÃO WHATSAPP - Evolution API v2
Sistema SUS Hackapel 2025

Funcionalidades:
- Envio de mensagens de texto
- Envio de áudio (Text-to-Speech automático)
- Gerenciamento de instância WhatsApp
- Polling de mensagens recebidas
"""

import requests
import os
import uuid
from datetime import datetime
from gtts import gTTS

# ==================== CONFIGURAÇÕES ====================

class Config:
    """Configurações centralizadas"""
    
    # Evolution API
    EVOLUTION_URL = os.environ.get('EVOLUTION_API_URL', '')
    EVOLUTION_KEY = os.environ.get('EVOLUTION_API_KEY', '')
    INSTANCE_NAME = os.environ.get('EVOLUTION_INSTANCE', 'sus-agendamentos')
    
    # Diretórios
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    AUDIO_DIR = os.path.join(BASE_DIR, 'static', 'audios')
    
    # URL pública para áudios (Railway)
    PUBLIC_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
    
    @classmethod
    def get_evolution_url(cls):
        """Retorna URL da Evolution API com protocolo"""
        url = cls.EVOLUTION_URL
        if url and not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        return url
    
    @classmethod
    def get_audio_url(cls, filename):
        """Retorna URL pública do áudio"""
        if cls.PUBLIC_URL:
            return f"https://{cls.PUBLIC_URL}/static/audios/{filename}"
        return f"http://localhost:5000/static/audios/{filename}"

# Criar diretório de áudios
os.makedirs(Config.AUDIO_DIR, exist_ok=True)

# ==================== TEXT-TO-SPEECH ====================

class TextToSpeech:
    """Gerador de áudio a partir de texto"""
    
    @staticmethod
    def gerar_audio(texto, nome_arquivo=None):
        """
        Gera arquivo de áudio MP3 a partir do texto
        
        Args:
            texto: Texto para converter em áudio
            nome_arquivo: Nome do arquivo (opcional, gera UUID se não informado)
            
        Returns:
            dict: {sucesso: bool, arquivo: str, url: str}
        """
        try:
            # Gerar nome único se não informado
            if not nome_arquivo:
                nome_arquivo = f"audio_{uuid.uuid4().hex[:8]}.mp3"
            
            # Caminho completo
            caminho = os.path.join(Config.AUDIO_DIR, nome_arquivo)
            
            # Limpar texto para TTS (remover emojis problemáticos)
            texto_limpo = TextToSpeech._limpar_texto(texto)
            
            # Gerar áudio com gTTS
            tts = gTTS(text=texto_limpo, lang='pt-br', slow=False)
            tts.save(caminho)
            
            print(f"🔊 Áudio gerado: {nome_arquivo}")
            
            return {
                "sucesso": True,
                "arquivo": nome_arquivo,
                "caminho": caminho,
                "url": Config.get_audio_url(nome_arquivo)
            }
            
        except Exception as e:
            print(f"❌ Erro ao gerar áudio: {e}")
            return {"sucesso": False, "erro": str(e)}
    
    @staticmethod
    def _limpar_texto(texto):
        """Remove caracteres problemáticos para TTS"""
        # Substituir emojis comuns por texto
        substituicoes = {
            '✅': 'Confirmado.',
            '❌': 'Cancelado.',
            '📅': 'Data:',
            '⏰': 'Horário:',
            '🏥': 'Local:',
            '👨‍⚕️': 'Especialidade:',
            '👵': 'Idade:',
            '👴': '',
            '📲': '',
            '1️⃣': 'Um.',
            '2️⃣': 'Dois.',
            '🔊': '',
            '📝': '',
            '🎧': '',
            '🔔': 'Atenção.',
            '⚠️': 'Atenção.',
            '📞': 'Telefone:',
            '\n\n': '. ',
            '\n': '. ',
        }
        
        for emoji, texto_sub in substituicoes.items():
            texto = texto.replace(emoji, texto_sub)
        
        # Remover outros emojis (caracteres unicode especiais)
        texto_final = ''.join(c for c in texto if ord(c) < 0x1F600 or ord(c) > 0x1F9FF)
        
        return texto_final.strip()

# ==================== CLIENTE WHATSAPP ====================

class WhatsAppClient:
    """Cliente para Evolution API - WhatsApp"""
    
    def __init__(self):
        self.base_url = Config.get_evolution_url()
        self.api_key = Config.EVOLUTION_KEY
        self.instance = Config.INSTANCE_NAME
        
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        
        # Verificar modo
        self.modo_simulacao = not self.api_key
        
        if self.modo_simulacao:
            print("⚠️  WhatsApp em modo SIMULAÇÃO (API não configurada)")
        else:
            print(f"✅ WhatsApp conectado: {self.base_url}")
    
    # ==================== FORMATAÇÃO ====================
    
    def _formatar_numero(self, telefone):
        """
        Formata telefone para Evolution API
        Entrada: qualquer formato (55XXXXXXXXXXX, XXXXXXXXXXX, etc)
        Saída: XXXXXXXXXXX (DDD + número, sem código do país)
        """
        # Converter para string e limpar
        numero = ''.join(c for c in str(telefone) if c.isdigit())
        
        # Remover código 55 do Brasil se presente
        if numero.startswith('55') and len(numero) > 11:
            numero = numero[2:]
        
        return numero
    
    # ==================== ENVIO DE MENSAGENS ====================
    
    def enviar_texto(self, telefone, mensagem):
        """
        Envia mensagem de texto simples
        
        Args:
            telefone: Número do destinatário
            mensagem: Texto da mensagem
            
        Returns:
            dict: {sucesso: bool, ...}
        """
        if self.modo_simulacao:
            print(f"📱 [SIM] Texto para {telefone}: {mensagem[:50]}...")
            return {"sucesso": True, "simulado": True}
        
        try:
            numero = self._formatar_numero(telefone)
            
            payload = {
                "number": numero,
                "textMessage": {"text": mensagem}
            }
            
            url = f"{self.base_url}/message/sendText/{self.instance}"
            response = requests.post(url, json=payload, headers=self.headers, timeout=15)
            
            if response.status_code in [200, 201]:
                print(f"✅ Texto enviado para {numero}")
                return {"sucesso": True}
            else:
                print(f"❌ Erro texto: {response.status_code}")
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {"sucesso": False, "erro": str(e)}
    
    def enviar_audio(self, telefone, audio_url):
        """
        Envia arquivo de áudio
        
        Args:
            telefone: Número do destinatário
            audio_url: URL pública do áudio
            
        Returns:
            dict: {sucesso: bool, ...}
        """
        if self.modo_simulacao:
            print(f"🔊 [SIM] Áudio para {telefone}: {audio_url}")
            return {"sucesso": True, "simulado": True}
        
        try:
            numero = self._formatar_numero(telefone)
            
            payload = {
                "number": numero,
                "mediaMessage": {
                    "mediatype": "audio",
                    "media": audio_url
                }
            }
            
            url = f"{self.base_url}/message/sendMedia/{self.instance}"
            response = requests.post(url, json=payload, headers=self.headers, timeout=15)
            
            if response.status_code in [200, 201]:
                print(f"✅ Áudio enviado para {numero}")
                return {"sucesso": True}
            else:
                print(f"❌ Erro áudio: {response.status_code}")
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {"sucesso": False, "erro": str(e)}
    
    def enviar_mensagem_completa(self, telefone, mensagem, com_audio=True):
        """
        Envia mensagem de texto + áudio (TTS)
        
        Args:
            telefone: Número do destinatário
            mensagem: Texto da mensagem
            com_audio: Se True, também envia versão em áudio
            
        Returns:
            dict: {sucesso: bool, texto_enviado: bool, audio_enviado: bool}
        """
        resultado = {
            "sucesso": False,
            "texto_enviado": False,
            "audio_enviado": False
        }
        
        # 1. Enviar texto
        res_texto = self.enviar_texto(telefone, mensagem)
        resultado["texto_enviado"] = res_texto.get("sucesso", False)
        
        # 2. Gerar e enviar áudio (se solicitado)
        if com_audio:
            audio = TextToSpeech.gerar_audio(mensagem)
            
            if audio.get("sucesso"):
                res_audio = self.enviar_audio(telefone, audio["url"])
                resultado["audio_enviado"] = res_audio.get("sucesso", False)
                resultado["audio_url"] = audio["url"]
        
        # Sucesso se pelo menos o texto foi enviado
        resultado["sucesso"] = resultado["texto_enviado"]
        
        return resultado
    
    # ==================== GERENCIAMENTO DE INSTÂNCIA ====================
    
    def verificar_conexao(self):
        """Verifica se o WhatsApp está conectado"""
        if self.modo_simulacao:
            return {"conectado": False, "simulacao": True}
        
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                state = data.get('state') or data.get('instance', {}).get('state')
                return {
                    "conectado": state == 'open',
                    "status": state,
                    "dados": data
                }
            else:
                return {"conectado": False, "erro": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"conectado": False, "erro": str(e)}
    
    def obter_qrcode(self):
        """Obtém QR Code para conectar WhatsApp"""
        if self.modo_simulacao:
            return {"sucesso": False, "erro": "API não configurada"}
        
        try:
            # Tentar conectar (gera QR)
            url = f"{self.base_url}/instance/connect/{self.instance}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "sucesso": True,
                    "qrcode": data.get('base64'),
                    "code": data.get('code')
                }
            elif response.status_code == 404:
                # Criar instância automaticamente
                return self._criar_instancia()
            else:
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def _criar_instancia(self):
        """Cria nova instância WhatsApp"""
        try:
            payload = {
                "instanceName": self.instance,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS"
            }
            
            url = f"{self.base_url}/instance/create"
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                return {
                    "sucesso": True,
                    "qrcode": data.get('qrcode', {}).get('base64'),
                    "mensagem": "Instância criada"
                }
            else:
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    # ==================== BUSCAR MENSAGENS (POLLING) ====================
    
    def buscar_mensagens(self, limite=5):
        """
        Busca últimas mensagens recebidas
        
        Args:
            limite: Quantidade de mensagens a buscar
            
        Returns:
            list: Lista de mensagens [{numero, texto, timestamp, id}, ...]
        """
        if self.modo_simulacao:
            return []
        
        try:
            url = f"{self.base_url}/chat/findMessages/{self.instance}"
            
            payload = {
                "where": {"key": {"fromMe": False}},
                "limit": limite,
                "sort": {"messageTimestamp": -1}
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            dados = response.json()
            
            # Normalizar formato
            mensagens_raw = dados
            if isinstance(dados, dict):
                mensagens_raw = dados.get('messages', dados.get('data', []))
            
            if not isinstance(mensagens_raw, list):
                mensagens_raw = [mensagens_raw] if mensagens_raw else []
            
            # Extrair dados relevantes
            mensagens = []
            for msg in mensagens_raw:
                key = msg.get('key', {})
                message = msg.get('message', {})
                
                # Ignorar mensagens enviadas por nós
                if key.get('fromMe'):
                    continue
                
                # Extrair número
                numero = key.get('remoteJid', '').replace('@s.whatsapp.net', '')
                
                # Extrair texto
                texto = message.get('conversation') or \
                        message.get('extendedTextMessage', {}).get('text', '')
                
                mensagens.append({
                    "id": key.get('id'),
                    "numero": numero,
                    "texto": texto.strip(),
                    "timestamp": msg.get('messageTimestamp', 0)
                })
            
            return mensagens
            
        except Exception as e:
            print(f"❌ Erro ao buscar mensagens: {e}")
            return []

# ==================== MENSAGENS PRÉ-DEFINIDAS ====================

class MensagensSUS:
    """Templates de mensagens do sistema SUS"""
    
    @staticmethod
    def agendamento_confirmado(nome, exame, data, horario, clinica, idade=None):
        """Mensagem de agendamento realizado"""
        
        prioridade = ""
        if idade and idade >= 60:
            prioridade = f"\n👴 Idade: {idade} anos - ATENDIMENTO PRIORITÁRIO"
        
        return f"""✅ AGENDAMENTO CONFIRMADO

Olá, {nome}!

Sua consulta foi agendada com sucesso:

📅 Data: {data}
⏰ Horário: {horario}
🏥 Local: {clinica}
👨‍⚕️ Especialidade: {exame}{prioridade}

📲 Por favor, confirme sua presença:
1️⃣ Digite 1 para CONFIRMAR
2️⃣ Digite 2 para CANCELAR

Aguardamos sua resposta!
Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def consulta_confirmada(nome):
        """Mensagem de confirmação de presença"""
        return f"""✅ CONSULTA CONFIRMADA!

Olá, {nome}!

Sua presença está confirmada.
Compareça no dia e horário agendados.

Leve seus documentos:
- RG ou CNH
- Cartão SUS
- Exames anteriores (se houver)

Obrigado pela confirmação!
Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def consulta_cancelada(nome):
        """Mensagem de cancelamento"""
        return f"""❌ CONSULTA CANCELADA

Olá, {nome}!

Sua consulta foi cancelada conforme solicitado.
O horário foi liberado para outros pacientes.

Caso precise reagendar, entre em contato:
📞 Telefone: (53) 3000-0000

Esperamos atendê-lo em breve!
Sistema SUS - Hackapel 2025"""
    
    @staticmethod
    def lembrete(nome, exame, data, horario, clinica, dias_restantes):
        """Mensagem de lembrete"""
        
        urgencia = ""
        if dias_restantes == 1:
            urgencia = "⚠️ SUA CONSULTA É AMANHÃ!"
        elif dias_restantes <= 3:
            urgencia = f"⏰ Faltam apenas {dias_restantes} dias!"
        
        return f"""🔔 LEMBRETE DE CONSULTA

Olá, {nome}!

{urgencia}

Sua consulta de {exame} está marcada para:

📅 Data: {data}
⏰ Horário: {horario}
🏥 Local: {clinica}

Não se esqueça de levar seus documentos!

Sistema SUS - Hackapel 2025"""

# ==================== INSTÂNCIA GLOBAL ====================

# Cliente WhatsApp (singleton)
whatsapp_client = WhatsAppClient()

# ==================== FUNÇÕES DE COMPATIBILIDADE ====================
# (Para manter compatibilidade com código existente no app.py)

def enviar_mensagem_texto(telefone, mensagem):
    """Wrapper para compatibilidade - envia texto + áudio"""
    return whatsapp_client.enviar_mensagem_completa(telefone, mensagem, com_audio=True)

def enviar_audio(telefone, audio_url):
    """Wrapper para compatibilidade"""
    return whatsapp_client.enviar_audio(telefone, audio_url)

def verificar_status_instancia():
    """Wrapper para compatibilidade"""
    return whatsapp_client.verificar_conexao()

def obter_qrcode():
    """Wrapper para compatibilidade"""
    return whatsapp_client.obter_qrcode()
