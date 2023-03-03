# -*- coding: utf-8 -*-
# Define here the models for your scraped items
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    follower_id = scrapy.Field()
    following_id = scrapy.Field()
    # likes = scrapy.Field()
    # post = scrapy.Field()
    username = scrapy.Field()
    username_follower = scrapy.Field()
    username_following = scrapy.Field()
    full_name = scrapy.Field()
    photo = scrapy.Field()
    user_attribute = scrapy.Field()
    full_info = scrapy.Field()