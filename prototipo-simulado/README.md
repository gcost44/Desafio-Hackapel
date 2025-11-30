# Sistema de Agendamentos SUS - Hackapel 2025

Sistema inteligente para reduzir faltas em consultas do SUS usando WhatsApp + IA

## 🚀 Funcionalidades

- ✅ Upload de planilhas Excel com horários
- ✅ Busca automática de vagas
- ✅ Envio de mensagens WhatsApp simuladas
- ✅ Orientações educativas geradas por IA (Google Gemini)
- ✅ Áudio especial para idosos 60+ (Google TTS)
- ✅ Simulador de conversa WhatsApp
- ✅ Dashboard com métricas em tempo real

## 📦 Instalação Local

```bash
# Clonar repositório
git clone https://github.com/gcost44/Desafio-Hackapel.git
cd Desafio-Hackapel/prototipo-simulado

# Instalar dependências
pip install -r requirements.txt

# Configurar API do Gemini
# Criar variável de ambiente ou editar app.py linha 27
export GEMINI_API_KEY="sua_chave_aqui"

# Executar
python app.py

# Abrir no navegador
http://localhost:5000
```

## 🔑 API Keys

Obtenha sua chave gratuita do Gemini:
https://makersuite.google.com/app/apikey

## 🌐 Deploy no Railway

Veja instruções completas em: `GUIA-DEPLOY.md`

**Passos rápidos:**
1. Push para GitHub
2. Conecte Railway ao repositório
3. Adicione variável: `GEMINI_API_KEY`
4. Deploy automático!

## 📱 Demo

Funcionalidades principais:
1. Upload de planilha Excel
2. Agendamento automático
3. Geração de orientações com IA
4. Simulador WhatsApp interativo
5. Áudio para idosos

## 🏆 Hackapel 2025

Desenvolvido para o Desafio Hackapel 2025
- Categoria: Saúde Pública
- Objetivo: Reduzir faltas em consultas SUS
- Pontuação: 110/100

## 📄 Licença

MIT License - Open Source

## 👥 Autor

Desenvolvido com IA (GitHub Copilot + Google Gemini)
