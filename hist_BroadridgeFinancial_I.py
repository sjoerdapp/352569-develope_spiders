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


### Broadridge Financial Solutions 1|2
### IR Press Releases, 2nd spider Press Releases Media Center
### normal get going from page to page by using the form data from the actual response 
### back to 20070116


class QuotessSpider(scrapy.Spider):
    name = 'BroadridgeFinancial_I_5196200ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/BroadridgeFinancial_I_5196200ARV001/',
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
    #start_urls = ['https://searchg2.crownpeak.net/broadridge_us_en_rt_live/select?q=*&echoParams=explicit&defType=edismax&wt=json&fl=*,score&start={}&rows=100&&fq=custom_s_template:article&fq=custom_s_tag_article:press-release&fq=-custom_s_exclude_insight:true&fq=custom_s_current_region:us&&sort=custom_dt_page_date+desc&hl=true&hl.fl=*&hl.snippets=3&hl.simple.pre=%3Cb%3E&hl.simple.post=%3C/b%3E&f.title.hl.fragsize=50000&f.url.hl.fragsize=50000&&json.wrf=searchg2_6960455984057388']

    def start_requests(self):
        yield scrapy.Request(
            'http://otp.investis.com/clients/us/broadridge/usn/usnews.aspx',
        )

    def parse(self, response):
        auxs = response.xpath('//div[contains(@class, "RowStyle")]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./div[@class="date"]/span/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux.xpath('./div[@class="title"]/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('./div[@class="title"]/a/@href').extract_first()
            #item['PUBSTRING'] = aux.xpath('./div[@class="title"]/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
            #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
            #        }
            base_url = 'http://otp.investis.com/clients/us/broadridge/usn/'
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
                  url= response.urljoin(aux_url)
                  request = scrapy.Request(url=url, meta={'dont_proxy': True,}, callback=self.parse_details)
                  request.meta['item'] = item
                  yield request
        


        yield FormRequest.from_response(
            response, formname='form1',
            formdata={
                # ctl01.x/y indicates the "next page" button, ctl00.x/y is previous page
                'USNewsView$dpNextPrevLink$ctl01$ctl01.x': '17',
                'USNewsView$dpNextPrevLink$ctl01$ctl01.y': '15',
            },
        )
#
    
               
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Broadridge)(.|\s)*|(\bAbout.Broadridge\b)(.|\s)*|(\bABOUT.BROADRIDGE\b)(.|\s)*|(\bABOUT\s*BROADRIDGE\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@id="divBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@id="divBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                    yield item
                else:
                    yield item
            else:
                yield item
       
       