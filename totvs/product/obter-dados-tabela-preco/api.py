import requests
import pandas as pd
import json
from datetime import datetime
import sys
import os

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN


# === FUNÇÕES AUXILIARES ===
def fetch_page(url, headers, params):
    """Executa uma requisição GET e retorna o JSON."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        sys.exit(1)
    except ValueError:
        print("❌ Erro ao decodificar JSON da resposta.")
        sys.exit(1)


def get_all_pages(url, headers, base_params):
    """Busca todas as páginas da API, usando paginação automática."""
    all_items = []
    page = 1

    while True:
        params = {**base_params, "Page": page}
        print(f"📄 Buscando página {page}...")

        data = fetch_page(url, headers, params)
        items = data.get("items", [])
        if not items:
            break

        all_items.extend(items)

        if not data.get("hasNext"):
            break
        page += 1

    print(f"✅ Total de registros obtidos: {len(all_items)}")
    return all_items


def save_debug(data, prefix):
    """Salva JSON bruto para análise posterior."""
    filename = f"debug_{prefix}_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Debug salvo em: {filename}")


# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/price-tables-headers"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

PARAMS = {
    "StartChangeDate": "2023-09-01T00:00:00Z",
    "EndChangeDate": "2025-10-28T23:59:59Z",
}


# === EXECUÇÃO ===
print("🚀 Consultando cabeçalhos de tabelas de preço...")

items = get_all_pages(URL, HEADERS, PARAMS)

if not items:
    print("⚠️ Nenhum registro encontrado.")
    sys.exit(0)

save_debug(items, "price_tables_headers")

# === CONVERTE E TRATA DADOS ===
df_main = pd.DataFrame(items)

# === FLAT: salesOrderClassification, personClassification, paymentConditions ===
def flatten_nested(df, field, prefix, key="code"):
    """Desmembra listas aninhadas em DataFrames separados."""
    rows = []
    for item in df.to_dict(orient="records"):
        base_code = item.get("code")
        for sub in item.get(field, []) or []:
            sub[f"priceTableCode"] = base_code
            rows.append(sub)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


df_sales_class = flatten_nested(df_main, "salesOrderClassification", "SalesOrder")
df_person_class = flatten_nested(df_main, "personClassification", "PersonClass")
df_payment_cond = flatten_nested(df_main, "paymentConditions", "PaymentCond")
df_avg_period = flatten_nested(df_main, "averagePeriod", "AvgPeriod")
df_avg_qty = flatten_nested(df_main, "averagePeriodQuantity", "AvgPeriodQty")

# === RENOMEIA COLUNAS PRINCIPAIS ===
df_main.rename(columns={
    "code": "Codigo",
    "description": "Descricao",
    "codeName": "NomeCodigo",
    "type": "Tipo",
    "maxChangeFilterDate": "DataUltimaAlteracao",
    "startDate": "DataInicio",
    "endDate": "DataFim",
    "variationPercentage": "VariacaoPercentual",
    "variationValue": "VariacaoValor"
}, inplace=True)

# === EXPORTA PARA EXCEL ===
excel_file = f"price_tables_headers_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_main.to_excel(writer, index=False, sheet_name="Headers")
    if not df_sales_class.empty:
        df_sales_class.to_excel(writer, index=False, sheet_name="SalesOrderClass")
    if not df_person_class.empty:
        df_person_class.to_excel(writer, index=False, sheet_name="PersonClass")
    if not df_payment_cond.empty:
        df_payment_cond.to_excel(writer, index=False, sheet_name="PaymentConditions")
    if not df_avg_period.empty:
        df_avg_period.to_excel(writer, index=False, sheet_name="AveragePeriod")
    if not df_avg_qty.empty:
        df_avg_qty.to_excel(writer, index=False, sheet_name="AveragePeriodQuantity")

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
