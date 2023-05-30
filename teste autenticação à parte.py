from requests.auth import HTTPBasicAuth
import requests

# Autenticando solicitações com módulo request

resultado = requests.get('http://localhost:5000/login', auth=('daniel', '123456'))
print(resultado.json())

resultado_autores = requests.get('http://localhost:5000/autores', headers={'x-acess-token': resultado.json()['token']})
print(resultado_autores.json())
