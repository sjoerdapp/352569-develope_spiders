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

### UPDATES
### latest 20 news

### L Brands Inc 2|2
### phoenix page 
### back to 20000601


class QuotessSpider(scrapy.Spider):
    name = 'Lbrands_II_2664000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Lbrands_II_2664000ARV002/',
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
    start_urls = ['http://investors.lb.com/financial-information/press-releases?bb7509dd_year%5Bvalue%5D=_none&op=Filter&bb7509dd_widget_id=bb7509dd&form_build_id=form-YmCm3pIne1JV4BXKKJ9FsATGb0gCLMHUFg8NurRXKz4&form_id=widget_form_base']

    def parse(self, response):
          auxs = response.xpath('//tr[@class="ccbnBgTblOdd"]')[0:20]
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "date-time")]//text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[contains(@class, "headline")]/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div[contains(@class, "headline")]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'http://investors.lb.com/'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*|(\bABOUT\s*LIMITED\s*BRANDS\b)(.|\s)*|(\bABOUT.LIMITED.BRANDS\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       