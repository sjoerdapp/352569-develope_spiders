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

### Idex Corp 1|3
### 1st spider Investor Press Releases, 2nd spider News releases, 3rd spider Company News
### normal get 
### back to 20140107


class QuotessSpider(scrapy.Spider):
    name = 'IdexCorp_I_2207500ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/IdexCorp_I_2207500ARV001/',
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
    #start_urls = ['https://investor.kelloggs.com/News']

    def start_requests(self):  # follow drop down menue for different years
         years = list(range(2001, 2021)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://investors.idexcorp.com/news-releases?field_nir_news_date_value%5Bmin%5D={}&items_per_page=50#views-exposed-form-widget-news-table'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//table//tr[not(ancestor::thead)]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//time/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('./td[contains(@class, "title")]/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('./td[contains(@class, "title")]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://investors.idexcorp.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'#|(Wabtec\s*Corporation\s*(\(\s*www.wabtec.com\s*\)\s*)?is\s*a\s*global\s*provider\s*of)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        name_regex_2= r'(\bAbout\s*IDEX\b)(.|\s)*|(\bAbout.IDEX\b)(.|\s)*|(\bAbout. Wabtec\b)(.|\s)*|(\bABOUT\s*IDEX\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       