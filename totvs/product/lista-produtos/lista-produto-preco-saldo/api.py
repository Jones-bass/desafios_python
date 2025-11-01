import requests
import pandas as pd
import json
from datetime import datetime
import sys
import os
import time

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from auth.config import TOKEN

# === FUNÇÃO AUXILIAR ===
def safe_list(value):
    return value if isinstance(value, list) else []

# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/balances/search"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("🚀 Consultando saldos de produtos...")

# === PAGINAÇÃO ===
all_items = []
page = 1
page_size = 1000  

while True:
    payload = {
        "filter": {
            "change": {
                "startDate": "2025-09-01T00:00:00Z",
                "endDate": "2025-09-30T23:59:59Z",
                "inBranchInfo": True,
                "branchInfoCodeList": [1],
            },
            "branchInfo": {"branchCode": 1},
            "classifications": [
                {"type": 104, "codeList": ["001","002","003","004","005","006"]}
            ]
        },
        "option": {
            "balances": [{"branchCode": 1, "stockCodeList": [1]}]
        },
        "order": "productCode",
        "expand": "",
        "page": page,
        "pageSize": page_size
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na conexão: {e}")
        sys.exit(1)

    items = data.get("items", [])
    if not items:
        break

    all_items.extend(items)

    if not data.get("hasNext", False):
        break

    page += 1
    time.sleep(0.2)

print(f"✅ Total de produtos retornados: {len(all_items)}")

# === SALVA DEBUG ===
debug_file = f"debug_balances_{datetime.now():%Y%m%d_%H%M%S}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === TRATAMENTO DOS DADOS ===
produtos, saldos, localizacoes = [], [], []

for item in all_items:
    produtos.append({
        "productCode": item.get("productCode"),
        "productName": item.get("productName"),
        "productSku": item.get("productSku"),
        "referenceCode": item.get("referenceCode"),
        "colorCode": item.get("colorCode"),
        "colorName": item.get("colorName"),
        "sizeName": item.get("sizeName"),
        "maxChangeFilterDate": item.get("maxChangeFilterDate")
    })

    for b in safe_list(item.get("balances")):
        saldos.append({
            "productCode": item.get("productCode"),
            "branchCode": b.get("branchCode"),
            "stockCode": b.get("stockCode"),
            "stockDescription": b.get("stockDescription"),
            "stock": b.get("stock"),
            "salesOrder": b.get("salesOrder"),
            "inputTransaction": b.get("inputTransaction"),
            "outputTransaction": b.get("outputTransaction"),
            "productionPlanning": b.get("productionPlanning"),
            "purchaseOrder": b.get("purchaseOrder"),
            "productionOrderProgress": b.get("productionOrderProgress"),
            "productionOrderWaitLib": b.get("productionOrderWaitLib"),
            "stockTemp": b.get("stockTemp")
        })

    for loc in safe_list(item.get("locations")):
        localizacoes.append({
            "productCode": item.get("productCode"),
            "branchCode": loc.get("branchCode"),
            "locationCode": loc.get("locationCode"),
            "description": loc.get("description")
        })

# === CONVERTE PARA DATAFRAMES ===
df_produtos = pd.DataFrame(produtos)
df_saldos = pd.DataFrame(saldos)
df_localizacoes = pd.DataFrame(localizacoes)

# === EXPORTA PARA EXCEL ===
excel_file = f"product_balances_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_produtos.to_excel(writer, index=False, sheet_name="Produtos")
    if not df_saldos.empty:
        df_saldos.to_excel(writer, index=False, sheet_name="Saldos")
    if not df_localizacoes.empty:
        df_localizacoes.to_excel(writer, index=False, sheet_name="Localizacoes")

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
