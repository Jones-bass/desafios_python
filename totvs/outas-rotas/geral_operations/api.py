import requests
import pandas as pd
from datetime import datetime, timezone
import json
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/general/v2/operations"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PARÂMETROS OPCIONAIS ===
# Exemplo: buscar operações ativas e ordenadas por código
start_date = datetime(2025, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2025, 10, 8, 23, 59, 59, tzinfo=timezone.utc)

PAGE_SIZE = 100  # limite padrão seguro
page = 1
all_records = []

while True:
    params = {
        "Page": page,
        "PageSize": PAGE_SIZE,
        "Order": "operationCode",
        # filtros opcionais:
        # "IsInactive": False,
        # "OperationTypeList": ["S"],  # S = saída, E = entrada
        "StartChangeDate": start_date.isoformat(),
        "EndChangeDate": end_date.isoformat(),
        "Expand": "calculations,values,balances,classifications"
    }

    print(f"📄 Buscando página {page}...")

    resp = requests.get(URL, headers=headers, params=params)
    print("Status:", resp.status_code)

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
    except Exception as e:
        print("❌ Erro ao ler JSON:", e)
        break

    # Extrai os registros principais
    records = data.get("items", [])
    if not records or len(records) == 0:
        print("⚠️ Nenhum dado encontrado nesta página.")
        break

    all_records.extend(records)

    print(f"✅ Página {page}: {len(records)} registros")

    # Paginação
    if len(records) < PAGE_SIZE or not data.get("hasNext", False):
        break

    page += 1
    time.sleep(0.3)

# === CONSTRUÇÃO DO DATAFRAME ===
if not all_records:
    print("⚠️ Nenhum registro retornado da API.")
else:
    # Como a estrutura é aninhada, vamos normalizar os dados principais
    df_main = pd.json_normalize(all_records)

    # Converte colunas de datas
    for col in df_main.columns:
        if "date" in col.lower():
            df_main[col] = pd.to_datetime(df_main[col], errors="coerce")

    # Exporta o resultado
    df_main.to_excel("operacoes.xlsx", index=False)
    df_main.to_csv("operacoes.csv", index=False, encoding="utf-8-sig")

    print(f"✅ Total coletado: {len(df_main)} registros")
    print("📂 Arquivos gerados: operacoes.xlsx e operacoes.csv")
