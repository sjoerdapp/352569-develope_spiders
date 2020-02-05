# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
import json
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
from collections import defaultdict
import datetime

### UPDATES
### latest 20 news

### Pepesi Company 1|1
### 1st spider Quaterly Earnings Announcements and Press Releases integrated through mapping
### normal get 
### back to 2015


class QuotessSpider(scrapy.Spider):
    name = 'PepsiCo_III_2138400ARV003'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/PepsiCo_III_2138400ARV003/',
        }
    start_urls = [
        'https://www.pepsico.com/investors/financial-information/quarterly-earnings',
    ]

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for year_div in response.xpath('//div[@class="card accordion__item"]')[0:6]:
            Ttl_year = year_div.xpath('.//button/text()').extract_first()
            year = re.search(r'\d{4}', Ttl_year).group(0)
            quarter = re.search(r'Q\d{1}', Ttl_year).group(0)
            href = year_div.xpath('.//div[@class="card-body"]/a[span[contains(text(), "Press Release")]]/@href').extract_first()
            self.doc_mapping[year][quarter].setdefault('er', href)
            
        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))  # noqa
        #yield scrapy.Request(
        #    'https://media.expediagroup.com/press-releases?l=25',
        #    callback=self.parse_pr_list)

    
        headers = {
            'Accept': ' */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/x-www-form-urlencoded; charset="UTF-8"',
            'Cookie': 'ServerID=1025',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.pepsico.com',
            'Referer': 'https://www.pepsico.com/news/media-resources/press-releases',
            #'perc-tid': '2013CM1-4bda-f455-9ac7-2a26',
            #'perc-version': '5.3.15',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            #'X-Requested-With': 'XMLHttpRequest',
           }

        #cookies = {'visid_incap_1246096': 'nu9KgX4GRbu+o2Vne+eawwktTlwAAAAAQUIPAAAAAAByH42r0JBEzG3yLY+HSfNu',
        #            '_ga': 'GA1.2.2143087210.1548627217',
        #            'SC_ANALYTICS_GLOBAL_COOKIE': '1a70df17b7a44f05b12fcc8f44eb006f|True',
        #            'com.silverpop.iMAWebCookie': 'e6825de4-ce53-b87c-d433-c4e2a8d3c4c7',
        #            '__atssc': 'google%3B1',
        #            'notice_preferences': '2:',
        #            'notice_gdpr_prefs': '0,1,2:',
        #            '__atuvc': '8%7C5%2C0%7C6%2C4%7C7',
        #            'wtw#lang': 'en',
        #            'ASP.NET_SessionId': 'sg2vkfeqj00ssxys30jknpte',
        #            '__RequestVerificationToken': '_JNT7w3kcWA8aRZZfiIp7uV1PWfhkvuudK4fgue2kBICTvdQvkBCToHvzCRGGua3oiqVxxMguoj8UDIDynAyJHfW3wY1',
        #            'TS0121b28a': '01324cfcfdfc173ac91c1bebf34a8ecf2649106c0e3381bd868516223b72d3345939cbf359e0d82bc0a8883e4f03d9ffc21b858e98acb103de6d4c31b4cca6ae62570302999e7a24ccf8bc2ba1234fdba8717840970243440272661475387324995140a40f6baf597d8d1983b7c010c856864ad39137bb0a986a445c4dd9c321ccd8a730a62a61f0ec7bf24221a77edf35c3f1f5f7',
        #            'incap_ses_287_1246096': 'K9ZIa+BqA0OMHYlRU6L7AzNubVwAAAAAY3FA0R3/dM6FQhxglqqiYA==',
        #            'resolution': '1920'}
        data = {
            'searchTerm' : '',
            'page': '1',
            #'view_path': '/views/ajax',
            'pageSize': '6',
            }

        #years = list(range(0, 1, 50)) # - 2051 for all News Releases (inkl subbrands) 
        #del years[0]  # delets first element "NULL" from list of years
        for num in range(1,5):  # loop iterating over different pages of ajax request
            data['page'] = str(num)
            s_url = 'https://www.pepsico.com/data/PressReleasesSearch'
            yield FormRequest(url=s_url, formdata=data, headers=headers, meta={'dont_proxy': True,}, callback=self.parse_next )

    def parse_next(self, response):
          body = json.loads(response.text)
          for dat in body['posts']:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = re.match(r'\d{8}',dat['publicationDate']).group(0) # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= dat['postTitle']
              item['DOCLINK']= dat['postUrl'] 
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              #yield item
              base_url = 'https://www.pepsico.com'
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
        name_regex = r'(\bABOUT\s*PepsiCo\s*(?!\'s)\b) (.|\s)*|(\bABOUT.PepsiCo\s* (?!\'s)\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="news-story"]/div[@class="container"]//text()[not(ancestor::h1 or ancestor::div[contains(@class, "social-links")] or ancestor::span[@class="news-story__date"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            title = item['HEADLINE']
            quarter_regex = r'\b(First)\b \b(Quarter)\b|\b(Second)\b \b(Quarter)\b|\b(Third)\b \b(Quarter)\b|\b(Fourth)\b \b(Quarter)\b'
            quarter_match = re.search(quarter_regex, item['HEADLINE'])
            year_match = re.search(r'\d{4}', item['HEADLINE'])
            #quarter_match = re.search(r'\bQ([1-4])\b', item['HEADLINE'])
            if quarter_match and year_match:
              quarter = {
                'First Quarter': 'Q1',
                'Second Quarter': 'Q2',
                'Third Quarter': 'Q3',
                'Fourth Quarter': 'Q4',
              }.get(quarter_match.group())
              year = year_match.group()
              text = item['DESCRIPTION']
              if re.search('financial results [^.]* available', text.lower()):
                item['file_urls'] = ['https://www.pepsico.com' + self.doc_mapping[year][quarter].get('er')]
            
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       