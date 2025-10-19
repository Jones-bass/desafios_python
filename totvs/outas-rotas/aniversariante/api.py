import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os
# Assumindo que a importação do TOKEN está correta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN 


PERSON_DATA_URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/analytics/v2/seller-panel/seller/period-birthday" 
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

FILTERS_PAYLOAD = {
    "datemin": "2025-12-01T00:00:00Z",    # Início do período
    "datemax": "2025-12-31T23:59:59Z",    # Fim do período
}

# === PAGINAÇÃO ===
page = 1
page_size = 500
all_person_details = []

print("🚀 Iniciando consulta de Dados Cadastrais de Pessoas...")

while True:
    # Montando o payload: apenas datas, page e pageSize
    payload = {
        "datemin": FILTERS_PAYLOAD.get("datemin"),
        "datemax": FILTERS_PAYLOAD.get("datemax"),
        "page": page,
        "pageSize": page_size
    }
    
    print(f"\n👤 Consultando página {page} de registros de pessoas…")
    
    resp = requests.post(PERSON_DATA_URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        # Acessando a lista de detalhes
        person_rows = data.get("dataRow", []) 
        items_to_check = person_rows # Usamos para controle de paginação

    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check:
        if page == 1:
             print("⚠️ Nenhuma pessoa encontrada para os filtros de data aplicados.")
        else:
             print("✅ Paginação concluída (não há mais dados).")
        break
    
    
    # Processa os itens
    for item in person_rows:
        all_person_details.append({
            "CodigoPessoa": item.get("personCode"),
            "NomePessoa": item.get("personName"),
            "Documento": item.get("documentNumber"),
            "Telefone": item.get("phoneNumber"),
            "DataNascimento": item.get("birthdayDate"),
            
            # Adiciona contexto de filtro
            "Periodo_Filtro": f"{FILTERS_PAYLOAD.get('datemin').split('T')[0]} a {FILTERS_PAYLOAD.get('datemax').split('T')[0]}",
        })

    # Controle de Paginação
    if len(person_rows) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
# --- EXPORTAÇÃO ---
df_details = pd.DataFrame(all_person_details)

print("-" * 30)

if df_details.empty:
    print("⚠️ Nenhum dado de pessoas encontrado para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("datemin").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("datemax").split('T')[0]
    
    excel_file = f"cadastro_pessoas_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_details.to_excel(writer, sheet_name="DetalhesPessoas", index=False)
            print(f"Total de registros de pessoas: {len(df_details)}")
        
        print(f"✅ Relatório gerado: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")