import requests
import pandas as pd
from datetime import datetime
import json
import time
import sys
import os

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES DA API ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/management/v2/global-parameter"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === FILTROS DE CONSULTA ===
PAGE_SIZE = 500
page = 1
all_records = []

# ⚙️ Aqui você define os parâmetros corporativos que deseja consultar
params_base = {
    "ParameterCodeList": [
        "CD_CLASS_PESSOA_ETIQ",
        "CD_CLAS_PRD_CAIXA_FECHADA",
    ],
    "PageSize": PAGE_SIZE
}

print("🚀 Iniciando coleta de Parâmetros Corporativos TOTVS (ADMFM013)...")
print(f"📦 Endpoint: {URL}")
print(f"📄 Página inicial: {page} | Tamanho por página: {PAGE_SIZE}")
print("-" * 70)

# === LOOP DE PAGINAÇÃO ===
while True:
    params = params_base.copy()
    params["Page"] = page

    print(f"\n📄 Buscando página {page}...")

    try:
        resp = requests.get(URL, headers=headers, params=params, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão na página {page}: {e}")
        break

    print(f"📡 Status HTTP: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Erro na requisição:")
        print(resp.text)
        break

    try:
        data = resp.json()
    except requests.exceptions.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta.")
        break

    # === SALVA DEBUG DE CADA PÁGINA ===
    debug_file = f"debug_corporate_parameters_page_{page}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Debug salvo: {debug_file}")

    # === EXTRAI OS ITENS ===
    records = data.get("items", [])
    if not records:
        print("⚠️ Nenhum dado encontrado nesta página. Encerrando.")
        break

    all_records.extend(records)
    print(f"✅ Página {page}: {len(records)} registros | Total acumulado: {len(all_records)}")

    # === CONTROLE DE PAGINAÇÃO ===
    if not data.get("hasNext", False):
        print("🏁 Última página alcançada.")
        break

    page += 1
    time.sleep(0.3)

print("-" * 70)

# === EXPORTAÇÃO FINAL ===
if not all_records:
    print("⚠️ Nenhum registro retornado da API.")
else:
    df = pd.DataFrame(all_records)

    # Reorganiza as colunas principais se existirem
    colunas_principais = ["parameterCode", "globalValue", "value"]
    df = df[[c for c in colunas_principais if c in df.columns]]

    excel_file = f"parametros_corporativos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    try:
        df.to_excel(excel_file, index=False)
        print(f"✅ Total coletado: {len(df)} registros")
        print(f"📂 Arquivo salvo: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")

print("✅ Execução finalizada com sucesso.")
