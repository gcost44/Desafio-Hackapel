# 🚂 Guia Railway - Passo a Passo Completo

## 📋 Visão Geral

Você vai criar **2 projetos** no Railway:
1. **Evolution API** (para WhatsApp)
2. **Sistema SUS** (seu projeto)

---

## PARTE 1: Evolution API (WhatsApp)

### 1️⃣ Criar conta Railway
- Acesse: https://railway.app
- **"Login"** → **"Login with GitHub"**
- Autorize o Railway

### 2️⃣ Deploy Evolution API

**Use Docker Image (mais simples):**

1. No dashboard, clique em **"+ New Project"**
2. Clique em **"Deploy Docker Image"**
3. Cole esta imagem:
   ```
   atendai/evolution-api:v2.1.1
   ```
4. Clique em **"Deploy"**
5. Aguarde 2-3 minutos

### 3️⃣ Configurar variáveis

1. Clique no serviço **"evolution-api"**
2. Aba **"Variables"** → **"+ New Variable"**
3. Adicione:

```
AUTHENTICATION_API_KEY
hackapel2025secret
```

4. Clique em **"Add"**

### 4️⃣ Gerar domínio público

1. Aba **"Settings"**
2. Role até **"Networking"** → **"Public Networking"**
3. Clique em **"Generate Domain"**
4. **COPIE A URL** (exemplo: `evolution-api-production-xxxx.up.railway.app`)
5. ⚠️ **GUARDE ESSA URL!** Vai usar depois

### 5️⃣ Configurar porta (importante!)

1. Ainda na aba **"Variables"**
2. Adicione mais uma variável:

```
PORT
8080
```

3. Aguarde redeploy automático (1-2 minutos)

### ✅ Verificar se funcionou

Acesse no navegador:
```
https://sua-url-evolution.up.railway.app
```

Deve aparecer uma página da Evolution API (pode ser erro 401, está ok!)

---

## PARTE 2: Sistema SUS (Seu Projeto)

### 6️⃣ Deploy do sistema

1. Volte ao dashboard Railway
2. Clique em **"+ New Project"**
3. Escolha **"Deploy from GitHub repo"**
4. Selecione: **`gcost44/Desafio-Hackapel`**
5. Clique em **"Deploy Now"**
6. Aguarde 3-5 minutos

### 7️⃣ Configurar variáveis de ambiente

1. Clique no serviço deployado
2. Aba **"Variables"**
3. Adicione estas **4 variáveis** (uma por vez):

**Variável 1:**
```
GEMINI_API_KEY
AIzaSyAC68hEyU437imZXY7CsCn0Jp41cygRvPc
```

**Variável 2:**
```
EVOLUTION_API_URL
https://sua-url-evolution-que-voce-copiou.up.railway.app
```
⚠️ Use a URL que você copiou no passo 4!

**Variável 3:**
```
EVOLUTION_API_KEY
hackapel2025secret
```
⚠️ Mesma senha do passo 3!

**Variável 4:**
```
EVOLUTION_INSTANCE
sus-agendamentos
```

### 8️⃣ Gerar domínio do sistema

1. Aba **"Settings"** → **"Networking"**
2. Clique em **"Generate Domain"**
3. **COPIE A URL** (exemplo: `desafio-hackapel-production-xxxx.up.railway.app`)

### ✅ Verificar se funcionou

Acesse no navegador:
```
https://sua-url-sistema.up.railway.app
```

Deve aparecer o painel do operador!

---

## PARTE 3: Conectar WhatsApp

### 9️⃣ Acessar configuração WhatsApp

No navegador:
```
https://sua-url-sistema.up.railway.app/whatsapp-config
```

### 🔟 Verificar status

1. Clique em **"🔄 Atualizar Status"**
2. Deve mostrar: **"WhatsApp Desconectado"** (ok!)

### 1️⃣1️⃣ Gerar QR Code

1. Clique em **"📱 Obter QR Code"**
2. Aguarde 5-10 segundos
3. **QR Code aparecerá na tela** (instância é criada automaticamente se não existir)

**Se der erro "instância não existe":**
- Clique em **"➕ Criar Instância"**
- Aguarde a criação
- QR Code aparecerá automaticamente

**Outros erros, verifique:**
- Evolution API está rodando? (acesse a URL diretamente)
- URL da Evolution está correta nas variáveis?
- API KEY está igual nos dois projetos?

### 1️⃣2️⃣ Escanear com WhatsApp

