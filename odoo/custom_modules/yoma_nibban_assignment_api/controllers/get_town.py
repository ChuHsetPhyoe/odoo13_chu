#!/usr/bin/python3

import requests
import json

url = "http://192.168.100.252:2078/GetTown"
# url = "http://147.139.5.4:8070/GetPartnerType"
payload = {
    "params":  {
        "token": "43QGXEQ40JU5UX8"
    }
}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print ('response', response.text)