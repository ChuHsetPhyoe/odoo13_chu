import requests
import json

# url = "http://147.139.33.25:8078/GetPartnerTask"
url = "http://localhost:8013/SavePartnerTask"

payload = {
        "params": {
                "token": "LVB5IPOQXUOBE8E",
                "assignment_id": 5,
                "route_id": 1,
                "partner_id": 17264,
                "task_id": 2,
                "task_title": 'xxx',
                "task_description": 'xxx',
                "task_image": '(Multipart upload)'
        }
}

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
res = json.loads(response.text)
print(response.text)
