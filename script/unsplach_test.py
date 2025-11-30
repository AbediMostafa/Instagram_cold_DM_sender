import requests

access_key = 'WNPnUKwqSrvuneSBHJjGrnvcSR0uJdWWkz57nQN8yuQ'
url = f'https://api.unsplash.com/photos/random?client_id={access_key}'
res = requests.get(url)

print(res.status_code)
print(res.json)
