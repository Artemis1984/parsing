# -*- coding: utf-8 -*-
import scrapy
from JobParser.items import JobparserItem


class SjSpider(scrapy.Spider):
    name = 'SuperJob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&page=1']

    def parse(self, response):

        names = response.xpath("//div[@class= '_3mfro CuJz5 PlM3e _2JVkc _3LJqf']").extract()

        for i in names:
            names[names.index(i)] = str(i)[str(i).index('PlM3e _2JVkc _3LJqf">') + 21:-6].replace(
                '<span class="_1rS-s">', '').replace('</span>', '')

        links = response.xpath("//a[starts-with(@class, 'icMQ_ _1QIBo f-test-link-')]/@href").extract()

        for i in range(len(links)):
            links[i] = 'https://superjob.ru' + str(links[i])

        salary = response.xpath(
            "//span[@class= '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz']").extract()

        yield JobparserItem(name=names, link=links, salary=salary)

        next_page_link = response.xpath("//a[@class= 'icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-Dalshe']/@href").extract_first()
        yield response.follow(next_page_link, callback=self.parse)


