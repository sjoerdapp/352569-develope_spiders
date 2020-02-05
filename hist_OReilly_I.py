# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### O'Reilly Automotive Inc. 1|1
### all news with pdfs -> therefore everything workds via pdf
### back to 20020423


class QuotessSpider(scrapy.Spider):
    name = 'OReill_I_1209700ARV001'
    start_urls = ['https://corporate.oreillyauto.com/corporate-information-news-room']
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/OReill_I_1209700ARV001/',
        }
    
    def parse(self, response):
        auxs = response.xpath('//div[@class="content-zone-container" and not(@data-czid="Content Zone One")]/div')
        for aux in auxs:
            aux_url = aux.xpath('./div/a[1]/@href').extract_first()
            if aux_url.startswith('http'):
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [aux_url]
                item['PUBSTRING'] = aux.xpath('.//h2//div[@class="subheader"]/text()').extract_first()
                item['HEADLINE']= aux.xpath('.//h2//div[@class="header"]/text()').extract_first()
                item['DOCLINK']= aux_url
                item['DESCRIPTION'] = ''
                yield item
            else:
                item = SwisscomIvCrawlerItem()
                base_url = 'https://corporate.oreillyauto.com'
                item_url= base_url + aux_url
                item['file_urls'] = [item_url]
                item['PUBSTRING'] = aux.xpath('.//h2//div[@class="subheader"]/text()').extract_first()
                item['HEADLINE']= aux.xpath('.//h2//div[@class="header"]/text()').extract_first()
                item['DOCLINK']= item_url
                item['DESCRIPTION'] = ''
                yield item
                
            

        # follow pagination link vianext page url
        #next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()     
        #next_page_url = response.urljoin(next_page_url)
        #yield scrapy.Request(url=next_page_url, callback=self.parse)


       






















