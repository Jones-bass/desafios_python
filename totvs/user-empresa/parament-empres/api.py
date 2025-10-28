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
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/management/v2/branch-parameter"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === CONFIGURAÇÃO DE CONSULTA ===
page = 1
PAGE_SIZE = 100
all_records = []

# 🔹 Parâmetros de exemplo — personalize conforme necessário
params_base = {
    "BranchCodeList": [1],  # Lista de empresas
    "ParameterCodeList": ["IN_HAB_LANCAM_DEV.CX_FIN", "VL_BASE_ENDERECO_NFCE"],  # Parâmetros a consultar
    "PageSize": PAGE_SIZE
}

print("🚀 Iniciando coleta de Parâmetros por Empresa TOTVS (ADMFM014)...")
print(f"📦 Endpoint: {URL}")
print(f"🏢 Empresas: {params_base['BranchCodeList']}")
print(f"⚙️ Parâmetros: {params_base['ParameterCodeList']}")
print("-" * 80)

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

    # === DEBUG DE CADA PÁGINA ===
    debug_file = f"debug_company_parameters_page_{page}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Debug salvo: {debug_file}")

    # === PROCESSA OS DADOS ===
    records = data.get("items", [])
    if not records:
        print("⚠️ Nenhum dado encontrado nesta página. Encerrando.")
        break

    all_records.extend(records)
    print(f"✅ Página {page}: {len(records)} registros | Total acumulado: {len(all_records)}")

    # === PAGINAÇÃO ===
    if not data.get("hasNext", False):
        print("🏁 Última página alcançada.")
        break

    page += 1
    time.sleep(0.3)

print("-" * 80)

# === EXPORTAÇÃO FINAL ===
if not all_records:
    print("⚠️ Nenhum registro retornado da API.")
else:
    # Cria um DataFrame principal (parâmetros)
    df_main = pd.DataFrame(all_records)

    # Cria DataFrame expandido com valores por filial
    expanded_records = []
    for rec in all_records:
        parameter = rec.get("parameterCode")
        global_val = rec.get("globalValue")
        values = rec.get("values", [])
        for v in values:
            v["parameterCode"] = parameter
            v["globalValue"] = global_val
            expanded_records.append(v)

    df_expanded = pd.DataFrame(expanded_records) if expanded_records else pd.DataFrame()

    excel_file = f"parametros_por_empresa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    try:
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            df_main.to_excel(writer, index=False, sheet_name="Resumo")
            if not df_expanded.empty:
                df_expanded.to_excel(writer, index=False, sheet_name="Valores por Empresa")

        print(f"✅ Total de parâmetros: {len(df_main)}")
        print(f"✅ Total de valores por empresa: {len(df_expanded)}")
        print(f"📂 Arquivo salvo: {excel_file}")

    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")

print("✅ Execução finalizada com sucesso.")
