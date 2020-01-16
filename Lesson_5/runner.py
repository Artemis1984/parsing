from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from Lesson_5 import setings
from Lesson_5.spiders.hh import hh_Spider
from Lesson_5.spiders.sj import sj_Spider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(setings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(hh_Spider)
    process.crawl(sj_Spider)
    process.start()




