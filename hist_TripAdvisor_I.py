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
from collections import defaultdict

### Trip Advisor Inc. 1|3
### 1st spider Investor Press Releases, 2nd Press Releases, 3rd in the News
### normal get ernas come from news and event page with dictionary
### back to 20090113


class QuotessSpider(scrapy.Spider):
    name = 'TripAdvisor_I_5396400ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/TripAdvisor_I_5396400ARV001/',
        }
    
    start_urls = ['http://ir.tripadvisor.com/events-and-presentations?field_nir_event_start_date_value_1=now&sort_order=DESC&items_per_page=100&page=0']

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for aux in response.xpath('//div[@class="view-content"]/table//tr[not(ancestor::thead)]//a[contains(text(), "Financial Results")]'):
            text = aux.xpath('./text()').extract_first()
            year = re.search(r'\d{4}', text).group(0)
            quarter = re.split(r' \d{4}', text.split('Reports ')[1])[0]
            if 'and Full Year' in quarter: # get rid of 'and full year' if neccessary
              quarter = re.split(r' and', text.split('Reports ')[1])[0]
            
            href = aux.xpath('./@href').extract_first()
            self.doc_mapping[year][quarter].setdefault('er', href)

        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))  # noqa
        #yield scrapy.Request(
        #    'https://media.expediagroup.com/press-releases?l=25',
        #    callback=self.parse_pr_list)

    #def parse(self, response):  # follow drop down menue for different years
        years = list(range(0, 13)) #13 fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'http://ir.tripadvisor.com/press-releases?field_nir_news_date_value%5Bmin%5D=&items_per_page=50&page={}'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div[@class="item-list"]//ul/li')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[@class="dateformat"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[@class="field-content"]/a[2]/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div[@class="field-content"]/a[2]/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'http://ir.tripadvisor.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Safe\s*Harbor\s*Statement\b)(.|\s)*'
        name_regex_2=r'(\bAbout\s*TripAdvisor\b)(.|\s)*|(\bAbout.TripAdvisor\b)(.|\s)*|(\bABOUT.TRIPADVISOR\b)(.|\s)*|(\bAbout.TripAdvisor\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            title = item['HEADLINE']
            release_match = re.search(r'Earnings.Press.Release.Available', item['HEADLINE'])
            if release_match:
              text_aux = re.search(r'issued.its\s*(.*)\d{4}.earnings', item['DESCRIPTION']).group(0)
              quarter_match = re.split(r' \d{4}', text_aux.split('its ')[1])[0]              
              quarter = {
                'first quarter': 'First Quarter',
                'First Quarter': 'First Quarter',
                'second quarter': 'Second Quarter',
                'Second Quarter': 'Second Quarter',
                'third quarter': 'Third Quarter',
                'Third Quarter': 'Third Quarter',
                'Fourth Quarter': 'Fourth Quarter',
                'fourth quarter and full year': 'Fourth Quarter',
                'Fourth Quarter and Full Year' : 'Fourth Quarter',
                'fourth quarter and year': 'Fourth Quarter',
                'fourth quarter and year end': 'Fourth Quarter',
              }.get(quarter_match)
              year = re.search(r'\d{4}', text_aux).group(0)
              item['file_urls'] = [self.doc_mapping[year][quarter].get('er')]

            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       