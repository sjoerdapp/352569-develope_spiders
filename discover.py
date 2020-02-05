# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Discover Financial Services 1|1
### splash request 
### files pipeline für padf 
### goes back to 20040120

class QuotessSpider(scrapy.Spider):
    name = 'discover_5239600ARV001'
    #http_user = '535209af07354fbbb4110611b27f7504'
    #custom_settings = {
    #    'ROBOTSTXT_OBEY':'False',
    #    'USER_AGENT': "'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
    #    }
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/discover_5239600ARV001/',
    #    'SPLASH_URL': 'http://localhost:8050',
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'scrapy_splash.SplashCookiesMiddleware': 723,
    #         'scrapy_splash.SplashMiddleware': 725,
    #         'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    #     },
    #     'SPIDER_MIDDLEWARES': {
    #         'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    #     },
    #     'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    }
    
    def start_requests(self):
        url = 'https://investorrelations.discover.com/newsroom/press-releases/default.aspx'
        request = SplashRequest(url=url, splash_headers={'Authorization': basic_auth_header('535209af07354fbbb4110611b27f7504', '')}, args={'wait': 0.5}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/201,00101 Firefox/62.0'}, callback=self.parse)
        yield request

        #yield SplashRequest(
        #    url='https://investorrelations.discover.com/newsroom/press-releases/default.aspx',
        #    #splash_headers={'Authorization': basic_auth_header(self.settings['535209af07354fbbb4110611b27f7504'], ''),},
        #    #args={'wait': 0.5},
        #    #headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/201,00101 Firefox/62.0'},
        #    callback=self.parse,
        #)

    def parse(self, response):
         years = response.xpath('//select/option/@value').extract()
         for year in years:
             yield scrapy.Request(url=year, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div[@class="ModuleItemRow ModuleItem"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//span[@class="ModuleDate"]/text()').extract_first()
              item['HEADLINE']= aux.xpath('.//span[@class="ModuleHeadline"]/text()').extract_first()
              item['DOCLINK']= aux.xpath('./a/@href').extract_first()
              #item = {
              #        'Date': aux.xpath('.//span[@class="ModuleDate"]/text()').extract_first(),
              #        'Header': aux.xpath('.//span[@class="ModuleHeadline"]/text()').extract_first(),
              #        'url': aux.xpath('./a/@href').extract_first(),
              #        }
              base_url = 'https://investorrelations.discover.com'
              aux_url = aux.xpath('./a/@href').extract_first()


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
        name_regex = r'xxx'#(\bAbout\s*Discover\b)(.|\s)* | (\bAbout.Discover\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        if not item['DESCRIPTION']:
              item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="ModuleBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        # check if press release is pdf and if yes download pdf
              if not item['DESCRIPTION']:
                    item= SwisscomIvCrawlerItem()
                    ht = 'https:'
                    pdfs = [ht + response.xpath('//div[@class="ModuleLinks"]/a/@href').extract_first()]
                    item['file_urls'] = pdfs # files url has to be in a listobject 
                    item['DESCRIPTION'] = ''
                    yield item
              else:
                yield item
        else:
             yield item
       
       