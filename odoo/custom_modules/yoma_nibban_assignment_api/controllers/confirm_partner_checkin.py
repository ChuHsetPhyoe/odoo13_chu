import requests
import json

# url = "http://149.129.134.206:8078/GetPartnersfromRoute"
url = "http://192.168.100.252:2078/ConfirmPartnerCheckIn"
payload = {"params":  {
    "token": "QQRGDLIV1Y3BFTQ",
    "assignment_id": 5,
    "route_id": 1,
    "partner_id": 17264,
    "check_in_datetime": "2021-02-19 10:45:51",
    "check_in_longitude": 30.683457,
    "check_in_latitude": 76.404948,
}}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print('response', response.text)