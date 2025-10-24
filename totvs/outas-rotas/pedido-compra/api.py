import requests
import pandas as pd
import json
import sys
import os
from datetime import datetime

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES DA API ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/purchase-order/v2/search"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PARÂMETROS DE CONSULTA ===
payload = {
  "filter": {
    "change": {
      "startDate": "2025-09-01T00:00:00Z",
      "endDate": "2025-09-30T23:59:59Z"
    },
    "branchCodeList": [1]
  },
  "page": 1,
  "pageSize": 100
}

print("🚀 Iniciando consulta de Pedidos de Compra TOTVS...")
print(f"📄 Payload: {json.dumps(payload, indent=2)}")

# === REQUISIÇÃO ===
response = requests.post(URL, headers=headers, json=payload)
print(f"📡 Status HTTP: {response.status_code}")

if response.status_code != 200:
    print("❌ Erro ao consultar pedidos de compra:")
    print(response.text)
    sys.exit(1)

try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    print("❌ Erro ao decodificar JSON da resposta.")
    sys.exit(1)

# === SALVA JSON PARA DEBUG ===
debug_file = f"debug_purchase_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Resposta completa salva em: {debug_file}")

# === INSPEÇÃO DE CHAVES ===
print("🔍 Estrutura principal da resposta:")
for key, value in data.items():
    tipo = type(value).__name__
    tamanho = len(value) if isinstance(value, (list, dict)) else "-"
    print(f"   - {key} ({tipo}) tamanho: {tamanho}")
print("-" * 60)

# === 1️⃣ DADOS PRINCIPAIS (Resumo da consulta) ===
main_fields = {
    "Count": data.get("count"),
    "TotalPages": data.get("totalPages"),
    "HasNext": data.get("hasNext"),
    "TotalItems": data.get("totalItems")
}
df_main = pd.DataFrame([main_fields])
print("✅ Dados principais extraídos com sucesso.")

# === 2️⃣ LISTA DE PEDIDOS ===
if data.get("items"):
    df_orders = pd.json_normalize(
        data["items"],
        sep="_",
        max_level=1
    )
    print(f"📦 Total de pedidos encontrados: {len(df_orders)}")

    # === 3️⃣ ITENS DE PEDIDO (expand) ===
    items_expanded = []
    for order in data["items"]:
        branch = order.get("branchCode")
        order_code = order.get("orderCode")
        if "items" in order and order["items"]:
            for item in order["items"]:
                item["branchCode"] = branch
                item["orderCode"] = order_code
                items_expanded.append(item)

    df_items = pd.DataFrame(items_expanded) if items_expanded else pd.DataFrame()
    print(f"🧾 Itens de pedidos encontrados: {len(df_items)}")

else:
    df_orders = pd.DataFrame()
    df_items = pd.DataFrame()
    print("⚠️ Nenhum pedido encontrado nesse período.")

# === 4️⃣ EXPORTAÇÃO PARA EXCEL ===
excel_file = f"pedidos_compra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
try:
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        df_main.to_excel(writer, index=False, sheet_name="Resumo")
        if not df_orders.empty:
            df_orders.to_excel(writer, index=False, sheet_name="Pedidos")
        if not df_items.empty:
            df_items.to_excel(writer, index=False, sheet_name="Itens")

    print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
except Exception as e:
    print(f"❌ Erro ao exportar para Excel: {e}")
