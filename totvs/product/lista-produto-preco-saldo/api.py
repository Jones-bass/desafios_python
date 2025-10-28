import requests
import pandas as pd
import json
from datetime import datetime
import sys
import os

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === FUNÇÃO AUXILIAR ===
def safe_list(value):
    """Garante que o retorno seja sempre uma lista."""
    return value if isinstance(value, list) else []

# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/balances/search"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("🚀 Consultando saldos de produtos...")

# === REQUEST BODY ===
payload = {
    "filter": {
        "change": {
            "startDate": "2025-09-01T00:00:00Z",
            "endDate": "2025-09-30T23:59:59Z",
            "inBranchInfo": True,
            "branchInfoCodeList": [1],
        },
        "branchInfo": {
            "branchCode": 1
        }
    },
    "option": {
        "balances": [
            {
                "branchCode": 1,
                "stockCodeList": [1]
            }
        ]
    },
    "page": 1,
    "pageSize": 100,
    "order": "productCode",
    "expand": ""
}

# === REQUISIÇÃO POST ===
try:
    response = requests.post(URL, headers=headers, json=payload, timeout=60)
except requests.exceptions.RequestException as e:
    print(f"❌ Erro na conexão com a API: {e}")
    sys.exit(1)

print(f"📡 Status HTTP: {response.status_code}")
if response.status_code != 200:
    print("❌ Erro na resposta da API:")
    print(response.text)
    sys.exit(1)

# === TRATAMENTO DO JSON ===
try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    print("❌ Erro ao decodificar JSON da resposta.")
    sys.exit(1)

# === SALVA DEBUG ===
debug_file = f"debug_balances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === PROCESSA RESPOSTA ===
items = data.get("items", [])
if not items:
    print("⚠️ Nenhum produto retornado pela API.")
    sys.exit(0)

# === TABELAS ===
produtos = []
saldos = []
localizacoes = []

for item in items:
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
excel_file = f"product_balances_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_produtos.to_excel(writer, index=False, sheet_name="Produtos")
    if not df_saldos.empty:
        df_saldos.to_excel(writer, index=False, sheet_name="Saldos")
    if not df_localizacoes.empty:
        df_localizacoes.to_excel(writer, index=False, sheet_name="Localizacoes")

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
