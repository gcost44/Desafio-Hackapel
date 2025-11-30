# 🚀 Guia Rápido - Push para GitHub e Deploy

## 1️⃣ Preparar Repositório Local

```powershell
# Navegar para a pasta
cd C:\Users\Win10\Desktop\Desafio-Hackapel\prototipo-simulado

# Inicializar Git
git init

# Adicionar todos os arquivos
git add .

# Fazer commit
git commit -m "Sistema SUS Hackapel 2025 - Pronto para deploy"

# Definir branch principal
git branch -M main
```

## 2️⃣ Criar Repositório no GitHub

1. Acesse: https://github.com/gcost44
2. Clique em **"New repository"**
3. Nome: `sistema-sus-hackapel`
4. Descrição: `Sistema de Agendamentos SUS - Hackapel 2025`
5. **Público** ou Privado
6. **NÃO** marque "Initialize with README"
7. Clique em **"Create repository"**

## 3️⃣ Conectar e Fazer Push

```powershell
# Conectar ao repositório remoto
git remote add origin https://github.com/gcost44/sistema-sus-hackapel.git

# Fazer push
git push -u origin main
```

Se pedir autenticação:
- Username: `gcost44`
- Password: Use **Personal Access Token**
  - GitHub → Settings → Developer Settings → Personal Access Tokens → Generate new token

## 4️⃣ Deploy no Railway ⭐

1. Acesse: **https://railway.app**
2. Login com GitHub
3. **"New Project"** → **"Deploy from GitHub repo"**
4. Selecione: `gcost44/sistema-sus-hackapel`
5. Railway detecta tudo automaticamente
6. Aba **"Variables"** → Add:
   - `GEMINI_API_KEY` = `AIzaSyAC68hEyU437imZXY7CsCn0Jp41cygRvPc`
7. Aba **"Settings"** → **"Generate Domain"**
8. Aguarde deploy (~5 min)
9. ✅ Pronto! Sistema online

**Guia detalhado:** Veja `RAILWAY.md`

## 5️⃣ Alternativa: Render (se preferir gratuito)

1. Acesse: https://render.com
2. Faça login com GitHub
3. **New** → **Web Service**
4. Conecte o repositório: `sistema-sus-hackapel`
5. Configure:
   - Name: `sistema-sus-hackapel`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
6. Environment Variables:
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyAC68hEyU437imZXY7CsCn0Jp41cygRvPc`
7. Clique em **"Create Web Service"**
8. Aguarde ~5 minutos

## 6️⃣ Verificar Deploy

Após deploy, teste:
- ✅ Página inicial carrega
- ✅ Upload de Excel funciona
- ✅ Agendamento funciona
- ✅ Simulador WhatsApp abre
- ✅ Orientações são geradas

## 🔧 Comandos Git Úteis

```powershell
# Ver status
git status

# Ver histórico
git log --oneline

# Fazer novos commits
git add .
git commit -m "Mensagem"
git push

# Ver repositórios remotos
git remote -v
```

## ⚠️ Problemas Comuns

### Erro: "fatal: not a git repository"
```powershell
git init
```

### Erro: "Permission denied"
Use Personal Access Token em vez de senha

### Erro: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/gcost44/sistema-sus-hackapel.git
```

## 📱 Resultado Final

Após deploy bem-sucedido:
- 🌐 URL pública do sistema
- ✅ Acessível de qualquer lugar
- ✅ Pronto para apresentação Hackapel

---

**Dica:** Recomendo Railway - é o mais simples e funciona 100%! 🚀
