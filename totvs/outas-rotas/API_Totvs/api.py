import requests
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from auth.config import TOKEN

url = "https://apitotvsmoda.bhan.com.br/api/totvsmoda/sale-panel/v2/sale-items/searc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Se quiser, já pode passar parâmetros (exemplo: datas e filial)
payload = {
    "branchs": [5],
    "datemin": "2025-09-01T00:00:00Z",
    "datemax": "2025-09-30T23:59:59Z"
}


#possible_paths = [ 
#                 "sale-panel/v2/totals-seller/search", 
#                 "sale-panel/v2/sales/search", 
#                 "sale-panel/v2/sale-items/search", 
#                 "sale-panel/v2/clients/search", 
#                 "sale-panel/v2/sellers/search", 
#                 "sale-panel/v2/branches/search", 
#                 "sale-panel/v2/summary/search", 
#                "sale-panel/v2/products/search" 
#               ]

resp = requests.post(url, headers=headers, json=payload)

print(f"🔍 Status: {resp.status_code}")

if resp.status_code == 200:
    try:
        data = resp.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("❌ Erro ao decodificar JSON:", e)
        print(resp.text)
else:
    print("⚠️ Erro na requisição:")
    print(resp.text)
