# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
from urllib.parse import urlunparse, urlparse, urlencode
import scrapy.http

### UPDATES
### get last page, nececessary to change "token" for updates

### E*trade Financial Corporation 1|2
### 1st spider actual news, 2nd spider archive
### complex get with json
### evtl. neccessary to change the "token" when making updates
### back to 20171016


class QuotessSpider(scrapy.Spider):
    name = 'E-Trade_I_1491500ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/E-Trade_I_1491500ARV001/',
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
                'Origin': 'https://about.etrade.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            }
        data = {
                'topic': 'ETFC',
                'resultsPerPage': '25',
                'page': '2',
                'thumbnailurl': 'false',
                'summary': 'true',
                'newslang': 'en',
                'summLen': '300',
                'videoonly': 'false',
                'src': 'bwi',
                'excludeTopics': 'NONCOMPANY',
                'token': '41cf226534bb0624a5713e386a48c1c13f15f228d828863818b6aeda8d579f03',
            }

        for num in range(1,2):  # loop iterating over different pages of ajax request
            data['page'] = str(num)
            #s_url = 'https://www.bhge.com/views/ajax?_wrapper_format=drupal_ajax'
            yield scrapy.http.Request(
            urlunparse(urlparse(
                'https://app.quotemedia.com/datatool/getHeadlines.json'
            )._replace(query=urlencode(data))),
            headers=headers)
              


    def parse(self, response):
          body = json.loads(response.text)
          for dat in body['results']['news'][0]['newsitem']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['datetime'].split('T')[0] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['headline']
              item['DOCLINK']= dat['storyurl'] 
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.cmsenergy.com'
              aux_url = item['DOCLINK'] 
              
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*E.Trade)(.|\s)*|(\bAbout.E.Trade\b)(.|\s)*|(\bABOUT\s*E.TRADE\b)(.|\s)*|(\bABOUT\s*.E.TRADE\b)(.|\s)*|(\bAbout\s*E\*Trade)(.|\s)*|(\bAbout.E\*Trade\b)(.|\s)*|(\bABOUT\s*E\*TRADE\b)(.|\s)*|(\bAbout\s*.E\*TRADE\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@id="story"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       