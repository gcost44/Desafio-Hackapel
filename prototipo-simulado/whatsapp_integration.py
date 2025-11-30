"""
🟢 INTEGRAÇÃO WHATSAPP REAL - Evolution API
Sistema de envio de mensagens via WhatsApp Business
Evolution API: https://github.com/EvolutionAPI/evolution-api
"""

import requests
import os
from datetime import datetime

class WhatsAppEvolution:
    """Cliente para Evolution API - WhatsApp Real"""
    
    def __init__(self):
        # Configurações da Evolution API
        base_url = os.environ.get('EVOLUTION_API_URL', 'http://localhost:8080')
        
        # Garantir que a URL tenha protocolo
        if base_url and not base_url.startswith(('http://', 'https://')):
            base_url = f'https://{base_url}'
        
        self.base_url = base_url
        self.api_key = os.environ.get('EVOLUTION_API_KEY', '')
        self.instance_name = os.environ.get('EVOLUTION_INSTANCE', 'sus-agendamentos')
        
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        
        # Flag para modo de simulação (se API não configurada)
        self.modo_simulacao = not self.api_key or self.api_key == ''
        
        if self.modo_simulacao:
            print("⚠️  Evolution API não configurada - Modo SIMULAÇÃO ativo")
        else:
            print(f"✅ Evolution API configurada: {self.base_url}")
    
    def formatar_numero(self, telefone):
        """Formata número para padrão WhatsApp: 5511999999999@s.whatsapp.net"""
        # Remove caracteres especiais
        numero = ''.join(filter(str.isdigit, telefone))
        
        # Adiciona código do país se não tiver
        if not numero.startswith('55'):
            numero = '55' + numero
        
        # Formato Evolution API
        return f"{numero}@s.whatsapp.net"
    
    def enviar_mensagem_texto(self, telefone, mensagem):
        """Envia mensagem de texto simples - Evolution API v2 format"""
        if self.modo_simulacao:
            print(f"\n📱 [SIMULAÇÃO] WhatsApp para {telefone}")
            print(f"   Mensagem: {mensagem[:100]}...")
            return {"sucesso": True, "simulado": True}
        
        try:
            numero_formatado = self.formatar_numero(telefone)
            
            # Evolution API v2 formato correto
            payload = {
                "number": numero_formatado,
                "textMessage": {
                    "text": mensagem
                }
            }
            
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            print(f"📤 Enviando para: {url}")
            print(f"📦 Payload: {payload}")
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 201 or response.status_code == 200:
                print(f"✅ Mensagem enviada para {telefone}")
                return {"sucesso": True, "response": response.json()}
            else:
                print(f"❌ Erro ao enviar: {response.status_code} - {response.text}")
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            print(f"❌ Erro na API: {e}")
            return {"sucesso": False, "erro": str(e)}
    
    def enviar_audio(self, telefone, audio_url):
        """Envia áudio para WhatsApp - Evolution API v2 format"""
        if self.modo_simulacao:
            print(f"\n🔊 [SIMULAÇÃO] Áudio WhatsApp para {telefone}")
            print(f"   URL: {audio_url}")
            return {"sucesso": True, "simulado": True}
        
        try:
            numero_formatado = self.formatar_numero(telefone)
            
            # Evolution API v2 formato correto para áudio
            payload = {
                "number": numero_formatado,
                "mediaMessage": {
                    "mediatype": "audio",
                    "media": audio_url
                }
            }
            
            url = f"{self.base_url}/message/sendMedia/{self.instance_name}"
            print(f"🔊 Enviando áudio para: {url}")
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 201 or response.status_code == 200:
                print(f"✅ Áudio enviado para {telefone}")
                return {"sucesso": True, "response": response.json()}
            else:
                print(f"❌ Erro ao enviar áudio: {response.status_code} - {response.text}")
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            print(f"❌ Erro ao enviar áudio: {e}")
            return {"sucesso": False, "erro": str(e)}
    
    def enviar_mensagem_com_botoes(self, telefone, mensagem, botoes):
        """Envia mensagem com botões interativos (Evolution API v2+)"""
        if self.modo_simulacao:
            print(f"\n📱 [SIMULAÇÃO] Mensagem com botões para {telefone}")
            print(f"   Botões: {[b['displayText'] for b in botoes]}")
            return {"sucesso": True, "simulado": True}
        
        try:
            numero_formatado = self.formatar_numero(telefone)
            
            payload = {
                "number": numero_formatado,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "buttonMessage": {
                    "text": mensagem,
                    "buttons": botoes,
                    "footerText": "Sistema SUS Hackapel 2025"
                }
            }
            
            url = f"{self.base_url}/message/sendButtons/{self.instance_name}"
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            
            if response.status_code == 201:
                print(f"✅ Mensagem com botões enviada para {telefone}")
                return {"sucesso": True, "response": response.json()}
            else:
                print(f"❌ Erro ao enviar: {response.status_code}")
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {"sucesso": False, "erro": str(e)}
    
    def verificar_status_instancia(self):
        """Verifica se a instância está conectada"""
        if self.modo_simulacao:
            return {"conectado": False, "simulacao": True}
        
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            print(f"🔍 Verificando status em: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📱 Dados recebidos: {data}")
                
                # Evolution API v2 retorna diferentes formatos
                state = data.get('state') or data.get('instance', {}).get('state')
                conectado = state == 'open'
                
                return {
                    "conectado": conectado,
                    "status": state,
                    "response": data
                }
            elif response.status_code == 404:
                return {"conectado": False, "erro": "Instância não existe. Clique em 'Criar Instância'"}
            else:
                print(f"❌ Erro: {response.text}")
                return {"conectado": False, "erro": f"Erro {response.status_code}: {response.text}"}
                
        except requests.exceptions.Timeout:
            return {"conectado": False, "erro": "Timeout - Evolution API não responde"}
        except Exception as e:
            print(f"❌ Exceção: {e}")
            return {"conectado": False, "erro": str(e)}
    
    def criar_instancia(self):
        """Cria nova instância do WhatsApp - verifica se já existe primeiro"""
        if self.modo_simulacao:
            return {"sucesso": False, "erro": "Configure Evolution API primeiro"}
        
        try:
            # Verificar se instância já existe
            url_check = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            check_response = requests.get(url_check, headers=self.headers, timeout=5)
            
            if check_response.status_code == 200:
                # Instância já existe - tentar obter QR Code
                return {"sucesso": False, "erro": "Instância já existe. Use 'Obter QR Code' para conectar.", "ja_existe": True}
            
            # Instância não existe - criar
            payload = {
                "instanceName": self.instance_name,
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
                    "response": data
                }
            elif response.status_code == 403:
                # Nome já em uso
                return {"sucesso": False, "erro": "Instância já existe. Use 'Obter QR Code' para conectar.", "ja_existe": True}
            else:
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}
    
    def obter_qrcode(self):
        """Obtém QR Code para conectar WhatsApp - cria instância se não existir"""
        if self.modo_simulacao:
            return {"sucesso": False, "erro": "Configure Evolution API primeiro"}
        
        try:
            # Tentar obter QR Code
            url = f"{self.base_url}/instance/connect/{self.instance_name}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "sucesso": True,
                    "qrcode": data.get('base64'),
                    "code": data.get('code')
                }
            elif response.status_code == 404:
                # Instância não existe - criar automaticamente
                print(f"⚠️  Instância '{self.instance_name}' não existe. Criando...")
                resultado_criacao = self.criar_instancia()
                
                if resultado_criacao.get('sucesso'):
                    return {
                        "sucesso": True,
                        "qrcode": resultado_criacao.get('qrcode'),
                        "mensagem": "Instância criada automaticamente"
                    }
                else:
                    return resultado_criacao
            else:
                return {"sucesso": False, "erro": response.text}
                
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

# Cliente global
whatsapp_client = WhatsAppEvolution()
