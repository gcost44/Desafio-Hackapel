# 🚂 Deploy no Railway - Guia Completo

## ⚡ Por que Railway?

- ✅ **100% funcional** - Suporta tudo que o sistema precisa
- ✅ **$5 grátis/mês** - Suficiente para o Hackapel
- ✅ **Deploy em 5 min** - Mais rápido que outros
- ✅ **Auto-deploy** - Atualiza sozinho quando faz push

---

## 📋 Passo a Passo

### 1️⃣ Push para GitHub (Se ainda não fez)

```powershell
# Na pasta do projeto
cd C:\Users\Win10\Desktop\Desafio-Hackapel\prototipo-simulado

# Inicializar Git
git init
git add .
git commit -m "Sistema SUS Hackapel 2025"
git branch -M main

# Criar repo no GitHub e conectar
git remote add origin https://github.com/gcost44/sistema-sus-hackapel.git
git push -u origin main
```

### 2️⃣ Criar Conta no Railway

1. Acesse: **https://railway.app**
2. Clique em **"Login"**
3. Escolha **"Login with GitHub"**
4. Autorize o Railway

### 3️⃣ Criar Novo Projeto

1. Clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Se pedir permissão, autorize
4. Escolha o repositório: **`sistema-sus-hackapel`**

### 4️⃣ Configurar Variáveis

1. Railway inicia deploy automaticamente
2. Clique na aba **"Variables"**
3. Clique em **"New Variable"**
4. Adicione:
   - **Variable:** `GEMINI_API_KEY`
   - **Value:** `AIzaSyAC68hEyU437imZXY7CsCn0Jp41cygRvPc`
5. Clique em **"Add"**

### 5️⃣ Gerar Domain

1. Vá na aba **"Settings"**
2. Seção **"Networking"**
3. Clique em **"Generate Domain"**
4. Railway gera URL tipo: `sistema-sus-production.up.railway.app`

### 6️⃣ Aguardar Deploy

- Railway instala dependências automaticamente
- Leva ~3-5 minutos
- Acompanhe os logs na aba **"Deployments"**

### 7️⃣ Testar!

1. Copie a URL gerada
2. Abra no navegador
3. Teste todas as funcionalidades:
   - ✅ Upload de Excel
   - ✅ Agendamento
   - ✅ Simulador WhatsApp
   - ✅ Áudio para idosos

---

## 🔧 Arquivos Necessários (Já criados!)

✅ `Procfile` - Comando para iniciar
✅ `requirements.txt` - Dependências
✅ `runtime.txt` - Versão do Python
✅ `.gitignore` - Arquivos ignorados

---

## 📊 Monitoramento

No painel Railway você pode ver:
- 📈 Uso de CPU/Memória
- 📜 Logs em tempo real
- 🔄 Histórico de deploys
- 💰 Créditos restantes ($5)

---

## 🔄 Atualizar Sistema

Quando fizer alterações:

```powershell
git add .
git commit -m "Descrição da mudança"
git push
```

Railway faz **deploy automático**! 🚀

---

## ⚠️ Créditos Grátis

- **$5/mês** grátis para sempre
- Reinicia no dia 1º de cada mês
- Suficiente para:
  - ✅ Demonstrações
  - ✅ Testes
  - ✅ Apresentação Hackapel
  - ✅ ~500 horas/mês de uso

---

## 🆘 Problemas Comuns

### Deploy falhou?
- Veja os logs na aba "Deployments"
- Verifique se `requirements.txt` está correto
- Confirme que `GEMINI_API_KEY` foi adicionada

### Site não abre?
- Certifique-se que gerou o domain
- Aguarde ~5 min após deploy
- Verifique logs de erro

### Excedeu créditos?
- Use local até dia 1º (reset)
- Ou adicione cartão ($0.000743/hora extra)

---

## 💡 Dicas

1. **Nome do projeto:** Clique no nome no topo para editar
2. **Logs em tempo real:** Aba "Deployments" → Clique no deploy
3. **Restart manual:** Settings → "Restart" (se necessário)
4. **Environment:** Produção automático

---

## 🎯 Checklist Final

- [ ] Push para GitHub ✅
- [ ] Conta Railway criada ✅
- [ ] Projeto conectado ✅
- [ ] `GEMINI_API_KEY` configurada ✅
- [ ] Domain gerado ✅
- [ ] Deploy concluído ✅
- [ ] Sistema testado ✅
- [ ] URL compartilhada ✅

---

## 🚀 Pronto!

Seu sistema está online e acessível de qualquer lugar!

**URL final:** `https://seu-projeto.up.railway.app`

Compartilhe essa URL na apresentação do Hackapel! 🏆

---

## 📱 Suporte

- Railway Docs: https://docs.railway.app
- Discord Railway: https://discord.gg/railway
- GitHub Issues: Seu repositório

**Qualquer dúvida, é só perguntar!** 😊
