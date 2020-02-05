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
from collections import defaultdict

### UPDATES
### actual year, if more than 20 news break
### 

### Citirx Systems Inc 1|3
### first spider investor Relations, 2nd spider Announcements 3rd spider Blog
### normal get request with classic json (GetPressRelease....)
### back to 20020123


class QuotessSpider(scrapy.Spider):
    name = 'Citrix_I_1420100ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Citrix_I_1420100ARV001/',
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
    start_urls = ['https://investors.citrix.com/feed/FinancialReport.svc/GetFinancialReportList?apiKey=BF185719B0464B3CB809D23926182246&reportTypes=First%20Quarter%7CSecond%20Quarter%7CThird%20Quarter%7CFourth%20Quarter&reportSubType%5B%5D=First%20Quarter&reportSubType%5B%5D=Second%20Quarter&reportSubType%5B%5D=Third%20Quarter&reportSubType%5B%5D=Fourth%20Quarter&reportSubTypeList%5B%5D=First%20Quarter&reportSubTypeList%5B%5D=Second%20Quarter&reportSubTypeList%5B%5D=Third%20Quarter&reportSubTypeList%5B%5D=Fourth%20Quarter&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=2019&excludeSelection=1',]

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        data = json.loads(response.text)
        for dat in data['GetFinancialReportListResult']:
            #Ttl_year = dat['']year_div.xpath('./h2/text()').extract_first()
            year = str(dat['ReportYear']) 
            quarter = dat['ReportSubType']
            href = dat['Documents'][1]['DocumentPath']
            self.doc_mapping[year][quarter].setdefault('er', href)
            
        
        #self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))
        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))
        

        years = list(range(2019, 2021)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
             aux_url = 'https://investors.citrix.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&bodyType=0&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year={}&excludeSelection=1'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          body = json.loads(response.text)
          auxs = body['GetPressReleaseListResult']
          if len(auxs) > 20:
            auxs = auxs[0:20]

          for dat in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['PressReleaseDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['Headline']
              item['DOCLINK']= dat['LinkToDetailPage']
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://investors.citrix.com'
              aux_url = dat['LinkToDetailPage']
              
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
        name_regex = r'(This\s*release\scontains\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*citrix (?!\'s))(.|\s)*|(\bABOUT.citrix (?!\'s))(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="module_body"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if re.search(r'Citrix Reports (Second|Third|Fourth) Quarter (and Fiscal Year )?2019 Financial Results', item['HEADLINE']):
            #if re.search(r'Citrix\s*Reports\s*(.*)\s*Financial\s*Results', item['HEADLINE']):
               quarter_regex = r'\b(First)\b \b(Quarter)\b|\b(Second)\b \b(Quarter)\b|\b(Third)\b \b(Quarter)\b|\b(Fourth)\b \b(Quarter)\b'
               quarter= re.search(quarter_regex, item['HEADLINE']).group(0)
               year = re.search(r'\b(20[0-9]{2})\b', item['HEADLINE']).group(0)
               item['file_urls'] = [self.doc_mapping[year][quarter].get('er')] 
            
            #if not item['DESCRIPTION']:
            #    item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "node__content")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            #    else:
            #        yield item
            else:
                yield item
       
       