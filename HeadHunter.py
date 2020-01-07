import requests
from bs4 import BeautifulSoup as Bs
from pprint import pprint
from pymongo import MongoClient
import time

# 1) Необходимо собрать информацию о вакансиях на вводимую должность (используем input или
# через аргументы) с сайта superjob.ru и hh.ru. Приложение должно анализировать несколько страниц
# сайта(также вводим через input или аргументы). Получившийся список должен содержать в себе
# минимум:

#  *Наименование вакансии
#  *Предлагаемую зарплату (отдельно мин. и и отдельно макс.)
#  *Ссылку на саму вакансию
#  *Сайт откуда собрана вакансия

# По своему желанию можно добавить еще работодателя и расположение. Данная структура должна
# быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью
# dataFrame через pandas.


user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

name = 'HeadHunter'
vacancy = input('Введите вакансию: ').replace(' ', '+').replace('+', '%2B').replace('#', '%23')
page_button = True
page = 0
HH_list = []
while page_button:

    main_link = 'https://hh.ru/search/vacancy?L_is_autosearch=false&area=1&clusters=' \
                'true&enable_snippets=true&text'

    link = main_link + '=' + vacancy + '&' + 'page=' + str(page)

    response = requests.get(link, headers=user_agent).text

    html_response = Bs(response, 'html.parser')

    page_list = html_response.findChildren('div', {'class': 'vacancy-serp-item'})

    for item in range(len(page_list)):

        sal_min, sal_max = 'Nan', 'Nan'

        temp_dict = {'Компания': '',
                     'Вакансия': '',
                     'От': '',
                     'До': '',
                     'Ссылка': ''}

        salary = page_list[item].find('div', {'class': 'vacancy-serp-item__compensation'})

        if salary:

            sal_text = salary.getText().replace('\xa0', '').replace('руб.', '').replace('EUR', '').replace('USD', '').replace(' ', '')
            if '-' in sal_text:
                sal_min = int(sal_text[:sal_text.index('-')])
                sal_max = int(sal_text[sal_text.index('-') + 1:])

            if 'от' in sal_text:

                if 'до' in sal_text:
                    sal_min = int(sal_text[2:sal_text.index('до')])
                else:
                    sal_min = int(sal_text[2:])

            if 'до' in sal_text:
                sal_max = int(sal_text[sal_text.index('до') + 2:])

        else:
            sal_min, sal_max = 'Nan', 'Nan'

        vac_link = page_list[item].find('a', {'class': 'bloko-link HH-LinkModifier'})

        vac_name = page_list[item].find('a', {'class': 'bloko-link HH-LinkModifier'}).getText()

        temp_dict['Компания'] = name
        temp_dict['Вакансия'] = vac_name
        temp_dict['Ссылка'] = vac_link['href']

        temp_dict['От'] = sal_min
        temp_dict['До'] = sal_max

        HH_list.append(temp_dict)

        page_button = html_response.find('a', {'data-qa': 'pager-next'})

    if len(HH_list) == 0:
        print('Ничего не найдено!')
        page_button = False

    if page_button:
        page += 1


if len(HH_list) == 0:
    pass

else:

    client = MongoClient('localhost', 27017)
    db = client['HeadHunter']
    HeadHunter = db.HeadHunter
    HeadHunter.insert_many(HH_list)

    # over = int(input('Больше: '))
    #
    # for i in HeadHunter.find({'$or': [{'От': {'$gt': over}}, {'До': {'$gt': over}}]}):
    #
    #     pprint(i)

    for i in HeadHunter.find():
        pprint(i)

    print(HeadHunter.count_documents({}))
    HeadHunter.delete_many({})

