import requests
import json

url = "http://147.139.33.25:8078/UpdatePartnerTask"
# url = "http://localhost:8013/UpdatePartnerTask"

payload = {
        "params": {
                "token": "TYYPX1MQX2UF1KP",
                "assignment_id":5,
                "route_id":1,
                "partner_id":17265,
                "task_id":4,
                "task_title":"Demo test here",
                "task_description":"demo description here"
        }
}

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
res = json.loads(response.text)
print(response.text)
