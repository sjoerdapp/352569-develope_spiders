# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
import json
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### get latest 20 news (first two pages)

### US Bancorp 2|2
### 1st with dexi does not work anymore
### 2nd spider Investor Press Releases
### works with normal get 
### back to 20050127



class QuotessSpider(scrapy.Spider):
    name = 'US_BanCorp_1645000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/US_BanCorp_1645000ARV002/',
        }
    #custom_settings = {
    #    'SPLASH_URL': 'http://localhost:8050',
    #    'DOWNLOADER_MIDDLEWARES': {
    #        'scrapy_splash.SplashCookiesMiddleware': 723,
    #        'scrapy_splash.SplashMiddleware': 725,
    #        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    #    },
    #    'SPIDER_MIDDLEWARES': {
    #        'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
    #    },
    #    'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    #}
    #start_urls = ['https://www.tractorsupply.com/']

    def start_requests(self):  # follow drop down menue for different years
         years = list(range(0, 2)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://ir.usbank.com/investor-relations/news-and-events?page={}'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div[@class="row article"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "date-time")]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[contains(@class, "headline")]/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div[contains(@class, "headline")]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://ir.usbank.com'
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
               
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(\bAbout[^A-Za-z]*U[^A-Za-z]*S[^A-Za-z]*Ban(corp|k)\b)(.|\s)*'#|(\bABOUT.Martin.Marietta\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"][not(ancestor::div[@class="box__right"])]//text()[not(ancestor::table[@class="gnw_news_media_box"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            pdf_link = response.xpath('//ul/li/a[contains(text(), "Earnings Release")]/@href').extract_first()
            if pdf_link:
              pdf_url = [response.urljoin(pdf_link)][0]
              request = scrapy.Request(url=pdf_url, callback=self.parse_pdf)
              request.meta['item'] = item
              yield request
            
            #if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            #    item['DESCRIPTION'] = "FEHLER" #re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="irwFilePageBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            #    yield item
            else:
                yield item

    def parse_pdf(self, response):
        item = response.meta['item']
        quarter_regex = r'\b(First)\b \b(Quarter)\b|\b(Second)\b \b(Quarter)\b|\b(Third)\b \b(Quarter)\b|\b(Fourth)\b \b(Quarter)\b'
        quarter_match = re.search(quarter_regex, item['HEADLINE'])
        if quarter_match:
          quarter = {
            'First Quarter': 'Q1',
            'Second Quarter': 'Q2',
            'Third Quarter': 'Q3',
            'Fourth Quarter': 'Q4',
            }.get(quarter_match.group())
          year = re.search(r'\b(20[0-9]{2})\b', item['HEADLINE']).group(1)
          xpath_1 = '//div[child::h3[contains(text(), "{}")]]'
          xpath_1 = xpath_1.format(year)
          xpath_2 = '//div[child::h5[contains(text(), "{}")]]//a[contains(text(), "Earnings")]/@href'
          xpath_2 = xpath_2.format(quarter)
          pdf_link = response.xpath(xpath_1 + xpath_2).extract_first()
          item['file_urls'] = [response.urljoin(pdf_link)]
          yield item

       
       

       #'//div[child::h3[contains(text(), year)]]//div[child::h5[contains(text(), "Q3")]]//a[contains(@title, "Earnings_Release")]/@href'