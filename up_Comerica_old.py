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
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
import json
from collections import defaultdict

### UPDATES
### actual year, get latest 25 news (first page)

### Comerica Incorporated 1|1
### spider News Room, there also exists a IR site but little news and all news are also in the newsroom
### ERNAS have to be downloaded from other page, stored in list and matched at the end
### normal get request for each year an then follow links
### back to 20010401



class QuotessSpider(scrapy.Spider):
    name = 'Comerica_I_1261000ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Comerica_I_1261000ARV001/',
        }
    start_urls = [
        'http://investor.comerica.com/phoenix.zhtml?c=114699&p=irol-reportsother',
    ]

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for year_div in response.xpath('//table[@class="reportsOtherTable"]'):
            Ttl_year = year_div.xpath('.//span[@class="ccbnTblTtl"]/text()').extract_first()
            year = re.search(r'\d{4}', Ttl_year).group(0)
            for idx, line in enumerate(year_div.xpath('.//tr[@class="ccbnBgTblOdd"]/td'), start=1):
                href = line.xpath('.//a[contains(text(), "News Release")]/@href').extract_first()
                
                quarter = 'Q' + str(idx)
                self.doc_mapping[year][quarter].setdefault('er', href)
        
        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))

                

    
        years = list(range(2019, 2020)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'http://comerica.mediaroom.com/news-releases?year={}&l=50'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_pages)

    def parse_pages(self, response):

          auxs = response.xpath('//div[@class="wd_newsfeed_releases"]/ul/li')
          

          for aux in auxs[0:20]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[@class="wd_date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[@class="wd_title"]//a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div[@class="wd_title"]//a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'http://comerica.mediaroom.com'
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

          #next_page_url = response.xpath('//tfoot/tr/td//a/@href').extract_first()
          #if next_page_url:
          #    next_page_urls = response.xpath('//tfoot/tr/td//a/@href').extract()
          #    for next_page in next_page_urls:
          #      yield scrapy.Request(url=next_page, callback=self.parse_next)


    def parse_next(self, response):
          auxs = response.xpath('//div[@class="wd_news_releases"]//table//div[@class="item"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./div[@class="item_date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('./div[@class="item_name"]/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('./div[@class="item_name"]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'http://comerica.mediaroom.com'
              aux_url = aux.xpath('./div[@class="item_name"]/a/@href').extract_first()
              
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
        name_regex = r'(Comerica\s*Incorporated\s*(\(\s*NYSE\s*:\s*CMA\s*\)\s*)?is\s*a\s*financial\s*services\s*company\s*headquartered\s*in\s*Dallas)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*Comerica\s*(?!\'s)\b)(.|\s)*|(\bABOUT.Comerica\s*(?!\'s)\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="wd_subtitle wd_language_left"]/text() | //div[@class="wd_body wd_news_body"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
              item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="wd_news_releases-detail"]/h2/text() | //div[@class="article-text"]//text()[not(ancestor::div[@class="middle-column"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            title = item['HEADLINE']
            quarter_regex = r'\b(First)\b \b(Quarter)\b|\b(Second)\b \b(Quarter)\b|\b(Third)\b \b(Quarter)\b|\b(Fourth)\b \b(Quarter)\b'
            quarter_match = re.search(quarter_regex, item['HEADLINE'])
            if quarter_match:
              quarter = {
                'First Quarter': 'Q1',
                'Second Quarter': 'Q2',
                'Third Quarter': 'Q3',
                'Fourth Quarter': 'Q4',
              }.get(quarter_match.group())
              #year = re.search(r'\b(20[0-9]{2})\b', title).group(1)
              text = item['DESCRIPTION']
              if re.search(r'results\s*are\s*available', text.lower()):
                year = re.search(r'\b(20[0-9]{2})\b', title).group(1)
                item['file_urls'] = [] #[self.doc_mapping[year][quarter].get('er')]  
                pdf_link = ''
                if not item['file_urls']:

                  pdf_link = ''
                  item['file_urls'] = [response.xpath('//a[@class="itemlink"][descendant::span[@class="wd_attachment_title"][contains(text(), "Earnings Release")]]/@href').extract_first()]
                if not item['file_urls'] or re.search('[a-zA-Z]', pdf_link):
                  item['file_urls'] = ['http://comerica.mediaroom.com' + response.xpath('//*[@class="wd_attachment_title"]/a[contains(text(), "Earnings Release")]/@href').extract_first()]
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                  item['DESCRIPTION'] = 'FEHLER'
                  yield item
            else:
                  yield item
                  
       
       