# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from scrapy_splash import SplashRequest
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Twitter Inc 2|2
### 1nd spider blog
### blog spider rather plane 

class QuotessSpider(scrapy.Spider):
    name = 'twitter_II_9900249ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/twitter_II_9900249ARV002/',
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
    start_urls = ['https://blog.twitter.com/en_us/_jcr_content/par/nowrap/column/topic-results.1.html']

    def parse(self, response):  # follow drop down menue for different years
         pages = list(range(1, 19)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for page in pages:
             aux_url = 'https://blog.twitter.com/en_us/_jcr_content/par/nowrap/column/topic-results.{}.html'
             year_url = [aux_url.format(page)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div[@class="result__copy"]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[@class="result__byline"]//time/text()').extract_first()
              item['HEADLINE']= aux.xpath('.//a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('.//div[@class="result__byline"]//time/text()').extract_first(),
              #        'HEADLINE': aux.xpath('.//a/text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//a/@href').extract_first(),
              #        }
              base_url = 'https://blog.twitter.com'
              aux_url =aux.xpath('.//a/@href').extract_first()
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
             
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(\bAbout.Twitterxx\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class,"bl13-rich-text-editor")]//text()[not(ancestor::div[contains(@class,"tweet")] or ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item
       
       