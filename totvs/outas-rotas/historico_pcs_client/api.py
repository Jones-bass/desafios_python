import requests
import pandas as pd
from datetime import datetime, timezone

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN 

SALES_HISTORY_URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/analytics/v2/seller-panel/seller/customer-purchased-products" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

FILTERS_PAYLOAD = {
    "branchCodes": [2],                       # Lista de códigos de filiais
    "startDate": "2025-01-01T00:00:00Z",      # Início do período
    "endDate": "2025-10-30T23:59:59Z",        # Fim do período
    
    "customerCode": 575, 
}

# === PAGINAÇÃO ===
page = 1 # 💥 CORREÇÃO: MUDANÇA PARA PÁGINA 1 💥
page_size = 500
all_sales_items = []

print("🚀 Iniciando consulta de Histórico de Compras Detalhado (Item a Item)...")

while True:
    # Montando o payload com base no modelo fornecido
    payload = {
        "branchCodes": FILTERS_PAYLOAD.get("branchCodes", []),
        "startDate": FILTERS_PAYLOAD.get("startDate"),
        "endDate": FILTERS_PAYLOAD.get("endDate"),
        
        # Incluindo customerCode explicitamente
        "customerCode": FILTERS_PAYLOAD.get("customerCode", 0),
        
        # Paginação
        "page": page,
        "pageSize": page_size
    }
    
    print(f"\n🛒 Consultando página {page} de itens vendidos…")
    
    resp = requests.post(SALES_HISTORY_URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
        
        items_list = data.get("items", []) 
        items_to_check = items_list 

    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    if not items_to_check:
        if page == 1: # Mudança de 0 para 1
             print("⚠️ Nenhum item encontrado para os filtros aplicados.")
        else:
             print("✅ Paginação concluída (não há mais dados).")
        break
    
    
    # Processa os itens
    for item in items_list:
        all_sales_items.append({
            # Informações de Transação
            "Filial": item.get("branchCode"),
            "SequenciaNota": item.get("invoiceSequence"),
            "DataCompra": item.get("purchaseDate"),
            "NumeroNota": item.get("invoiceNumber"),
            
            # Cliente e Vendedor
            "CodCliente": item.get("customerCode"),
            "CPF_CNPJ": item.get("customerCpfCnpj"),
            "CodVendedor": item.get("sellerCode"),
            
            # Detalhes do Produto
            "CodProduto": item.get("productCode"),
            "DescricaoProduto": item.get("productDescription"),
            "CodCor": item.get("colorCode"),
            "DescricaoCor": item.get("colorDescription"),
            "CodTamanho": item.get("sizeCode"),
            "DescricaoTamanho": item.get("sizeDescription"),
            "CodGrupo": item.get("groupCode"),
            "NomeReferencia": item.get("referenceName"),
            
            # Valores
            "Quantidade": item.get("quantity"),
            "ValorBruto": item.get("totalGrossValue"),
            "ValorLiquido": item.get("totalNetValue"),
        })

    # Controle de Paginação
    if len(items_list) < page_size:
        print("✅ Paginação concluída (última página preenchida parcialmente).")
        break
    
    page += 1
    
# --- EXPORTAÇÃO ---
df_details = pd.DataFrame(all_sales_items)

print("-" * 30)

if df_details.empty:
    print("⚠️ Nenhum dado de histórico de compras encontrado para exportar.")
else:
    start_date = FILTERS_PAYLOAD.get("startDate").split('T')[0]
    end_date = FILTERS_PAYLOAD.get("endDate").split('T')[0]
    
    excel_file = f"historico_compras_detalhe_{start_date}_a_{end_date}.xlsx"
    
    # Exporta para Excel
    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_details.to_excel(writer, sheet_name="HistoricoComprasItem", index=False)
            print(f"Total de registros detalhados de compras: {len(df_details)}")
        
        print(f"✅ Relatório gerado: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")