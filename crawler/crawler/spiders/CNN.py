# -*- coding: utf-8 -*-
import scrapy
import urlparse
import crawler.commons as commons


class CnnSpider(scrapy.Spider):
    name = "CNN"
    start_urls = ['http://www.cnn.com']

    targets = {
        'Trump': lambda s: 'Trump' in s,
        'Clinton': lambda s: 'Clinton' in s
    }

    def parse(self, response):
        response.css('a')
