from pprint import pprint
import requests
from lxml.html import fromstring
from pymongo import MongoClient


class YandexNews:
    def __init__(self):
        self.url = "https://yandex.ru/"
        self.headers = {
            'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        self.items_xpath = "//ol[contains(@class, 'news__list')]//a"
        self.title_xpath = ".//span[contains (@class, 'news__item-content')]//text()"
        self.ref_xpath = ".//@href"
        self.datetime_xpath = 'deep dark xpath'  # Там нет дейттайма. И при переходе по ссылке новости нет дейттайма.
        # И вообще, было бы здорово рассматривать соизмеримые примеры на уроке
        # (с вложенными запросами и вот этим всем).
        self.source_xpath = ".//span[@class='news-story__subtitle-text']//text()"

    def get_news(self):
        r = requests.get(self.url, headers=self.headers)
        dom = fromstring(r.text)
        items = dom.xpath(self.items_xpath)

        for item in items:
            info = {}
            title = item.xpath(self.title_xpath)[0]
            new_url = item.xpath(self.ref_xpath)[0]
            new_r = requests.get(new_url, headers=self.headers)
            new_dom = fromstring(new_r.text)
            datetime = "04.20.69"
            source = new_dom.xpath(self.source_xpath)
            info["title"] = title.replace('\xa0', ' ')
            info["url"] = new_url
            info["datetime"] = datetime
            info["source"] = source
            mongo.save_one_item_with_update(info)


class MailRuNews:
    def __init__(self):
        self.url = "https://news.mail.ru/"
        self.headers = {
            'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        self.items_xpath = '//ul/li[contains(@class, "list__item")][position() > 2]/a'
        self.title_xpath = './/text()'
        self.ref_xpath = ".//@href"
        self.datetime_xpath = './/span[contains (@class, "js-ago")]//@datetime'
        self.source_xpath = './/a[contains (@class, "breadcrumbs__link")]//@href'

    def get_news(self):
        r = requests.get(self.url, headers=self.headers)
        dom = fromstring(r.text)
        items = dom.xpath(self.items_xpath)

        for item in items:
            info = {}
            title = item.xpath(self.title_xpath)[0]
            new_url = item.xpath(self.ref_xpath)[0]
            new_r = requests.get(new_url, headers=self.headers)
            new_dom = fromstring(new_r.text)
            datetime = new_dom.xpath(self.datetime_xpath)[0]
            source = new_dom.xpath(self.source_xpath)[0]
            info["title"] = title.replace('\xa0', ' ')
            info["url"] = new_url
            info["datetime"] = datetime
            info["source"] = source
            mongo.save_one_item_with_update(info)


class LentaRuNews:
    def __init__(self):
        self.url = "https://lenta.ru/"
        self.headers = {
            'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        self.items_xpath = "//div[contains (@class, 'topnews')]//div[contains (@class, 'card-mini__text')]"
        self.title_xpath = ".//text()"
        self.ref_xpath = "./parent::a/@href"
        self.datetime_xpath = './/span[contains (@class, "js-ago")]//@datetime'
        self.source_xpath = './/a[contains (@class, "breadcrumbs__link")]//@href'

    def get_news(self):
        r = requests.get(self.url, headers=self.headers)
        dom = fromstring(r.text)
        items = dom.xpath(self.items_xpath)

        for item in items:
            info = {}
            title = item.xpath(self.title_xpath)[0]
            datetime = item.xpath(self.title_xpath)[1]
            source = 'lenta.ru'
            url = self.url + item.xpath(self.ref_xpath)[0]
            info["title"] = title.replace('\xa0', ' ')
            info["url"] = url
            info["datetime"] = datetime
            info["source"] = source
            mongo.save_one_item_with_update(info)


class MongoMagic:
    def __init__(self):
        self.mongo_host = "localhost"
        self.mongo_port = 27017
        self.mongo_db = "bullshit_news"
        self.mongo_collection = "bullshit_news"

    def save_one_item_with_update(self, item):
        with MongoClient(self.mongo_host, self.mongo_port) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            collection.update_one(
                {"url": item["url"]},
                {"$set": {"title": item["title"],
                          "datetime": item["datetime"],
                          "source": item["source"]}
                 },
                upsert=True,
            )


if __name__ == "__main__":
    mongo = MongoMagic()
    mr = MailRuNews()
    mr.get_news()

    ya = YandexNews()
    ya.get_news()

    lenta = LentaRuNews()
    lenta.get_news()
