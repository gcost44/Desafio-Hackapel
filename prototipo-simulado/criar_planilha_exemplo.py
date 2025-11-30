import pandas as pd
from datetime import datetime, timedelta

print("Criando planilha exemplo...")

# Criar dados
data = []
clinicas = ["Hospital Central", "UBS Norte", "UBS Sul", "Clínica Popular"]
exames = ["Cardiologista", "Oncologista", "Ortopedista", "Oftalmologista", "Neurologista"]

for dia in range(30):  # 30 dias
    data_exame = datetime.now() + timedelta(days=dia)
    for clinica in clinicas:
        for exame in exames:
            # 5 horários por dia
            for hora in [8, 10, 14, 16, 18]:
                data.append({
                    "clinica": clinica,
                    "exame": exame,
                    "data": data_exame.strftime("%d/%m/%Y"),
                    "horario": f"{hora}:00",
                    "disponivel": "SIM",
                    "paciente": "",
                    "telefone": ""
                })

# Criar DataFrame e salvar
df = pd.DataFrame(data)
df.to_excel("planilha_exemplo.xlsx", index=False)

print(f"✅ Planilha criada: planilha_exemplo.xlsx")
print(f"📊 Total: {len(df)} horários disponíveis")
print(f"🏥 Clínicas: {', '.join(clinicas)}")
print(f"👨‍⚕️ Exames: {', '.join(exames)}")
print(f"📅 Período: {df['data'].iloc[0]} até {df['data'].iloc[-1]}")
