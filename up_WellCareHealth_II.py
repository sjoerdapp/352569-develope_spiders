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
### actual year, if more than 20 news break

### WellCare Health Plans Inc. 2|2
### 2nd spider News and Press
### Classic get, data comes in json 
### content of Detail page comes with first json as well
### back to 20040516


class QuotessSpider(scrapy.Spider):
    name = 'WellCareHealth_II_4539400ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/WellCareHealth_II_4539400ARV002/',
         'CRAWLERA_ENABLED': False,
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
    #start_urls = ['https://www.mccormickcorporation.com/en/news-center']

    def start_requests(self):  # follow drop down menue for different years
         years = list(range(2019, 2021)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://www.wellcare.com/api/News/getNews/{}'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          body = json.loads(response.body.decode('utf-8'))
          auxs = body
          if len(auxs) > 20:
            auxs = auxs[0:20]

          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux['DLU'].split('T')[0] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux['Title']
              item['DOCLINK']= 'https://www.wellcare.com/en/Corporate/NewsDetail/?newsid=' + aux['ReleaseID']
              body = aux['ReleaseText']
              name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
              name_regex_2=r'(\bAbout\s*WellCare)(.|\s)*|(\bAbout.WellCare\b)(.|\s)*|(\bABOUT.WellCare\b)(.|\s)*|(\bABOUT\s*.WELLCARE\b)(.|\s)*'
              #Selector(text=body).xpath('//span/text()').get()
              item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(Selector(text=body).xpath('//text()').extract()), flags=re.IGNORECASE)
              item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
              yield item
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              #base_url = 'https://www.mccormickcorporation.com'
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
    #    name_regex = r'xxx'#(This\s*release\scontains\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*MSCI\b)(.|\s)*|(\bABOUT.MSCI\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
    #    #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
    #    if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
    #        item['file_urls'] = [response.url]
    #        item['DOCLINK'] = response.url
    #        item['DESCRIPTION'] = ''
    #        yield item
    #    else:
    #        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//section[contains(@class, "text_module")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
    #        item['DOCLINK'] = response.url
    #        if not item['DESCRIPTION']:
    #            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "node__content")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
    #            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
    #                item['DESCRIPTION'] = 'FEHLER'
    #                yield item
    #            else:
    #                yield item
    #        else:
    #            yield item
       
       