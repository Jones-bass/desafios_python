import requests
import pandas as pd
from datetime import datetime, timezone
import json
import sys
import os

# === IMPORTA TOKEN ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES DA API ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/analytics/v2/fiscal-movement/search"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PAGINAÇÃO ===
page = 1
page_size = 500
all_movements = []
all_summaries = []

print("🚀 Iniciando consulta de Movimentos Fiscais (Analytics + DEBUG)...")

while True:
    payload = {
        "filter": {
            "branchCodeList": 2,
            "startMovementDate": "2025-09-01T00:00:00Z",
            "endMovementDate": "2025-09-30T00:00:00Z",
        },
        "page": page,
        "pageSize": page_size,
    }

    print(f"\n📄 Consultando página {page} de movimentos fiscais…")
    resp = requests.post(URL, headers=headers, json=payload)
    print(f"📡 Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:", resp.text)
        break

    try:
        data = resp.json()
    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    # === DEBUG: SALVAR RESPOSTA ===
    debug_file = f"debug_response_fiscal_movement_page_{page}.json"
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Resposta salva em: {debug_file}")

    # === DEBUG: EXIBIR ESTRUTURA ===
    print("🔍 Estrutura da resposta:")
    for key, value in data.items():
        tipo = type(value).__name__
        tam = len(value) if isinstance(value, (list, dict)) else "1"
        print(f"   - {key}: {tipo} ({tam})")

    # === DEBUG: AMOSTRA DO CONTEÚDO ===
    print("🧩 Amostra do conteúdo (primeiros 1200 caracteres):")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1200])
    print("-" * 60)

    # === PROCESSAMENTO DE DADOS ===
    items = data.get("items", [])
    if not items:
        print("⚠️ Nenhum movimento encontrado nesta página.")
        break

    for item in items:
        all_movements.append({
            "Filial": item.get("branchCode"),
            "Produto": item.get("productCode"),
            "Pessoa": item.get("personCode"),
            "Representante": item.get("representativeCode"),
            "DataMovimento": item.get("movementDate"),
            "Operacao": item.get("operationCode"),
            "ModeloOperacao": item.get("operationModel"),
            "Estoque": item.get("stockCode"),
            "Comprador": item.get("buyerCode"),
            "Vendedor": item.get("sellerCode"),
            "ValorBruto": item.get("grossValue"),
            "ValorDesconto": item.get("discountValue"),
            "ValorLiquido": item.get("netValue"),
            "Quantidade": item.get("quantity"),
        })

    # === RESUMO POR PÁGINA ===
    summary = {
        "Page": page,
        "Count": data.get("count"),
        "TotalItems": data.get("totalItems"),
        "TotalPages": data.get("totalPages"),
    }
    all_summaries.append(summary)

    # === PAGINAÇÃO ===
    total_pages = data.get("totalPages")
    has_next = data.get("hasNext", False)

    if total_pages and page >= total_pages:
        print("✅ Todas as páginas foram processadas.")
        break
    elif not has_next or len(items) < page_size:
        print("✅ Última página (sem próxima).")
        break

    page += 1

# === EXPORTAÇÃO ===
df_movements = pd.DataFrame(all_movements)
df_summary = pd.DataFrame(all_summaries).drop_duplicates(subset=["Page"])

print("-" * 40)

if df_movements.empty:
    print("⚠️ Nenhum dado encontrado para exportar.")
else:
    excel_file = f"movimentos_fiscais.xlsx"

    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_movements.to_excel(writer, sheet_name="MovimentosFiscais", index=False)
            if not df_summary.empty:
                df_summary.to_excel(writer, sheet_name="ResumoPaginas", index=False)
        print(f"✅ Relatório gerado: {excel_file}")
        print(f"Total de registros de movimentos fiscais: {len(df_movements)}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")
