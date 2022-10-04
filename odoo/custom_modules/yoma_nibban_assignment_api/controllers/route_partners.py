import requests
import json

url = "http://147.139.33.25:8078/GetPartnersfromRoute"
# url = "http://localhost:8013/GetPartnersfromRoute"
payload = {"params":  {
    "token": "Q9YF7DPW24X3V18",
    "assignment_id": 14,
    "route_id": 10,
    "salesperson_lat": 25.629235,
    "salesperson_long": 85.137566,
    }
}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print('response', response.text)