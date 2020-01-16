import scrapy
from scrapy.http import HtmlResponse
from pprint import pprint
from pymongo import MongoClient


class hh_Spider(scrapy.Spider):

    name = 'HeadHunter'
    a = input('Вакансия: HeadHunter').replace(' ', '+').replace('+', '%2B').replace('#', '%23')
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&area=1&enable_snippets=true&salary=&st=searchVacancy&text=' + a + '&page=0']
    allowed_domains = ['hh.ru']

    client = MongoClient('localhost', 27017)
    hh_db = client['hhdb']
    hh = hh_db.hh

    def parse(self, response: HtmlResponse):

        names = response.xpath("//div[@class= 'vacancy-serp-item__row vacancy-serp-item__row_header']//a/text()").extract()
        links = response.xpath("//div[@class= 'vacancy-serp-item__row vacancy-serp-item__row_header']//a/@href").extract()

        salary = response.xpath("//div[@class= 'vacancy-serp-item__sidebar']")

        just_list = []
        fit_list = list()

        for i in salary:
            just_list.append(i.extract())

        for i in range(0, len(just_list), 2):

            if len(str(just_list[i])) > 46:

                sal_text = str(just_list[i])[
                           str(just_list[i]).index('compensation">') + 14:str(just_list[i]).index('</div></div>')]

                sal_text = sal_text.replace('\xa0', '').replace('руб.', '').replace('EUR', '').replace('USD', '').replace(' ', '')

                just_list[i] = sal_text

        for i in range(0, len(just_list), 2):

            fit_list.append(just_list[i])

        sal_min, sal_max = 'Nan', 'Nan'

        for i in range(len(names)):

            if fit_list[i].startswith('<'):

                sal_min, sal_max = 'Nan', 'Nan'

            else:

                if '-' in fit_list[i]:
                    sal_min = int(fit_list[i][:fit_list[i].index('-')])
                    sal_max = int(fit_list[i][fit_list[i].index('-') + 1:])

                if 'от' in fit_list[i]:

                    if 'до' in fit_list[i]:
                        sal_min = int(fit_list[i][2:fit_list[i].index('до')])
                    else:
                        sal_min = int(fit_list[i][2:])

                if 'до' in fit_list[i]:
                    sal_max = int(fit_list[i][fit_list[i].index('до') + 2:])

            temp_dict = {'Название': names[i],
                         'Ссылка': links[i],
                         'От': sal_min,
                         'До': sal_max,
                         'Источник': 'HeadHunter'}

            hh_Spider.hh.update({'Ссылка': temp_dict['Ссылка']}, {'$set': temp_dict}, upsert=True)

            pprint(temp_dict)

        next_page_link = response.xpath("//a[@class='bloko-button HH-Pager-Controls-Next HH-Pager-Control']/@href").extract_first()

        yield response.follow(next_page_link, callback=self.parse)

    print(hh.count_documents({}))
