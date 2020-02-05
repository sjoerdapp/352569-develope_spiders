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
from scrapy.http import FormRequest
import scrapy.http
import js2xml

### Eastman Chemical Company 1|1
### 2nd Media Releases
### complex post, content comes in html use special method to get formdata
### back to 20160106


class QuotessSpider(scrapy.Spider):
    name = 'EastmanChemicalComp_3007000ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/EastmanChemicalComp_3007000ARV001/',
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
        yield scrapy.http.Request(
            'https://www.eastman.com/Company/News_Center/Pages/NewsArchiveSearch.aspx', meta={'dont_proxy': True,},
        )

    #meta={'dont_proxy': True,},
    def parse(self, response):
        #yield from self.parse_news_page(response)
        #for page in response.css('#mediaReleasePaging a'):
        #    sel = js2xml.parse(page.root.attrib['href'].split('javascript:')[-1])
        #    target = str(sel.xpath('//arguments/string/text()')[0])
        yield scrapy.http.FormRequest.from_response(
            response,
            formname='aspnetForm',
            formdata={
                #"__EVENTTARGET": target,
                "ctl00$PlaceHolderMain$NewsArchive$cboFromDateMonth": "1",
                "ctl00$PlaceHolderMain$NewsArchive$cboFromDateYear": "2016",
                "ctl00$PlaceHolderMain$NewsArchive$cboToDateMonth": "10",
                "ctl00$PlaceHolderMain$NewsArchive$cboToDateYear": "2019",
                "ctl00$PlaceHolderMain$NewsArchive$cboDisplayPerPage": "ALL",


            },
            meta={'dont_proxy': True,},
            callback=self.parse_news_page,
        )

    def parse_news_page(self, response):
          #body = json.loads(response.text)
          auxs = response.xpath('//a[@class="newsRelease"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./text()').extract_first().split(' - ')[0] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('./text()').extract_first()
              item['DOCLINK']= aux.xpath('./@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.eastman.com'
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
               
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Eastman\s*is\s*a\s*global\s*specialty\s*chemical\s*company\s*that\s*produces\s*a\s*broad)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        name_regex_2 = r'(\bAbout\s*Eastman\b)(.|\s)*|(\bAbout.Eastman\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'#item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//td[@class="main"]//text()[not(ancestor::h1 or ancestor::h2 or ancestor::div[@id="ctl00_PlaceHolderMain_rchPageContent_label"] or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2, '', item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       