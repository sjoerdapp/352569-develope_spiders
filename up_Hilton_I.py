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
### get latest 20 news (first two pages)

### Hilton worldwide Holdings 1|1
### second scraper (lastest version) Hilton_Is should yield identical result
### many dupefilter issues 208 -> nachfragen bei scrapy
### check if scrapers a really identical

class QuotessSpider(scrapy.Spider):
    name = 'Hilt_9900192ARV001'
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Hilt_9900192ARV001/',
        }

    start_urls = ['http://newsroom.hilton.com/corporate/news']
    
    def parse(self, response):  # follow drop down menue for different years
         years = list(range(1, 3)) #66
         #del years[0]  # delets first element "NULL" from list of years
         for date in years:
             aux_url = 'http://newsroom.hilton.com/corporate/news?pn={}'
             year_url = [aux_url.format(date)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)
    
    def parse_next(self, response):
        auxs = response.xpath('//div[@class="items-container"]//a')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            #item['file_urls'] = [auxx_url]
            item['PUBSTRING'] = aux.xpath('./div/h4/span/text()').extract_first()
            item['HEADLINE']= aux.xpath('./div/h4/text()').extract_first()
            item['DOCLINK']= aux.xpath('./@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./div/h4/span/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./div/h4/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./@href').extract_first(),
            #        }
            aux_url = item['DOCLINK']
            base_url = 'http://newsroom.hilton.com'
            

            if '.pdf' in aux_url.lower():
                if aux_url.startswith('http'):
                    url= aux_url
                    item['file_urls'] = [url]
                    item['DOCLINK'] = url
                    item['DESCRIPTION'] = ''
                    yield item
                
                else:
                    if aux_url.startswith('/'):
                        url= base_url + aux_url
                        item['file_urls'] = [url]
                        item['DOCLINK'] = url
                        item['DESCRIPTION'] = ''
                        yield item
                    else:
                        url= base_url + '/' + aux_url
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
                    if aux_url.startswith('/'):
                        url= base_url + aux_url
                        request = scrapy.Request(url=url, callback=self.parse_details)
                        request.meta['item'] = item
                        yield request
                    else:
                        url= base_url + '/' + aux_url
                        request = scrapy.Request(url=url, callback=self.parse_details)
                        request.meta['item'] = item
                        yield request


        # follow pagination link vianext page url
        #next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()     
        #next_page_url = response.urljoin(next_page_url)
        #yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        #name_regex ='xxx'# r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Hilton\b)(.|\s)*|(\bAbout.Hilton\b)(.|\s)*'
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*'
        name_regex_2=r'(\bAbout\s*Hilton)(.|\s)*|(\bAbout.Hilton\b)(.|\s)*|(\bABOUT.Hilton\b)(.|\s)*|(\bABOUT\s*.HILTON\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="container"]/*[not(self::h1 or descendant::h1 or self::div[@class="rail-items"] or descendant::div[@class="rail-items"] or self::div[@id="add-this-wrap"] or descendant::div[@id="add-this-wrap"] or self::div[@id="article-details"] or descendant::div[@id="article-details"] or self::div[@id="category-tags"] or descendant::div[@id="category-tags"])]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['DOCLINK'] = response.url
        pdf_check = response.xpath('//div[@class="container"]//p/a[contains(@href, ".PDF")]/@href').extract()
        if pdf_check:
            item['file_urls'] = ['http://newsroom.hilton.com' + pdf_check[0]]
            item['DESCRIPTION'] = ''  
        else:
            pdf_check = response.xpath('//p/a[contains(text(), "Click here to view the full release")]/@href').extract()
            if pdf_check:
                item['file_urls'] = [response.urljoin(pdf_check[0])]
                item['DESCRIPTION'] = ''
        
        yield item
       






















