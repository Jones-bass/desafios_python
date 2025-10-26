import requests
import pandas as pd
from datetime import datetime
import json
import sys
import os

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES DA API ===
URL = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/person/v2/person-statistics"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# === PARÂMETROS DE CONSULTA ===
params = {
    "CustomerCode": 575,                 # Código do cliente (opcional se usar CPF/CNPJ)
    # "CustomerCpfCnpj": "12345678000199", # Alternativa: CPF ou CNPJ do cliente
    "BranchCode": [2]                      # Lista de filiais (empresas)
}

print("🚀 Iniciando consulta de Estatísticas de Cliente (Person Statistics)...")
print(f"📦 Parâmetros enviados:\n{json.dumps(params, indent=2)}")

# === REQUISIÇÃO GET ===
try:
    response = requests.get(URL, headers=headers, params=params, timeout=60)
except requests.exceptions.RequestException as e:
    print(f"❌ Erro na conexão: {e}")
    sys.exit(1)

print(f"📡 Status HTTP: {response.status_code}")

if response.status_code != 200:
    print("❌ Erro na resposta da API:")
    print(response.text)
    sys.exit(1)

# === TRATAMENTO DO JSON ===
try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    print("❌ Erro ao decodificar JSON da resposta.")
    sys.exit(1)

# === SALVA DEBUG ===
debug_file = f"debug_person_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === ESTRUTURAÇÃO DOS DADOS ===
if isinstance(data, dict) and data:
    df_stats = pd.DataFrame([data])  # Converte o dicionário em DataFrame
    print(f"✅ Estatísticas do cliente carregadas com sucesso.")
else:
    df_stats = pd.DataFrame()
    print("⚠️ Nenhum dado retornado pela API.")

# === RENOMEAR COLUNAS (opcional) ===
if not df_stats.empty:
    rename_map = {
        "averageDelay": "Atraso Medio (dias)",
        "maximumDelay": "Maior Atraso (dias)",
        "purchaseQuantity": "Qtde Compras",
        "purchasePiecesQuantity": "Qtde Peças",
        "totalPurchaseValue": "Valor Total Compras",
        "averagePurchaseValue": "Valor Medio Compras",
        "biggestPurchaseDate": "Data Maior Compra",
        "biggestPurchaseValue": "Valor Maior Compra",
        "firstPurchaseDate": "Primeira Compra",
        "lastPurchaseDate": "Ultima Compra",
        "highestDebt": "Maior Divida",
        "affiliateLimitAmount": "Limite do Afiliado",
        "lastDebtNoticeDate": "Data Ultimo Aviso de Divida"
    }
    df_stats.rename(columns=rename_map, inplace=True)
    print("📝 Colunas renomeadas para nomes amigáveis.")

# === EXPORTAÇÃO PARA EXCEL ===
excel_file = f"person_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
try:
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        if not df_stats.empty:
            df_stats.to_excel(writer, index=False, sheet_name="PersonStatistics")
        else:
            pd.DataFrame([{"Aviso": "Nenhum dado retornado da API"}]).to_excel(
                writer, index=False, sheet_name="PersonStatistics"
            )

    print(f"✅ Relatório Excel gerado com sucesso: {excel_file}")
except Exception as e:
    print(f"❌ Erro ao exportar para Excel: {e}")

print("🏁 Execução finalizada com sucesso.")
