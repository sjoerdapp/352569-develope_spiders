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

### UPDATES
### first 5 pages, latest 10 news

### Wabtec Corp 2|2
### 2nd spider Newsroom
### post, html comes in json
### back to 20180117


class QuotessSpider(scrapy.Spider):
    name = 'Wabtec_II_3091300ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Wabtec_II_3091300ARV002/',
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
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.wabteccorp.com',
            'Referer': 'https://www.wabteccorp.com/newsroom/press-release',
            #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
            #'perc-version': '5.3.15',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }
        
        cookies = {'s_cc': 'true',
                   '_ga': 'GA1.2.2111307417.1575496443',
                   '_gid': 'GA1.2.685756091.1575496443',
                   '_evidon_consent_cookie': '{"consent_date":"2019-12-04T21:55:16.982Z"}',
                   's_sq': '%5B%5BB%5D%5D',
                   '_gat_UA-132669767-1': '1'}

        data = {'view_name': 'press_release',
                'view_display_id': 'pressrelease',
                'view_args': '',
                'view_path': '%2Fnewsroom%2Fpress-release',
                'view_base_path': 'newsroom%2Fpress-release',
                'view_dom_id': 'c80061aec3d0e7883f4af034855faf7b43c36b209ef8cf7cc6ce50aab510b98b',
                'pager_element': '0',
                'field_press_month_value': 'All',
                'field_press_year_value': 'All',
                'sort_by': 'field_press_published_on_value',
                'sort_order': 'DESC',
                'page': '1',
                '_drupal_ajax': '1',
                'ajax_page_state%5Btheme%5D': 'wabtec',
                'ajax_page_state%5Btheme_token%5D': '',
                'ajax_page_state%5Blibraries%5D': 'better_exposed_filters%2Fauto_submit%2Cbetter_exposed_filters%2Fgeneral%2Ccore%2Fhtml5shiv%2Csimple_popup_blocks%2Fsimple_popup_blocks%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module%2Cwabtec%2Fglobal-styling'}
       
        for num in range(0,5):  # loop iterating over different pages of ajax request
            data['page'] = str(num)
            s_url = 'https://www.wabteccorp.com/views/ajax?field_press_month_value=All&field_press_year_value=All&sort_order=DESC&sort_by=field_press_published_on_value&_wrapper_format=drupal_ajax'
            yield FormRequest(url=s_url, formdata=data, headers=headers, cookies=cookies, callback=self.parse )
              


    def parse(self, response):
          body = json.loads(response.text)
          auxs = Selector(text=body[4]['data']).xpath('//ul[@class="result-list"]/li')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//span[@class="release-date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//h4/a[2]/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//h4/a[2]/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.wabteccorp.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Wabtec\s*Corporation\s*(\(\s*www.wabtec.com\s*\)\s*)?is\s*a\s*global\s*provider\s*of)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        name_regex_2= r'(\bAbout\s*Wabtec\b)(.|\s)*|(\bAbout.Wabtec\b)(.|\s)*|(\bAbout. Wabtec\b)(.|\s)*|(\bABOUT\s*WABTECT\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="press-rel-content"]//text()[not(ancestor::h1 or ancestor::h2 or ancestor::div[@class="PRN_ImbeddedAssetReference"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       