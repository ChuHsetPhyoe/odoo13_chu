
import requests
import json

url = "http://147.139.33.25:8078/CreatePartner"

payload = {
    "params":  {
        "token": "Q9YF7DPW24X3V18",
        "assignment_id": 14,
        "route_id": 10,
        "partner_name": 'ABC Pvt Ltd',
        "address_line1": "xxxxx",
        "address_line2": "xxxxx",
        "town": 522,
        # "city": 3,
        "state": 22,
        "zip": "123234",
        "country": 11,
        "phone": "0120223344",
        "mobile": "9711327387",
        "email": "1234er856@yahoo.com",
        "website": "http://www.abc.com",
        "latitude": 30.68346,
        "longitude": 76.40495,
    }
}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print('response', response.text)
