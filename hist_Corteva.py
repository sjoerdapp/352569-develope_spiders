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

### Corteva Inc 1|1
### 1st spider Media-Center, additional spider evtl Blog ?
### normal get with json 
### back to 


class QuotessSpider(scrapy.Spider):
    name = 'Corteva_9900314ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Corteva_9900314ARV001/',
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
    start_urls = ['https://www.corteva.com/resources/media-center.html']

    def parse(self, response):  # follow drop down menue for different years
        
        auxs = response.xpath('//div[@class="item row"]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = re.search(r'\d+.\d+.\d{4}', aux.xpath('.//span[@class="eyebrow"]/text()').extract_first()).group() # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux.xpath('.//h3/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//h3/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
            #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
            #        }
            base_url = 'https://www.corteva.com'
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


        years = list(range(5, 86, 5)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'https://www.corteva.com/bin/corteva/articleFilter.All.All.All.{}.media-center.json'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          body = json.loads(response.body.decode('utf-8'))
          for aux in body['articlePagesList']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['customDisplayDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['articleTitle']
              item['DOCLINK']= aux['articlePagePath']
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.corteva.com'
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
        name_regex_2= r'(\bAbout\s*Corteva)(.|\s)*|(\bAbout.Corteva\b)(.|\s)*|(\bAbout. Corteva\b)(.|\s)*|(\bABOUT\s*CORTEVA\b)(.|\s)*|(\bABOUT\s*Corteva)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="intro"]//text() | //div[contains(@class, "aem-wrap--rich-text")]//div[@class="band-content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="module_body"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item
            else:
                yield item
       
       