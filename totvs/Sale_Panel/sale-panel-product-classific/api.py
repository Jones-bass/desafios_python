import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/branch-ranking/search" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Lista de campos de métricas para mapeamento
DETAIL_FIELDS = [
    "branchCode", "branch_name", "invoice_qty", "invoice_value", "itens_qty", 
    "tm", "pa", "pmpv", "cash_value", "pix_value", "credit_value", 
    "debit_value", "installment_value", "other_value"
]

# === FILTROS DE CONSULTA (PAYLOAD) ===
# ⚠️ AJUSTE ESTES VALORES PARA SUA NECESSIDADE ⚠️
FILTERS_PAYLOAD = {
    "branchs": [5],                       # Lista de códigos de filiais
    "datemin": "2025-09-01T00:00:00Z",    # Data/Hora inicial no formato ISO 8601
    "datemax": "2025-09-30T23:59:59Z",    # Data/Hora final no formato ISO 8601
    # Adicione outros filtros se a rota exigir
}

# === PAGINAÇÃO ===
page = 1
page_size = 500
all_sales_details = []
all_summaries = [] 

print("🚀 Iniciando consulta de Vendas Detalhadas (por Filial e Pagamento)...")

while True:
    # Montando o payload para a requisição POST (sem a chave "filter")
    payload = {
        "branchs": FILTERS_PAYLOAD.get("branchs", []),
        "datemin": FILTERS_PAYLOAD.get("datemin"),
        "datemax": FILTERS_PAYLOAD.get("datemax"),
        "page": page,
        "pageSize": page_size
    }

    print(f"\n🏬 Consultando página {page} de detalhes de vendas…")
    
    resp = requests.post(URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        # 1. Extração dos Detalhes (por Filial)
        detail_items = data.get("dataRow", []) 
        items_to_check = detail_items # Usamos esta lista para controle de loop

        # --- Processamento do Resumo Geral (apenas na primeira página) ---
        if page == 1 and data.get("invoiceValue") is not None:
            # O resumo está no nível principal, e os campos são os mesmos da lista DETAIL_FIELDS,
            # exceto por branchCode e branch_name.
            summary_data = {"Tipo": "TOTAL_GERAL"}
            summary_data.update({
                k.replace('_value', 'Value').replace('_qty', 'Quantity').upper(): data.get(k) 
                for k in DETAIL_FIELDS if k not in ["branchCode", "branch_name"]
            })
            all_summaries.append(summary_data)

    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check:
        print("✅ Paginação concluída (não há mais dados).")
        break
    
    # Processa os itens detalhados (dataRow)
    for item in detail_items:
        # Mapeamento completo de todos os campos
        all_sales_details.append({
            "BranchCode": item.get("branchCode"),
            "BranchName": item.get("branch_name"),
            "FaturaQty": item.get("invoice_qty"),
            "ValordaLiquido": item.get("invoice_value"),
            "ItensQty": item.get("itens_qty"),
            "TM": item.get("tm"),
            "PA": item.get("pa"),
            "PMPV": item.get("pmpv"),
            "CashValor": item.get("cash_value"),
            "PixValor": item.get("pix_value"),
            "CreditoValor": item.get("credit_value"),
            "DebitoValor": item.get("debit_value"),
            "ValordaParcela": item.get("installment_value"),
            "OutroValor": item.get("other_value"),
        })

    # Controle de Paginação
    if len(detail_items) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
# --- EXPORTAÇÃO ---
df_details = pd.DataFrame(all_sales_details)
df_summary = pd.DataFrame(all_summaries)

print("-" * 30)

if df_details.empty:
    print("⚠️ Nenhum dado de vendas detalhado encontrado para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("datemin").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("datemax").split('T')[0]
    excel_file = f"vendas_detalhadas_filial_pagamento_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel com abas separadas
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_details.to_excel(writer, sheet_name="DetalhesPorFilial", index=False)
            print(f"Total de registros detalhados: {len(df_details)}")

            if not df_summary.empty:
                df_summary.to_excel(writer, sheet_name="ResumoGeral", index=False)
                print("Resumo Geral exportado.")
        
        print(f"✅ Relatório gerado: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")