# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from JobParser.items import JobparserItem


class HhSpider(scrapy.Spider):

    name = 'HeadHunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=1&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse):

        names = response.xpath(
            "//div[@class= 'vacancy-serp-item__row vacancy-serp-item__row_header']//a/text()").extract()
        links = response.xpath(
            "//div[@class= 'vacancy-serp-item__row vacancy-serp-item__row_header']//a/@href").extract()

        salary = response.xpath("//div[@class= 'vacancy-serp-item__sidebar']")

        yield JobparserItem(name=names, link=links, salary=salary)

        next_page_link = response.xpath("//a[@class='bloko-button HH-Pager-Controls-Next HH-Pager-Control']/@href").extract_first()




        yield response.follow(next_page_link, callback=self.parse)





