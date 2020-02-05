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
### actual year, if more than 20 news break

### Qorvo Inc. 2|2
### 2nd spider Newsroom 
### normal get with query string. Each yer special yearkey 
### just put all urls in start_urls
### back to 20150102


class QuotessSpider(scrapy.Spider):
    name = 'Qorvo_II_1550600ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Qorvo_II_1550600ARV002/',
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
    start_urls = ['https://www.qorvo.com/newsroom/news',
                  'https://www.qorvo.com/QorvoPublic/Press/NewsListingResult?selectedYear=ad910d31-c8db-4be3-b3d6-828839672ed3&selectedType=all&pageId=91cb4708-73a2-4191-b4ed-297fd2da04a2&_=1578916593848',
                  ]

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 1)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://ir.qorvo.com/press-releases?items_per_page=50&page={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          auxs = response.xpath('//table//tr[not(ancestor::thead)]')
          
          if len(auxs) > 10:
            auxs = auxs[0:10]

          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./td[1]/text()').extract_first().split(u'\xa0')[0] # \xa0 is a non breaking space in unicode which has to be cut out
              item['HEADLINE']= aux.xpath('./td/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('./td/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.qorvo.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Certain\s*of\s*the\s*statements\s*in\s*the\s*immediately\s*preceding\s*paragraphs)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Qorvo)(.|\s)*|(\bAbout.Qorvo\b)(.|\s)*|(\bABOUT.QORVO\b)(.|\s)*|(\bABOUT\s*QORVO\b)(.|\s)*|(\bAbout\s*TriQuint)(.|\s)*|(\bAbout.TriQuint\b)(.|\s)*|(\bABOUT.TRIQUINT\b)(.|\s)*|(\bABOUT\s*TRIQUINT\b)(.|\s)*|(\bAbout\s*RFMD)(.|\s)*|(\bAbout.RFMD\b)(.|\s)*|(\bABOUT.RFMD\b)(.|\s)*|(\bABOUT\s*RFMD\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="container u-section-container rich-text"]//text()[not(ancestor::div[@class="nesTitle"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       