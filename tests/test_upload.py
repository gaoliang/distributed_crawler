import requests

with open("/Users/gaoliang/Desktop/www_2.zip", 'rb') as file:
    files = {'file': file}
    r = requests.post("http://127.0.0.1:800/api/upload", files=files)
    print r.text
