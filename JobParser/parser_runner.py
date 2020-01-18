from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from JobParser import settings
from JobParser.spiders.hh import HhSpider
from JobParser.spiders.sj import SjSpider


if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    vacancy = input('Введите вакансию: ')
    process.crawl(HhSpider, section=vacancy)
    process.crawl(SjSpider, section=vacancy)
    process.start()
    process.start()
