import requests
import pandas as pd
from datetime import datetime, timezone
import json
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/general/v2/payment-conditions"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 🔹 Tente primeiro sem filtro de data
PAGE_SIZE = 100
page = 1
all_records = []

while True:
    params = {
        "Page": page,
        "PageSize": PAGE_SIZE
    }

    print(f"📄 Buscando página {page}...")

    resp = requests.get(URL, headers=headers, params=params)
    print("Status:", resp.status_code)

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    data = resp.json()

    # Extrai lista de condições de pagamento
    records = data.get("items", [])
    if not records or len(records) == 0:
        print("⚠️ Nenhum dado encontrado nesta página.")
        break

    all_records.extend(records)

    print(f"✅ Página {page}: {len(records)} registros")

    # Paginação: se count menor que PAGE_SIZE, acabou
    if len(records) < PAGE_SIZE or not data.get("hasNext", False):
        break

    page += 1
    time.sleep(0.2)

# === Criação do DataFrame ===
if not all_records:
    print("⚠️ Nenhum registro retornado da API.")
else:
    df = pd.DataFrame(all_records)
    df.to_excel("condicoes_pagamento.xlsx", index=False)
    print(f"✅ Total coletado: {len(df)} registros")
    print("📂 Arquivo salvo: condicoes_pagamento.xlsx")
