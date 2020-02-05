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

### Universal Health Services Inc. 2|2
### 2nd Company News Releases
### normal get, all news in one page
### back to 20180227



class QuotessSpider(scrapy.Spider):
    name = 'UniversalHealthServices_II_4655000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/UniversalHealthServices_II_4655000ARV002/',
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
         #years = list(range(0, 8)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         ##del years[0]  # delets first element "NULL" from list of years
         #for year in years:
         #    aux_url = 'https://ir.uhsinc.com/news-releases?items_per_page=50&page={}'
         #    year_url = [aux_url.format(year)][0]
        yield scrapy.Request(url='https://www.uhsinc.com/about-uhs/uhs-news-releases/', meta={'dont_proxy': True,}, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div[@class="accordion__item"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "news-date")]/div/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//p/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//p/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.uhsinc.com'
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
                    request = scrapy.Request(url=url, meta={'dont_proxy': True,}, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
                    
                
                else:
                    url= base_url + aux_url
                    request = scrapy.Request(url=url, meta={'dont_proxy': True,}, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request
               
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(One of the nation’s largest and most respected hospital (management)? companies, Universal Health Services, Inc. (NYSE: UHS) has built)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Universal\s*Health\s*Services,\s*Inc.\s*is)(.|\s)*|(\bABOUT\s*Universal\s*Health\b)(.|\s)*|(\bABOUT.Universal.Health\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="siteorigin-widget-tinymce textwidget"]//text()[not(ancestor::img)][not(ancestor::table[@class="gnw_news_media_box"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::img)][not(ancestor::table[@class="gnw_news_media_box"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                yield item
            else:
                yield item
       
       