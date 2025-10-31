import requests
import pandas as pd
import json
from datetime import datetime
import sys
import os
import time

# === IMPORTA TOKEN DE AUTH ===
# Assume-se que esta parte funciona
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/fiscal/v2/invoices/search"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("🚀 Consultando notas fiscais autorizadas...")

# === PAYLOAD DINÂMICO ===
def make_payload(page: int) -> dict:
    return {
        "filter": {
            "branchCodeList": [5],
            "operationType": "Output",  # Saídas
            "operationCodeList": [5102, 5103, 5105, 5952, 701, 702, 7101, 6108, 111, 112, 151],
            "origin": "All",
            "eletronicInvoiceStatusList": ["Authorized"],  # Apenas NF-es autorizadas
            "startIssueDate": "2025-09-01T00:00:00Z",
            "endIssueDate": "2025-09-30T23:59:59Z",
        },
        # Adiciona a paginação necessária na API
        "pagination": {
            "pageNumber": page,
            "pageSize": 50 # Ajuste conforme necessário
        },
        "order": "invoiceCode",
        "expand": ""
    }

# === FUNÇÃO DE PAGINAÇÃO ===
def get_all_pages():
    all_items = []
    page = 1
    while True:
        print(f"🔎 Página {page}...")
        payload = make_payload(page)
        try:
            response = requests.post(URL, headers=HEADERS, json=payload, timeout=90)
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na conexão: {e}")
            break

        if response.status_code != 200:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            break

        data = response.json()
        items = data.get("items", [])
        
        # O modelo de paginação da sua API parece depender de 'hasNext' e/ou 'totalItems'
        # e a necessidade de enviar o 'pageNumber' no payload. 
        # O break atual para quando não há mais itens, o que funciona.
        if not items:
            print("⚠️ Nenhum item encontrado nesta página.")
            break

        all_items.extend(items)
        
        # A API de exemplo tem 'hasNext' e 'totalItems'. 
        # Use o 'hasNext' se a API for consistente.
        # if not data.get("hasNext", False):
        #     break
            
        page += 1
        time.sleep(0.3) # Pequena pausa para evitar sobrecarregar a API
        
        # Proteção extra para evitar loop infinito se 'hasNext' não for confiável
        if data.get("totalPages", 1) < page:
             break
             
    return all_items

# === EXECUTA A COLETA ===
items = get_all_pages()

if not items:
    print("⚠️ Nenhuma nota fiscal retornada.")
    sys.exit(0)

# === SALVA DEBUG COMPLETO ===
debug_file = f"debug_fiscal_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === TRATAMENTO DE DADOS COM MAIS CAMPOS ===
invoices, items_detalhes, impostos, pagamentos, transportadoras, observacoes, pessoas, items_produtos = [], [], [], [], [], [], [], []

