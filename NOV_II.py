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
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### National Oilwell Varco Inc 2|2
### classical News page
### back to 20120203 
### 

class QuotessSpider(scrapy.Spider):
    name = 'NOV_II_3176900ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/NOV_II_3176900ARV002/',
        }
    start_urls = ['https://www.nov.com/news.aspx']

    def parse(self, response):
        auxs = response.xpath('//div[@class="story-list-container"]/div[@class="story-list-item"]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//div[@class="story-list-item-date"]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux.xpath('.//div[@class="story-list-item-title"]/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//div[@class="story-list-item-link"]/a/@href').extract_first()
            
            #item = {
            #        'PUBSTRING': aux.xpath('.//div[@class="story-list-item-date"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('.//div[@class="story-list-item-title"]/text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//div[@class="story-list-item-link"]/a/@href').extract_first(),
            #        }
            #base_url = 'https://www.nov.com'
            url= base_url + aux.xpath('.//div[@class="story-list-item-link"]/a/@href').extract_first()
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request

        # follow pagination link vianext page url
        next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()     
        next_page_url = response.urljoin(next_page_url)
        yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
        #re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ,test) regex to cut out about apache
        #item['Textbody'] = " ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text()').extract()) join connects scraped lists
        item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Williams\b)(.|\s)* | (\bAbout.Williams\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="panel-pane pane-pr-body"]//*[not(self::script or self::style)]//text()').extract()))
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['DOCLINK'] = response.url
        yield item
       
       






















