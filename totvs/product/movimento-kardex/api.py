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
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/kardex-movement"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PARÂMETROS PADRÃO ===
BRANCH_CODE = 5
PRODUCT_CODES = [5118, 5120, 5145]   # 🔁 Você pode listar vários produtos aqui
BALANCE_TYPE = 1
START_DATE = "2025-05-01T00:00:00Z"
END_DATE = "2025-09-30T23:59:59Z"

# === FUNÇÃO PRINCIPAL ===
def get_kardex(branch_code: int, product_code: int, start_date: str, end_date: str, balance_type: int):
    """Consulta o Kardex de um produto específico."""
    params = {
        "BranchCode": branch_code,
        "ProductCode": product_code,
        "StartDate": start_date,
        "EndDate": end_date,
        "BalanceType": balance_type
    }

    try:
        response = requests.get(URL, headers=HEADERS, params=params, timeout=90)
        if response.status_code != 200:
            print(f"❌ Erro HTTP {response.status_code} para produto {product_code}: {response.text}")
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão para produto {product_code}: {e}")
        return None

# === EXECUÇÃO ===
todos_movimentos = []

for code in PRODUCT_CODES:
    print(f"🚀 Consultando Kardex do produto {code} na empresa {BRANCH_CODE}...")
    data = get_kardex(BRANCH_CODE, code, START_DATE, END_DATE, BALANCE_TYPE)

    if not data or not safe_list(data.get("movements")):
        print(f"⚠️ Nenhum movimento encontrado para o produto {code}.")
        continue

    # Salva debug individual
    debug_file = f"debug_kardex_{code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Processa movimentos
    for m in safe_list(data.get("movements")):
        todos_movimentos.append({
            "branchCode": data.get("branchCode"),
            "balanceType": data.get("balanceType"),
            "productCode": data.get("productCode"),
            "productDescription": data.get("productDescription"),
            "groupSequenceCode": data.get("groupSequenceCode"),
            "groupCode": data.get("groupCode"),
            "groupDescription": data.get("groupDescription"),
            "colorCode": data.get("colorCode"),
            "colorDescription": data.get("colorDescription"),
            "sizeDescription": data.get("sizeDescription"),
            "previousBalance": data.get("previousBalance"),
            "movementDate": m.get("movementDate"),
            "historyCode": m.get("historyCode"),
            "historyDescription": m.get("historyDescription"),
            "operationCode": m.get("operationCode"),
            "operationDescription": m.get("operationDescription"),
            "documentType": m.get("documentType"),
            "documentNumber": m.get("documentNumber"),
            "unitValue": m.get("unitValue"),
            "inQuantity": m.get("inQuantity"),
            "outQuantity": m.get("outQuantity"),
            "balance": m.get("balance")
        })

# === CONVERSÃO E EXPORTAÇÃO ===
if not todos_movimentos:
    print("⚠️ Nenhum movimento retornado para os produtos consultados.")
    sys.exit(0)

df_kardex = pd.DataFrame(todos_movimentos)

# Converte data e ordena
df_kardex["movementDate"] = pd.to_datetime(df_kardex["movementDate"], errors="coerce")
df_kardex = df_kardex.sort_values(by=["productCode", "movementDate"])

# === EXPORTA PARA EXCEL ===
excel_file = f"kardex_movimentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_kardex.to_excel(writer, index=False, sheet_name="Kardex")

print(f"✅ Relatório Kardex gerado com sucesso: {excel_file}")
print(f"📊 Total de movimentos exportados: {len(df_kardex)}")
print(f"📦 Produtos processados: {len(PRODUCT_CODES)}")
