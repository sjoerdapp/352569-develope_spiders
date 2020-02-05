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
#from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### J.M. Smucker Company 2|2
### 2nd spider Brand Releases
### normal get 
### back to 20130905


class QuotessSpider(scrapy.Spider):
    name = 'JM_Smucker_II_2162900ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/JM_Smucker_II_2162900ARV002/',
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
    start_urls = ['https://www.jmsmucker.com']

    def parse(self, response):  # follow drop down menue for different years
         years = list(range(2014, 2020)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://www.jmsmucker.com/company-news/brand-news-releases?Search=&Year={}'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div[@class="releases"]/div[@class="release"]')
          for aux in auxs:
              #item = SwisscomIvCrawlerItem()
              #item['PUBSTRING'] = aux.xpath('.//p[not(@class="title")]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              #item['HEADLINE']= aux.xpath('.//p[@class="title"]/a[@id="regularLink"]/text()').extract_first()
              #item['DOCLINK']= aux.xpath('.//p[@class="title"]/a[@id="regularLink"]/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.jmsmucker.com'
              aux_url = aux.xpath('.//p[@class="title"]/a[@id="regularLink"]/@href').extract_first()
              
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
        #item = response.meta['item']
        name_regex = r'yyyyyyyyy'#(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*MSCI\b)(.|\s)*|(\bABOUT.MSCI\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item = {
               'DESCRIPTION':  re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="content"]//text()[not(ancestor::h4)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)}
        yield item
        #item['DOCLINK'] = response.url
        #if not re.search('[a-zA-Z]', item['DESCRIPTION']):
        #    item['DESCRIPTION'] = 'FEHLER'
        #    yield item
        #else:
        #    yield item
       
       