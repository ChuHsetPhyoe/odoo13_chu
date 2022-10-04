
import requests
import json

url = "http://147.139.33.25:8078/GetPartner"

payload = {
    "params":
        {
            "token": "ICHH08EAZYVJ1JU",
            "assignment_id": 5,
            "route_id": 1,
        }
}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print('response', response.text)