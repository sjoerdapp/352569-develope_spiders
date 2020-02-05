# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
import scrapy.http
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
from scrapy.http import FormRequest

### Arist Networks Inc. 2|2
### 2nd Company Press Releases
### classic post next page comes with get, follow pagination link
### back to 20071105


class QuotessSpider(scrapy.Spider):
    name = 'AristaNetworks_II_9900264ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/AristaNetworks_II_9900264ARV002/',
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
    #start_urls = ['https://www.tsys.com/news-innovation/press-media/press-releases']
    def start_requests(self):
        yield scrapy.http.Request('https://www.arista.com/en/company/news/press-release')

    def parse(self, response):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.arista.com',
            'Referer': 'https://www.arista.com/en/company/news/press-release',
            #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
            #'perc-version': '5.3.15',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            #'X-Requested-With': 'XMLHttpRequest',
           }
        
        #cookies = {'ASP.NET_SessionId': 'qiwxj0b2ksp4lece40ngprh4',
        #            '_ga': 'A1.2.890213369.1563141441',
        #            'cookieconsent_status': 'dismiss',
        #            '_gid': 'GA1.2.672569217.1563273511',
        #            }

        data = {'yearSelected': '2014',
                } 

        for num in range(2012, 2013):  # loop iterating over different pages of ajax request
            data['yearSelected'] = str(num)
            s_url = 'https://www.arista.com/en/company/news/press-release'
            yield scrapy.http.FormRequest(url=s_url, formdata=data, headers=headers, meta={'dont_proxy': True,}, callback=self.parse_next )
              


    def parse_next(self, response):
        #body = json.loads(response.text)
        auxs = response.xpath('//div[@class="item"]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            #item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "date")]/div/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux.xpath('.//h2/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//h2/a/@href').extract_first()
            item['PUBSTRING'] = item['DOCLINK'].split('pr-')[1]
            #item = {
            #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
            #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
            #        }
            base_url = 'https://www.arista.com'
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
                  request = scrapy.Request(url=url, meta={'dont_proxy': True,}, callback=self.parse_details)
                  request.meta['item'] = item
                  yield request
                  
              
              else:
                  url= base_url + aux_url
                  request = scrapy.Request(url=url, meta={'dont_proxy': True,}, callback=self.parse_details)
                  request.meta['item'] = item
                  yield request

        next_page_url = response.xpath('//div[@class="pagination"]/ul/li/a[@title="Next"]/@href').extract_first()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, meta={'dont_proxy': True,}, callback=self.parse_next)
               
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Arista)(.|\s)*|(\bAbout.Arista\b)(.|\s)*|(\bABOUT.ARISTA\b)(.|\s)*|(\bABOUT\s*.ARISTA\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="item-page"]//text()[not(ancestor::h2[@class="pageTitle"])][not(ancestor::h1 or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       