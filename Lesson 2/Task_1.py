import requests
from bs4 import BeautifulSoup as Bs

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
while page_button:

    main_link = 'https://hh.ru/search/vacancy?L_is_autosearch=false&area=1&clusters=' \
                'true&enable_snippets=true&text'

    link = main_link + '=' + vacancy + '&' + 'page=' + str(page)

    response = requests.get(link, headers=user_agent).text

    html_response = Bs(response, 'html.parser')

    page_list = html_response.findChildren('div', {'class': 'vacancy-serp-item'})

    for item in range(len(page_list)):

        salary = page_list[item].find('div', {'class': 'vacancy-serp-item__compensation'})

        if salary:
            salary = salary.getText()
        else:
            salary = 'по договоренности'

        vac_link = page_list[item].find('a', {'class': 'bloko-link HH-LinkModifier'})

        vac_name = page_list[item].find('a', {'class': 'bloko-link HH-LinkModifier'}).getText()
        print(name, vac_link['href'], vac_name, salary, sep='\n')
        print('='*50)

        page_button = html_response.find('div', {'class': 'bloko-gap bloko-gap_top'}). \
            findChildren('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})

    if page_button:
        page += 1

