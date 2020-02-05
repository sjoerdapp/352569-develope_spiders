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

### UPDATES
### first two pages, latest 20 news

### CBRE Group Inc 2|2
### 2nd spider Media Center
### normal get with json
### back to 20150108


class QuotessSpider(scrapy.Spider):
    name = 'CBRE_II_4527000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/CBRE_II_4527000ARV002/',
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
    start_urls = ['https://www.cbre.us/about/media-center']

    def parse(self, response):  # follow drop down menue for different years
         years = list(range(1, 3)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url_I = 'https://www.cbre.us/api/searchapi/mediasearch?r=&pg='
             aux_url_II ='&k=&yrs=&cats=&cin={E89A8224-DF83-411A-9AD6-A63B1776F857}&t=&xt=case%20study&pi=617f69b3be70479f981205544476da03&lp=4e73f72b31034db5b899005cc2350fd4&pgSize='
             #https://www.cbre.us/api/searchapi/mediasearch?r=&pg=3&k=&yrs=&cats=&cin={E89A8224-DF83-411A-9AD6-A63B1776F857}&t=&xt=case%20study&pi=617f69b3be70479f981205544476da03&lp=4e73f72b31034db5b899005cc2350fd4&pgSize=
             year_url = aux_url_I + str(year) + aux_url_II
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          body = json.loads(response.text)
          for aux in body['Results']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['PublicationDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['Title']#['CompositeTitle']
              item['DOCLINK']= aux['FullPath']
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.cbre.us'
              aux_url = aux['FullPath']
              
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*CBRE\s*Group\b)(.|\s)*|(\bABOUT.CBRE\s*Group\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="body-content    bottom-double"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            #//div[contains(@class, "main-content")]//div[contains(@class, "body-content")][1]//text()
            item['DOCLINK'] = response.url
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="body-content    bottom-double"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item
            else:
                yield item
       
       