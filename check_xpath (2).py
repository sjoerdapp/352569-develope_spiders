

import scrapy
import re
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Huntington Bancshares Incorporate 1|1
### 1st spider Investor News
### classic get
### HTML structure changes in 2016
### back to 20130117


class QuotessSpider(scrapy.Spider):
    name = 'check_xpath'
    start_urls = ['http://huntington-ir.com/ne/news/index.htm',
                  'http://huntington-ir.com/ne/news/2018.htm',
                  'http://huntington-ir.com/ne/news/2017.htm',
                  'http://huntington-ir.com/ne/news/2016.htm',
                  'http://huntington-ir.com/ne/news/2015.htm',
                  'http://huntington-ir.com/ne/news/2014.htm',
                  'http://huntington-ir.com/ne/news/2013.htm']

    def parse(self, response):

    	item = {}
        item['PUBSTRING']: len(response.xpath('//div[@class="col-10"]//div//p[@class="no-max-width"]/following-sibling::em/text() |//div[@class="col-10"]//div//p[@class="no-max-width"]/strong/following-sibling::em/text()').extract()),
        item['HEADLINE']: len(response.xpath('./strong/text()').extract()),
        item['DOCLINK']: len(response.xpath('//div[@class="col-10"]//div//p[@class="no-max-width"]/a[text()="VIEW IN BROWSER" or text()="Earnings Press Release and Supplement"]/@href |//div[@class="col-10"]//div//p[@class="no-max-width"]/following-sibling::a[text()="VIEW IN BROWSER" or text()="Earnings Press Release and Supplement"]/@href').extract())
        yield item 