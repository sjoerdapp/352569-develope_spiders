# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import scrapy.http
import re
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### actual year, if more than 20 news break

### Tiffany & Co. 2|2
### second spider News
### post with huge payload, content comes in xpath 
### back to 20080301


class QuotessSpider(scrapy.Spider):
    name = 'Tiffany_II_2175300ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Tiffany_II_2175300ARV002/',
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

    start_urls = [
        'http://press.tiffany.com/News/News.aspx',
    ]

    def parse(self, response):

        data={
                '__EVENTTARGET': 'lstYear',
                'lstYear': '2015',
            }
        

        for num in range(2019,2021):  # loop iterating over different pages of ajax request
            data['lstYear'] = str(num)
            yield scrapy.http.FormRequest.from_response(
            response,
            formname='frmNewsSummary',
            formdata=data,
            callback=self.parse_next,)
              


    def parse_next(self, response):
          auxs = response.xpath('//div[@class="newsItem"]')
          if len(auxs) > 20:
            auxs = auxs[0:20]

          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//span[contains(@id, "PostedDate")]/text()').extract_first().split('(')[1].split(')')[0] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//span[contains(@id, "lblTitle")]/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//span[@class="readMoreLink"]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'http://press.tiffany.com/News/'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Tiffany\s*&\s*Co.\s*operates\s*jewelry\s*stores\s*and\s*manufactures\s*products)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Tiffany)(.|\s)*|(\bAbout.Tiffany\b)(.|\s)*|(\bABOUT.Tiffany\b)(.|\s)*|(\bABOUT\s*.TIFFANY\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@id="newsCopy"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       