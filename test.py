import json
import scrapy
import requests
from scrapy.selector import Selector
import re
#from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Zimmer Biomet 1|1
### All description urls as pdf. think about using text as well
### back to 20010716




class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = 'Lbrands_II_test'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Lbrands_II_test/',
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
    start_urls = ['http://investors.lb.com/phoenix.zhtml?c=94854&p=irol-news']

    def parse(self, response):
          auxs = response.xpath('//div[@class="ndq-content"]/table[5]//table//tr[not(self::*[contains(@class, "Ttl")] or self::*[contains(@class, "Txt")])]')
          for aux in auxs:
              item = {}
              item['PUBSTRING'] = aux.xpath('./td[1]/span/text()').extract_first() 
              item['HEADLINE']= aux.xpath('./td[2]/span/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('./td[2]/span/a/@href').extract_first()
              yield item