import requests
import json

url = "http://192.168.100.252:2078/AddPartnerTask"
# url = "http://localhost:8013/AddPartnerTask"

payload = {
        "params":  {
                "token": "ICHH08EAZYVJ1JU",
                "assignment_id": 6,
                "route_id": 4,
                "partner_id": 17272,
                "task_title": "there",
                "task_description": "hey"
        }
}

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
res = json.loads(response.text)
print(response.text)
