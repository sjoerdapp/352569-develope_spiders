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

### PulteGroup Inc 1|1
### 1st spider Investor NEWS RELEASES
### get with standard json, all news in one page
### back to 20080116


class QuotessSpider(scrapy.Spider):
    name = 'PulteGroup_I_2134900ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/PulteGroup_I_2134900ARV001/',
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
    start_urls = ['http://www.pultegroupinc.com/feed/PressRelease.svc/GetPressReleaseList?apiKey=BF185719B0464B3CB809D23926182246&bodyType=0&pressReleaseDateFilter=3&categoryId=00000000-0000-0000-0000-000000000000&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1']

    #def start_requests(self):
    #    headers = {
    #        'Accept': 'application/json, text/javascript, */*; q=0.01',
    #        'Accept-Encoding': 'gzip, deflate, br',
    #        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    #        'Connection': 'keep-alive',
    #        #'Content-Length': '316',
    #        'Content-Type': 'application/json; charset=UTF-8',
    #        'Cookie': 'ServerID=1025',
    #         #'Host': 'investor.twitterinc.com',
    #        'Origin': 'https://www.cmsenergy.com',
    #        'Referer': 'https://www.cmsenergy.com/investor-relations/news-releases/default.aspx',
    #        #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
    #        #'perc-version': '5.3.15',
    #        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    #        'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
    #        'X-Requested-With': 'XMLHttpRequest',
    #       }
#
#    #    data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","StartIndex":0,"Signature":"","TagList":[]},"pressReleaseBodyType":3,"pressReleaseSelection":3,"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","year":2019}
#    #    for year in list(range(2009, 2020)):  # loop iterating over different pages of ajax request
#    #        data["year"] = year
#    #        s_url = 'https://www.cmsenergy.com/Services/PressReleaseService.svc/GetPressReleaseList'
    #        yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse) 

      


    def parse(self, response):
          body = json.loads(response.text)
          for dat in body['GetPressReleaseListResult']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['PressReleaseDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['Headline']
              item['DOCLINK']= dat['LinkToDetailPage'] 
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'http://www.pultegroupinc.com'
              aux_url = item['DOCLINK']
              
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Certain\s*statements\s*contained\s*in\s*this\s*release\s*are\s*Forward(.|\s*)Looking\s*in\s*nature)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Pulte)(.|\s)*|(\bAbout.Pulte)(.|\s)*|(\bABOUT.PULTE)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="module_body clearfix"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       