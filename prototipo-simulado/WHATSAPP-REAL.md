# 🟢 Integração WhatsApp Real - Evolution API

## 📋 O que mudou?

O sistema agora envia mensagens **REAIS via WhatsApp** usando **Evolution API** (open source).

✅ **Antes:** Simulação (mensagens apareciam apenas no simulador)  
✅ **Agora:** WhatsApp REAL (mensagens chegam no celular do paciente)

---

## 🚀 Como Configurar (3 passos)

### **Opção 1: Docker Local (Desenvolvimento)**

1. **Instalar Docker**
   - Windows/Mac: https://docker.com/get-started
   - Linux: `sudo apt install docker.io`

2. **Rodar Evolution API**
```bash
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=SUA_CHAVE_SECRETA_AQUI \
  atendai/evolution-api:latest
```

3. **Configurar variáveis locais**
```bash
# Windows PowerShell
$env:EVOLUTION_API_URL="http://localhost:8080"
$env:EVOLUTION_API_KEY="SUA_CHAVE_SECRETA_AQUI"
$env:EVOLUTION_INSTANCE="sus-agendamentos"

# Linux/Mac
export EVOLUTION_API_URL="http://localhost:8080"
export EVOLUTION_API_KEY="SUA_CHAVE_SECRETA_AQUI"
export EVOLUTION_INSTANCE="sus-agendamentos"
```

---

### **Opção 2: Railway (Produção)**

1. **Deploy Evolution API no Railway**
   - Acesse: https://railway.app
   - New Project → Deploy from GitHub
   - Use o repo: https://github.com/EvolutionAPI/evolution-api
   - Adicione variável: `AUTHENTICATION_API_KEY` = `sua-chave-secreta`
   - Generate Domain (ex: `evolution-api-production.up.railway.app`)

2. **Configurar no sistema principal**
   - No Railway do seu projeto `Desafio-Hackapel`
   - Aba **Variables** → Add:
     - `EVOLUTION_API_URL` = `https://evolution-api-production.up.railway.app`
     - `EVOLUTION_API_KEY` = `sua-chave-secreta`
     - `EVOLUTION_INSTANCE` = `sus-agendamentos`

3. **Conectar WhatsApp**
   - Acesse: `seu-sistema.railway.app/whatsapp-config`
   - Clique em "Obter QR Code"
   - Escaneie com WhatsApp no celular
   - ✅ Pronto!

---

## 📱 Como Funciona

### **Fluxo Automático:**

1. **Operador agenda** → Sistema envia WhatsApp REAL
2. **Paciente recebe** no celular dele
3. **Se idoso (60+)** → Recebe áudio explicativo
4. **Paciente responde** → Sistema atualiza automaticamente
5. **Lembretes automáticos** → 7, 5, 3 dias e 24h antes

### **Tipos de Mensagem:**

- ✅ Texto simples (confirmações)
- 🔊 Áudio (para idosos)
- 🔔 Lembretes automáticos
- 📋 Orientações educativas por especialidade

---

## 🔧 Verificar Status

Acesse no navegador:
```
http://localhost:5000/whatsapp-config
```

Vai mostrar:
- 🟢 Conectado (WhatsApp funcionando)
- 🔴 Desconectado (precisa escanear QR Code)
- 🟡 Simulação (API não configurada)

---

## 🆘 Problemas Comuns

### **"Modo Simulação" não sai**
✅ Certifique-se que configurou as 3 variáveis de ambiente  
✅ Reinicie o servidor após configurar  
✅ Verifique se Evolution API está rodando

### **QR Code não aparece**
✅ Acesse: `http://seu-evolution-api:8080`  
✅ Verifique se `AUTHENTICATION_API_KEY` está correta  
✅ Tente criar instância manualmente na interface

### **Mensagens não chegam**
✅ Verifique status da conexão  
✅ WhatsApp precisa estar conectado (QR Code válido)  
✅ Número precisa estar no formato: +55 11 99999-9999

---

## 📚 Documentação Evolution API

- **GitHub:** https://github.com/EvolutionAPI/evolution-api
- **Docs:** https://doc.evolution-api.com
- **Discord:** https://evolution-api.com/discord

---

## 🎯 Comandos Úteis

### **Testar Evolution API:**
```bash
curl http://localhost:8080/instance/fetchInstances \
  -H "apikey: SUA_CHAVE"
```

### **Ver logs Docker:**
```bash
docker logs evolution-api -f
```

### **Reiniciar container:**
```bash
docker restart evolution-api
```

---

## ✅ Checklist Rápido

- [ ] Evolution API rodando (Docker ou Railway)
- [ ] Variáveis de ambiente configuradas
- [ ] QR Code escaneado no WhatsApp
- [ ] Status mostrando "Conectado"
- [ ] Teste enviando um agendamento
- [ ] Mensagem chegou no celular

**🎉 Sistema pronto para Hackapel 2025!**

---

## 💡 Custos

- **Evolution API:** 100% gratuito (open source)
- **Railway:** $5/mês grátis (suficiente para demonstração)
- **WhatsApp Business API:** Não precisa (usa WhatsApp pessoal)

**Total:** R$ 0,00 para desenvolvimento e apresentação! 🎊
