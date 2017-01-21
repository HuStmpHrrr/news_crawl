# -*- coding: utf-8 -*-
import scrapy
import urlparse
import crawler.commons as commons
import logging
import datetime


class Target(object):
    def __init__(self, name, predicate, limit):
        self._name = name
        self._predicate = predicate
        self._limit = limit
        self._cnt = 0

    @property
    def cnt(self):
        return self._cnt

    def inc(self):
        if not self.is_done: self._cnt += 1
        return self._cnt

    def is_done(self):
        return self._cnt >= self._limit


class CnnSpider(scrapy.Spider):
    name = "CNN"
    start_urls = ['http://www.cnn.com']

    targets = {
        'Trump': Target("Trump", lambda s: 'Trump' in s, 25),
        'Clinton': Target("Clinton", lambda s: 'Clinton' in s, 25)
    }

    today = datetime.date.today()
    limit = today - datetime.timedelta(days=1)

    def should_crawl(self, uri):
        url = urlparse.urlparse(uri)
        try:
            date = datetime.date(*url.path.split('/')[1:4])
            return date >= self.limit
        except:
            return False

    def should_stop(self):
        return all(t.is_done for t in self.targets.values())

    def parse(self, response):
        if self.should_stop: return
        for href in response.xpath('//a/@href').extract():
            if href.startswith('/') and not href.startswith('/video'):
                nex = response.urljoin(href)
                logging.info(nex)
                yield scrapy.Request(nex, self.news_crawler)

        for req in self.news_crawler(response):
            yield req

    def news_crawler(self, response):
        stories = commons.cnnparser.extract_content_model(response)
        for story in stories:
            if self.should_crawl(story.uri):
                logging.info(story.uri)
                yield scrapy.Request(story.uri, self.news_parse)

    def news_parse(self, response):
        pass
