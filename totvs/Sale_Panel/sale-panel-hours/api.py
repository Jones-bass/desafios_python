import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

# === CONFIGURAÇÕES DA API DE VENDAS POR HORA DETALHADA ===
SALES_DETAIL_URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/hours/search"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === FILTROS DE CONSULTA (PAYLOAD) ===
# ⚠️ AJUSTE ESTES VALORES PARA SUA NECESSIDADE ⚠️
FILTERS_PAYLOAD = {
    "branchs": [5],                       # Lista de códigos de filiais
    "datemin": "2025-09-01T00:00:00Z",    # Data/Hora inicial no formato ISO 8601
    "datemax": "2025-09-30T23:59:59Z",    # Data/Hora final no formato ISO 8601
    # "operations": [1, 2],                 # Exemplo de filtro opcional
    # "sellers": [100],                     # Exemplo de filtro opcional
}

# === PAGINAÇÃO ===
page = 1
page_size = 500 # Valor máximo recomendado ou permitido pela API
all_sales_details = []
# Lista para armazenar o resumo de cada página (se houver necessidade)
all_summaries = [] 

print("🚀 Iniciando consulta de Vendas por Hora (Detalhada)...")

while True:
    # Montando o payload sem a chave "filter"
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

    print(f"\n⏰ Consultando página {page} de vendas detalhadas…")
    
    resp = requests.post(SALES_DETAIL_URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        # 1. Extração dos Detalhes de Vendas por Hora
        classification_items = data.get("dataRow", []) 
        items_to_check = classification_items 

        # --- Processamento do Resumo ---
        # Armazena o resumo, usando "InvoiceValue" para consistência
        all_summaries.append({
            "InvoiceQuantity": data.get("invoiceQuantity"),
            "InvoiceValue": data.get("invoiceValue"), # <--- CORREÇÃO APLICADA AQUI!
            "ItemQuantity": data.get("itemQuantity"),
            "Page": page 
        })

    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check:
        print("⚠️ Nenhuma venda encontrada nesta página ou para os filtros aplicados.")
        break
    
    # Processa os itens
    for item in items_to_check:
        all_sales_details.append({
            "DataHoraVenda": item.get("saledatetime_hour"),
            "Qtd": item.get("invoice_qty"),
            "ValorLiquido": item.get("invoice_value"),
            # Campos extras podem ser adicionados aqui se o retorno da API mudar
        })

    # Controle de Paginação
    if len(items_to_check) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
# --- EXPORTAÇÃO ---
df_sales_detail = pd.DataFrame(all_sales_details)

# CORREÇÃO: Usando 'InvoiceValue' corretamente para drop_duplicates
df_summary = pd.DataFrame(all_summaries).drop_duplicates(subset=['InvoiceValue']) 

print("-" * 30)

if df_sales_detail.empty:
    print("⚠️ Nenhum dado de vendas por hora encontrado para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("datemin").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("datemax").split('T')[0]
    excel_file = f"vendas_por_hora_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel com abas separadas
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_sales_detail.to_excel(writer, sheet_name="VendasPorHora", index=False)
            
            if not df_summary.empty:
                # Seleciona apenas a primeira linha do resumo e remove a coluna de rastreio 'Page'
                df_summary.head(1).drop(columns=['Page']).to_excel(writer, sheet_name="ResumoGeral", index=False)
        
        print(f"✅ Relatório gerado: {excel_file}")
        print(f"Total de registros de vendas por hora: {len(df_sales_detail)}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")