import requests
import pandas as pd
from datetime import datetime, timezone
import json

# === CONFIGURAÇÕES ===
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJsYWdlYSIsImlkIjoieHVrWTk0KzJRKy84VU9paDdEVHJwd0s1ZDR4SFNZRG1sV0thSWVBekIrdVVmbWk0YVNXWERQZmpCQUsrc1NGQVZxMlEwZ29Jc28wZ20vZlBaMXo4ZjVkbDhDcG5nd2xwQm80clAwRzJWazQ2dWIvcGpkeVp6Zlc3ZEhoNTF1dzZRQXh6ZlpNeVdJbytkWEYzUmJsYzBRPT0iLCJqdGkiOiIyMGU5YmVmNy0zYjNiLTQ2NDQtYmRiMi0wYjhkNTUyNTZmMzkiLCJ2ZXJzaW9uIjoidjIiLCJ0eXBlIjoiZGVmYXVsdCIsInJvbGVzIjpbIkFETSIsIkFOTCIsIkNBUCIsIkNNQyIsIkNNUCIsIkVOUCIsIkZDQyIsIkZDUCIsIkZDUiIsIkZHUiIsIkZJUyIsIkdFRCIsIkdFTiIsIkdMQiIsIklNR1BSRCIsIklOVCIsIk1ORyIsIk1PUCIsIk1XQVBQIiwiUENQIiwiUEVEIiwiUEVTIiwiUFJEIiwiU0RQIiwiU0VMIiwiU1JWIiwiVFJBIiwiVk9VIl0sInNvdXJjZSI6ImFwaS90b3R2c21vZGEvYXV0aG9yaXphdGlvbi92Mi90b2tlbiIsImNsaWVudGlkIjoibGFnZWFhcGl2MiIsInN1YiI6IjMiLCJicmFuY2hlcyI6WyIxIiwiMiIsIjMiLCI0IiwiNSIsIjYiLCI3IiwiOCJdLCJleHAiOjE3NjAyMzU1MTAsImlzcyI6InRvdHZzLmNvbSJ9.VPspzSLx0q6Knmjen98HU1_AfSc33kX70WynKz9_aBE"
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/api/totvsmoda/sales-order/v2/invoices"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Intervalo de datas

payload = {
    "BranchCode": 2, 
    "OrderCode": 640,
}

# === REQUISIÇÃO POST ===
resp = requests.post(URL, headers=headers, json=payload)
print("Status:", resp.status_code)

if resp.status_code != 200:
    print("❌ Erro na requisição:", resp.text)
    exit()

# === TRATA JSON ===
try:
    data = resp.json()
except Exception as e:
    print("❌ Erro ao ler JSON:", e)
    exit()

# Extrai invoices
all_invoices = []
for invoice in data.get("invoices", []):
    flat_invoice = invoice.copy()
    # Extrai dados de "electronic" para o mesmo nível
    if "electronic" in flat_invoice:
        for k, v in flat_invoice["electronic"].items():
            flat_invoice[f"electronic_{k}"] = v
        del flat_invoice["electronic"]
    all_invoices.append(flat_invoice)

if not all_invoices:
    print("⚠️ Nenhuma nota fiscal encontrada no período selecionado.")
    exit()

# Cria DataFrame
df = pd.DataFrame(all_invoices)

# Converte datas e valores
for col in df.columns:
    if "date" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce")
    elif "value" in col.lower() or "quantity" in col.lower() or "weight" in col.lower():
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Salva em Excel e CSV
df.to_excel("totvs_invoices.xlsx", index=False)
df.to_csv("totvs_invoices.csv", index=False, encoding="utf-8-sig")

print(f"✅ Relatório gerado: {len(df)} notas fiscais")
