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
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### CenterPoint Energy 2|2
### 2nd spider News articles
### using splash as data comes in json within sourcecode
### data comes in sêcond XHR request....search in response
### back to 20020208


class QuotessSpider(scrapy.Spider):
    name = 'CenterP_II_2093900ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/CenterP_II_2093900ARV002/',
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
    
    start_urls = ['https://www.centerpointenergy.com/en-us/corporate/about-us/news']

    def parse(self, response):
        for page in [11, 21, 31]: #list(range(1, 272, 10)):
            url = 'https://www.centerpointenergy.com/en-us/corporate/about-us/news#k=#s={}'
            url = url.format(page)
            request = SplashRequest(url=url, splash_headers={'Authorization': basic_auth_header('535209af07354fbbb4110611b27f7504', '')}, args={'wait': 0.5, 'timeout':15}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/201,00101 Firefox/62.0'},   callback=self.parse_next)
            yield request

        

    def parse_next(self, response):
          auxs = response.xpath('//div[@class="news-results-items"]//div[@class="media"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              #item['PUBSTRING'] = aux.xpath('./td//div[@class="datetime"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//h3/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//h3/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.centerpointenergy.com'
              aux_url = aux.xpath('.//h3/a/@href').extract_first()
              
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
                    request = SplashRequest(url=url, splash_headers={'Authorization': basic_auth_header('535209af07354fbbb4110611b27f7504', '')}, args={'wait': 0.5, 'timeout':15}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/201,00101 Firefox/62.0'}, callback=self.parse_details)
                    #scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
                    
                
                else:
                    url= base_url + aux_url
                    request = SplashRequest(url=url, splash_headers={'Authorization': basic_auth_header('535209af07354fbbb4110611b27f7504', '')}, args={'wait': 0.5, 'timeout':15}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/201,00101 Firefox/62.0'}, callback=self.parse_details)
                    #scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
               
        
    def parse_details(self, response):
        item = response.meta['item']
        item['PUBSTRING'] = response.xpath('//div[@class=" visiblexs"]//h6/text()').extract_first()
        name_regex = r'xxx'#(This\s*release\scontains\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*MSCI\b)(.|\s)*|(\bABOUT.MSCI\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class=" visiblexs"]//text()[not(ancestor::h1 or ancestor::h6 )][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       