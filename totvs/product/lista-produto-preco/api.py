import requests
import pandas as pd
import json
from datetime import datetime
import sys
import os

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/prices/search"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("🚀 Consultando preços de produtos...")

# === REQUEST BODY CORRIGIDO ===
payload = {
    "filter": {
        "change": {
            "startDate": "2025-09-01T00:00:00Z",
            "endDate": "2025-10-27T23:59:59Z",
            "inBranchInfo": True,
            "branchInfoCodeList": [2],
        },
    },
    "option": {
        "prices": [
            {
                "branchCode": 1,           
                "priceCodeList": [1],       
                "isPromotionalPrice": True,
                "isScheduledPrice": True
            }
        ],
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
    print(f"❌ Erro na conexão: {e}")
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
debug_file = f"debug_product_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === PROCESSA RESPOSTA ===
items = data.get("items", [])
if not items:
    print("⚠️ Nenhum produto retornado pela API.")
    sys.exit(0)

# === TABELA PRINCIPAL: PRODUTOS ===
produtos = []
precos = []

for item in items:
    produto = {
        "productCode": item.get("productCode"),
        "productName": item.get("productName"),
        "productSku": item.get("productSku"),
        "referenceCode": item.get("referenceCode"),
        "colorCode": item.get("colorCode"),
        "colorName": item.get("colorName"),
        "sizeName": item.get("sizeName"),
        "maxChangeFilterDate": item.get("maxChangeFilterDate")
    }
    produtos.append(produto)

    # === PREÇOS ===
    for preco in item.get("prices", []):
        precos.append({
            "productCode": item.get("productCode"),
            "priceCode": preco.get("priceCode"),
            "priceName": preco.get("priceName"),
            "price": preco.get("price"),
            "promotionalPrice": preco.get("promotionalPrice"),
            "promotionalDescription": (
                preco.get("promotionalInformation", {}).get("description")
                if preco.get("promotionalInformation") else None
            ),
            "promoStartDate": (
                preco.get("promotionalInformation", {}).get("startDate")
                if preco.get("promotionalInformation") else None
            ),
            "promoEndDate": (
                preco.get("promotionalInformation", {}).get("endDate")
                if preco.get("promotionalInformation") else None
            )
        })

# === CONVERTE EM DATAFRAMES ===
df_produtos = pd.DataFrame(produtos)
df_precos = pd.DataFrame(precos)

# === EXPORTA PARA EXCEL ===
excel_file = f"product_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_produtos.to_excel(writer, index=False, sheet_name="Produtos")
    if not df_precos.empty:
        df_precos.to_excel(writer, index=False, sheet_name="Precos")

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
