import requests
import pandas as pd
from datetime import datetime, timezone

# === CONFIGURAÇÕES ===
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJsYWdlYSIsImlkIjoieHVrWTk0KzJRKy84VU9paDdEVHJwd0s1ZDR4SFNZRG1sV0thSWVBekIrdVVmbWk0YVNXWERQZmpCQUsrc1NGQVZxMlEwZ29Jc28wZ20vZlBaMXo4ZjVkbDhDcG5nd2xwQm80clAwRzJWazQ2dWIvcGpkeVp6Zlc3ZEhoNTF1dzZRQXh6ZlpNeVdJbytkWEYzUmJsYzBRPT0iLCJqdGkiOiIwM2JlNDFmNi1mNjNlLTQ5YzQtOGE5NS00ZjE2MDc2YTQ3YzAiLCJ2ZXJzaW9uIjoidjIiLCJ0eXBlIjoiZGVmYXVsdCIsInJvbGVzIjpbIkFETSIsIkFOTCIsIkNBUCIsIkNNQyIsIkNNUCIsIkVOUCIsIkZDQyIsIkZDUCIsIkZDUiIsIkZHUiIsIkZJUyIsIkdFRCIsIkdFTiIsIkdMQiIsIklNR1BSRCIsIklOVCIsIk1ORyIsIk1PUCIsIk1XQVBQIiwiUENQIiwiUEVEIiwiUEVTIiwiUFJEIiwiU0RQIiwiU0VMIiwiU1JWIiwiVFJBIiwiVk9VIl0sInNvdXJjZSI6ImFwaS90b3R2c21vZGEvYXV0aG9yaXphdGlvbi92Mi90b2tlbiIsImNsaWVudGlkIjoibGFnZWFhcGl2MiIsInN1YiI6IjEwMDAyIiwiYnJhbmNoZXMiOlsiMSIsIjIiLCIzIiwiNCIsIjUiLCI2IiwiNyIsIjgiXSwiZXhwIjoxNzU5OTg2ODU5LCJpc3MiOiJ0b3R2cy5jb20ifQ.ahk8UqWL6hlfe4CLwSTVd3l3SURuLnGWQTgsUPKhee8"
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
