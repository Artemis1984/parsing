import requests
from pprint import pprint
from pymongo import MongoClient
from lxml import html
from hashlib import sha1
import warnings
warnings.filterwarnings('ignore')

user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}


def mail_parser():
    link = 'https://mail.ru'
    response = requests.get(link, headers=user_agent)
    root = html.fromstring(response.text)

    links = root.xpath("//div[@class = 'tabs__content']/div//a[starts-with(@href,'https://news.mail.ru')]/@href")

    case = root.xpath("//div[@class = 'tabs__content']/div//a[starts-with(@href,'https://news.mail.ru')]")

    names = list()

    names.append(root.xpath(
        "//div[@class = 'tabs__content']/div//a[starts-with(@href,'https://news.mail.ru')]/div/div/h3/text()")[
                     0].replace('\xa0', ''))
    for i in case:
        if i.text:
            names.append(i.text.replace('\xa0', ''))

    dates = list()
    sources = list()

    for i, j in zip(names, links):
        new_resp = requests.get(j, headers=user_agent)
        new_root = html.fromstring(new_resp.text)
        date = new_root.xpath("//span[@class='note__text breadcrumbs__text js-ago']/text()")[0]
        dates.append(date)

        source = new_root.xpath("//a[@class='link color_gray breadcrumbs__link']/span/text()")[0]
        sources.append(source)

    mail_ru_list = list()

    for name, link, source, date in zip(names, links, sources, dates):
        temp_dict = {'Название': name,
                     'Ссылка': link,
                     'Источник': source,
                     'Время': date}
        temp_dict['hash'] = sha1(str(temp_dict).encode('utf-8')).hexdigest()

        mail_ru_list.append(temp_dict)

    return mail_ru_list


def yandex_parser():

    link = 'https://yandex.ru/news'
    response = requests.get(link, headers=user_agent)
    root = html.fromstring(response.text)
    links = root.xpath("//div[@class = 'story__topic']/h2/a/@href")
    names = root.xpath("//div[@class = 'story__topic']/h2/a/text()")
    link_list = list()
    name_list = list()
    data_list = list()
    fin_list = list()
    for i in links:
        if i.startswith('/news'):
            link_list.append('https://yandex.ru' + i)
        else:
            link_list.append(i)

    for j in names:
        name_list.append(j)

    datas = root.xpath("//div[@class= 'story__date']/text()")
    for i in datas:
        data_list.append(i)

    for name, link, source_date in zip(name_list, link_list, data_list):
        temp_dict = {'Название': name,
                     'Ссылка': link,
                     'Источник': source_date[:-5],
                     'Время': source_date[-5:]}
        temp_dict['hash'] = sha1(str(temp_dict).encode('utf-8')).hexdigest()

        fin_list.append(temp_dict)

    return fin_list


def lenta_parser():

    link = 'https://lenta.ru/'
    response = requests.get(link, headers=user_agent)
    root = html.fromstring(response.text)
    links = root.xpath("//section[@class= 'row b-top7-for-main js-top-seven']/div/div/a/@href")
    fin_list = list()
    for i in range(len(links)):
        if links[i].startswith('/news/'):

            links[i] = 'https://lenta.ru' + links[i]
        else:
            links[i] = None

    links.remove(None)

    names = root.xpath("//section[@class= 'row b-top7-for-main js-top-seven']/div/div/a[text()!='Больше новостей']/text()")
    names.insert(0, root.xpath("//div[@class='first-item']/h2/a/text()"))

    datas = root.xpath("//div[@class= 'item']/a/time/text()")
    datas.insert(0, root.xpath("//div[@class='first-item']/h2//a/time/text()")[0])

    for name, link, time in zip(names, links, datas):
        temp_dict = {'Название': name,
                     'Ссылка': link,
                     'Источник': 'Lenta.ru',
                     'Время': time}
        temp_dict['hash'] = sha1(str(temp_dict).encode('utf-8')).hexdigest()

        fin_list.append(temp_dict)

    return fin_list


client = MongoClient('localhost', 27017)
db_lenta = client['lenta']
db_yandex = client['yandex']
db_mail = client['mail']
lenta = db_lenta.lenta
yandex = db_yandex.yandex
mail = db_mail.mail


if lenta_parser():

    for i in lenta_parser():

        if lenta.find_one('hash', i['hash']):

            continue
        else:
            lenta.update({'Ссылка': i['Ссылка']}, {'$set': i}, upsert=True)

if yandex_parser():

    for i in yandex_parser():

        if yandex.find_one('hash', i['hash']):

            continue
        else:
            yandex.update({'Ссылка': i['Ссылка']}, {'$set': i}, upsert=True)


if mail_parser():

    for i in mail_parser():

        if mail.find_one('hash', i['hash']):

            continue
        else:
            mail.update({'Ссылка': i['Ссылка']}, {'$set': i}, upsert=True)


for i in lenta.find():
    pprint(i)

for i in yandex.find():
    pprint(i)

for i in mail.find():
    pprint(i)

print('='*70)
print('lenta.ru:', lenta.count_documents({}))
print('yandex.ru:', yandex.count_documents({}))
print('mail.ru:', mail.count_documents({}))

