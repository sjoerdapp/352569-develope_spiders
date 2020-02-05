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

### Hormel Foods Corporation 4|4
### 4th spider Press Releases Responsibility
### 1st page comes with get and html other pagers come with get and json, 
### back to 20080123



class QuotessSpider(scrapy.Spider):
    name = 'Hormel_Foo_IV_2093200ARV004'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Hormel_Foo_IV_2093200ARV004/',
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
    start_urls = ['https://www.hormelfoods.com/newsroom/press-releases/category/responsibility/']

    def parse(self, response):  # follow drop down menue for different years
          auxs = response.xpath('//div[contains(@class,"c-feature c-feature")]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = '' #aux.xpath('./div[contains(@class, "prDateCol")]//div[@class="irwPRDate"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[@class="c-feature-label__title c-feature-label__title--divider"]/text()').extract_first()
              item['DOCLINK']= aux.xpath('./a/@href').extract_first()

              base_url = 'https://www.hormelfoods.com'
              aux_url = aux.xpath('./a/@href').extract_first()

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
               
          ### second part of start page     
          auxss = response.xpath('//div[@class="c-card "]')
          for aux in auxss:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./div[contains(@class, "prDateCol")]//div[@class="irwPRDate"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//a[@class="c-card__title"]/text()[1] | .//a[@class="c-card__title"]/text()[2]').extract_first()
              item['DOCLINK']= aux.xpath('.//a[@class="c-card__title"]/@href').extract_first()

              base_url = 'https://www.hormelfoods.com'
              auxx_url = aux.xpath('.//a[@class="c-card__title"]/@href').extract_first()

              if '.pdf' in auxx_url.lower() or 'static-files' in auxx_url.lower():
                if aux_url.startswith('http'):
                    url= auxx_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    item['DESCRIPTION'] = ''
                    yield item
                
                else:
                    url= base_url + auxx_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    item['DESCRIPTION'] = ''
                    yield item
              else:
                if auxx_url.startswith('http'):
                    url= auxx_url
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
                    
                
                else:
                    url= base_url + auxx_url
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request



          years = list(range(2, 15)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
          #del years[0]  # delets first element "NULL" from list of years
          for year in years:
              aux_url = 'https://www.hormelfoods.com/wp-json/wp/v2/posts?orderby=date&order=desc&per_page=20&exclude=28345%2C28282%2C28176&categories=30&news_type=14&content=1&page={}'
              year_url = [aux_url.format(year)][0]
              yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          body = json.loads(response.body.decode('utf-8'))
          for aux in body:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['date']
              item['HEADLINE']= aux['title']['rendered']
              item['DOCLINK']= aux['link']
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.hormelfoods.com'
              aux_url = aux['link']
              
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
        if not  item['PUBSTRING']:
          item['PUBSTRING'] = response.xpath('//time[@class="c-article-header__date"]/text()').extract_first()


        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT.Hormel.Foods)(.|\s)*|(\bABOUT\s*Hormel\s*Foods)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="content-module__rich-text"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       