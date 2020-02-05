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

### UPDATES
### first two pages, latest 20 news

### Jacobs Engineering Group Inc. 2|2
### 2nd spider Newsroom
### classic get with xpath
### back to 20050308


class QuotessSpider(scrapy.Spider):
    name = 'Jacobs_Engineenring_II_2101100ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Jacobs_Engineenring_II_2101100ARV002/',
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
    start_urls = ['https://www.jacobs.com/newsroom']

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 2)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.jacobs.com/newsroom?field_newsroom_target_id=All&tid=All&page={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          auxs = response.xpath('//div [@class="node__content"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = " ".join(aux.xpath('.//div[@class="node__submitted"]/text()').extract()) # cuts out the part berfore the date as well as the /n at the end of the string
              if 'By' in item['PUBSTRING']:
                item['PUBSTRING'] = " ".join(aux.xpath('.//div[@class="node__submitted"]/text()').extract()).split('By')[1]
              item['HEADLINE']= aux.xpath('.//h2/span/text()').extract_first()
              item['DOCLINK']= aux.xpath('./ancestor::a[@class="article-wrap-link"]/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.jacobs.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Jacobs\s*leads\s*the\s*global\s*professional\s*services\s*sector\b)(.|\s)*|(Jacobs\s*is\s*one\s*of\s*the\s*world.s\s*largest\s*and\s*most\s*diverse\s*providers)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Jacobs\b)(.|\s)*|(\bAbout.Jacobs\b)(.|\s)*|(\bABOUT.JACOBS\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "subtitle")]//text() | //div[@class="content-wrap"]//div[contains(@class, "field field-node--body field-name-body field-type-text-with-summary field-label-hidden")]//text()[not(ancestor::div[contains(@class,"ds-layout-right")] or ancestor::div[contains(@class,"ds-layout-slices")])][not(ancestor::div[contains(@class, "node-title")])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            #//div[@class="content-wrap"]//text()
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       