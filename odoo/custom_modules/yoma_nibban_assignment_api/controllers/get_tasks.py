import requests
import json

# url = "http://147.139.33.25:8078/GetPartnerTask"
url = "http://192.168.100.252:2078/GetPartnerTask"
payload = {
    "params": {
        "token": "LVB5IPOQXUOBE8E",
        "assignment_id": 5,
        "route_id": 1,
        "partner_id": 17264
    }
}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
res = json.loads(response.text)
print(response.text)