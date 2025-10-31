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
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/category"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PARÂMETROS ===
params = {
    "startChangeDate": "2023-10-01T00:00:00Z",
    "endChangeDate": "2025-10-28T23:59:59Z",     
    "order": "-code,maxChangeFilterDate"
}

print("🚀 Consultando categorias de produtos...")

# === REQUISIÇÃO GET ===
try:
    response = requests.get(URL, headers=headers, params=params, timeout=60)
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
debug_file = f"debug_category_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === PROCESSA DADOS ===
items = data.get("items", [])
if not items:
    print("⚠️ Nenhuma categoria retornada pela API.")
    sys.exit(0)

categorias = []
for item in items:
    categorias.append({
        "code": item.get("code"),
        "name": item.get("name"),
        "parentCategoryCode": item.get("parentCategoryCode"),
        "categoryType": item.get("categoryType"),
        "maxChangeFilterDate": item.get("maxChangeFilterDate")
    })

# === CONVERTE PARA DATAFRAME ===
df_categorias = pd.DataFrame(categorias)

# === EXPORTA PARA EXCEL ===
excel_file = f"product_categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_categorias.to_excel(writer, index=False, sheet_name="Categorias")

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
