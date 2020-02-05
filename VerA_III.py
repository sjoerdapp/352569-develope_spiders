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

### Verisk Analytics 3|3
### 3 spiders 1&2 für press releases 3 für IR
### spider for IR press releases

class QuotessSpider(scrapy.Spider):
    name = 'VerA_III_9900044ARV003'
    start_urls = ['https://investor.verisk.com/news-events/press-releases/default.aspx']
    
      
    def parse(self, response):
        auxs = response.xpath('//article[@class="archive-table"]/table//tr')
        for aux in auxs:
            item = {
                    'PUBSTRING': aux.xpath('./td[@class="date"]/text()').extract_first() + ' ' + re.findall(r'\d{4}',  response.xpath('//main/h1/text()').extract_first())[0],
                    'HEADLINE': aux.xpath('./td/a//text()').extract_first(),
                    'DOCLINK': aux.xpath('./td/a/@href').extract_first(),
                    }
            base_url = 'https://www.devonenergy.com'
            url= base_url + aux.xpath('./td/a/@href').extract_first()
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request

        # follow pagination link vianext page url
        #next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()     
        #next_page_url = response.urljoin(next_page_url)
        #yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
        #re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ,test) regex to cut out about apache
        #item['Textbody'] = " ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text()').extract()) join connects scraped lists
        item['Textbody'] = re.sub(r'(\bAbout\s*Devon\s*Energy\b)(.|\s)* | (\bAbout.Devon.Energy\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="container line"]/main/*[not(self::h1)]//text()').extract()))
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['url'] = response.url
        yield item
       
       






















