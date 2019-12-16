# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests
from pprint import pprint

username = input('Введите логин')
password = input('Введите пароль')

my_request = requests.get('https://api.github.com/user/repos', auth=(username, password)).json()

for repo in my_request:
    if repo['private']:
        pprint(repo['html_url'])
