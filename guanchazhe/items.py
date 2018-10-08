# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GuanchazheItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cate = scrapy.Field()
    title = scrapy.Field()
    # abstract = scrapy.Field()
    user_name = scrapy.Field()
    comment_text = scrapy.Field()
    tread_num = scrapy.Field()
    praise_num = scrapy.Field()