# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DataElectorateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Electorate(scrapy.Item):
    city = scrapy.Field()
    electorate = scrapy.Field()
    year_electorate = scrapy.Field()
    month_electorate = scrapy.Field()

class Population(scrapy.Item):
    year_estimed = scrapy.Field()
    value_estimed = scrapy.Field()
    year_censo = scrapy.Field()
    value_censo = scrapy.Field()
