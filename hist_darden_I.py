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

### Darden Restaurants Inc. 1|1
### 1st spider Investor Press Releases
### normal get 
### back to 20000104


class QuotessSpider(scrapy.Spider):
    name = 'Darden_I_3088600ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Darden_I_3088600ARV001/',
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
    start_urls = ['https://investor.darden.com/investors/press-releases/default.aspx']

    def parse(self, response):  # follow drop down menue for different years
         years = list(range(2000, 2020)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://investor.darden.com/investors/press-releases/{}/default.aspx'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div [@class="ModuleContainerInner"]/div[contains(@class, "ModuleItem")]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./span[@class="ModuleDate"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//span[@class="ModuleHeadline"]/text()').extract_first()
              item['DOCLINK']= aux.xpath('./a[@class="ModuleHeadlineLink"]/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://investor.darden.com'
              aux_url = aux.xpath('./a[@class="ModuleHeadlineLink"]/@href').extract_first()
              
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
        name_regex = r'(Darden\s*is\s*a\s*restaurant\s*company\s*featuring\s*a\s*portfolio\s*of)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Darden\s*Restaurants.\s*Inc.\s*.\s*\(NYSE\s*:\s*DRI\s*\).\s*owns\s*and\s*operates)(.|\s)*|(\bABOUT\s*Darden\s*Restaurants\b)(.|\s)*|(\bABOUT.Darden.Restaurants\b)(.|\s)*|(\bABOUT\s*Darden(.|\s*)Darden\s*Restaurants\b)(.|\s)*|(\bABOUT.Darden(.|\s*)Darden.Restaurants\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not item['DESCRIPTION']:
              item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="ModuleBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
              if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                  item['DESCRIPTION'] = 'FEHLER'
                  yield item
              else:
                  yield item
            else:
              yield item
       
       