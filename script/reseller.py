import requests

url = f'https://radicalsmm.shop/api/v1'
params = {
    'key':'JKl7fTVuVc6ONgrkwH3YruOkzsrlBgqE',
    'action':'status',
    'orders':"334864",
}
res = requests.post(url, data=params)

print(res.status_code)
print(res.text)
# {"334851": {"order": "334851", "status":"Completed",    "start_count":0,"remains":0}}
# {"334851": {"order": "334851", "status": "In progress", "charge": "0.2500", "start_count": null, "remains": "0", "currency": "USD"}}