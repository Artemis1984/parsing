import requests
import json
from pprint import pprint

# 1. Посмотреть документацию к API GitHub, разобраться как вывести список
# репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.

my_request = requests.get('https://api.github.com/users/Artemis1984/repos')

print()

for repo in my_request.json():

    with open('file.json', 'a') as f:
        json.dump(repo['html_url'], f, indent=5)
        json.dump(', ', f)

print()

with open('file.json') as f:
    pprint(f.read())

