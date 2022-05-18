import scrapy
from scrapy.http import TextResponse

from lesson6.hhru.items import JobparserItem

TEMPLATE_URL = "https://russia.superjob.ru/vacancy/search/?keywords="


class SjruSpider(scrapy.Spider):
    name = "sjru"
    allowed_domains = ["russia.superjob.ru"]
    max_page_number = 2

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [TEMPLATE_URL + query]

    @staticmethod
    def parse_item(response: TextResponse):
        title_xpath = "//h1/text()"
        salary_xpath = "//h1/parent::*/span/span[1]/text()"
        title = response.xpath(title_xpath).getall()
        salary = response.xpath(salary_xpath).getall()
        item = JobparserItem()
        item["title"] = title
        item["salary"] = salary
        item["url"] = response.url
        item["source"] = 'superjob.ru'
        yield item

    def parse(self, response: TextResponse, page_number: int = 1, **kwargs):
        items = response.xpath("//div[contains (@class, 'search-result-item')]"
                               "/div/div/div/div/div/div/div/span/a[contains(@class, 'f-test-link')]")
        for item in items[:5]:
            url = item.xpath("./@href").get()
            yield response.follow(url, callback=self.parse_item)

        next_url_xpath = "//a[contains(@class, 'Dalshe')]/@href"
        next_url = response.xpath(next_url_xpath).get()
        if next_url and page_number < self.max_page_number:
            new_kwargs = {
                "page_number": page_number + 1,
            }
            yield response.follow(
                next_url,
                callback=self.parse,
                cb_kwargs=new_kwargs
            )
