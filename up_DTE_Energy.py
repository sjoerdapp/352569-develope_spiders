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
### 100 news per page, get first 20

### Achtung spider wurde angepasst, News inkl. Description kommen in json mit initial response
### Momentan keine weiterleitung auf eine Detailpage nötig. 

### DTE Energy Company 1|1
### 1st spider Newsroom
### normal get 
### back to 20070110


class QuotessSpider(scrapy.Spider):
    name = 'DTE_Energy_2057400ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/DTE_Energy_2057400ARV001/',
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
    start_urls = ['https://skrift-2-bff.meltwater.io/livecontent/5e12ac481b7bea03e16a9079']

    #def start_requests(self):  # follow drop down menue for different years
    #     years = list(range(0, 100, 100)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'http://newsroom.dteenergy.com/index.php?s=26817&_ga=2.50592297.1073990813.1575475544-875611992.1575475544&l=100&o={}#sthash.ha8jLLq2.dpbs'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse(self, response):
          auxs = json.loads(response.text)['response']
          
          for dat in auxs[0:10]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['date'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['title']
              item['DOCLINK']= response.url

              raw_text = " ".join(Selector(text=dat['main_Body']).xpath('//p//text()').extract())

              name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(DTE\s*Energy\s*(\(\s*NYSE\s*:\s*DTE\s*\)\s*)?is\s*a\s*Detroit\s*.based\s*diversified\s*energy\s*company)(.|\s)*'
              name_regex_2=r'(\bAbout\s*DTE\s*Energy)(.|\s)*|(\bAbout.DTE.Energy\b)(.|\s)*|(\bABOUT.DTE.Energy\b)(.|\s)*|(\bABOUT\s*DTE\s*Energy\b)(.|\s)*'
              item['DESCRIPTION'] = re.sub(name_regex,'' ,raw_text)
              item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])

              yield item






              #base_url = 'http://newsroom.dteenergy.com'
              #aux_url = item['DOCLINK']
              #
              #if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
              #  if aux_url.startswith('http'):
              #      url= aux_url
              #      item['file_urls'] = [url]
              #      item['DOCLINK'] = url
              #      item['DESCRIPTION'] = ''
              #      yield item
              #  
              #  else:
              #      url= base_url + aux_url
              #      item['file_urls'] = [url]
              #      item['DOCLINK'] = url
              #      item['DESCRIPTION'] = ''
              #      yield item
              #else:
              #  if aux_url.startswith('http'):
              #      url= aux_url
              #      request = scrapy.Request(url=url, callback=self.parse_details)
              #      request.meta['item'] = item
              #      yield request
              #      
              #  
              #  else:
              #      url= base_url + aux_url
              #      request = scrapy.Request(url=url, callback=self.parse_details)
              #      request.meta['item'] = item
              #      yield request
               
        
    #def parse_details(self, response):
    #    item = response.meta['item']
    #    name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(DTE\s*Energy\s*(\(\s*NYSE\s*:\s*DTE\s*\)\s*)?is\s*a\s*Detroit\s*.based\s*diversified\s*energy\s*company)(.|\s)*'
    #    name_regex_2=r'(\bAbout\s*DTE\s*Energy)(.|\s)*|(\bAbout.DTE.Energy\b)(.|\s)*|(\bABOUT.DTE.Energy\b)(.|\s)*|(\bABOUT\s*DTE\s*Energy\b)(.|\s)*'
    #    if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
    #        item['file_urls'] = [response.url]
    #        item['DOCLINK'] = response.url
    #        item['DESCRIPTION'] = ''
    #        yield item
    #    else:
    #        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "wd_subtitle")]//text() | //div[contains(@class, "wd_body")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
    #        item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
    #        item['DOCLINK'] = response.url
    #        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
    #            item['DESCRIPTION'] = 'FEHLER'
    #            yield item
    #        else:
    #            yield item
       
       