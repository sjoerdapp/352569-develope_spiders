
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
import requests
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
from scrapy import FormRequest


### Discovery Communications Inc. 2|2
### 2nd spider newsroom
### trick system by requesting all in one page and than use xpath 
# normal simple post with formdata, content comes as html under json key html
### back to 20100105



class QuotessSpider(scrapy.Spider):
    name = 'DiscoveryCom_II_4701100ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/DiscoveryCom_II_4701100ARV002/',
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
    start_urls = ['https://corporate.discovery.com/discovery-newsroom/?P=340']

    def parse(self, response):
          #body = json.loads(response.text)
          #content = body['html']
          
          #auxs = Selector(text=content).xpath('//article')
          auxs = response.xpath('//div[@class="articles"]/article[contains(@id, "post-")]')
          #body = str(response.body)
          #item = SwisscomIvCrawlerItem()
          #item['DOCLINK']= response.xpath('//div[@class="articles"]/article[contains(@id, "post-51390")]//text()').extract()#body[0 : 10000]#str(response.body)#
          #yield item
          for aux in auxs[0:30]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//time[contains(@class, "published")]/text()').extract_first()
              item['HEADLINE']= aux.xpath('.//h2/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//h2/a/@href').extract_first()
              #yield item  #

              base_url = 'https://corporate.discovery.com'
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
        name_regex_2=r'(\bAbout\s*Discovery)(.|\s)*|(\bAbout.Discovery\b)(.|\s)*|(\bABOUT.Discovery\b)(.|\s)*|(\bABOUT\s*.DISCOVERY\b)(.|\s)*'
        if not item['HEADLINE']:
          item['HEADLINE'] = ''.join(response.xpath('//header[@class="entry-header"]//text()').extract())

        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="entry-content"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       