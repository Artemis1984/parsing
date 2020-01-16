import scrapy
from scrapy.http import HtmlResponse
from pprint import pprint
from pymongo import MongoClient


class  sj_Spider(scrapy.Spider):

    name = 'SuperJob'
    a = input('Вакансия: SuperJob ').replace(' ', '+').replace('+', '%2B').replace('#', '%23')
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=' + a + '&page=1']
    allowed_domains = ['superjob.ru']

    client = MongoClient('localhost', 27017)
    sj_db = client['sjdb']
    sj = sj_db.sj

    def parse(self, response: HtmlResponse):

        names = response.xpath("//div[@class= '_3mfro CuJz5 PlM3e _2JVkc _3LJqf']").extract()

        for i in names:

            names[names.index(i)] = str(i)[str(i).index('PlM3e _2JVkc _3LJqf">') + 21:-6].replace(
                '<span class="_1rS-s">', '').replace('</span>', '')

        links = response.xpath("//a[starts-with(@class, 'icMQ_ _1QIBo f-test-link-')]/@href").extract()

        for i in range(len(links)):

            links[i] = 'https://superjob.ru' + str(links[i])

        salary = response.xpath("//span[@class= '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz']").extract()

        for i in range(len(salary)):

            sal_min, sal_max = 'Nan', 'Nan'

            salary[i] = str(salary[i]).replace('<span>', '').replace('</span>', '').replace('<!-- -->', '').replace('₽', '').replace('\xa0', '')
            salary[i] = salary[i][salary[i].index('_2VHxz">')+8:]

            if '—' in str(salary[i]):

                sal_min = salary[i][:salary[i].index('—')]
                sal_max = salary[i][salary[i].index('—')+1:]

            elif 'от' in salary[i]:

                if 'до' in salary[i]:
                    sal_min = salary[i][2:salary[i].index('до')]
                else:
                    sal_min = salary[i][2:]

            elif 'до' in salary[i]:
                sal_max = salary[i][salary[i].index('до') + 2:]

            else:
                sal_max = salary[i]

            if salary[i] == 'По договорённости':

                sal_min, sal_max = 'Nan', 'Nan'

            temp_dict = {'Название': names[i],
                         'Ссылка': links[i],
                         'От': sal_min,
                         'До': sal_max,
                         'Источник': 'SuperJob'}

            pprint(temp_dict)

            sj_Spider.sj.update({'Ссылка': temp_dict['Ссылка']}, {'$set': temp_dict}, upsert=True)

        next_page_link = response.xpath("//a[@class= 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe']/@href").extract_first()

        yield response.follow(next_page_link, callback=self.parse)

    print(sj.count_documents({}))
