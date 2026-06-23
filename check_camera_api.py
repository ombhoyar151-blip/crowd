import requests

# Obtain token
r = requests.post('http://127.0.0.1:8000/api/v1/auth/token', json={'username':'admin','password':'changeme'})
print('token status:', r.status_code)
print('token body:', r.text)

if r.status_code == 200:
    token = r.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    r2 = requests.get('http://127.0.0.1:8000/api/v1/cameras', headers=headers)
    print('cameras status:', r2.status_code)
    print('cameras body:', r2.text)
else:
    print('Failed to obtain token')
