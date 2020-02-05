# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
import json
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Flowserve Corporation 1|1
### 1st spider IR Press Releases
### normal get 
### back to 20140109


class QuotessSpider(scrapy.Spider):
    name = 'Flowserve_1425000ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Flowserve_1425000ARV001/',
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
    start_urls = ['https://flowservecorporation.gcs-web.com/news-releases?c00a0a13_year%5Bvalue%5D=_none&op=Filter&c00a0a13_widget_id=c00a0a13&form_build_id=form-aUp0gLGsWf1BFEmpqNmLIP4gztWUhXeZG5LY9uWD8fY&form_id=widget_form_base']

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 6)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://leggett.gcs-web.com/financial-information/press-releases?field_nir_news_date_value%5Bmin%5D=&items_per_page=50&promote=All&page={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          auxs = response.xpath('//article[@class="news-list-item"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./div[@class="news-list-date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('./div[@class="news-list-title"]/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://flowservecorporation.gcs-web.com'
              aux_url = item['DOCLINK']
              
              if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Safe(.|\s*)Harbor\s*Statement)(.|\s)*|(Certain\s*statements\s*in\s*this\s*news\s*release\s*contain\s*"forward-looking"\s*information)(.|\s)*|(Certain\s*statements\s*in\s*this\s*news\s*release\s*contain\s*or\s*may\s*suggest\s*"forward-looking"\s*information)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Flowserve\b)(.|\s)*|(\bAbout.Flowserve\b)(.|\s)*|(\bABOUT.FLOWSERVE\b)(.|\s)*|(Safe(.|\s*)Harbor\s*Statement)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            #pdf_link = 'https://www.news.xerox.com' + response.xpath('//a[contains(text(), "Financial Results")]/@href')
            #item['file_urls'] = [pdf_link]
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = 'FEHLER' #re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="entry-content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                yield item
            else:
                yield item
       
       