for nf in items:
    try:
        eletronic = nf.get("eletronic", {}) or {}
        shipping = nf.get("shippingCompany", {}) or {}
        person = nf.get("person", {}) or {}

        # 1. NOTAS FISCAIS
        invoices.append({
            "branchCode": nf.get("branchCode"),
            "branchCnpj": nf.get("branchCnpj"), # NOVO
            "invoiceCode": nf.get("invoiceCode"),
            "serialCode": nf.get("serialCode"), # NOVO
            "invoiceDate": nf.get("invoiceDate"),
            "issueDate": nf.get("issueDate"),
            "releaseDate": nf.get("releaseDate"),
            "lastchangeDate": nf.get("lastchangeDate"), # NOVO
            "maxChangeFilterDate": nf.get("maxChangeFilterDate"),
            "personCode": nf.get("personCode"),
            "personName": nf.get("personName"),
            "invoiceStatus": nf.get("invoiceStatus"),
            "operationType": nf.get("operationType"),
            "operationCode": nf.get("operationCode"), # NOVO
            "documentType": nf.get("documentType"), # NOVO
            "paymentConditionName": nf.get("paymentConditionName"),
            "discountPercentage": nf.get("discountPercentage"),
            "quantity": nf.get("quantity"), # NOVO
            "productValue": nf.get("productValue"), # NOVO
            "shippingValue": nf.get("shippingValue"), # NOVO
            "insuranceValue": nf.get("insuranceValue"), # NOVO
            "ipiValue": nf.get("ipiValue"), # NOVO
            "baseIcmsValue": nf.get("baseIcmsValue"), # NOVO
            "icmsValue": nf.get("icmsValue"), # NOVO
            "icmsSubStValue": nf.get("icmsSubStValue"), # NOVO
            "totalValue": nf.get("totalValue"),
            # Campos Eletronic
            "accessKey": eletronic.get("accessKey"),
            "electronicInvoiceStatus": eletronic.get("electronicInvoiceStatus"),
        })
        
        # 2. PESSOAS (CLIENTE/FORNECEDOR)
        if person:
             pessoas.append({
                "invoiceCode": nf.get("invoiceCode"),
                "personCode": person.get("personCode"),
                "personName": person.get("personName"),
                "personType": person.get("personType"),
                "personCpfCnpj": person.get("personCpfCnpj"),
                "rgIe": person.get("rgIe"),
                "address": person.get("address"),
                "addressNumber": person.get("addressNumber"),
                "complement": person.get("complement"),
                "neighborhood": person.get("neighborhood"),
                "city": person.get("city"),
                "cityCode": person.get("cityCode"),
                "stateAbbreviation": person.get("stateAbbreviation"),
                "cep": person.get("cep"),
                "foneNumber": person.get("foneNumber")
            })

        # 3. ITENS DA NOTA
        for item in nf.get("items") or []:
            rateDifferential = item.get("rateDifferential", {}) or {} # NOVO
            
            items_detalhes.append({
                "invoiceCode": nf.get("invoiceCode"),
                "sequence": item.get("sequence"),
                "code": item.get("code"),
                "name": item.get("name"),
                "ncm": item.get("ncm"),
                "cest": item.get("cest"), # NOVO
                "cfop": item.get("cfop"),
                "measureUnit": item.get("measureUnit"),
                "quantity": item.get("quantity"),
                "grossValue": item.get("grossValue"),
                "discountValue": item.get("discountValue"),
                "netValue": item.get("netValue"),
                "unitNetValue": item.get("unitNetValue"),
                "unitGrossValue": item.get("unitGrossValue"), # NOVO
                "unitDiscountValue": item.get("unitDiscountValue"), # NOVO
                "additionalValue": item.get("additionalValue"), # NOVO
                "freightValue": item.get("freightValue"), # NOVO
                "insuranceValue": item.get("insuranceValue"), # NOVO
                "additionalItemInformation": item.get("additionalItemInformation"), # NOVO
                # Diferencial de Alíquota
                "calcBaseValue_difal": rateDifferential.get("calculationBaseValue"), # NOVO
                "internalRate_difal": rateDifferential.get("internalRate"), # NOVO
                "interstateRate_difal": rateDifferential.get("interstateRate"), # NOVO
                "fcpRate_difal": rateDifferential.get("fcpRate"), # NOVO
                "fcpValue_difal": rateDifferential.get("fcpValue"), # NOVO
            })
            
            # 3.1 PRODUTOS DETALHADOS (dentro de item)
            for prod in item.get("products") or []:
                 items_produtos.append({
                    "invoiceCode": nf.get("invoiceCode"),
                    "itemSequence": item.get("sequence"), # Chave para ligar ao item pai
                    "productCode": prod.get("productCode"),
                    "productName": prod.get("productName"),
                    "dealerCode": prod.get("dealerCode"),
                    "quantity": prod.get("quantity"),
                    "unitNetValue": prod.get("unitNetValue"),
                    "netValue": prod.get("netValue"),
                })
            
            # 3.2 IMPOSTOS
            for imp in item.get("taxes") or []:
                impostos.append({
                    "invoiceCode": nf.get("invoiceCode"),
                    "itemCode": item.get("code"),
                    "taxCode": imp.get("code"),
                    "taxName": imp.get("name"),
                    "cst": imp.get("cst"),
                    "taxPercentage": imp.get("taxPercentage"),
                    "calculationBasisPercentage": imp.get("calculationBasisPercentage"), # NOVO
                    "calculationBasisValue": imp.get("calculationBasisValue"),
                    "taxValue": imp.get("taxValue"),
                    "freeValue": imp.get("freeValue"), # NOVO
                    "otherValue": imp.get("otherValue"), # NOVO
                    "benefitCode": imp.get("benefitCode"), # NOVO
                })

        # 4. PAGAMENTOS
        for pg in nf.get("payments") or []:
            card_info = pg.get("cardInformation", {}) or {}
            
            pagamentos.append({
                "invoiceCode": nf.get("invoiceCode"),
                "documentNumber": pg.get("documentNumber"),
                "documentType": pg.get("documentType"),
                "documentTypeCode": pg.get("documentTypeCode"), # NOVO
                "installment": pg.get("installment"), # NOVO
                "paymentValue": pg.get("paymentValue"),
                "expirationDate": pg.get("expirationDate"),
                "bearerName": pg.get("bearerName"),
                "cardOperatorName": card_info.get("cardOperatorName"),
                "cardFlag": card_info.get("cardFlag"),
                "authorizationCode": card_info.get("authorizationCode"), # NOVO
                "nsu": card_info.get("nsu"), # NOVO
            })

        # 5. TRANSPORTADORA
        if shipping:
            transportadoras.append({
                "invoiceCode": nf.get("invoiceCode"),
                "shippingCompanyName": shipping.get("shippingCompanyName"),
                "shippingCompanyCode": shipping.get("shippingCompanyCode"), # NOVO
                "cpfCnpj": shipping.get("cpfCnpj"),
                "freitghtType": shipping.get("freitghtType"),
                "freightValue": shipping.get("freightValue"),
                "packageNumber": shipping.get("packageNumber"), # NOVO
                "grossWeight": shipping.get("grossWeight"), # NOVO
                "netWeight": shipping.get("netWeight"), # NOVO
                "species": shipping.get("species"), # NOVO
                "cityName": shipping.get("cityName"),
                "stateAbbreviation": shipping.get("stateAbbreviation"),
                "plaqueCode": shipping.get("plaqueCode"),
                "plaqueUf": shipping.get("plaqueUf")
            })

        # 6. OBSERVAÇÕES
        # Mantido como no original, cobrindo observationNF (lista) e observationNFE (direto)
        for obs in nf.get("observationNF") or []:
            observacoes.append({
                "invoiceCode": nf.get("invoiceCode"),
                "sequence": obs.get("sequence"),
                "observation": obs.get("observation")
            })
        if nf.get("observationNFE"):
            observacoes.append({
                "invoiceCode": nf.get("invoiceCode"),
                "sequence": None,
                "observation": nf.get("observationNFE")
            })

    except Exception as e:
        print(f"⚠️ Erro ao processar NF {nf.get('invoiceCode')}: {e}")

