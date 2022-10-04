import requests
import json

url = "http://192.168.100.252:2078/CheckUserLogin"
# url = "http://localhost:8013/CheckUserLogin"
payload = {
    "params": {
        "login": "assignment_user",
        "password": "12345",
    }
}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
res = json.loads(response.text)
print(response.text)