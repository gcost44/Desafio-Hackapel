# 🤖 Integração com Google Gemini API

## 📋 Visão Geral

O sistema utiliza a API do **Google Gemini 1.5 Flash** para gerar automaticamente orientações educativas personalizadas para qualquer tipo de exame ou consulta médica.

## 🎯 Funcionalidade

### Antes (Estático)
- Orientações manuais para apenas 5 especialidades
- Impossível cobrir todos os tipos de exames
- Atualização manual trabalhosa

### Depois (Dinâmico com Gemini)
- **Orientações automáticas para QUALQUER exame**
- Geração em tempo real baseada em IA
- Conteúdo sempre atualizado e contextualizado
- Linguagem simples e acessível para o público SUS

## 🚀 Como Configurar

### 1. Obter Chave da API (Gratuito)

1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### 2. Configurar no Sistema

**Opção A - Variável de Ambiente (Recomendado)**
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="sua_chave_aqui"
python app.py
```

```bash
# Linux/Mac
export GEMINI_API_KEY="sua_chave_aqui"
python app.py
```

**Opção B - Direto no Código**
Edite o arquivo `app.py`, linha ~23:
```python
GEMINI_API_KEY = 'SUA_CHAVE_AQUI'
```

### 3. Instalar Dependência

```powershell
pip install google-generativeai
```

## 📝 Como Funciona

### Fluxo de Geração

1. **Paciente agenda** consulta para "Dermatologista"
2. **Sistema chama** `gerar_orientacoes_educativas("Dermatologista")`
3. **Gemini recebe** prompt estruturado:
   ```
   Gere orientações educativas para: Dermatologista
   Formato: [EMOJI] ORIENTAÇÕES + Itens + Jejum + Dicas Preventivas
   ```
4. **IA gera** conteúdo personalizado em ~2 segundos
5. **Sistema envia** orientação via WhatsApp junto com confirmação

### Exemplo de Output

```
🌟 ORIENTAÇÕES - DERMATOLOGIA

📋 O que levar:
• Documentos de identificação (RG, CPF, Cartão SUS)
• Fotos de lesões anteriores (se tiver)
• Lista de produtos que usa na pele

⚠️ Jejum: NÃO é necessário
🏃 Chegue 10 minutos antes

💡 DICAS PREVENTIVAS:
• Use protetor solar FPS 30+ diariamente
• Evite sol das 10h às 16h
• Hidrate a pele com produtos adequados
• Observe mudanças em pintas ou manchas
```

## 🎨 Prompt Engineering

### Template Otimizado

O sistema usa um prompt estruturado que garante:

✅ **Formato consistente** - Sempre segue o padrão com emojis  
✅ **Linguagem acessível** - Adaptado para público SUS  
✅ **Informações precisas** - Baseado em guidelines médicos  
✅ **Foco preventivo** - Enfatiza educação em saúde (EIXO 3)  
✅ **Tamanho ideal** - Máximo 150 palavras para WhatsApp  

## 🔒 Segurança e Limites

### Limites Gratuitos (Gemini 1.5 Flash)
- **15 requisições/minuto**
- **1.500 requisições/dia**
- **1 milhão tokens/mês**

**Uso estimado no sistema:**
- ~500 tokens por orientação
- ~3.000 orientações/mês grátis
- Suficiente para até 100 agendamentos/dia

### Fallback Automático

Se a API falhar (sem internet, cota excedida, erro):
```python
# Sistema usa orientação genérica automática
return """
📋 ORIENTAÇÕES GERAIS
O que levar: Documentos, exames anteriores...
"""
```

## 📊 Benefícios para o EIXO 3

### Educação em Saúde Automatizada

1. **Cobertura Total**
   - Gera orientações para +100 tipos de exames
   - Não limitado a especialidades pré-definidas

2. **Conteúdo Atualizado**
   - IA usa conhecimento médico recente
   - Dicas preventivas baseadas em evidências

3. **Personalização**
   - Adaptado para cada tipo de exame
   - Linguagem adequada ao contexto

4. **Escala Ilimitada**
   - Gera milhares de orientações/dia
   - Sem custo adicional de equipe

## 🧪 Teste Rápido

### Comando no PowerShell

```powershell
# Configure a chave
$env:GEMINI_API_KEY="sua_chave"

# Inicie o sistema
cd prototipo-simulado
python app.py

# No navegador (http://localhost:5000):
# 1. Faça upload da planilha
# 2. Agende para "Nutricionista" (não está na lista estática)
# 3. Veja a orientação gerada automaticamente!
```

### Exemplos de Exames para Testar

Teste com exames que NÃO estavam no sistema original:
- Nutricionista
- Psiquiatra
- Reumatologista
- Endocrinologista
- Gastroenterologista
- Pneumologista
- Urologista

## 📈 Métricas de Sucesso

O dashboard rastreia:
- **Orientações Educativas:** Contador de mensagens enviadas
- **Taxa de Resposta:** Impacto da educação em saúde
- **Tipos de Exame:** Diversidade de orientações geradas

## 🛠️ Troubleshooting

### Erro: "API key not valid"
```powershell
# Verifique se a chave está correta
echo $env:GEMINI_API_KEY
# Gere nova chave em: https://makersuite.google.com/app/apikey
```

### Erro: "Module not found: generativeai"
```powershell
pip install --upgrade google-generativeai
```

### Orientação genérica aparece
- Sistema está usando fallback (sem internet ou cota excedida)
- Verifique logs do terminal para detalhes do erro
- Normal durante desenvolvimento sem chave configurada

## 💡 Próximos Passos

### Melhorias Futuras
1. **Cache de orientações** - Evitar regenerar para mesmo exame
2. **Múltiplos idiomas** - Português, Espanhol, Inglês
3. **Personalização por região** - Adaptar para características locais
4. **Feedback loop** - Melhorar prompts com base em respostas dos pacientes

### Integração com Outras APIs
- **WhatsApp Business API** - Envio real de mensagens
- **Google Calendar** - Sincronização de agendamentos
- **Prontuário Eletrônico** - Integração com sistemas municipais

---

## 📞 Suporte

**Documentação Gemini:** https://ai.google.dev/docs  
**GitHub Issues:** https://github.com/gcost44/Desafio-Hackapel/issues

---

**Desenvolvido para Hackapel 2025**  
**EIXO 3: Educação em Saúde Automatizada com IA**
