import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/branch-ranking/search" 

# === CONFIGURAÇÕES DA API DE VENDAS (COMPARATIVO) ===
# Mantendo a mesma URL, pois o retorno pode variar com os filtros ou parâmetros.
SALES_COMPARATIVE_URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/totals/search" 
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === FILTROS DE CONSULTA (PAYLOAD) ===
# ⚠️ AJUSTE ESTES VALORES PARA SUA NECESSIDADE ⚠️
# Para um comparativo anual, você deve consultar o período do ANO ATUAL.
# A API se encarrega de buscar o ano anterior (dataRowLastYear) com base neste filtro.
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
all_sales_summaries = [] # Para armazenar dados de resumo do retorno (se houver)

print("🚀 Iniciando consulta de Vendas (Comparativo Anual)...")

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

    print(f"\n⏰ Consultando página {page} de dados comparativos…")
    
    resp = requests.post(SALES_COMPARATIVE_URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        # 1. Extração do Ano Atual
        current_items = data.get("dataRow", []) 
        
        # 2. Extração do Ano Passado
        last_year_items = data.get("dataRowLastYear", [])
        
        # Usamos 'current_items' para controle de paginação
        items_to_check = current_items 

    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check and page == 1:
        print("⚠️ Nenhuma venda encontrada para o período atual e filtros aplicados.")
        break
    
    if not items_to_check and page > 1:
        print("✅ Paginação concluída (não há mais dados).")
        break
    
    
    # Processa os itens do ANO ATUAL
    for item in current_items:
        all_sales_current.append({
            "Ano": "Atual",
            "Qtd": item.get("invoice_qty"),
            "ValorLiquido": item.get("invoice_value"),
            "Itens_Qty": item.get("itens_qty"),
            "TicketMedio": item.get("tm"),       # Ticket Médio
            "Pca-Atendida": item.get("pa"),       # Peças por Atendimento
            "PMPV": item.get("pmpv"),   # Preço Médio por Peça Vendida
        })

    # Processa os itens do ANO PASSADO
    for item in last_year_items:
        all_sales_last_year.append({
            "Ano": "Anterior",
            "Invoice_Qty": item.get("invoice_qty"),
            "Invoice_Value": item.get("invoice_value"),
            "Itens_Qty": item.get("itens_qty"),
            "TM": item.get("tm"),
            "PA": item.get("pa"),
            "PMPV": item.get("pmpv"),
        })

    # Controle de Paginação:
    # Assumimos que a ausência de itens (current_items vazio) ou um total de itens que atinge o pageSize para a página
    # Controla a quebra do loop.
    if len(current_items) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
# --- EXPORTAÇÃO ---
df_current = pd.DataFrame(all_sales_current)
df_last_year = pd.DataFrame(all_sales_last_year)

print("-" * 30)

if df_current.empty and df_last_year.empty:
    print("⚠️ Nenhum dado de vendas para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("datemin").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("datemax").split('T')[0]
    excel_file = f"vendas_comparativo_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel com duas abas
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            if not df_current.empty:
                df_current.to_excel(writer, sheet_name="AnoAtual", index=False)
                print(f"Total de registros Ano Atual: {len(df_current)}")
            
            if not df_last_year.empty:
                df_last_year.to_excel(writer, sheet_name="AnoAnterior", index=False)
                print(f"Total de registros Ano Anterior: {len(df_last_year)}")
        
        print(f"✅ Relatório gerado: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")