import os
import sys
import json
import requests
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN  # Certifique-se de que auth/config.py existe

# === CONFIGURAÇÕES GERAIS ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/fiscal/v2/invoices/search"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}", 
    "Content-Type": "application/json"
}

# === FUNÇÕES UTILITÁRIAS ===
def log(msg: str):
    print(f"[{msg}")

def make_payload() -> Dict[str, Any]:
    """Cria o payload de busca completo (sem paginação)."""
    return {
        "filter": {
            "branchCodeList": [5],
            "operationType": "Output",
            "operationCodeList": [5102, 5103, 5105, 5952, 701, 702, 7101, 6108, 111, 112, 151],
            "origin": "All",
            "eletronicInvoiceStatusList": ["Authorized"],
            "startIssueDate": "2025-09-01T00:00:00Z",
            "endIssueDate": "2025-09-30T23:59:59Z",
        },
        "order": "invoiceCode",
        "expand": "eletronic, shippingCompany, person, payments, items"
    }

def fetch_all_invoices() -> List[Dict[str, Any]]:
    """Busca todas as notas fiscais em uma única requisição."""
    payload = make_payload()
    try:
        log("🔎 Enviando requisição única para buscar todas as notas fiscais...")
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        log(f"✅ {len(items)} notas fiscais retornadas.")
        return items
    except requests.RequestException as e:
        log(f"❌ Erro ao consultar notas fiscais: {e}")
        return []

# === PROCESSAMENTO DE DADOS ===
def process_invoice(nf: Dict[str, Any]) -> Dict[str, Any]:
    """Processa dados principais de uma nota fiscal, incluindo quantidade total de products."""
    eletronic = nf.get("eletronic", {}) or {}
    shipping = nf.get("shippingCompany", {}) or {}
    person = nf.get("person", {}) or {}

    # Pagamento principal (pega o primeiro, se existir)
    pg_first = (nf.get("payments") or [{}])[0]
    card_info = pg_first.get("cardInformation", {}) or {}

    # Pega os itens
    items = nf.get("items", []) or []

    # Quantidade total de produtos na nota
    total_produtos = 0
    for item in items:
        for prod in item.get("products") or []:
            total_produtos += prod.get("quantity", 0)

    first_item = items[0] if items else {}

    return {
        # Dados principais
        "Empresa": nf.get("branchCode"),
        "Emissao": nf.get("issueDate"),
        "Transacao": nf.get("transactionCode"),
        "Operacao": nf.get("operationCode"),
        "CFOP": first_item.get("cfop"),
        "Codigo": nf.get("personCode"),
        "Cliente": nf.get("personName"),

        # Pessoa
        "Cidade": person.get("city"),
        "UF": person.get("stateAbbreviation"),
        "CEP": person.get("cep"),
        "Telefone": person.get("foneNumber"),

        # Transportadora
        "Transportadora": shipping.get("shippingCompanyName"),

        # Pagamento
        "Total_Produtos": total_produtos,
        "Desconto": first_item.get("discountValue"),
        "Valor_liquido": first_item.get("netValue"),
        "Valor_Bruto": first_item.get("unitGrossValue"),
        "Valor_Total": nf.get("totalValue"),
        "Liquidacao": pg_first.get("documentType"),
        "Banco": card_info.get("cardOperatorName"),
        "Cartao": card_info.get("cardFlag"),
        "NSU": card_info.get("nsu"),
        "Autorizacao": card_info.get("authorizationCode"),

        # Eletronic
        "Serie": nf.get("serialCode"),
        "Chave": eletronic.get("accessKey"),
        "Status_NFe": eletronic.get("electronicInvoiceStatus"),
    }

def process_related_data(nf: Dict[str, Any], df_dicts: Dict[str, list]):
    person = nf.get("person", {}) or {}
    shipping = nf.get("shippingCompany", {}) or {}

    # Pessoa
    if person:
        df_dicts["pessoas"].append({
            "invoiceCode": nf.get("invoiceCode"),
            "personName": person.get("personName"),
            "cpfCnpj": person.get("personCpfCnpj"),
            "city": person.get("city"),
            "state": person.get("stateAbbreviation"),
        })

    # Transportadora
    if shipping:
        df_dicts["transportadoras"].append({
            "invoiceCode": nf.get("invoiceCode"),
            "shippingCompanyName": shipping.get("shippingCompanyName"),
            "cpfCnpj": shipping.get("cpfCnpj"),
            "city": shipping.get("cityName"),
            "state": shipping.get("stateAbbreviation"),
            "plaqueCode": shipping.get("plaqueCode"),
            "freightValue": shipping.get("freightValue"),
        })

    # Pagamentos
    for pg in nf.get("payments") or []:
        card_info = pg.get("cardInformation", {}) or {}
        df_dicts["pagamentos"].append({
            "invoiceCode": nf.get("invoiceCode"),
            "paymentValue": pg.get("paymentValue"),
            "installment": pg.get("installment"),
            "documentType": pg.get("documentType"),
            "cardFlag": card_info.get("cardFlag"),
            "nsu": card_info.get("nsu"),
            "authorizationCode": card_info.get("authorizationCode")
        })

    # Itens e Produtos
    for item in nf.get("items") or []:
        df_dicts["itens"].append({
            "invoiceCode": nf.get("invoiceCode"),
            "cfop": item.get("cfop"),
            "productCode": item.get("code"),
            "description": item.get("name"),
            "quantity": item.get("quantity"),
            "discountValue": item.get("discountValue"),
            "netValue": item.get("netValue"),
            "unitNetValue": item.get("unitNetValue"),
            "unitGrossValue": item.get("unitGrossValue"),
            "unitDiscountValue": item.get("unitDiscountValue"),
        })

        for prod in item.get("products") or []:
            df_dicts["products"].append({
                "invoiceCode": nf.get("invoiceCode"),
                "productCode": prod.get("productCode"),
                "productName": prod.get("productName"),
                "dealerCode": prod.get("dealerCode"),
                "quantity": prod.get("quantity"),
            })

# === EXECUÇÃO ===
if __name__ == "__main__":
    log("🚀 Iniciando consulta de notas fiscais...")
    items = fetch_all_invoices()

    debug_file = f"debug_fiscal_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    log(f"💾 Arquivo debug salvo: {debug_file}")

    # Inicializa dicionários
    df_dicts = {"pessoas": [], "pagamentos": [], "transportadoras": [], "itens": [], "products": []}
    invoices = []

    for nf in items:
        try:
            invoices.append(process_invoice(nf))
            process_related_data(nf, df_dicts)
        except Exception as e:
            log(f"⚠️ Erro ao processar NF {nf.get('invoiceCode')}: {e}")

    # === CONVERTE EM DATAFRAMES ===
    dfs = {
        "NotasFiscais": pd.DataFrame(invoices),
        "Pessoas": pd.DataFrame(df_dicts["pessoas"]),
        "Pagamentos": pd.DataFrame(df_dicts["pagamentos"]),
        "Transportadoras": pd.DataFrame(df_dicts["transportadoras"]),
        "Itens": pd.DataFrame(df_dicts["itens"]),
        "Products": pd.DataFrame(df_dicts["products"]),
    }

    # === EXPORTA PARA EXCEL ===
    excel_file = f"fiscal_invoices_full_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        for name, df in dfs.items():
            if not df.empty:
                df.to_excel(writer, index=False, sheet_name=name)

    log(f"✅ Excel completo gerado: {excel_file}")
    log(f"📊 Total de notas exportadas: {len(invoices)}")
