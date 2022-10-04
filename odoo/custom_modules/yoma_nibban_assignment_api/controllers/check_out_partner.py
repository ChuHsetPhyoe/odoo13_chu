import requests
import json

# url = "http://147.139.33.25:8078/GetPartnerTask"
url = "http://192.168.100.252:2078/CheckOutPartner"

payload = {
        "params":  {
            "token": "LVB5IPOQXUOBE8E",
            "assignment_id": 5,
            "route_id": 1,
            "partner_id": 17264,
            "check_out_longitude": 30.683457,
            "check_out_latitude": 76.404948,
       }
}

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
res = json.loads(response.text)
print(response.text)
