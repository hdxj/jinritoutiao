# -*- coding: utf-8 -*-
import scrapy
import json
import random
import re
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from scrapy import Request,FormRequest
from jinritoutiao.items import JinritoutiaoItem


class ToutiaoSpider(scrapy.Spider):
    name = "toutiao"
    allowed_domains = ["www.toutiao.com"]


    def start_requests(self):
        start_url = 'http://www.toutiao.com/api/pc/feed/?category=news_society&utm_source=toutiao&widen=1&max_behot_time=0&max_behot_time_tmp=0&tadrequire=true&as=A185B9497A9F0BD&cp=599A2FF0CB3DFE1'
        yield Request(url=start_url,callback=self.parse_index)

    def parse_index(self, response):
        lists = json.loads(response.text).get('data')
        for each in lists:
            item = {}
            item['abstract'] = each.get('abstract')
            if item['abstract'] == '':
                continue
            item['article_genre'] = each.get('article_genre')
            if item['article_genre'] != 'article':
                continue
            item['title'] = each.get('title')
            item['chinese_tag'] = each.get('chinese_tag')
            item['label'] = each.get('label')
            item['source'] = each.get('source')
            url = each.get('source_url')
            item['source_url'] = 'http://www.toutiao.com/a'+re.compile('/group/(\d+)/').search(url).group(1)+'/'
            item['tag'] = each.get('tag')
            yield Request(url=item['source_url'],callback=self.parse_content,meta={'item':item})

        ##翻页
        max_behot_time = json.loads(response.text).get('next').get('max_behot_time')
        str1 = '1234567890ABCDEF'
        as1 = [random.choice(str1) for i in range(13)]
        cp1 = [random.choice(str1) for j in range(9)]
        url = 'http://www.toutiao.com/api/pc/feed/' \
              '?category=news_society&utm_source=toutiao' \
              '&widen=1&max_behot_time={max_behot_time}' \
              '&max_behot_time_tmp={max_behot_time_tmp}&tadrequire=true&as={as1}' \
              '&cp={cp1}'.format(max_behot_time=max_behot_time, max_behot_time_tmp=max_behot_time, as1=as1, cp1=cp1)
        yield Request(url=url,callback=self.parse_index)

    def parse_content(self, response):
        items = response.meta.get('item')
        html = re.compile("content: '(.*?);'.replace").search(response.text).group(1)
        H = HTMLParser()
        html = BeautifulSoup(H.unescape(html))
        text = html.get_text()
        time = re.compile("time: '(.*?)'").search(response.text).group(1)

        item = JinritoutiaoItem()
        item['abstract'] = items['abstract']
        item['article_genre'] = items['article_genre']
        item['chinese_tag'] = items['chinese_tag']
        item['label'] = items['label']
        item['source'] = items['source']
        item['source_url'] = items['source_url']
        item['tag'] = items['tag']
        item['title'] = items['title']
        item['content'] = text
        item['time'] = time
        yield item



