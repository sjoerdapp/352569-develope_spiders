# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from calendar import month_name
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Harris Corporation 1|1
### 1 spiders for Newsroom
### classic get request
### goes back to 20040109


class QuotessSpider(scrapy.Spider):
    name = 'HarrisL3_2088300ARV002'
    custom_settings = {
        'JOBDIR' : 'None',
        'FILES_STORE' : 's3://352569/HarrisL3_2088300ARV002/',
       }
    start_urls = ['https://www.harris.com/press-releases']
    
      
    def parse(self, response):
        auxs = response.xpath('//div[contains(@class, "press-release")]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./div//span/text()').extract_first()
            item['HEADLINE']= aux.xpath('.//h3/text()').extract_first()
            item['DOCLINK']= aux.xpath('./parent::a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./div//span/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./h3/a/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./h3/a/@href').extract_first(),
            #        }
            if not item['DOCLINK']:
                item['DOCLINK']= aux.xpath('.//a/@href').extract_first()
                
            base_url = 'https://www.l3harris.com'
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
            

        # follow pagination link vianext page url
        if response.xpath('//li [@class="pager-next"]/a/@href').extract_first():
            base_url = 'https://www.harris.com'
            next_page_url = base_url + response.xpath('//li [@class="pager-next"]/a/@href').extract_first()     
            #next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Harris\s*Corporation\b)(.|\s)* | (\bAbout.Harris.Corporation\b)(.|\s)*|(\bABOUT.Harris.Corporation\b)(.|\s)*|(\bABOUT\s*.HARRIS\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class,"pane-node-body")]//div[@class="field-item odd"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
        else:
            yield item
       
       






















