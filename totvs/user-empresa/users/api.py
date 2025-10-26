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
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/management/v2/users"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PARÂMETROS INICIAIS ===
PAGE_SIZE = 100
page = 1
all_records = []

# === FILTROS OPCIONAIS ===
params_base = {
    "PageSize": PAGE_SIZE,
    "Order": "-login,maxChangeFilterDate",
    # "UserCode": 3,
    # "StartChangeDate": "2025-10-01T00:00:00Z",
    # "EndChangeDate": "2025-10-26T23:59:59Z",
    # "LoginNameList": ["admin", "usuario1"],
    # "TypeList": ["Administrator", "Representative"],
    # "StatusList": ["Released"],
}

print("🚀 Iniciando coleta de Usuários TOTVS (ADMFM026)...")
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
    debug_file = f"debug_users_page_{page}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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

    # Reordena colunas principais se existirem
    colunas_principais = [
        "code", "name", "login", "personCode",
        "type", "status", "maxChangeFilterDate"
    ]
    df = df[[c for c in colunas_principais if c in df.columns]]

    excel_file = f"usuarios_totvs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    try:
        df.to_excel(excel_file, index=False)
        print(f"✅ Total coletado: {len(df)} registros")
        print(f"📂 Arquivo salvo: {excel_file}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")

print("✅ Execução finalizada.")
