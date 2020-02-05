# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Arthur J. Gallagher & Co. 2|2
### 2nd spider News and Insights
### calssic post with cookies
### back to 20060720


class QuotessSpider(scrapy.Spider):
    name = 'ArthurGallagher_II_7094000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/ArthurGallagher_II_7094000ARV002/',
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
            'Origin': 'https://www.ajg.com',
            'Referer': 'https://www.ajg.com/us/news-and-insights/',
            'requestverificationtoken': '3fhW-dl3nGnql10HCamKwg-Tkp2jWJ_YFEF2qzFqW1AJpzzMu9BFNM8rblMkVzkEDS0VI8LLhqB8XXwLgrAB-5oomWmgdZ6ZGche6PTm2fk1:4BXCnZq0Kcqr1t3E76RZYgM15eIB-ZBJskuoQEF7gzCnv01ixQPx51T_DkztCWvfm2kKLCaGUGZO-jLQpXorpFckQhEellnH1-V4PYMAQSg1',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
            #'perc-version': '5.3.15',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'x-dtpc': '5$340279830_235h17vCEDNIAAOAGDQLFOBTKFAGJLGMPIANBOJ',
            'X-Requested-With': 'XMLHttpRequest',
           }

        cookies = {'gallagher#lang': 'en',
                   'ASP.NET_SessionId': 'sn14iqxpouirujqsg5baub3p',
                   'rxVisitor': '1578340248511Q03SE96UTRBAQVNSQ4Q7UURD1PR4FLT9',
                   'wscrCookieConsent': '1=true&2=true&3=true&4=true&5=true',
                   'visid_incap_1824001': 'ngEE31mXRNOb53E8c4feVpmPE14AAAAAQUIPAAAAAAB6hltAIAxrtk1yqMj0SxKr',
                   'incap_ses_629_1824001': 'bBzUXxDbLiIKaO0p3qi6CJ2PE14AAAAADk7XaIyc7Fk/n5NKupQNFA==',
                   'sp': 'us',
                   'gallagherus#lang': 'en',
                   'ajgPageEntry': '{%22page%22:%22/us/%22}',
                   'AjgStickyClosed': 'false',
                   '_gcl_au': '1.1.904851558.1578340264',
                   '_ga': 'GA1.2.1941541205.1578340264',
                   '_gid': 'GA1.2.789100157.1578340264',
                   'website#lang': 'en',
                   '_hjid': '6cf1dbb7-52a7-4d17-ae9f-be6e5e28aba8',
                   'nmstat': '1578340291759',
                   '_hjIncludedInSample': '1',
                   's_cc': 'true',
                   '__RequestVerificationToken': 'ode7hpqil0vxrb6XruH3sWndMlXaE5OmnfLg8ZEQU4zlwqp5dYuYdD86kWkYoAkkten7SbuWfzp7pV6DzVUN5-dPnHGpZturH7Et4MQlwNE1',
                   'dtSa': '-',
                   'SC_ANALYTICS_GLOBAL_COOKIE': '9139819721574bd5aa820655ec71df6d|True',
                   'dtCookie': '5$3145D019964A94C6CF5110C15E95B9B9|f54147a75dc79652|1',
                   'dtLatC': '2',
                   '_gat_UA-126852301-5': '1',
                   's_sq': '%5B%5BB%5D%5D',
                   'dtPC': '5$340279830_235h17vCEDNIAAOAGDQLFOBTKFAGJLGMPIANBOJ',
                   'rxvt': '1578342302303|1578340248514'
                   }

        data = {
            'ID': '{CC25EC6C-2471-42C5-B1FF-B0EB1ABCBBA5}',
            'Page': '2',
            'PageSize': '6',
            #'view_path': '/views/ajax',
            'CurrentPageSize': '8',
            'filters' : '',
            'Language': 'en',
            'Sort': '0',
            }

        for num in range(2, 6):  # 45loop iterating over different pages of ajax request
            data['Page'] = str(num)
            data['CurrentPageSize'] = str(2+ (num-1)*6)
            s_url = 'https://www.ajg.com/api/articles/getarticles'
            yield FormRequest(url=s_url, formdata=data, headers=headers, cookies=cookies, callback=self.parse )
              


    def parse(self, response):
          body = json.loads(response.text)
          for dat in body['Articles']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = dat['PublishDate'] # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['Title']
              item['DOCLINK']= dat['Url'] 
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.ajg.com'
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
        name_regex = r'xxx'#(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*TSYS\b)(.|\s)*|(\bABOUT.TSYS\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #//div[contains(@class, "sub-heading-content")]//text() | 
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "content-container")]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            yield item
            #if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            #    item['DESCRIPTION'] = 'FEHLER'
            #    yield item
            #else:
            #    yield item
       
       