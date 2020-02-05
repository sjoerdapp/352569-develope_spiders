# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### 

### Baker hugehes a Genereal Electric Comapny 1|2
### Investor Page
### following pagination links
### goes back to 20161031


class QuotessSpider(scrapy.Spider):
    name = 'BHGE_I_2025300ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/BHGE_I_2025300ARV001/',
        }
    start_urls = ['https://investors.bhge.com/press-releases']



    def parse(self, response):
          auxs = response.xpath('//div[@class="nir-widget--list"]/article')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./div[contains(@class, "date-time")]/text()').extract_first()
              item['HEADLINE']= aux.xpath('./div[contains(@class, "headline")]/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('./div[contains(@class, "headline")]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./td//div[@class="field-content"]//div[@class="field__item"]/text()').extract_first(),
              #        'HEADLINE': aux.xpath('./td/div[@class="views-field views-field-field-nir-news-title"]/div[@class="field-content"]//a/text()').extract_first(),
              #        'DOCLINK': aux.xpath('./td/div[@class="views-field views-field-field-nir-news-title"]/div[@class="field-content"]/a/@href').extract_first(),
              #        }
              base_url = 'https://investors.bakerhughes.com'
              aux_url = item['DOCLINK']
              
              if 'static-files' in aux_url.lower() or '.pdf' in aux_url.lower():
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
          next_page_url = response.xpath('//nav[@class="pager"]/ul/li[@class="pager__item pager__item--next"]/a/@href').extract_first()     
          if '2' in next_page_url:
            return
          next_page_url = response.urljoin(next_page_url)
          yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout.Baker.Hughes\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[contains(@class, "file-link")])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
              item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//section[@class="entry-content"]//text()[not(ancestor::div[contains(@class, "file-link")])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
              yield item
        else:
              yield item
       
       

