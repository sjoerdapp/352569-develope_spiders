# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### scrape first 2 pages, 20 latest news

### Williams Companies Inc 1|1
###  classic get
### back to 20120103


class QuotessSpider(scrapy.Spider):
    name = 'Williams_2192300ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Williams_2192300ARV001/',
        }
    start_urls = ['https://investor.williams.com/newsroom/all/all/Williams']

    def parse(self, response):
        auxs = response.xpath('//div[@class="view-content"]//div[@class="view-inner-wrapper"]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//div[@class="views-field-item views-field-created"]//span[@class="field-content"]/text()').extract_first()
            item['HEADLINE']= aux.xpath('.//div[@class="views-field-item views-field-title"]//span[@class="field-content"]/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//div[@class="views-field-item views-field-title"]//span[@class="field-content"]/a/@href').extract_first()

            #item = {
            #        'PUBSTRING': aux.xpath('.//div[@class="views-field-item views-field-created"]//span[@class="field-content"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('.//div[@class="views-field-item views-field-title"]//span[@class="field-content"]/a/text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//div[@class="views-field-item views-field-title"]//span[@class="field-content"]/a/@href').extract_first(),
            #        }
            base_url = 'https://investor.williams.com'
            aux_url = aux.xpath('.//div[@class="views-field-item views-field-title"]//span[@class="field-content"]/a/@href').extract_first()
            
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
        next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()
        if 'page=2' in next_page_url:
            return     
        next_page_url = response.urljoin(next_page_url)
        yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Williams\b)(.|\s)* | (\bAbout.Williams\b)(.|\s)*'
        #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
        #re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ,test) regex to cut out about apache
        #item['Textbody'] = " ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text()').extract()) join connects scraped lists
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class,"fieldpressreleasesubheadline")]//text()|//div[@class="panel-pane pane-pr-body"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item
       
       






















