import time

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from lxml.html import fromstring


class VkSelenium:
    def __init__(self):
        self.driver_path = './chromedriver/chromedriver.exe'
        self.url = 'https://vk.com/tokyofashion'
        self.options = webdriver.ChromeOptions().add_argument("--start-maximized")
        self.max_scroll_limit = 6
        self.driver = webdriver.Chrome(self.driver_path, options=self.options)

    def get_url(self):
        self.driver.get(self.url)
        time.sleep(2)

    def find_word_in_posts(self):
        """Don`t understand how this should interact with the other parts of code. ToDo: refine the terms of reference.
         Anyway, it works"""
        keyword = input('Введите слово для поиска: ')
        find_field_activation = self.driver.find_element_by_class_name('ui_tab_search')
        find_field_activation.click()
        time.sleep(2)
        find_field = self.driver.find_element_by_id('wall_search')
        find_field.send_keys(keyword)
        find_field.send_keys(Keys.ENTER)

    def close_auth_popup(self):
        try:
            auth_popup = self.driver.find_element_by_class_name('UnauthActionBox__close')
            auth_popup.click()
            time.sleep(0.5)
        except:
            pass

    def scroll_page(self):
        self.close_auth_popup()
        time.sleep(2)
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.END)
        actions.perform()
        self.close_auth_popup()

    def process(self):
        for _ in range(self.max_scroll_limit):
            self.scroll_page()
        self.html = self.driver.page_source
        self.driver.quit()
        return self.html


class VkXPath:
    def __init__(self, html):
        self.dom = fromstring(html)
        self.items_xpath = "//h5[contains(@class, 'post_author')]/parent::*/parent::*/parent::*"
        self.datetime_xpath = ".//div[contains(@class, 'post_date')][1]//span[@class = 'rel_date']//text()"
        self.text_xpath = ".//div[@class = 'wall_post_text']//text()"
        self.ref_xpath = ".//a[@class = 'post_link']//@href"
        self.likes_xpath = ".//div[contains (@class, 'PostButtonReactions__title')]//text()"
        self.shares_xpath = ".//div[contains(@class, '_share')]//@data-count"
        self.views_xpath = ".//span[contains(@class, 'views')]//text()"
        self.items = self.dom.xpath(self.items_xpath)
        self.site = 'https://vk.com'

    @staticmethod
    def formatting(some):
        try:
            return some[0].replace('\xa0', ' ')
        except:
            return some

    @staticmethod
    def formatting_text(text):
        try:
            return '\n'.join(text)
        except:
            return text

    def process(self):
        for item in self.items:
            info = {}
            datetime = self.formatting(item.xpath(self.datetime_xpath))
            ref = self.site + self.formatting(item.xpath(self.ref_xpath))
            text = self.formatting_text(item.xpath(self.text_xpath))
            likes = self.formatting(item.xpath(self.likes_xpath))
            shares = self.formatting(item.xpath(self.shares_xpath))
            views = self.formatting(item.xpath(self.views_xpath))
            info["ref"] = ref
            info["datetime"] = datetime
            info["text"] = text
            info["likes"] = likes
            info["shares"] = shares
            info["views"] = views
            mongo.save_one_item_with_update(info)


class MongoMagic:
    def __init__(self):
        self.mongo_host = "localhost"
        self.mongo_port = 27017
        self.mongo_db = "vk_tokyofashion"
        self.mongo_collection = "posts"

    def save_one_item_with_update(self, item):
        with MongoClient(self.mongo_host, self.mongo_port) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            collection.update_one(
                {"ref": item["ref"]},
                {"$set": {"datetime": item["datetime"],
                          "text": item["text"],
                          "likes": item["likes"],
                          "shares": item["shares"],
                          "views": item["views"],
                          }
                 },
                upsert=True,
            )


if __name__ == '__main__':
    vk = VkSelenium()
    vk.get_url()
    # vk.find_word_in_posts()  # not sure where it should be because not sure how it should interact with the other
    # parts of code. ToDo: refine the terms of reference.
    html = vk.process()
    mongo = MongoMagic()
    xpath = VkXPath(html)
    xpath.process()
