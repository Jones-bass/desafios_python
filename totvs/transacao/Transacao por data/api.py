import requests
import pandas as pd
from datetime import datetime, timezone

# === CONFIGURAÇÕES ===
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/general/v2/transactions"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PARÂMETROS ===
params = {
    "BranchCode": "2",                   # código da filial
    "TransactionCode": "39086",          # código da transação
    "TransactionDate": "2025-10-07T00:00:00Z",
    "Expand": "itemPromotionalEngines,originDestination"
}

print("🔍 Buscando dados da transação...")
response = requests.get(URL, headers=headers, params=params)
print("Status:", response.status_code)

if response.status_code != 200:
    print("❌ Erro:", response.text)
    exit()

data = response.json()

# === 1️⃣ DADOS PRINCIPAIS ===
main_fields = {
    "branchCode": data.get("branchCode"),
    "transactionCode": data.get("transactionCode"),
    "transactionDate": data.get("transactionDate"),
    "customerCode": data.get("customerCode"),
    "operationCode": data.get("operationCode"),
    "sellerCode": data.get("sellerCode"),
    "guideCode": data.get("guideCode"),
    "paymentConditionCode": data.get("paymentConditionCode"),
    "priceTableCode": data.get("priceTableCode"),
    "status": data.get("status"),
    "lastChangeDate": data.get("lastchangeDate")
}
df_main = pd.DataFrame([main_fields])

# === 2️⃣ ITENS ===
df_items = pd.json_normalize(data.get("items", [])) if data.get("items") else pd.DataFrame()


# === 💾 SALVAR EM UM ÚNICO EXCEL ===
with pd.ExcelWriter("transacao_completa.xlsx", engine="xlsxwriter") as writer:
    df_main.to_excel(writer, index=False, sheet_name="Dados Principais")
    df_items.to_excel(writer, index=False, sheet_name="Itens")

print("✅ Tudo salvo em: transacao_completa.xlsx")
