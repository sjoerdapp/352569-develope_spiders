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


class QuotessSpider(scrapy.Spider):
    name = 'Hilt_I_9900192ARV001'
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://sp5001/Hilt_9900192ARV001/',
        }

    start_urls = ['http://newsroom.hilton.com/corporate/news']
    
    def parse(self, response):  # follow drop down menue for different years
         years = list(range(1, 66)) #66
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
            auxx_url = aux.xpath('./@href').extract_first()
            if auxx_url.startswith('http'):
                if re.search('.pdf', auxx_url, re.IGNORECASE):
                    item['file_urls'] = [auxx_url]
                    item['PUBSTRING'] = aux.xpath('./div/h4/span/text()').extract_first()
                    item['HEADLINE']= aux.xpath('./div/h4/text()').extract_first()
                    item['DOCLINK']= auxx_url
                    yield item 

                else:
                    request = scrapy.Request(url=auxx_url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request

            else:
                base_url = 'http://newsroom.hilton.com'
                if re.search('.pdf', aux.xpath('./@href').extract_first(), re.IGNORECASE):
                    if aux.xpath('./@href').extract_first().startswith('/'):
                        url= base_url + aux.xpath('./@href').extract_first()
                        item['file_urls'] = [url]
                        item['PUBSTRING'] = aux.xpath('./div/h4/span/text()').extract_first()
                        item['HEADLINE']= aux.xpath('./div/h4/text()').extract_first()
                        item['DOCLINK']= url
                        yield item

                    else:
                        item['file_urls'] = ['http://newsroom.hilton.com/' + aux.xpath('./@href').extract_first()]
                        item['PUBSTRING'] = aux.xpath('./div/h4/span/text()').extract_first()
                        item['HEADLINE']= aux.xpath('./div/h4/text()').extract_first()
                        item['DOCLINK']= 'http://newsroom.hilton.com/' + aux.xpath('./@href').extract_first()
                        yield item 

                else:
                    if aux.xpath('./@href').extract_first().startswith('/'):
                        detail_url= 'http://newsroom.hilton.com' + aux.xpath('./@href').extract_first()
                        request = scrapy.Request(url=detail_url, callback=self.parse_details)
                        request.meta['item'] = item
                        yield request

                    else:
                        detail_url= 'http://newsroom.hilton.com/' + aux.xpath('./@href').extract_first()
                        request = scrapy.Request(url=detail_url, callback=self.parse_details)
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
        item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Hilton\b)(.|\s)* | (\bAbout.Hilton\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="container"]/*[not(self::h1 or descendant::h1)]//text()').extract()))
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['DOCLINK'] = response.url
        pdf_check = response.xpath('//div[@class="container"]//p/a[contains(@href, ".PDF")]/@href').extract()
        if pdf_check:
            item['file_urls'] = ['http://newsroom.hilton.com' + pdf_check[0]]
            yield item
        else:
            yield item
       
       






















