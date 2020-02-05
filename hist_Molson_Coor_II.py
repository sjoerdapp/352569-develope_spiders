# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from scrapy import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Molson Coors Brewing Company 2|2
### 2nd spider news
### normal post with formdata and json, last 5 news come without date 
### 1 Fehler due to broken link
### back to 20150908


class QuotessSpider(scrapy.Spider):
    name = 'Molson_Coor_II_3300000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Molson_Coor_II_3300000ARV002/',
        }
    #custom_settings = {
    #    'SPLASH_URL': 'http://localhost:8050',
    #    'DOWNLOADER_MIDDLEWARES': {
    #        'scrapy_splash.SplashCookiesMiddleware': 723,
    #        'scrapy_splash.SplashMiddleware': 725,
    #        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    #    },
    #    'SPIDER_MIDDLEWARES': {
    #        'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    #    },
    #    'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    #}
    #start_urls = ['https://www.tsys.com/news-innovation/press-media/press-releases']

    def start_requests(self):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            #'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://molsoncoors.com',
            'Referer': 'https://molsoncoors.com/en/news',
            #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
            #'perc-version': '5.3.15',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }
        data = {
            'index' : '1',
            'tag': '',}
            #'view_args': 'dyamic_cards_with_filters/109541/0/1582816',
            ##'view_path': '/views/ajax',
            #'view_path': '/newsroom',
            #'view_base_path': '',
            #'view_dom_id': 'f950b72b00e43adae46270566a492b3f57f151aabf50c40403c6e0ad493a26b5',
            #'pager_element': '0',
            #'type': 'news_item',
            #'field_categories_target_id': 'All',
            #'year': 'all',
            #'page': '0',
            #'_drupal_ajax': '1',
            #'ajax_page_state[theme]': 'bhge',
            #'ajax_page_state[theme_token]': '',
            #'ajax_page_state[libraries]': 'bhge/global-styling,bhge_dynamic_filter_comp/bhge-video-popup,bhge_dynamic_filter_comp/bhge-views-counter,bhge_dynamic_filter_comp/bhge-youtube-popup,bhge_marketo/marketo,calendar/calendar.theme,classy/base,classy/messages,core/drupal.date,core/drupal.date,core/html5shiv,core/normalize,paragraphs/drupal.paragraphs.unpublished,seven/global-styling,views/views.ajax,views/views.ajax,views/views.module,views/views.module,views_infinite_scroll/views-infinite-scroll,views_infinite_scroll/views-infinite-scroll' ,
            #}

        for num in range(0,8):  # loop iterating over different pages of ajax request
            data['index'] = str(num)
            aux_url = 'https://molsoncoors.com/molsoncoors/news/feed?index={}&tag='
            s_url=[aux_url.format(num)][0]
            yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
              


    def parse(self, response):
          body = json.loads(response.text)
          for dat in body['feed']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['date'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['headline']
              item['DOCLINK']= dat['url'] 
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://molsoncoors.com'
              aux_url = dat['url'] 
              
              if '.pdf' in aux_url.lower():
                if aux_url.startswith('http'):
                    url= aux_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    item['DESCRIPTION'] = ''
                    yield item
                
                else:
                    url= base_url + aux_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    item['DESCRIPTION'] = ''
                    yield item
              else:
                if aux_url.startswith('http'):
                    url= aux_url
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
                    
                
                else:
                    url= base_url + aux_url
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
               
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex =r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*Molson\s* (?!Coors\’))(.|\s)*|(\bABOUT.Molson\s* (?!Coors\’))(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="newsArticle-subtitle"]/text() | //section[@class="newsArticle-content"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       