**No seu celular:**
1. Abra **WhatsApp**
2. Toque em **Menu (⋮)** → **"Aparelhos conectados"**
3. Toque em **"Conectar um aparelho"**
4. **Aponte a câmera para o QR Code**
5. Aguarde conectar

### 1️⃣3️⃣ Confirmar conexão

1. Volte ao navegador
2. Clique em **"🔄 Atualizar Status"**
3. Deve mostrar: **"🟢 WhatsApp Conectado"**

---

## 🎯 TESTAR O SISTEMA

### Fazer um agendamento de teste

1. Acesse: `https://sua-url-sistema.up.railway.app`
2. Faça upload de uma planilha Excel ou use a existente
3. Preencha:
   - **Nome:** Seu nome
   - **Telefone:** Seu celular com DDD (ex: 11999999999)
   - **Data nascimento:** Sua data
   - **Exame:** Cardiologista
4. Clique em **"Agendar"**

### Verificar WhatsApp

**Abra o WhatsApp no celular** → Deve ter chegado mensagem! 🎉

Se tiver 60+ anos, receberá um áudio também!

---

## 📊 Verificar Logs (Se algo der errado)

### Sistema Principal:
1. Railway → Seu projeto
2. Aba **"Deployments"**
3. Clique no último deploy
4. **"View Logs"**

### Evolution API:
1. Railway → Projeto Evolution
2. Aba **"Deployments"**
3. Clique no último deploy
4. **"View Logs"**

---

## 🆘 Problemas Comuns

### ❌ "Modo Simulação" não sai

**Causa:** Variáveis erradas ou Evolution API não está rodando

**Solução:**
1. Verifique as 3 variáveis Evolution (URL, KEY, INSTANCE)
2. Teste a URL da Evolution no navegador
3. Redeploy: Aba "Deployments" → botão "..." → "Redeploy"

### ❌ QR Code não gera

**Causa:** Evolution API não acessível ou API KEY errada

**Solução:**
1. Acesse direto: `https://sua-evolution.up.railway.app`
2. Se der erro 404 ou timeout: Evolution não está rodando
3. Se der erro 401: API KEY está errada
4. Verifique variável `PORT=8080` na Evolution API

### ❌ Mensagem não chega no WhatsApp

**Causa:** WhatsApp desconectou ou número errado

**Solução:**
1. Verifique status: deve estar "Conectado"
2. Número deve ter DDD: `11999999999` (sem espaços, sem +55)
3. Verifique logs do sistema (podem ter erros)

### ❌ Deploy falhou

**Causa:** Falta arquivo Procfile ou requirements.txt

**Solução:**
1. Verifique se fez o último `git push`
2. No Railway: Settings → "Restart Deploy"
3. Veja os logs para identificar o erro

---

## 💰 Custos

- **Railway:** $5 grátis/mês
- **Evolution API:** Gratuito (open source)
- **WhatsApp:** Gratuito (seu WhatsApp pessoal)

**Total para Hackapel: R$ 0,00** 🎊

---

## ✅ Checklist Final

- [ ] Evolution API deployada no Railway
- [ ] Domínio Evolution gerado e copiado
- [ ] Variável `PORT=8080` adicionada na Evolution
- [ ] Variável `AUTHENTICATION_API_KEY` adicionada na Evolution
- [ ] Sistema SUS deployado no Railway
- [ ] 4 variáveis configuradas no sistema (GEMINI, EVOLUTION_URL, EVOLUTION_KEY, EVOLUTION_INSTANCE)
- [ ] Domínio do sistema gerado
- [ ] QR Code escaneado no WhatsApp
- [ ] Status mostrando "🟢 Conectado"
- [ ] Teste de agendamento enviou WhatsApp real

---

## 🔗 URLs Importantes

Depois do deploy, você terá:

1. **Evolution API:**
   - `https://evolution-api-production-xxxx.up.railway.app`

2. **Sistema Principal:**
   - `https://desafio-hackapel-production-xxxx.up.railway.app`

3. **Configuração WhatsApp:**
   - `https://seu-sistema.up.railway.app/whatsapp-config`

4. **Simulador (ainda funciona):**
   - `https://seu-sistema.up.railway.app/simulador`

---

**🎉 Pronto para demonstrar no Hackapel 2025!**

**Sistema 100% funcional com:**
- ✅ WhatsApp REAL (não é simulação)
- ✅ IA Gemini (orientações personalizadas)
- ✅ Áudio para idosos (Google TTS)
- ✅ Lembretes automáticos
- ✅ 100% open source
