import requests
import json
from datetime import datetime
import sys
import os
import base64

# === IMPORTA TOKEN DE AUTH ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.config import TOKEN

# === CONFIGURAÇÕES ===
ACCESS_KEY = "32251041791600000445550010000027241197481362"  # 👉 substitua pela chave de acesso da NF-e
URL = f"https://apitotvsmoda.bhan.com.br/api/totvsmoda/fiscal/v2/xml-contents/{ACCESS_KEY}"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print(f"🚀 Consultando XML da NF-e (chave: {ACCESS_KEY})...")

# === REQUISIÇÃO GET ===
try:
    response = requests.get(URL, headers=HEADERS, timeout=60)
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
debug_file = f"debug_invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(debug_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"💾 Debug salvo em: {debug_file}")

# === CAMPOS PRINCIPAIS ===
processing_type = data.get("processingType")
main_xml = data.get("mainInvoiceXml")
cancel_xml = data.get("cancelInvoiceXml")

print(f"📄 Status da NF-e: {processing_type}")

# === SALVA XMLS ===
if main_xml:
    xml_file = f"nfe_main_{ACCESS_KEY}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    with open(xml_file, "w", encoding="utf-8") as f:
        f.write(main_xml)
    print(f"✅ XML principal salvo em: {xml_file}")

if cancel_xml:
    xml_cancel_file = f"nfe_cancel_{ACCESS_KEY}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
    with open(xml_cancel_file, "w", encoding="utf-8") as f:
        f.write(cancel_xml)
    print(f"⚠️ XML de cancelamento salvo em: {xml_cancel_file}")

print("🏁 Consulta finalizada com sucesso.")
