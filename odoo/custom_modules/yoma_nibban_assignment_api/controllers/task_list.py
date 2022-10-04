
import requests
import json

url = "http://localhost:8016/GetPartnerTask"

payload = {"params":  {
    "token": "SM0WAU904BRX8V9",
    "partner_id": 16680,
    "assignment_id": 5,
    "route_id": 1,
}}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print('response', response.text)