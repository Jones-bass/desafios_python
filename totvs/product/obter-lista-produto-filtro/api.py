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
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/product-codes/search"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("🚀 Consultando lista de códigos de produtos alterados...")

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
            "branchCode": 1,
        }
    },
    "order": "productCode"
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
debug_file = f"debug_product_codes.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === PROCESSA RESPOSTA ===
items = data.get("items", [])
if not items:
    print("⚠️ Nenhum produto retornado pela API.")
    sys.exit(0)

# === CONVERTE PARA DATAFRAME ===
df = pd.DataFrame(items)

# === EXPORTA PARA EXCEL ===
excel_file = f"product_codes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
df.to_excel(excel_file, index=False)

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
