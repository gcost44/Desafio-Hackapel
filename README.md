# 🏥 Sistema de Agendamentos SUS - Hackapel 2025

Sistema inteligente de agendamento de consultas com **WhatsApp + Áudio (TTS)**.

## ✨ Funcionalidades

- 📱 **WhatsApp Real** via Evolution API
- 🔊 **Text-to-Speech** em todas as mensagens
- 👴 **Áudio especial** para idosos (60+)
- 🤖 **IA Gemini** para orientações médicas
- 📊 **Planilha Excel** para gestão de horários
- ✅ **Confirmação/Cancelamento** automático

## 🔄 Fluxo

```
1. Operador cadastra paciente (nome, telefone, exame)
2. Sistema busca vaga na planilha → marca PENDENTE
3. WhatsApp TEXTO + ÁUDIO enviado para paciente
4. Paciente responde: 1 (confirma) ou 2 (cancela)
5. Sistema atualiza planilha automaticamente
6. Se cancelar → horário LIBERADO
```

## 📁 Estrutura

```
prototipo-simulado/
├── app.py                    # Servidor Flask
├── whatsapp_integration.py   # Cliente WhatsApp + TTS
├── criar_planilha_exemplo.py # Gerador de planilha
├── agenda_clinicas.xlsx      # Planilha de horários
├── static/audios/            # Áudios gerados
└── templates/                # HTML
```

## ⚙️ Variáveis de Ambiente

```
EVOLUTION_API_URL=sua-url.up.railway.app
EVOLUTION_API_KEY=sua-chave
EVOLUTION_INSTANCE=sus-agendamentos
GEMINI_API_KEY=sua-chave
RAILWAY_PUBLIC_DOMAIN=seu-projeto.up.railway.app
```

## 🚀 Deploy

O sistema está configurado para **Railway**:
- `Procfile`: `web: cd prototipo-simulado && python app.py`
- `runtime.txt`: Python 3.12.0

## 📝 Licença

Hackapel 2025
