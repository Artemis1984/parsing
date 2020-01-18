import requests
from bs4 import BeautifulSoup as Bs
from pprint import pprint
from pymongo import MongoClient
from hashlib import sha1


vacancy = input('Введите вакансию: ').replace(' ', '+').replace('+', '%2B').replace('#', '%23')
name = 'SuperJob'
page_button = True
page = 1
div_class = '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'
SJ_list = []


while page_button:

    main_link = 'https://www.superjob.ru/vacancy/search/?keywords='

    link = main_link + vacancy + '&page=' + str(page)

    response = requests.get(link).text

    html_response = Bs(response, 'html.parser')

    item = html_response.findChildren('div', {'class': div_class})

    for item in item:

        temp_dict = {'Компания': 'SuperJob',
                     'Ссылка': '',
                     'Вакансия': '',
                     'От': '',
                     'До': ''}

        vac_name = item.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).getText()
        vac_link = item.findChildren({'a'})
        s = ''
        for i in range(2):
            if str(vac_link[i]).startswith('<a class="icMQ_ _1QIBo f-test-link-'):
                s = str(vac_link[i])
        s = s[s.index('href=') + 6:s.index('html') + 4]
        vac_link = 'https://superjob.ru' + s

        sal_min = 'Nan'
        sal_max = 'Nan'

        sal_text = item.find('div', {'class': '_2g1F-'}).findChildren\
            ('span', {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})

        sal_text = [i.getText() for i in sal_text]

        sal_text[0] = sal_text[0].replace('₽', '')

        if '—' in sal_text[0]:
            sal_min = sal_text[0][:sal_text[0].index('—')]
            sal_max = sal_text[0][sal_text[0].index('—') + 1:]

            if sal_max[-1] == '₽':
                sal_max = sal_text[0][sal_text[0].index('—') + 1:-1]

        if 'от' in sal_text[0]:

            if 'до' in sal_text:
                sal_min = sal_text[0][2:sal_text.index('до')]
            else:
                sal_min = sal_text[0][2:]
        if sal_text[0] == 'По договорённости':
            sal_min, sal_max = 'Nan', 'Nan'

        elif 'до' in sal_text[0]:
            sal_max = sal_text[0][sal_text[0].index('до') + 2:]

        if not('—' in sal_text[0]) and not('от' in sal_text[0]) and not('до' in sal_text[0]):
            sal_max = int(sal_text[0].replace('\xa0', ''))

        temp_dict['Компания'] = 'SuperJob'
        temp_dict['Вакансия'] = vac_name
        temp_dict['Ссылка'] = vac_link

        if type(sal_max) == int:

            temp_dict['До'] = sal_max,
            temp_dict['От'] = 'Nan'

        else:
            if sal_min.replace('\xa0', '') == 'Nan':
                temp_dict['От'] = 'Nan'
            else:
                temp_dict['От'] = int(sal_min.replace('\xa0', ''))

            if sal_max.replace('\xa0', '') == 'Nan':
                temp_dict['До'] = 'Nan'
            else:
                temp_dict['До'] = int(sal_max.replace('\xa0', ''))

        temp_dict['hash'] = sha1(str(temp_dict).encode('utf-8')).hexdigest()



        SJ_list.append(temp_dict)
    try:
        page_button = html_response.find('div', {'L1p51'}).findChildren({'span': {'class': 'qTHqo _2h9me DYJ1Y _2FQ5q _2GT-y'}})

    except AttributeError:
        page_button = []
    for i in page_button:
        if i.getText() == 'Дальше':
            page_button = 'Дальше'
            break

    if len(item) == 0:
        print('Ничего не найдено!')
        page_button = False

    elif page_button == 'Дальше':
        page += 1

    else:
        break

if len(SJ_list) == 0:
    pass

else:
    client = MongoClient('localhost', 27017)
    db = client['SuperJob']
    SuperJob = db.SuperJob


# Тестируем функционал по обновлению документа

    # print('Проверка функционала по обновлению и добавлению новых вакансий')
    # print('='*50)
    # print(SuperJob.find_one({'hash': 'c665efae3c7ce5f1ad768113501330850e2cca86'}))
    # SuperJob.update_one({'hash': 'c665efae3c7ce5f1ad768113501330850e2cca86'}, {'$set': {'От': 99999999, 'До': 99999999, 'hash': '123456789'}})
    # print('='*50)
    # print(SuperJob.find_one({'hash': '123456789'}))
    # print('='*50)

    for i in SJ_list:

        if SuperJob.find_one({'hash': i['hash']}):

            continue

        else:

            if SuperJob.find_one({'Ссылка': i['Ссылка']}):

                SuperJob.update_one({'Ссылка': i['Ссылка']}, {'$set': i})

            else:
                SuperJob.insert_one(i)

    for i in SuperJob.find():
        pprint(i)
        print('=' * 50)

    # over = int(input('Больше: '))
    #
    # for i in SuperJob.find({'$or': [{'От': {'$gt': over}}, {'До': {'$gt': over}}]}):
    #
    #     pprint(i)

    SuperJob.delete_many({})
