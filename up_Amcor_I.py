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
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### news starting from 2019-06
### make new in 2020

### Amcor Plc 1|2
### 1st spider Amcor Press releases, 2nd spider Bevis archive bevor merger
### normal get with json 
### back to 20070907


class QuotessSpider(scrapy.Spider):
    name = 'Amcor_I_9900372ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Amcor_I_9900372ARV001/',
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
    start_urls = ['https://cdn.contentful.com/spaces/f7tuyt85vtoa/environments/master/entries?access_token=8daaec5877c555c8711652031de344e597e4dd947a32cce59d664600b5f601af&include=5&content_type=newsPage&limit=400',
                  'https://cdn.contentful.com/spaces/f7tuyt85vtoa/environments/master/entries?access_token=8daaec5877c555c8711652031de344e597e4dd947a32cce59d664600b5f601af&include=5&content_type=oldNews&limit=400',
                  'https://cdn.contentful.com/spaces/f7tuyt85vtoa/environments/master/entries?access_token=8daaec5877c555c8711652031de344e597e4dd947a32cce59d664600b5f601af&include=3&content_type=blogPage&order=-fields.date&limit=400',
                  ]

    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(0, 80, 3)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.mccormickcorporation.com/api/sitecore/CORP18_generated_listing_with_filter?num_items=3&current_count={}&rootGuid=d0952d7d-aeea-4538-8c3f-0ad5cf3a95b7&templateGuids=02c1d0aa-0111-44a3-a3f0-5215df2d176f,9bdac2ca-5678-4cd7-84d8-21f5189f153a&category=All'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          body = json.loads(response.body.decode('utf-8'))
          for aux in body['items']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['fields']['date'] # cuts out the part berfore the date as well as the /n at the end of the string
              if re.search(r'2020-01|2020-02|2020-03|2020-04', item['PUBSTRING']):
                item['HEADLINE']= aux['fields']['title']
                item['DOCLINK']= aux['fields']['slug']
                if 'T' in item['PUBSTRING']:
                  item['PUBSTRING'] = aux['fields']['date'].split('T')[0]

                #item = {
                #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
                #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
                #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
                #        }
                base_url = response.url + '&fields.slug='
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Amcor\s*PET\s*Packaging\s*is\s*the\s*leading\s*manufacturer\s*of\s*PET)(.|\s)*'
        name_regex_2=r'(About\s*Amcor)(.|\s)*|(\bAbout.Amcor\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            body = json.loads(response.body.decode('utf-8'))
            try:
              def getByKeyName(inputVariable, searchKey):
                  foundItems = []
              
                  if isinstance(inputVariable, dict):
                      for currentKey, currentVar in inputVariable.items():
                          if currentKey == searchKey:
                              foundItems = foundItems + [currentVar]
                          else:
                              foundItems = foundItems + getByKeyName(currentVar, searchKey)
                  if isinstance(inputVariable, list):
                      for currentVar in inputVariable:
                          foundItems = foundItems + getByKeyName(currentVar, searchKey)
                                
                  return foundItems

              item['DESCRIPTION'] = ''.join(getByKeyName(body, "summary")) + ''.join(getByKeyName(body, "content"))
              item['DESCRIPTION'] = re.sub(name_regex,'' , item['DESCRIPTION'], flags=re.IGNORECASE)
              item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
              #if 'content' in body['items'][0]['fields'].keys():
              #  item['DESCRIPTION'] = body['items'][0]['fields']['content']
              #else:
              #  item['DESCRIPTION'] = body['includes']['Entry'][0]['fields']['content']
            except:
              item['DESCRIPTION'] = 'fürn Arsch'
            #re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="sc-gqjmRU iYDdZl"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            try:
              if len(body['includes']['Asset'])>1:
                pdf_link = body['includes']['Asset'][1]['fields']['file']['url']
                if pdf_link and '.pdf' in pdf_link:
                  if 'htpps' in pdf_link:
                    item['file_urls'] = [pdf_link]  
                  else:
                    item['file_urls'] = ["https:"+pdf_link]
                else: 
                  pdf_link = body['includes']['Asset'][0]['fields']['file']['url']
                  if pdf_link and '.pdf' in pdf_link:
                    if 'htpps' in pdf_link:
                      item['file_urls'] = [pdf_link]  
                    else:
                      item['file_urls'] = ["https:"+ pdf_link]
                      
            except KeyError:
              text = "yield item"
              #item['file_urls']=''
            
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "node__content")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item
            else:
                yield item
       
       