# === CONVERTE EM DATAFRAMES ===
df_nf = pd.DataFrame(invoices)
df_pessoas = pd.DataFrame(pessoas) # NOVO DATAFRAME
df_itens = pd.DataFrame(items_detalhes)
df_produtos = pd.DataFrame(items_produtos) # NOVO DATAFRAME
df_imp = pd.DataFrame(impostos)
df_pag = pd.DataFrame(pagamentos)
df_ship = pd.DataFrame(transportadoras)
df_obs = pd.DataFrame(observacoes)

# === EXPORTA PARA EXCEL ===
excel_file = f"fiscal_invoices_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
    df_nf.to_excel(writer, index=False, sheet_name="NotasFiscais")
    if not df_pessoas.empty: df_pessoas.to_excel(writer, index=False, sheet_name="Pessoas") # NOVO SHEET
    if not df_itens.empty: df_itens.to_excel(writer, index=False, sheet_name="Itens")
    if not df_produtos.empty: df_produtos.to_excel(writer, index=False, sheet_name="Itens_Produtos") # NOVO SHEET
    if not df_imp.empty: df_imp.to_excel(writer, index=False, sheet_name="Impostos")
    if not df_pag.empty: df_pag.to_excel(writer, index=False, sheet_name="Pagamentos")
    if not df_ship.empty: df_ship.to_excel(writer, index=False, sheet_name="Transportadoras")
    if not df_obs.empty: df_obs.to_excel(writer, index=False, sheet_name="Observacoes")

print(f"✅ Excel completo gerado: {excel_file}")
print(f"📊 Total de notas exportadas: {len(df_nf)}")