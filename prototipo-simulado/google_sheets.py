"""
📊 Google Sheets Integration
Sistema SUS - Hackapel 2025
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Escopo necessário para ler/escrever
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

class GoogleSheetsClient:
    """Cliente para Google Sheets"""
    
    def __init__(self):
        self.client = None
        self.sheet = None
        self.worksheet = None
        self.conectado = False
        self._conectar()
    
    def _conectar(self):
        """Conecta ao Google Sheets"""
        try:
            # Credenciais podem vir de arquivo ou variável de ambiente
            creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON', '')
            sheet_id = os.environ.get('GOOGLE_SHEET_ID', '')
            
            if not creds_json or not sheet_id:
                print("⚠️ Google Sheets: Credenciais não configuradas")
                print("   Configure GOOGLE_CREDENTIALS_JSON e GOOGLE_SHEET_ID")
                return
            
            # Parse das credenciais
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            
            # Conectar
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(sheet_id)
            self.worksheet = self.sheet.sheet1  # Primeira aba
            
            self.conectado = True
            print(f"✅ Google Sheets conectado: {self.sheet.title}")
            
        except Exception as e:
            print(f"❌ Erro ao conectar Google Sheets: {e}")
            self.conectado = False
    
    def carregar_dados(self):
        """Carrega todos os dados da planilha"""
        if not self.conectado:
            return None
        
        try:
            # Pegar todos os dados como lista de dicionários
            dados = self.worksheet.get_all_records()
            return dados
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return None
    
    def buscar_vaga(self, exame):
        """Busca primeira vaga disponível para um exame"""
        if not self.conectado:
            return None, None
        
        try:
            dados = self.worksheet.get_all_records()
            
            for idx, row in enumerate(dados):
                if row.get('exame') == exame and str(row.get('disponivel', '')).upper() == 'SIM':
                    return idx + 2, row  # +2 porque linha 1 é cabeçalho e índice começa em 0
            
            return None, None
        except Exception as e:
            print(f"❌ Erro ao buscar vaga: {e}")
            return None, None
    
    def reservar_vaga(self, linha, nome, telefone):
        """Reserva uma vaga para um paciente"""
        if not self.conectado:
            return False
        
        try:
            # Encontrar colunas
            cabecalho = self.worksheet.row_values(1)
            
            col_disponivel = cabecalho.index('disponivel') + 1
            col_paciente = cabecalho.index('paciente') + 1 if 'paciente' in cabecalho else None
            col_telefone = cabecalho.index('telefone') + 1 if 'telefone' in cabecalho else None
            col_status = cabecalho.index('status_confirmacao') + 1 if 'status_confirmacao' in cabecalho else None
            
            # Atualizar células
            self.worksheet.update_cell(linha, col_disponivel, 'NAO')
            
            if col_paciente:
                self.worksheet.update_cell(linha, col_paciente, nome)
            if col_telefone:
                self.worksheet.update_cell(linha, col_telefone, telefone)
            if col_status:
                self.worksheet.update_cell(linha, col_status, 'PENDENTE')
            
            print(f"✅ Vaga reservada: linha {linha} para {nome}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao reservar vaga: {e}")
            return False
    
    def buscar_por_telefone(self, telefone):
        """Busca paciente por telefone (últimos 8 dígitos)"""
        if not self.conectado:
            return None, None
        
        try:
            dados = self.worksheet.get_all_records()
            tel_busca = ''.join(c for c in str(telefone) if c.isdigit())[-8:]
            
            for idx, row in enumerate(dados):
                tel_row = ''.join(c for c in str(row.get('telefone', '')) if c.isdigit())
                if tel_row.endswith(tel_busca):
                    return idx + 2, row  # +2 por cabeçalho
            
            return None, None
        except Exception as e:
            print(f"❌ Erro ao buscar telefone: {e}")
            return None, None
    
    def atualizar_status(self, linha, status):
        """Atualiza status de confirmação"""
        if not self.conectado:
            return False
        
        try:
            cabecalho = self.worksheet.row_values(1)
            col_status = cabecalho.index('status_confirmacao') + 1 if 'status_confirmacao' in cabecalho else None
            
            if col_status:
                self.worksheet.update_cell(linha, col_status, status)
                print(f"✅ Status atualizado: linha {linha} -> {status}")
                return True
            return False
        except Exception as e:
            print(f"❌ Erro ao atualizar status: {e}")
            return False
    
    def liberar_vaga(self, linha):
        """Libera uma vaga (cancelamento)"""
        if not self.conectado:
            return False
        
        try:
            cabecalho = self.worksheet.row_values(1)
            
            col_disponivel = cabecalho.index('disponivel') + 1
            col_paciente = cabecalho.index('paciente') + 1 if 'paciente' in cabecalho else None
            col_telefone = cabecalho.index('telefone') + 1 if 'telefone' in cabecalho else None
            col_status = cabecalho.index('status_confirmacao') + 1 if 'status_confirmacao' in cabecalho else None
            
            self.worksheet.update_cell(linha, col_disponivel, 'SIM')
            if col_paciente:
                self.worksheet.update_cell(linha, col_paciente, '')
            if col_telefone:
                self.worksheet.update_cell(linha, col_telefone, '')
            if col_status:
                self.worksheet.update_cell(linha, col_status, 'CANCELADO')
            
            print(f"✅ Vaga liberada: linha {linha}")
            return True
        except Exception as e:
            print(f"❌ Erro ao liberar vaga: {e}")
            return False
    
    def contar_metricas(self):
        """Conta métricas da planilha"""
        if not self.conectado:
            return {"agendados": 0, "confirmados": 0, "cancelados": 0, "lembretes": 0}
        
        try:
            dados = self.worksheet.get_all_records()
            
            agendados = sum(1 for r in dados if r.get('paciente') and str(r.get('paciente')).strip())
            confirmados = sum(1 for r in dados if str(r.get('status_confirmacao', '')).upper() == 'CONFIRMADO')
            cancelados = sum(1 for r in dados if str(r.get('status_confirmacao', '')).upper() == 'CANCELADO')
            
            return {
                "agendados": agendados,
                "confirmados": confirmados,
                "cancelados": cancelados,
                "lembretes": 0
            }
        except Exception as e:
            print(f"❌ Erro ao contar métricas: {e}")
            return {"agendados": 0, "confirmados": 0, "cancelados": 0, "lembretes": 0}
    
    def listar_agendamentos(self):
        """Lista agendamentos com paciente"""
        if not self.conectado:
            return []
        
        try:
            dados = self.worksheet.get_all_records()
            
            agendamentos = []
            for idx, row in enumerate(dados):
                paciente = row.get('paciente', '')
                if paciente and str(paciente).strip():
                    agendamentos.append({
                        "id": idx + 1,
                        "paciente": str(paciente),
                        "telefone": str(row.get('telefone', '')),
                        "exame": str(row.get('exame', '')),
                        "clinica": str(row.get('clinica', '')),
                        "data": str(row.get('data', '')),
                        "horario": str(row.get('horario', '')),
                        "status": str(row.get('status_confirmacao', 'PENDENTE')).lower()
                    })
            
            return agendamentos
        except Exception as e:
            print(f"❌ Erro ao listar agendamentos: {e}")
            return []
    
    def status_planilha(self):
        """Retorna status da planilha"""
        if not self.conectado:
            return {"carregado": False}
        
        try:
            dados = self.worksheet.get_all_records()
            total = len(dados)
            disponiveis = sum(1 for r in dados if str(r.get('disponivel', '')).upper() == 'SIM')
            
            return {
                "carregado": True,
                "total_horarios": total,
                "vagas_disponiveis": disponiveis,
                "vagas_ocupadas": total - disponiveis
            }
        except Exception as e:
            print(f"❌ Erro ao verificar status: {e}")
            return {"carregado": False}


# Instância global
sheets_client = GoogleSheetsClient()
