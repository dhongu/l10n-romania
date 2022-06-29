

import requests
import json

param = {
    "client_id": "7736105cbf06d7e77d08676287920023e996dd82a7a4a962",
    "client_secret": "d85ae8aa7367e349d2d6b1dd6ffa1a98836f05e3003b0023e996dd82a7a4a962",
    'response_type': 'code',
    'redirect_uri': 'https://www.anaf.ro',
    'grant_type': 'authorization_code'
}

json_param = json.dumps(param)

headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

url = 'https://logincert.anaf.ro/anaf-oauth2/v1/authorize'
req = requests.get(url, param)

print(req)

param.update({
    'code':'x',
    'auth_code':'x'
})

url = 'https://logincert.anaf.ro/anaf-oauth2/v1/token'

req = requests.post(url, param)

print(req)
