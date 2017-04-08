import requests

files = {'file': open('', 'rb')}
r = requests.post('http://localhost:5000/api/upload',files=files)
print r.text