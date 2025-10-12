import requests
import pandas as pd
from datetime import datetime, timezone
import time

# === CONFIGURAÇÕES ===
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJsYWdlYSIsImlkIjoieHVrWTk0KzJRKy84VU9paDdEVHJwd0s1ZDR4SFNZRG1sV0thSWVBekIrdVVmbWk0YVNXWERQZmpCQUsrc1NGQVZxMlEwZ29Jc28wZ20vZlBaMXo4ZjVkbDhDcG5nd2xwQm80clAwRzJWazQ2dWIvcGpkeVp6Zlc3ZEhoNTF1dzZRQXh6ZlpNeVdJbytkWEYzUmJsYzBRPT0iLCJqdGkiOiIyMGU5YmVmNy0zYjNiLTQ2NDQtYmRiMi0wYjhkNTUyNTZmMzkiLCJ2ZXJzaW9uIjoidjIiLCJ0eXBlIjoiZGVmYXVsdCIsInJvbGVzIjpbIkFETSIsIkFOTCIsIkNBUCIsIkNNQyIsIkNNUCIsIkVOUCIsIkZDQyIsIkZDUCIsIkZDUiIsIkZHUiIsIkZJUyIsIkdFRCIsIkdFTiIsIkdMQiIsIklNR1BSRCIsIklOVCIsIk1ORyIsIk1PUCIsIk1XQVBQIiwiUENQIiwiUEVEIiwiUEVTIiwiUFJEIiwiU0RQIiwiU0VMIiwiU1JWIiwiVFJBIiwiVk9VIl0sInNvdXJjZSI6ImFwaS90b3R2c21vZGEvYXV0aG9yaXphdGlvbi92Mi90b2tlbiIsImNsaWVudGlkIjoibGFnZWFhcGl2MiIsInN1YiI6IjMiLCJicmFuY2hlcyI6WyIxIiwiMiIsIjMiLCI0IiwiNSIsIjYiLCI3IiwiOCJdLCJleHAiOjE3NjAyMzU1MTAsImlzcyI6InRvdHZzLmNvbSJ9.VPspzSLx0q6Knmjen98HU1_AfSc33kX70WynKz9_aBE"  # substitua pelo seu token
BRANCH_CODE = "2"         # código da filial
START_DATE = "2025-10-01T00:00:00Z"  # data inicial do período
END_DATE = "2025-10-08T23:59:59Z"    # data final do período
PAGE_SIZE = 50             # quantidade por página

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/general/v2/transactions"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === LISTAS PARA ARMAZENAR DADOS ===
all_main = []
all_items = []
all_promos = []
all_class = []
all_origin = []
all_dest = []

page = 1

while True:
    print(f"📄 Buscando página {page} de transações...")
    
    params = {
        "BranchCode": BRANCH_CODE,
        "StartChangeDate": START_DATE,
        "EndChangeDate": END_DATE,
        "Page": page,
        "PageSize": PAGE_SIZE,
        "Expand": "itemPromotionalEngines,originDestination"
    }

    resp = requests.get(URL, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    data = resp.json()
    transactions = data.get("items", [])

    if not transactions:
        print("⚠️ Nenhuma transação encontrada nesta página.")
        break

    for tx in transactions:
        # === 1️⃣ Dados principais ===
        main_fields = {
            "branchCode": tx.get("branchCode"),
            "transactionCode": tx.get("transactionCode"),
            "transactionDate": tx.get("transactionDate"),
            "customerCode": tx.get("customerCode"),
            "operationCode": tx.get("operationCode"),
            "sellerCode": tx.get("sellerCode"),
            "guideCode": tx.get("guideCode"),
            "paymentConditionCode": tx.get("paymentConditionCode"),
            "priceTableCode": tx.get("priceTableCode"),
            "status": tx.get("status"),
            "lastChangeDate": tx.get("lastchangeDate")
        }
        all_main.append(main_fields)

        # === 2️⃣ Itens ===
        for item in tx.get("items", []):
            item_row = item.copy()
            item_row["transactionCode"] = tx.get("transactionCode")
            all_items.append(item_row)

            # === 3️⃣ Promoções por item ===
            for promo in item.get("promotionalEngines", []):
                promo_row = {
                    "transactionCode": tx.get("transactionCode"),
                    "productCode": item.get("productCode"),
                    "engineSequence": promo.get("engineSequence"),
                    "engineDescription": promo.get("engineDescription"),
                    "mechanicsSequence": promo.get("mechanicsSequence"),
                    "mechanicsDescription": promo.get("mechanicsDescription"),
                    "previousValue": promo.get("previousValue"),
                    "currentValue": promo.get("currentValue")
                }
                all_promos.append(promo_row)

        # === 4️⃣ Classificações ===
        for cls in tx.get("classifications", []):
            cls_row = cls.copy()
            cls_row["transactionCode"] = tx.get("transactionCode")
            all_class.append(cls_row)

        # === 5️⃣ Origem / Destino ===
        origin = tx.get("originDestination", {})
        if origin:
            origin_row = origin.copy()
            origin_row["transactionCode"] = tx.get("transactionCode")
            origin_row.pop("destination", None)  # remove lista de destino
            all_origin.append(origin_row)

            for dest in origin.get("destination", []):
                dest_row = dest.copy()
                dest_row["transactionCode"] = tx.get("transactionCode")
                all_dest.append(dest_row)

    # Controle de paginação
    if not data.get("hasNext", False):
        break

    page += 1
    time.sleep(0.2)  # evita rate limit

# === CRIAR DATAFRAMES ===
df_main = pd.DataFrame(all_main)
df_items = pd.json_normalize(all_items) if all_items else pd.DataFrame()
df_promos = pd.DataFrame(all_promos)
df_class = pd.DataFrame(all_class)
df_origin = pd.DataFrame(all_origin)
df_dest = pd.DataFrame(all_dest)

# === SALVAR EM UM ÚNICO EXCEL ===
with pd.ExcelWriter("transacoes_periodo.xlsx", engine="xlsxwriter") as writer:
    df_main.to_excel(writer, index=False, sheet_name="Dados Principais")
    df_items.to_excel(writer, index=False, sheet_name="Itens")
    df_promos.to_excel(writer, index=False, sheet_name="Promocoes")
    df_class.to_excel(writer, index=False, sheet_name="Classificacoes")
    df_origin.to_excel(writer, index=False, sheet_name="Origem")
    df_dest.to_excel(writer, index=False, sheet_name="Destinos")

print(f"✅ Total de transações coletadas: {len(df_main)}")
print("📂 Dados salvos em: transacoes_periodo.xlsx")
