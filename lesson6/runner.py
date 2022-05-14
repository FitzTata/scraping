from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson6.hhru.spiders.sjru_spider import SjruSpider
from hhru import settings
from hhru.spiders.hhru_spider import HhruSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    q_kwargs = {"query": "python"}
    # process.crawl(HhruSpider, **q_kwargs)
    process.crawl(SjruSpider, **q_kwargs)

    process.start()