import requests
from datetime import datetime, timezone
import pandas as pd
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sales-order/v2/orders/search"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Intervalo de datas
start_date = datetime(2025, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2025, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

# Paginação
page = 1
page_size = 200
all_items = []

STATUS_MAP = {
    "InProgress": "Em andamento",
    "Attended": "Atendido",
    "Canceled": "Cancelado",
    "Blocked": "Bloqueado",
}

while True:
    payload = {
        "filter": {
            "change": {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat()
            },
            "startOrderDate": start_date.isoformat(),
            "endOrderDate": end_date.isoformat(),
            "branchCodeList": [3]  # Ajuste conforme sua filial,
        },
        "page": page,
        "pageSize": page_size
    }

    resp = requests.post(URL, headers=headers, json=payload)
    print(f"📄 Página {page} | Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    data = resp.json()

    # === DEBUG: mostra resumo do retorno
    print("\n🪣 Retorno da API (primeiros 1000 caracteres):")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
    print("------------------------------------------------------\n")

    # Extrai os pedidos do campo "items"
    orders = data.get("items", [])
    if not orders:
        print("⚠️ Nenhum pedido encontrado nesta página.")
        break


    for order in orders:
        # Traduz o status da lista retornada pela API
        status_pt = ", ".join([
            STATUS_MAP.get(status, status)
            for status in (order.get("orderStatus") or [])
        ])

        all_items.append({
            "Filial": order.get("branchCode"),
            "Pedido": order.get("orderCode"),
            "OrderID": order.get("orderId"),
            "CustomerOrderCode": order.get("customerOrderCode"),
            "DataInsercao": order.get("insertDate"),
            "DataPedido": order.get("orderDate"),
            "DataChegada": order.get("arrivalDate"),
            "DataUltimaAlteracao": order.get("maxChangeFilterDate"),
            "Cliente": order.get("customerName"),
            "CPF_CNPJ_Cliente": order.get("customerCpfCnpj"),
            "CodigoCliente": order.get("customerCode"),
            "Representante": order.get("representativeName"),
            "CodigoRepresentante": order.get("representativeCode"),
            "Operacao": order.get("operationName"),
            "CodigoOperacao": order.get("operationCode"),
            "CondicaoPagamento": order.get("paymentConditionName"),
            "CodigoCondicaoPagamento": order.get("paymentConditionCode"),
            "Quantidade": order.get("quantity"),
            "ValorBruto": order.get("grossValue"),
            "ValorDesconto": order.get("discountValue"),
            "ValorLiquido": order.get("netValue"),
            "ValorFrete": order.get("freightValue"),
            "TipoFrete": order.get("freightType"),
            "CodigoTransportadora": order.get("shippingCompanyCode"),
            "NomeTransportadora": order.get("shippingCompanyName"),
            "StatusPedido": status_pt,  # 👈 traduzido para PT-BR
            "TotalPedido": order.get("totalAmountOrder"),
            "Experiencia": order.get("experienceType"),
            "TemTransacaoPDV": order.get("hasPdvTransaction"),
            "TemFinanceiroProcessado": order.get("hasFinancialProcessed"),
            "CodigoIntegracao": order.get("integrationCode"),
            "CodigoGuia": order.get("guideCode"),
            "CPF_CNPJGuia": order.get("guideCpfCnpj"),
            "VendedorCodigo": order.get("sellerCode"),
            "VendedorCPF_CNPJ": order.get("sellerCpfCnpj"),
        })



    # Verifica se há próxima página
    if not data.get("hasNext", False):
        break
    page += 1

# === EXPORTAÇÃO PARA EXCEL ===
df = pd.DataFrame(all_items)

if df.empty:
    print("⚠️ Nenhum registro encontrado no período.")
else:
    for col in df.columns:
        if any(x in col.lower() for x in ["date", "pedido"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif any(x in col.lower() for x in ["valor", "peso", "quantidade", "qtde"]):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    excel_file = "relatorio_totvs_items.xlsx"
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Relatorio")

    print(f"✅ Relatório gerado com sucesso: {excel_file} ({len(df)} registros)")
    print("DEBUG status list:", order.get("orderStatus"))

