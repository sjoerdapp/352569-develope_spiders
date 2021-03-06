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

### A.O. Smith Corporation 2|2
### 2nd spider Current News
### normal get 
### back to 20110110


class QuotessSpider(scrapy.Spider):
    name = 'AoSmith_II_2162500ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/AoSmith_II_2162500ARV002/',
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
    start_urls = ['https://www.aosmith.com/News/',
                  'https://www.aosmith.com/News/2018-News-Archive/',
                  'https://www.aosmith.com/News/2017-News-Archive/',
                  'https://www.aosmith.com/News/2016-News-Archive/',
                  'https://www.aosmith.com/News/2015-News-Archive/',
                  'https://www.aosmith.com/News/2014-News-Archive/',
                  'https://www.aosmith.com/News/2013-News-Archive/',
                  'https://www.aosmith.com/News/2012-News-Archive/',
                  'https://www.aosmith.com/News/2011-News-Archive/',]

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 5)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'http://investor.aosmith.com/press-releases?bf2209de_items_per_page=50&bf2209de_year%5Bvalue%5D=_none&op=Filter&bf2209de_widget_id=bf2209de&form_build_id=form-FCDzpghoqyKI2S3w2Dpl8jYIrpP5Dd6VBY6v0znkDng&form_id=widget_form_base&page={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          auxs = response.xpath('//div[@class="newsItem"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[@class="date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//h3/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//h3/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.aosmith.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(A.\s*O.\s*Smith\s*Corporation.\s*with\s*headquarters\s*in\s*Milwaukee.\s*Wis..\s*is\s*a\s*leading)(.|\s)*|(Certain\s*statements\s*contained\s*in\s*this\s*release\s*are\s*Forward(.|\s*)Looking\s*in\s*nature)(.|\s)*'
        name_regex_2=r'(\bAbout\s*A.\s*O.\b)(.|\s)*|(\bAbout.A.\s*O\b)(.|\s)*|(\bABOUT\s*A.\s*O.\s*Smith\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="article RTF"]//text()[not(ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url  
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       