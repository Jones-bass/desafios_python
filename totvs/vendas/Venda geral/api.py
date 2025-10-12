import requests
import pandas as pd
from datetime import datetime, timezone
import json

# === CONFIGURAÇÕES ===
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/totals-seller/search"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Intervalo de datas
start_date = datetime(2025, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2025, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

payload = {
    "branchs": [3],
    "datemin": start_date.isoformat(),
    "datemax": end_date.isoformat()
}

# === REQUISIÇÃO ===
resp = requests.post(URL, headers=headers, json=payload)
print("Status:", resp.status_code)

if resp.status_code != 200:
    print("❌ Erro na requisição:", resp.text)
    exit()

data = resp.json()
print(json.dumps(data, indent=2, ensure_ascii=False))

# === TRATAMENTO DOS DADOS ===
# 1. Dados atuais
df_atual = pd.DataFrame(data.get("dataRow", []))
df_atual["periodo"] = "Atual"

# 2. Dados do ano anterior
df_anterior = pd.DataFrame(data.get("dataRowLastYear", []))
df_anterior["periodo"] = "Ano Anterior"

# 3. Totais agregados
totais = {
    "Periodo": ["Atual", "Ano Anterior"],
    "invoice_qty": [data["total"]["invoice_qty"], data["totalLastYear"]["invoice_qty"]],
    "invoice_value": [data["total"]["invoice_value"], data["totalLastYear"]["invoice_value"]],
    "itens_qty": [data["total"]["itens_qty"], data["totalLastYear"]["itens_qty"]],
    "tm": [data["total"]["tm"], data["totalLastYear"]["tm"]],
    "pa": [data["total"]["pa"], data["totalLastYear"]["pa"]],
    "pmpv": [data["total"]["pmpv"], data["totalLastYear"]["pmpv"]]
}
df_totais = pd.DataFrame(totais)

# === SALVA TUDO NO EXCEL ===
with pd.ExcelWriter("totvs_vendas_completo.xlsx") as writer:
    df_atual.to_excel(writer, sheet_name="Vendas_Atual", index=False)
    df_anterior.to_excel(writer, sheet_name="Vendas_Ano_Anterior", index=False)
    df_totais.to_excel(writer, sheet_name="Totais", index=False)

print("✅ Arquivo Excel gerado com sucesso: totvs_vendas_completo.xlsx")
print(f"🧾 Linhas atuais: {len(df_atual)}, Ano anterior: {len(df_anterior)}")
