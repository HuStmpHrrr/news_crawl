# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import scrapy
import urlparse
import crawler.commons as commons
import logging
import datetime
import os
import json


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

    @property
    def is_done(self):
        return self._cnt >= self._limit

    @property
    def predicate(self):
        return self._predicate


class CnnSpider(scrapy.Spider):
    name = "CNN"
    start_urls = ['http://www.cnn.com']

    targets = {
        'Trump': Target("Trump", lambda s: 'Trump' in s, 25),
        'Clinton': Target("Clinton", lambda s: 'Clinton' in s, 25)
    }

    today = datetime.date.today()
    limit = today - datetime.timedelta(days=1)

    def __init__(self, output_folder=None):
        self._output_folder = '.' if output_folder is None else output_folder
        self._target_folder = os.path.join(self._output_folder, 'targets')

        try:
            os.makedirs(self._target_folder)
        except OSError as e:
            if e.errno != 17: raise e

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        spider = cls(settings.get("OUTPUT_FOLDER"))
        spider._set_crawler(crawler)
        return spider

    def should_crawl(self, uri):
        url = urlparse.urlparse(uri)
        try:
            date = datetime.date(*map(int, url.path.split('/')[1:4]))
            return date >= self.limit
        except:
            return False

    @property
    def should_stop(self):
        return all(t.is_done for t in self.targets.values())

    def parse(self, response):
        if self.should_stop: return
        for href in response.xpath('//a/@href').extract():
            if href.startswith('/') and not href.startswith('/video'):
                nex = response.urljoin(href)
                logging.info('next url: {}'.format(nex))
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
        article = commons.cnnparser.to_structure(response)
        for (targ, track) in self.targets.items():
            if not track.is_done and commons.relates_to(article, track.predicate):
                track.inc()
                articled = article.todict()
                with open(os.path.join(self._target_folder, targ + '.jsonl'), 'a') as fd:
                    json.dump(articled, fd, separators=(',',':'))
                    fd.write('\n')
                print targ, track.cnt, article.orig
