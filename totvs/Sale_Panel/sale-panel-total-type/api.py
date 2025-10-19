import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/document-types/search" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

FILTERS_PAYLOAD = {
    "branchs": [1,2,3,5,7],                       # Lista de códigos de filiais
    "datemin": "2025-09-01T00:00:00Z",    # Data/Hora inicial no formato ISO 8601
    "datemax": "2025-09-30T23:59:59Z",    # Data/Hora final no formato ISO 8601
    # Outros filtros podem ser necessários (ex: tipo de operação)
}

# === PAGINAÇÃO ===
page = 1
page_size = 500
all_payment_details = []
all_summaries = [] 

print("🚀 Iniciando consulta de Vendas por Forma de Pagamento...")

while True:
    # Montando o payload para a requisição POST (sem a chave "filter")
    payload = {
        "branchs": FILTERS_PAYLOAD.get("branchs", []),
        "datemin": FILTERS_PAYLOAD.get("datemin"),
        "datemax": FILTERS_PAYLOAD.get("datemax"),
        "page": page,
        "pageSize": page_size
    }
    

    print(f"\n💳 Consultando página {page} de pagamentos…")
    
    resp = requests.post(URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        # 1. Extração dos Detalhes de Pagamento
        payment_items = data.get("dataRow", []) 
        items_to_check = payment_items # Usamos esta lista para controle de loop

        # --- Processamento do Resumo ---
        # Armazena o resumo apenas na primeira página
        if page == 1:
            all_summaries.append({
                "invoiceQuantity": data.get("invoiceQuantity"),
                "ValorLiquido": data.get("invoiceValue"),
                "itemQuantity": data.get("itemQuantity"),
            })

    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check:
        print("✅ Paginação concluída (não há mais dados).")
        break
    
    # Processa os itens de pagamento
    for item in payment_items:
        all_payment_details.append({
            "TipoDocumentoPagamento": item.get("payment_document_type"),
            "ValorPagamento": item.get("payment_value"),
            "BranchCode_Filtro": FILTERS_PAYLOAD.get("branchs", [None])[0],
        })

    if len(payment_items) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
df_details = pd.DataFrame(all_payment_details)
df_summary = pd.DataFrame(all_summaries)

print("-" * 30)

if df_details.empty:
    print("⚠️ Nenhum dado de pagamento encontrado para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("datemin").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("datemax").split('T')[0]
    excel_file = f"vendas_por_pagamento_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel com abas separadas
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_details.to_excel(writer, sheet_name="DetalhesPagamento", index=False)
            print(f"Total de registros de pagamento: {len(df_details)}")

            if not df_summary.empty:
                df_summary.to_excel(writer, sheet_name="ResumoGeral", index=False)
                print("Resumo Geral exportado.")
        
        print(f"✅ Relatório gerado: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")