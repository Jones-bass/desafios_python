import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/totals-branch/search" 
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === FILTROS DE CONSULTA (PAYLOAD) ===
# ⚠️ AJUSTE ESTES VALORES PARA SUA NECESSIDADE ⚠️
FILTERS_PAYLOAD = {
    "branchs": [5],                       # Lista de códigos de filiais
    "datemin": "2025-09-01T00:00:00Z",    # Início do período (Ano Atual)
    "datemax": "2025-09-30T23:59:59Z",    # Fim do período (Ano Atual)
    # "operations": [1],                  # Exemplo de filtro opcional
    # "sellers": [100],                   # Exemplo de filtro opcional
}

# === PAGINAÇÃO ===
page = 1
page_size = 500
all_sales_current = []
all_sales_last_year = []
all_summaries = [] # Para armazenar os objetos 'total' e 'totalLastYear'

print("🚀 Iniciando consulta de Vendas (Comparativo Anual com Detalhe de Filial)...")

# Dicionário para mapeamento dos campos de resumo
SUMMARY_FIELDS = ["invoice_qty", "invoice_value", "itens_qty", "tm", "pa", "pmpv"]

while True:
    # Montando o payload para a requisição POST (sem a chave "filter")
    payload = {
        "branchs": FILTERS_PAYLOAD.get("branchs", []),
        "datemin": FILTERS_PAYLOAD.get("datemin"),
        "datemax": FILTERS_PAYLOAD.get("datemax"),
        "page": page,
        "pageSize": page_size
    }
    
    # Adicionando filtros opcionais
    if 'operations' in FILTERS_PAYLOAD:
        payload['operations'] = FILTERS_PAYLOAD['operations']
    if 'sellers' in FILTERS_PAYLOAD:
        payload['sellers'] = FILTERS_PAYLOAD['sellers']

    print(f"\n⏰ Consultando página {page} de dados comparativos…")
    
    resp = requests.post(URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        current_items = data.get("dataRow", []) 
        last_year_items = data.get("dataRowLastYear", [])
        items_to_check = current_items # Usa current_items para controle de loop

        # --- Processamento dos Totais (Resumo) ---
        # Garantindo que os resumos sejam armazenados apenas na primeira página para evitar duplicação
        if page == 1:
            # Resumo do Ano Atual
            total_current = {"Ano": "Atual - TOTAL"}
            total_current.update({k: data.get("total", {}).get(k) for k in SUMMARY_FIELDS})
            all_summaries.append(total_current)
            
            # Resumo do Ano Anterior
            total_last_year = {"Ano": "Anterior - TOTAL"}
            total_last_year.update({k: data.get("totalLastYear", {}).get(k) for k in SUMMARY_FIELDS})
            all_summaries.append(total_last_year)


    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check:
        print("✅ Paginação concluída (não há mais dados).")
        break
    
    # Processa os itens do ANO ATUAL
    for item in current_items:
        all_sales_current.append({
            "Ano": "Atual",
            "CodeLoja": item.get("branch_code"),
            "Loja": item.get("branch_name"),
            "Qtd": item.get("invoice_qty"),
            "ValorLiquido": item.get("invoice_value"),
            "Itens_Qty": item.get("itens_qty"),
            "T-Medio": item.get("tm"),
            "P-Atendida": item.get("pa"),
            "PMPV": item.get("pmpv"),
        })

    # Processa os itens do ANO PASSADO
    for item in last_year_items:
        all_sales_last_year.append({
            "Ano": "Anterior",
            "BranchCode": item.get("branch_code"),
            "BranchName": item.get("branch_name"),
            "Invoice_Qty": item.get("invoice_qty"),
            "Invoice_Value": item.get("invoice_value"),
            "Itens_Qty": item.get("itens_qty"),
            "TM": item.get("tm"),
            "PA": item.get("pa"),
            "PMPV": item.get("pmpv"),
        })

    # Controle de Paginação (baseado no Ano Atual)
    if len(current_items) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
# --- EXPORTAÇÃO ---
df_current = pd.DataFrame(all_sales_current)
df_last_year = pd.DataFrame(all_sales_last_year)
df_summary = pd.DataFrame(all_summaries)

print("-" * 30)

if df_current.empty and df_last_year.empty:
    print("⚠️ Nenhum dado de vendas para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("datemin").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("datemax").split('T')[0]
    excel_file = f"vendas_comparativo_detalhado_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel com abas separadas
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            if not df_current.empty:
                df_current.to_excel(writer, sheet_name="AnoAtual_Detalhe", index=False)
                print(f"Total de registros Ano Atual: {len(df_current)}")
            
            if not df_last_year.empty:
                df_last_year.to_excel(writer, sheet_name="AnoAnterior_Detalhe", index=False)
                print(f"Total de registros Ano Anterior: {len(df_last_year)}")

            if not df_summary.empty:
                df_summary.to_excel(writer, sheet_name="Resumo_Geral", index=False)
                print(f"Resumo Geral (Total e Total Ano Anterior) exportado.")
        
        print(f"✅ Relatório gerado: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")