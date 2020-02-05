# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""
### Eversource Energy 4|4
### all in all 4 spiders 3 for different regeions and 4th for investor page
### 4th spider investor  financial press releases
### get request with  content as pdfs
### goes back to 20120928


import scrapy
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### scrape actual year, if more than 20 news, cut off

### Eversource Energy 4|4
### all in all 4 spiders 3 for different regeions and 4th for investor page
### Investor spider, all pdfs
### have to ad together time-stamp
### classic get, all content on one page


class QuotessSpider(scrapy.Spider):
    name = 'EverS_IV_2129900ARV004'
    start_urls = ['https://www.eversource.com/content/general/about/investors/investor-relations/financial-press-releases']
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/EverS_IV_2129900ARV004/',
        }
    
    def parse(self, response):
        years = list(range(2019, 2020))
        for year in years:
            xpath = '//div[@class="article-content"]/div[@class="sfContentBlock"]/h2[text()="{}"]/following-sibling::ul[1]/li' 
            auxs = response.xpath(xpath.format(year))
            if len(auxs) > 20:
                auxs = auxs[0:20]
                
            for aux in auxs:
                aux_url = aux.xpath('./a/@href').extract_first()
                base_url = 'https://www.eversource.com'
                #if aux_url.startswith('http'):
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [base_url + aux_url]
                item['PUBSTRING'] = str(year) + " " + aux.xpath('./text()').extract_first().split('(')[1].split(')')[0]
                item['HEADLINE']= aux.xpath('./a/text()').extract_first()
                item['DOCLINK']= base_url + aux_url
                item['DESCRIPTION'] = ''
                yield item
            #else:
            #    item = SwisscomIvCrawlerItem()
            #    base_url = 'https://corporate.oreillyauto.com'
            #    item_url= base_url + aux_url
            #    item['file_urls'] = [item_url]
            #    item['PUBSTRING'] = aux.xpath('.//h2//div[@class="subheader"]/text()').extract_first()
            #    item['HEADLINE']= aux.xpath('.//h2//div[@class="header"]/text()').extract_first()
            #    item['DOCLINK']= item_url
            #    yield item
                
            

        # follow pagination link vianext page url
        #next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()     
        #next_page_url = response.urljoin(next_page_url)
        #yield scrapy.Request(url=next_page_url, callback=self.parse)


       






















