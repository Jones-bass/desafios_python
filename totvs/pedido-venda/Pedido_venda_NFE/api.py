import requests
from datetime import datetime, timezone
import pandas as pd

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sales-order/v2/invoices"

# Filial e pedido
params = {
    "BranchCode": 2,    # Código da filial
    "OrderCode": 637    # Número do pedido
}

headers = {"Authorization": f"Bearer {TOKEN}"}

# === REQUISIÇÃO ===
resp = requests.get(URL, params=params, headers=headers)
print("Status:", resp.status_code)

if resp.status_code != 200:
    print("❌ Erro na requisição:", resp.text)
    exit()

data = resp.json()

# Lista de notas fiscais
invoices = data.get("invoices", [])

if not invoices:
    print("⚠️ Nenhuma nota fiscal encontrada.")
    exit()

# Extrai dados detalhados
items = []
for nf in invoices:
    elec = nf.get("electronic", {})
    items.append({
        "Filial": nf.get("transactionBranchCode"),
        "Pedido": data.get("orderCode"),
        "NotaFiscal": nf.get("code"),
        "Série": nf.get("serial"),
        "DataEmissao": nf.get("issueDate"),
        "StatusNota": nf.get("status"),
        "Transportadora": nf.get("shippingCompanyName"),
        "Pacote": nf.get("packageNumber"),
        "PesoBruto": nf.get("grossWeight"),
        "PesoLiquido": nf.get("netWeight"),
        "QtdeItens": nf.get("quantity"),
        "ValorProduto": nf.get("productValue"),
        "ValorAdicional": nf.get("additionalValue"),
        "ValorFrete": nf.get("shippingValue"),
        "ValorSeguro": nf.get("InsuranceValue"),
        "ValorIPI": nf.get("ipiValue"),
        "ValorTotal": nf.get("totalValue"),
        "DataTransacao": nf.get("transactionDate"),
        "CodigoTransacao": nf.get("transactionCode"),
        # Campos eletrônicos
        "ChaveAcesso": elec.get("accessKey"),
        "SituacaoEletronica": elec.get("electronicInvoiceStatus"),
        "Recibo": elec.get("receipt"),
        "DataAutorizacao": elec.get("receivementDate")
    })

# Cria DataFrame
df = pd.DataFrame(items)

# Converte datas e valores
for col in df.columns:
    if "date" in col.lower() or "emissao" in col.lower() or "autorizacao" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce")
    elif "valor" in col.lower() or "peso" in col.lower() or "qtde" in col.lower():
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Salva em Excel (.xlsx) com pandas
excel_file = "relatorio_notas.xlsx"
with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Notas")

print(f"✅ Relatório gerado com sucesso: {excel_file} ({len(df)} registros)")
