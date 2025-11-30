"""
Criador de planilha de agendamentos SUS
"""
import pandas as pd
from datetime import datetime, timedelta
from openpyxl import load_workbook

def criar_planilha(arquivo="agenda_clinicas.xlsx"):
    clinicas = ["Hospital Central", "UBS Norte", "UBS Sul", "Clínica Popular"]
    exames = ["Cardiologista", "Oncologista", "Ortopedista", "Oftalmologista", "Dermatologista", "Nutricionista"]
    horarios = ["08:00", "09:00", "10:00", "14:00", "15:00", "16:00"]
    
    dados = []
    for dia in range(30):
        data = (datetime.now() + timedelta(days=dia)).strftime("%d/%m/%Y")
        for clinica in clinicas:
            for exame in exames:
                for h in horarios:
                    dados.append({
                        "clinica": clinica, "exame": exame, "data": data, "horario": h,
                        "disponivel": "SIM", "paciente": "", "telefone": "", "status_confirmacao": ""
                    })
    
    df = pd.DataFrame(dados)
    df.to_excel(arquivo, index=False, engine='openpyxl')
    
    # Formatar telefone como texto
    wb = load_workbook(arquivo)
    ws = wb.active
    for row in range(2, ws.max_row + 1):
        ws.cell(row=row, column=7).number_format = '@'
    wb.save(arquivo)
    
    print(f"✅ {arquivo}: {len(df)} horários criados")

if __name__ == "__main__":
    criar_planilha()
