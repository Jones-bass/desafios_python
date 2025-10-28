import requests
import pandas as pd
import sys
import os
from datetime import datetime

# === IMPORTA TOKEN ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES DA API ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/analytics/v2/branch-sale"
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

page = 1
page_size = 100  # entre 1 e 1000
all_sales = []

print("🚀 Iniciando consulta de Vendas via Query Parameters...")

while True:
    params = {
        "BranchCnpj": "45877608000137",
        "start_date": "2025-09-01T00:00:00Z",
        "end_date": "2025-09-30T23:59:59Z",
        "Page": page,
        "PageSize": page_size
    }

    print(f"\n📄 Consultando página {page} de vendas…")
    resp = requests.get(URL, headers=headers, params=params)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    data = resp.json()

    items = data.get("items", [])
    if not items:
        print("⚠️ Nenhum registro encontrado nesta página.")
        break

    for item in items:
        all_sales.append({
            "CNPJ Filial": item.get("branchCnpj"),
            "Sequência NF": item.get("invoiceSequence"),
            "Valor Venda": item.get("SaleValue"),
            "Data Venda": item.get("saleDate"),
            "Hora Venda": item.get("SaleHour"),
            "Status NF": item.get("invoiceStatus"),
            "Tipo Operação": item.get("operationType"),
            "Código Operação": item.get("operationCode"),
        })

    total_pages = data.get("totalPages", 1)
    print(f"📖 Página {page}/{total_pages}")

    if page >= total_pages:
        print("✅ Todas as páginas processadas.")
        break

    page += 1

# === EXPORTAÇÃO ===
if all_sales:
    df_sales = pd.DataFrame(all_sales)
    date_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    excel_file = f"vendas_query_{date_now}.xlsx"

    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_sales.to_excel(writer, sheet_name="Vendas", index=False)
        print(f"✅ Relatório gerado: {excel_file}")
        print(f"Total de registros exportados: {len(df_sales)}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")
else:
    print("⚠️ Nenhum dado para exportar.")
