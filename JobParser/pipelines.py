# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pprint import pprint
from pymongo import MongoClient


class JobparserPipeline(object):

    client = MongoClient('localhost', 27017)
    hh_db = client['hh']
    sj_db = client['sj']
    hh = hh_db.hh
    sj = sj_db.sj

    def process_item(self, item, spider):

        if spider.name == 'HeadHunter':

            just_list = []
            fit_list = []

            for i in item['salary']:
                just_list.append(i.extract())

            for i in range(0, len(just_list), 2):

                if len(str(just_list[i])) > 46:
                    sal_text = str(just_list[i])[
                               str(just_list[i]).index('compensation">') + 14:str(just_list[i]).index('</div></div>')]

                    sal_text = sal_text.replace('\xa0', '').replace('руб.', '').replace('EUR', '').replace('USD',
                                                                                                           '').replace(
                        ' ',
                        '')

                    just_list[i] = sal_text

            for i in range(0, len(just_list), 2):
                fit_list.append(just_list[i])

            sal_min, sal_max = 'Nan', 'Nan'

            for i in range(len(fit_list)):

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

                temp_dict = {'Название': item['name'][i],
                             'Ссылка': item['link'][i],
                             'От': sal_min,
                             'До': sal_max,
                             'Источник': spider.name}

                pprint(temp_dict)

                JobparserPipeline.hh.update({'Ссылка': temp_dict['Ссылка']}, {'$set': temp_dict}, upsert=True)

            return item

        else:

            for i in range(len(item['salary'])):

                sal_min, sal_max = 'Nan', 'Nan'

                item['salary'][i] = str(item['salary'][i]).replace('<span>', '').replace('</span>', '').replace('<!-- -->', '').replace(
                    '₽', '').replace('\xa0', '')
                item['salary'][i] = item['salary'][i][item['salary'][i].index('_2VHxz">') + 8:]

                if '—' in str(item['salary'][i]):

                    sal_min = item['salary'][i][:item['salary'][i].index('—')]
                    sal_max = item['salary'][i][item['salary'][i].index('—') + 1:]

                elif 'от' in item['salary'][i]:

                    if 'до' in item['salary'][i]:
                        sal_min = item['salary'][i][2:item['salary'][i].index('до')]
                    else:
                        sal_min = item['salary'][i][2:]

                elif 'до' in item['salary'][i]:
                    sal_max = item['salary'][i][item['salary'][i].index('до') + 2:]

                else:
                    sal_max = item['salary'][i]

                if item['salary'][i] == 'По договорённости':
                    sal_min, sal_max = 'Nan', 'Nan'

                temp_dict = {'Название': item['name'][i],
                             'Ссылка': item['link'][i],
                             'От': sal_min,
                             'До': sal_max,
                             'Источник': spider.name}

                pprint(temp_dict)
                JobparserPipeline.sj.update({'Ссылка': temp_dict['Ссылка']}, {'$set': temp_dict}, upsert=True)
