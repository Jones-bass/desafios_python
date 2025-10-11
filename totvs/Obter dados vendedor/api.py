import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJsYWdlYSIsImlkIjoieHVrWTk0KzJRKy84VU9paDdEVHJwd0s1ZDR4SFNZRG1sV0thSWVBekIrdVVmbWk0YVNXWERQZmpCQUsrc1NGQVZxMlEwZ29Jc28wZ20vZlBaMXo4ZjVkbDhDcG5nd2xwQm80clAwRzJWazQ2dWIvcGpkeVp6Zlc3ZEhoNTF1dzZRQXh6ZlpNeVdJbytkWEYzUmJsYzBRPT0iLCJqdGkiOiI4NmI0MWJiMC0zYmU4LTQ2NDQtYTI4Ni0wNDcwNmQ4MThlODkiLCJ2ZXJzaW9uIjoidjIiLCJ0eXBlIjoiZGVmYXVsdCIsInJvbGVzIjpbIkFETSIsIkFOTCIsIkNBUCIsIkNNQyIsIkNNUCIsIkVOUCIsIkZDQyIsIkZDUCIsIkZDUiIsIkZHUiIsIkZJUyIsIkdFRCIsIkdFTiIsIkdMQiIsIklNR1BSRCIsIklOVCIsIk1ORyIsIk1PUCIsIk1XQVBQIiwiUENQIiwiUEVEIiwiUEVTIiwiUFJEIiwiU0RQIiwiU0VMIiwiU1JWIiwiVFJBIiwiVk9VIl0sInNvdXJjZSI6ImFwaS90b3R2c21vZGEvYXV0aG9yaXphdGlvbi92Mi90b2tlbiIsImNsaWVudGlkIjoibGFnZWFhcGl2MiIsInN1YiI6IjMiLCJicmFuY2hlcyI6WyIxIiwiMiIsIjMiLCI0IiwiNSIsIjYiLCI3IiwiOCJdLCJleHAiOjE3NjAyMTg4NzMsImlzcyI6InRvdHZzLmNvbSJ9.UbBDJPiuArTvszAR32JEf7Zwmn2sH8pIkGd5mJwrSyc"
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/analytics/v2/seller-panel/sales-vs-returns/search"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Intervalo de datas

start_date = datetime(2025, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2025, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

payload = {
    "branchs": [5],
    "datemin": start_date.isoformat(),
    "datemax": end_date.isoformat(),
    "operations": [0],
    "sellers": [5001]  # código numérico interno do vendedor
}

# Requisição POST
resp = requests.post(URL, headers=headers, json=payload)
print("Status:", resp.status_code)

if resp.status_code != 200:
    print("❌ Erro na requisição:", resp.text)
    exit()

# Tenta decodificar JSON
try:
    data = resp.json()
except Exception as e:
    print("❌ Erro ao ler JSON:", e)
    exit()

# Mostra o JSON para inspeção
print(json.dumps(data, indent=2, ensure_ascii=False))

# Detecta automaticamente o campo que contém os registros
if isinstance(data, dict):
    # Procura a primeira lista dentro do dict
    records = None
    for k, v in data.items():
        if isinstance(v, list) and len(v) > 0:
            records = v
            print(f"📦 Dados encontrados dentro de '{k}'")
            break
    if records is None:
        print("⚠️ Nenhuma lista de dados encontrada no JSON.")
        exit()
elif isinstance(data, list):
    records = data
else:
    print("❌ Estrutura de JSON inesperada.")
    exit()

# Cria DataFrame de forma dinâmica
df = pd.DataFrame(records)

if df.empty:
    print("⚠️ Nenhum dado válido retornado da API.")
else:
    # Tenta detectar colunas de datas e valores
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif "value" in col.lower() or "total" in col.lower():
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Salva arquivos
    df.to_excel("totais_vendas_filiais.xlsx", index=False)
    df.to_csv("totais_vendas_filiais.csv", index=False, encoding="utf-8-sig")

    print(f"✅ Relatório gerado: {len(df)} registros")
