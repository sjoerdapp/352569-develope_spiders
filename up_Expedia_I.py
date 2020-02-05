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

### UPDATES
### latest 20 news

### Expedia Group Inc 1|1
### 1st spider Press releases
### ATTENTION !!!!! only scrapes releases of expedia Group!
### First collect links to ERNAS as they are not in the news
### normal get  
### expedia group back to 20050809
### Complete source back to 20000717


class QuotessSpider(scrapy.Spider):
    name = 'Expedia_I_4701300ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Expedia_I_4701300ARV001/',
        }
    start_urls = [
        'https://ir.expediagroup.com/financial-information/quarterly-results',
    ]

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for year_div in response.css('.view-grouping'):
            year = year_div.xpath('./h2/text()').extract_first()
            for line in year_div.xpath('.//div[@class="view-grouping-content"]/div'):
                if 'acc-title' in line.xpath('./@class').extract_first():
                    quarter = line.xpath('./text()').extract_first()
                else:
                    for item in line.xpath('.//div[@class="item-list"]//a[contains(@type,"pdf")]'):
                        text = item.xpath('./text()').extract_first().lower()
                        href = item.xpath('./@href').extract_first()
                        if any(x in text for x in ['earnings release', 'results']):  # noqa
                            self.doc_mapping[year][quarter].setdefault('er', href)  # noqa
                        if 'earnings call transcript' in text:
                            self.doc_mapping[year][quarter].setdefault('ect', href)  # noqa
        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))  # noqa
        #yield scrapy.Request(
        #    'https://media.expediagroup.com/press-releases?l=25',
        #    callback=self.parse_pr_list)

    
        years = list(range(0, 1, 50)) # - 2051 for all News Releases (inkl subbrands) 
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'https://media.expediagroup.com/expedia-group-press-releases?l=50&o={}'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//ul[contains(@class, "wd_item_list")]/li')
          if len(auxs) > 20:
            auxs = auxs[0:20]

          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[@class="wd_date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[@class="wd_title"]/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div[@class="wd_title"]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://media.expediagroup.com'
              aux_url = aux.xpath('.//div[@class="wd_title"]/a/@href').extract_first()
              
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*Expedia\s*(?!\'s)\b)(.|\s)*|(\bABOUT.Expedia\s*(?!\'s)\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "wd_subtitle")]//text() | //div[contains(@class, "wd_body wd_news_body")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            title = item['HEADLINE']
            quarter_match = re.search(r'\bQ([1-4])\b', item['HEADLINE'])
            if quarter_match:
              quarter = {
                '1': 'First Quarter',
                '2': 'Second Quarter',
                '3': 'Third Quarter',
                '4': 'Fourth Quarter',

              }.get(quarter_match.group(1))
              year = re.search(r'\b(20[0-9]{2})\b', title).group(1)
              text = item['DESCRIPTION']
              if re.search('earnings release [^.]* available', text.lower()):
                item['file_urls'] = [self.doc_mapping[year][quarter].get('er')]
            else:
              quarter_match = re.search(r'\bfirst\s*quarter\b|\bthird\s*quarter\b|\bfourth\s*quarter\b', item['DESCRIPTION'], flags=re.IGNORECASE)
              if quarter_match:
                quarter = {
                  'first quarter': 'First Quarter',
                  'second quarter': 'Second Quarter',
                  'third quarter': 'Third Quarter',
                  'fourth quarter': 'Fourth Quarter',

                }.get(quarter_match.group())
                year = re.search(r'\b(20[0-9]{2})\b', item['PUBSTRING']).group(1)
                text = item['DESCRIPTION']
                if re.search('press release [^.]* available | earnings release [^.]* available', text.lower()):
                  item['file_urls'] = [self.doc_mapping[year][quarter].get('er')]
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       