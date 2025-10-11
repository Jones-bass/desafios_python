import requests
import json

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJsYWdlYSIsImlkIjoieHVrWTk0KzJRKy84VU9paDdEVHJwd0s1ZDR4SFNZRG1sV0thSWVBekIrdVVmbWk0YVNXWERQZmpCQUsrc1NGQVZxMlEwZ29Jc28wZ20vZlBaMXo4ZjVkbDhDcG5nd2xwQm80clAwRzJWazQ2dWIvcGpkeVp6Zlc3ZEhoNTF1dzZRQXh6ZlpNeVdJbytkWEYzUmJsYzBRPT0iLCJqdGkiOiI4NmI0MWJiMC0zYmU4LTQ2NDQtYTI4Ni0wNDcwNmQ4MThlODkiLCJ2ZXJzaW9uIjoidjIiLCJ0eXBlIjoiZGVmYXVsdCIsInJvbGVzIjpbIkFETSIsIkFOTCIsIkNBUCIsIkNNQyIsIkNNUCIsIkVOUCIsIkZDQyIsIkZDUCIsIkZDUiIsIkZHUiIsIkZJUyIsIkdFRCIsIkdFTiIsIkdMQiIsIklNR1BSRCIsIklOVCIsIk1ORyIsIk1PUCIsIk1XQVBQIiwiUENQIiwiUEVEIiwiUEVTIiwiUFJEIiwiU0RQIiwiU0VMIiwiU1JWIiwiVFJBIiwiVk9VIl0sInNvdXJjZSI6ImFwaS90b3R2c21vZGEvYXV0aG9yaXphdGlvbi92Mi90b2tlbiIsImNsaWVudGlkIjoibGFnZWFhcGl2MiIsInN1YiI6IjMiLCJicmFuY2hlcyI6WyIxIiwiMiIsIjMiLCI0IiwiNSIsIjYiLCI3IiwiOCJdLCJleHAiOjE3NjAyMTg4NzMsImlzcyI6InRvdHZzLmNvbSJ9.UbBDJPiuArTvszAR32JEf7Zwmn2sH8pIkGd5mJwrSyc"

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
