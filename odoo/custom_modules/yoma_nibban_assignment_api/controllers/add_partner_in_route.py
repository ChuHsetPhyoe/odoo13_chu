
import requests
import json

url = "http://192.168.100.252:2078/UpdatePartnerinRoute"

payload = {
    "params":
        {
            "token": "43QGXEQ40JU5UX8",
            "assignment_id": 5,
            "route_id": 1,
            "partner_id": 17268
        }
}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print('response', response.text)