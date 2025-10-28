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
def safe_list(value):
    """Garante que o retorno seja sempre uma lista."""
    return value if isinstance(value, list) else []

def export_to_excel(filename, dataframes):
    """Exporta múltiplos DataFrames para abas no mesmo Excel."""
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        for sheet, df in dataframes.items():
            if not df.empty:
                df.to_excel(writer, index=False, sheet_name=sheet)

# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/product/v2/products/search"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

payload = {
    "filter": {
        "change": {
            "startDate": "2025-09-01T00:00:00Z",
            "endDate": "2025-09-30T23:59:59Z",
            "inBranchInfo": True,
            "branchInfoCodeList": [1],
        },
        "branchInfo": {"branchCode": 1, "isActive": True},
    },
    "option": {"branchInfoCode": 1},
    "page": 1,
    "pageSize": 100,
    "order": "productCode"
}

print("🚀 Consultando produtos...")

# === REQUISIÇÃO ===
try:
    r = requests.post(URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    print(f"❌ Erro na requisição: {e}")
    sys.exit(1)

# === DEBUG ===
debug_file = f"debug_products_{datetime.now():%Y%m%d_%H%M%S}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

items = data.get("items", [])
if not items:
    print("⚠️ Nenhum produto retornado pela API.")
    sys.exit(0)

# === LISTAS ===
tabelas = {
    "Produtos": [],
    "Cores": [],
    "BarCodes": [],
    "Classificacoes": [],
    "CamposAdicionais": [],
    "Fornecedores": [],
    "Fabricantes": [],
    "Categorias": [],
    "RefSeq": [],
    "WebData": [],
    "Detalhes": [],
    "Bloqueios": [],
    "Conservacao": []
}

# === PROCESSAMENTO ===
for item in items:
    pc = item.get("productCode")
    tabelas["Produtos"].append({
        "productCode": pc,
        "productSku": item.get("productSku"),
        "productName": item.get("productName"),
        "referenceCode": item.get("referenceCode"),
        "referenceName": item.get("referenceName"),
        "referenceId": item.get("referenceId"),
        "gridCode": item.get("gridCode"),
        "colorCode": item.get("colorCode"),
        "colorName": item.get("colorName"),
        "size": item.get("size"),
        "ncm": item.get("ncm"),
        "ipi": item.get("ipi"),
        "cst": item.get("cst"),
        "cest": item.get("cest"),
        "measuredUnit": item.get("measuredUnit"),
        "minimumStockAmount": item.get("minimumStockAmount"),
        "maximumStockAmount": item.get("maximumStockAmount"),
        "idealStockAmount": item.get("idealStockAmount"),
        "salesStartDate": item.get("salesStartDate"),
        "salesEndDate": item.get("salesEndDate"),
        "isActive": item.get("isActive"),
        "isBlocked": item.get("isBlocked"),
        "isFinishedProduct": item.get("isFinishedProduct"),
        "isRawMaterial": item.get("isRawMaterial"),
        "isBulkMaterial": item.get("isBulkMaterial"),
        "isOwnProduction": item.get("isOwnProduction"),
        "maxChangeFilterDate": item.get("maxChangeFilterDate"),
    })

    sublistas = {
        "Cores": "additionalColorInformation",
        "BarCodes": "barCodes",
        "Classificacoes": "classifications",
        "CamposAdicionais": "additionalFields",
        "Fornecedores": "suppliers",
        "Fabricantes": "manufacturers",
        "Categorias": "referenceCategories",
        "RefSeq": "referenceCodeSequences",
        "WebData": "webData",
        "Detalhes": "details",
        "Bloqueios": "branchesProductBlocked",
    }

    # preenche todas as sublistas simples
    for nome, chave in sublistas.items():
        for i in safe_list(item.get(chave)):
            tabelas[nome].append({"productCode": pc, **i})

    # conservação tem subtabela
    for cons in safe_list(item.get("conservationInstructions")):
        base = {"productCode": pc, **{k: cons.get(k) for k in ("code", "description", "default", "grouperCode")}}
        for c in safe_list(cons.get("items")):
            tabelas["Conservacao"].append({**base, **c})

# === CONVERTE E EXPORTA ===
dfs = {k: pd.DataFrame(v) for k, v in tabelas.items()}
excel_file = f"products_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
export_to_excel(excel_file, dfs)

print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
