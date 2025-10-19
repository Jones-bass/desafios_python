import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

# === CONFIGURAÇÕES DA API DE CLASSIFICAÇÃO DE PRODUTOS ===
CLASSIFICATION_URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/product-classifications/search" 

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
    
    # 💥 CORREÇÃO PRINCIPAL: CAMPO OBRIGATÓRIO FALTANTE
    "classification_type_code": "102", # ⚠️ Substitua "GRUPO" pelo código real da classificação (ex: MARCA, COR, etc.)
}

# === PAGINAÇÃO ===
page = 1
page_size = 500
all_classification_details = []
all_summaries = [] 

print("🚀 Iniciando consulta de Vendas por Classificação de Produto...")

while True:
    # Montando o payload para a requisição POST (sem a chave "filter")
    payload = {
        "branchs": FILTERS_PAYLOAD.get("branchs", []),
        "datemin": FILTERS_PAYLOAD.get("datemin"),
        "datemax": FILTERS_PAYLOAD.get("datemax"),
        
        # 💥 CORREÇÃO: INCLUINDO O CAMPO OBRIGATÓRIO
        "classification_type_code": FILTERS_PAYLOAD.get("classification_type_code"),
        
        "page": page,
        "pageSize": page_size
    }
    
    # Adicionando filtros opcionais (nenhum nesta versão)

    print(f"\n🏷️ Consultando página {page} de classificações…")
    
    resp = requests.post(CLASSIFICATION_URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        # 1. Extração dos Detalhes por Classificação
        classification_items = data.get("dataRow", []) 
        items_to_check = classification_items 

        # --- Processamento do Resumo ---
        if page == 1:
            all_summaries.append({
                "InvoiceQuantity": data.get("invoiceQuantity"),
                "InvoiceValue": data.get("invoiceValue"),
                "ItemQuantity": data.get("itemQuantity"),
            })

    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check:
        print("✅ Paginação concluída (não há mais dados).")
        break
    
    # Processa os itens de classificação
    for item in classification_items:
        all_classification_details.append({
            "CodigoClassificacao": item.get("classification_code"),
            "NomeClassificacao": item.get("classification_name"),
            "ValorVenda": item.get("invoice_value"),
            "QuantidadeItens": item.get("item_quantity"),
            "BranchCode_Filtro": FILTERS_PAYLOAD.get("branchs", [None])[0],
            "TipoClassificacao_Filtro": FILTERS_PAYLOAD.get("classification_type_code") # Adiciona o tipo para contexto
        })

    # Controle de Paginação
    if len(classification_items) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
# --- EXPORTAÇÃO ---
df_details = pd.DataFrame(all_classification_details)
df_summary = pd.DataFrame(all_summaries)

print("-" * 30)

if df_details.empty:
    print("⚠️ Nenhum dado de vendas por classificação encontrado para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("datemin").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("datemax").split('T')[0]
    excel_file = f"vendas_por_classificacao_{FILTERS_PAYLOAD.get('classification_type_code')}_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel com abas separadas
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_details.to_excel(writer, sheet_name="DetalhesClassificacao", index=False)
            print(f"Total de registros de classificação: {len(df_details)}")

            if not df_summary.empty:
                df_summary.to_excel(writer, sheet_name="ResumoGeral", index=False)
                print("Resumo Geral exportado.")
        
        print(f"✅ Relatório gerado: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")