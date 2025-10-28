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
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/measurement-unit"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("🚀 Consultando unidades de medida...")

# === REQUEST PARAMS ===
params = {
    "StartChangeDate": "2024-01-01T00:00:00Z",
    "EndChangeDate": "2025-09-30T23:59:59Z",
    "Page": 1,
    "PageSize": 1000,
    "Expand": "additionalVariations"
}

# === REQUISIÇÃO GET ===
try:
    response = requests.get(URL, headers=headers, params=params, timeout=90)
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
debug_file = f"debug_measurement_unit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === PROCESSA RESPOSTA ===
items = data.get("items", [])
if not items:
    print("⚠️ Nenhuma unidade de medida retornada pela API.")
    sys.exit(0)

# === TABELAS ===
unidades = []
variacoes = []

for item in items:
    unidades.append({
        "code": item.get("code"),
        "description": item.get("description"),
        "maxChangeFilterDate": item.get("maxChangeFilterDate")
    })

    for var in safe_list(item.get("additionalVariations")):
        variacoes.append({
            "measurementUnitCode": item.get("code"),
            "variationCode": var.get("code"),
            "variationDescription": var.get("description"),
            "isTribXml": var.get("isTribXml")
        })

# === CONVERTE PARA DATAFRAMES ===
df_unidades = pd.DataFrame(unidades)
df_variacoes = pd.DataFrame(variacoes)

# === EXPORTA PARA EXCEL ===
excel_file = f"measurement_units_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_unidades.to_excel(writer, index=False, sheet_name="Unidades")
    if not df_variacoes.empty:
        df_variacoes.to_excel(writer, index=False, sheet_name="Variacoes")

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
