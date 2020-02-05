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

### ACHTUNG!!!
### Links DO NOT WORK

### Viacom Inc 2|2
### 2nd spider Media Center
### normal get ....Links DO NOT WORK
### back to 20101005


class QuotessSpider(scrapy.Spider):
    name = 'Viacom-CBS_corp_IV_2186600ARV004'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Viacom-CBS_corp_IV_2186600ARV004/',
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
    #start_urls = ['https://www.viacom.com']

    def start_requests(self,):  # follow drop down menue for different years
         years = list(range(0, 1, 15)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://www.viacbs.com/api/page/media-center.json?limit=15&offset=0'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          body = json.loads(response.body.decode('utf-8'))
          
          #auxs = response.xpath('//ul[@class="content-wrapper"]/li[contains(@class, "item")]')
          for aux in body['data']['blocks'][1]['data']['blocks'][0]['data']['articles'][0:3]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['datetime'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['title']
              item['DOCLINK']= aux['target']
              #item['PUBSTRING'] = aux.xpath('./a//p[@class="copy-02"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              #item['HEADLINE']= aux.xpath('./a//h2/text()').extract_first()
              #item['DOCLINK']= aux.xpath('./a/@href').extract_first()
              ##item = {//div [@class="buttons"]/a[1]/@href
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.viacbs.com/api/page'
              aux_url = item['DOCLINK']
              
              if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
                if aux_url.startswith('http'):
                    url= aux_url+'.json'
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
                    url= aux_url +'.json'
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
                    
                
                else:
                    url= base_url + aux_url +'.json'
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
               
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Cautionary\s*Statement\s*Concerning\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*Viacom (?!\'s))(.|\s)*|(\bABOUT.Viacom (?!\'s))(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        name_regexx = r'(\bAbout\s*ViacomCBS\b)(.|\s)*|(\bAbout.ViacomCBS\b)(.|\s)*|(\bAbout.Viacom\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            body = json.loads(response.body.decode('utf-8'))
            text = body['data']['blocks'][1]['data']['contents'][0]['data']['copy']
            text_I = re.sub(name_regex,'' ," ".join(Selector(text=text).xpath('//p/text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regexx,'' ,text_I)
            item['DOCLINK'] = response.url
            pdf_link = response.xpath('//div[@class="box__right"]//a[contains(text(), "Earnings")]/@href').extract_first()
            if pdf_link:
              item['file_urls'] = [pdf_link]
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       