import requests
from bs4 import BeautifulSoup as Bs
from pprint import pprint
from pymongo import MongoClient
from hashlib import sha1


# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
# и реализовать функцию, записывающую собранные вакансии в созданную БД
# 2) Написать функцию, которая производит поиск и выводит на экран
# вакансии с заработной платой больше введенной суммы
# 3)*Написать функцию, которая будет добавлять в вашу базу данных только
# новые вакансии с сайта. Доработать функцию, которая будет
# обновлять старые вакансии.


user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

vacancy = input('Введите вакансию: ').replace(' ', '+').replace('+', '%2B').replace('#', '%23')


def hh_parser(page=0):

    name = 'HeadHunter'
    page_button = True
    HH_list = []

    while page_button:

        main_link = 'https://hh.ru/search/vacancy?L_is_autosearch=false&area=1&clusters=' \
                    'true&enable_snippets=true&text'

        link = main_link + '=' + vacancy + '&' + 'page=' + str(page)

        response = requests.get(link, headers=user_agent).text

        html_response = Bs(response, 'html.parser')

        page_list = html_response.findChildren('div', {'class': 'vacancy-serp-item'})

        for i in range(len(page_list)):

            sal_min, sal_max = 'Nan', 'Nan'

            temp_dict = {'hash': '',
                         'Компания': '',
                         'Вакансия': '',
                         'От': '',
                         'До': '',
                         'Ссылка': ''}

            salary = page_list[i].find('div', {'class': 'vacancy-serp-item__compensation'})

            if salary:

                sal_text = salary.getText().replace('\xa0', '').replace('руб.', '').replace('EUR', '').replace('USD',
                                                                                                               '').replace(
                    ' ', '')
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

            vac_link = page_list[i].find('a', {'class': 'bloko-link HH-LinkModifier'})

            vac_name = page_list[i].find('a', {'class': 'bloko-link HH-LinkModifier'}).getText().replace('\u200e', '')

            temp_dict['Компания'] = name
            temp_dict['Вакансия'] = vac_name
            temp_dict['Ссылка'] = vac_link['href']
            temp_dict['От'] = sal_min
            temp_dict['До'] = sal_max
            temp_dict['hash'] = sha1(str(temp_dict).encode('utf-8')).hexdigest()

            HH_list.append(temp_dict)

            page_button = html_response.find('a', {'data-qa': 'pager-next'})

        if len(HH_list) == 0:
            print('Ничего не найдено!')
            page_button = False

        if page_button:
            page += 1

    return HH_list


def sj_parser(page=1):
    name = 'SuperJob'
    page_button = True
    div_class = '_3zucV _2GPIV f-test-vacancy-item i6-sc _3VcZr'
    SJ_list = []

    while page_button:

        main_link = 'https://www.superjob.ru/vacancy/search/?keywords='

        link = main_link + vacancy + '&page=' + str(page)

        response = requests.get(link).text

        html_response = Bs(response, 'html.parser')

        item = html_response.findChildren('div', {'class': div_class})

        for item in item:

            temp_dict = {'Компания': name,
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

            sal_text = item.find('div', {'class': '_2g1F-'}).findChildren \
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

            if not ('—' in sal_text[0]) and not ('от' in sal_text[0]) and not ('до' in sal_text[0]):
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
            page_button = html_response.find('div', {'L1p51'}).findChildren(
                {'span': {'class': 'qTHqo _2h9me DYJ1Y _2FQ5q _2GT-y'}})

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

    return SJ_list


client = MongoClient('localhost', 27017)
db_SuperJob = client['SuperJob']
db_HeadHunter = client['HeadHunter']
SuperJob = db_SuperJob.SuperJob
HeadHunter = db_HeadHunter.HeadHunter


HH_list = hh_parser()
SJ_list = sj_parser()


if HH_list:
    for i in HH_list:

        if HeadHunter.find_one({'hash': i['hash']}):

            continue

        else:

            if HeadHunter.find_one({'Ссылка': i['Ссылка']}):

                HeadHunter.update_one({'Ссылка': i['Ссылка']}, {'$set': i})

            else:
                HeadHunter.insert_one(i)


if SJ_list:

    for i in SJ_list:

        if SuperJob.find_one({'hash': i['hash']}):

            continue

        else:

            if SuperJob.find_one({'Ссылка': i['Ссылка']}):

                SuperJob.update_one({'Ссылка': i['Ссылка']}, {'$set': i})

            else:
                SuperJob.insert_one(i)

HH = HeadHunter.find()
SJ = SuperJob.find()


for i in SJ:
    pprint(i)
for j in HH:
    pprint(j)

print('='*50)

print('HeadHunter:', HeadHunter.count_documents({}), 'SuperJob:', SuperJob.count_documents({}))


over = int(input('Больше: '))
SJ = SuperJob.find({'$or': [{'От': {'$gt': over}}, {'До': {'$gt': over}}]})
HH = HeadHunter.find({'$or': [{'От': {'$gt': over}}, {'До': {'$gt': over}}]})


for i in SJ:
    pprint(i)
    print('='*50)

for j in HH:
    pprint(j)
    print('='*50)
