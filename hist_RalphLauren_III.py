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

### Ralph Lauren Corporation 3|3
### 1st spider Investor Press Releases with long history dead since mid 2019, 2nd spider News Room, 3rd spider IR Press Releases actual page
### normal get all news in one page
### back to 20141016


class QuotessSpider(scrapy.Spider):
    name = 'RalphLauren_III_3200900ARV003'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/RalphLauren_III_3200900ARV003/',
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
    start_urls = ['http://investor.ralphlauren.com/news-releases?ab7b0a08_year%5Bvalue%5D=_none&ab7b0a08_widget_id=ab7b0a08&form_build_id=form--Q5Tdvn8atsQ-sW6g-sGmbKdxfdUP6PfHRxKZZxw300&form_id=widget_form_base']

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 151)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'http://invest.grainger.com/phoenix.zhtml?c=76754&p=irol-news&nyo={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          auxs = response.xpath('//table[@class="nirtable"]//tr[not(ancestor::thead)]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "date-time")]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[contains(@class, "headline")]/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div[contains(@class, "headline")]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'http://investor.ralphlauren.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|((Polo\s*)?Ralph\s*Lauren\s*Corporation\s*(\(\s*NYSE\s*:\s*RL\s*\)\s*)?is\s*a\s*(global\s*)?leader\s*in\s*the\s*design)(.|\s)*|(Certain\s*statements\s*contained\s*in\s*this\s*release\s*are\s*Forward(.|\s*)Looking\s*in\s*nature)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Ralph\b)(.|\s)*|(\bAbout.Ralph\b)(.|\s)*|(\bABOUT.RALPH\b)(.|\s)*|(\bAbout\s*Polo\b)(.|\s)*|(\bAbout.Polo\b)(.|\s)*|(\bABOUT.POLO\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
              item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="article-text"]//text()[not(ancestor::div[@class="middle-column"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
              item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
              if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                  item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[@class="middle-column"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                  item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
                  if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                      item['DESCRIPTION'] = 'FEHLER'
                      yield item
              else:
                  yield item
            else:
              yield item
       
       