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
### latest 20 news, all news one page

### People's United Financial Inc. 1|1
### 1st spider Press Room
### normal get
### back to 20160121


class QuotessSpider(scrapy.Spider):
    name = 'PeoplesFinancial_9847000ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/PeoplesFinancial_9847000ARV001/',
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
    start_urls = ['https://www.peoples.com/press']

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 151)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://investor.kelloggs.com/News/4133514/NewsData?pageIndex={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          
          auxxs = response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-4 col-lg-4 util-flex-top util-flex-left pubui-col-control-component-column util-no-padding-mobile pubui-padding-top-10 pubui-padding-right-10 pubui-padding-bottom-10 pubui-padding-left-10"]')
          for auxx in auxxs:#[0:20]
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = auxx.xpath('.//span/span[@class="pubui-rte-dark-color"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= auxx.xpath('.//span[@class="pubui-rte-h5"]/strong/text()').extract_first()
              item['DOCLINK']= auxx.xpath('.//div[@class="button"]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.peoples.com/'
              aux_url = item['DOCLINK']

              if not aux_url:
                continue
              
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
              




          auxs = response.xpath('//div[@class="richtexteditor"]/p')
          for aux in auxs:#[0:20]
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./span[contains(@class, "pubui-rte")][1]/text()[1]').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              if item['PUBSTRING']:
                  if '2019' in item['PUBSTRING'] or '2020' in item['PUBSTRING']:
                      item['HEADLINE']= aux.xpath('.//a//text()').extract_first()
                      item['DOCLINK']= aux.xpath('.//a/@href').extract_first()
                      #item = {
                      #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
                      #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
                      #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
                      #        }
                      base_url = 'https://www.peoples.com/'
                      aux_url = item['DOCLINK']

                      if not aux_url:
                        continue
                      
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
                  else:
                      continue
              else:
                  continue

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Certain\s*statements\s*contained\s*in\s*this\s*release\s*are\s*Forward(.|\s*)Looking\s*in\s*nature)(.|\s)*'
        name_regex_2=r'(\bAbout\s*People.s\s*United\b)(.|\s)*|(\bAbout.People.s.United\b)(.|\s)*' 
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-12 col-lg-7 util-flex-top util-flex-left pubui-col-control-component-column util-no-padding-mobile    "]//div[@class="richtexteditor"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       