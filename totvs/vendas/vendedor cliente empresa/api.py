import requests
import pandas as pd
import sys
import os
from datetime import datetime, timezone

# === IMPORTA TOKEN ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/seller/v2/search"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === FILTROS ===
branch_codes = [5]   # [] significa todas as filiais
person_code = None
seller_code = None
is_inactive = False

# === PAGINAÇÃO ===
page = 1
page_size = 500
all_sellers = []
all_customers = []

while True:
    payload = {
        "filter": {},
        "page": page,
        "pageSize": page_size
    }

    # Só adiciona filtros se existirem
    if branch_codes:
        payload["filter"]["branchCodeList"] = branch_codes
    if person_code is not None:
        payload["filter"]["personCode"] = person_code
    if seller_code is not None:
        payload["filter"]["sellerCode"] = seller_code
    payload["filter"]["isInactive"] = is_inactive

    print(f"👤 Consultando página {page} de vendedores…")
    resp = requests.post(URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    data = resp.json()
    items = data.get("items", [])

    if not items:
        print("⚠️ Nenhum vendedor encontrado nesta página.")
        break

    for item in items:
        seller_id = item.get("sellerCode")
        seller_name = item.get("sellerName")
        person_id = item.get("personCode")
        person_name = item.get("personName")

        # === Cada filial separadamente ===
        for branch in item.get("branchInformations", []):
            all_sellers.append({
                "CódigoVendedor": seller_id,
                "NomeVendedor": seller_name,
                "CódigoPessoa": person_id,
                "NomePessoa": person_name,
                "BranchCode": branch.get("branchCode"),
                "AuxiliaryCode": branch.get("auxiliaryCode"),
                "FilialAtiva": not branch.get("isInactive", False),
                "SellerTypeCode": branch.get("sellerTypeCode"),
                "SellerTypeDescription": branch.get("sellerTypeDescription")
            })

        # === Cada cliente separadamente ===
        for customer in item.get("customers", []):
            all_customers.append({
                "CódigoVendedor": seller_id,
                "NomeVendedor": seller_name,
                "CódigoPessoaCliente": customer.get("personCode"),
                "NomeCliente": customer.get("name"),
                "DocumentoCliente": customer.get("document")
            })

    # Controle de paginação pelo hasNext
    if not data.get("hasNext", False):
        break
    page += 1

# === EXPORTAÇÃO ===
df_sellers = pd.DataFrame(all_sellers)
df_customers = pd.DataFrame(all_customers)

if df_sellers.empty:
    print("⚠️ Nenhum vendedor encontrado.")
else:
    # Excel com duas planilhas
    excel_file = "vendedores_com_clientes.xlsx"
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        df_sellers.to_excel(writer, sheet_name="Vendedores", index=False)
        df_customers.to_excel(writer, sheet_name="Clientes", index=False)
    
    print(f"✅ Relatório gerado: {excel_file}")
    print(f"Total vendedores: {len(df_sellers)} | Total clientes: {len(df_customers)}")
