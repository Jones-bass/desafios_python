import requests
from datetime import datetime, timezone
import pandas as pd
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJsYWdlYSIsImlkIjoieHVrWTk0KzJRKy84VU9paDdEVHJwd0s1ZDR4SFNZRG1sV0thSWVBekIrdVVmbWk0YVNXWERQZmpCQUsrc1NGQVZxMlEwZ29Jc28wZ20vZlBaMXo4ZjVkbDhDcG5nd2xwQm80clAwRzJWazQ2dWIvcGpkeVp6Zlc3ZEhoNTF1dzZRQXh6ZlpNeVdJbytkWEYzUmJsYzBRPT0iLCJqdGkiOiI1MmZjYTlkNS1mNTY5LTRhZDAtYmI3YS04OWNhZTE3MDBhZDciLCJ2ZXJzaW9uIjoidjIiLCJ0eXBlIjoiZGVmYXVsdCIsInJvbGVzIjpbIkFETSIsIkFOTCIsIkNBUCIsIkNNQyIsIkNNUCIsIkVOUCIsIkZDQyIsIkZDUCIsIkZDUiIsIkZHUiIsIkZJUyIsIkdFRCIsIkdFTiIsIkdMQiIsIklNR1BSRCIsIklOVCIsIk1ORyIsIk1PUCIsIk1XQVBQIiwiUENQIiwiUEVEIiwiUEVTIiwiUFJEIiwiU0RQIiwiU0VMIiwiU1JWIiwiVFJBIiwiVk9VIl0sInNvdXJjZSI6ImFwaS90b3R2c21vZGEvYXV0aG9yaXphdGlvbi92Mi90b2tlbiIsImNsaWVudGlkIjoibGFnZWFhcGl2MiIsInN1YiI6IjEwMDAyIiwiYnJhbmNoZXMiOlsiMSIsIjIiLCIzIiwiNCIsIjUiLCI2IiwiNyIsIjgiXSwiZXhwIjoxNzU5OTA1NDI5LCJpc3MiOiJ0b3R2cy5jb20ifQ.QoFPzO3Cs7zBelzs2Vx0xote9H1TuGXPFsHKeOABP1E"
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sales-order/v2/invoices"

params = {
    "BranchCode": "2",
    "OrderCode": 637
}

headers = {"Authorization": f"Bearer {TOKEN}"}

resp = requests.get(URL, params=params, headers=headers)
print("Status:", resp.status_code)

data = resp.json()

# Pega a lista de notas fiscais
invoices = data.get("invoices", [])

items = []
for nf in invoices:
    elec = nf.get("electronic", {})
    items.append({
        "Filial": nf.get("transactionBranchCode"),
        "Pedido": data.get("orderCode"),
        "NotaFiscal": nf.get("code"),
        "DataEmissao": nf.get("issueDate"),
        "Status": nf.get("status"),
        "Transportadora": nf.get("shippingCompanyName"),
        "QtdeItens": nf.get("quantity"),
        "ValorTotal": nf.get("totalValue"),
        "ChaveAcesso": nf.get("accessKey"),
        "SituacaoEletronica": elec.get("electronicInvoiceStatus"),
        "Recibo": elec.get("receipt"),
        "DataAutorizacao": elec.get("receivementDate")
    })

df = pd.DataFrame(items)
df.to_csv("relatorio_notas.csv", index=False, encoding="utf-8-sig")

print(f"✅ Relatório gerado com sucesso: relatorio_notas.csv ({len(df)} registros)")
