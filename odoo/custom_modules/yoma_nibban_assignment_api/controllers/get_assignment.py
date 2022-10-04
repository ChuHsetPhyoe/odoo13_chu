import requests
import json

# url = "http://149.129.134.206:8078/GetAssignmentsDetails"
url = "http://192.168.100.252:2078/GetAssignmentsDetails"
payload = {"params":  {
    "token": "SM0WAU904BRX8V9",
}}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print('response', response.text)