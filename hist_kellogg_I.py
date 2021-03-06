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
from collections import defaultdict

### Kellogg Company  1|2
### 1st spider Investor Press Releases, 2nd spider Corporate & US News
### egtl. post. aber works with normal get 
### back to 20061031



class QuotessSpider(scrapy.Spider):
    name = 'Kellogg_I_2104100ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Kellogg_I_2104100ARV001/',
        }
    start_urls = ['https://investor.kelloggs.com/QuarterlyResults#0']

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for year_div in response.xpath('//div[contains(@class, "panel panel-default")]'):
            year = re.search(r'\d{4}', year_div.xpath('.//a/span[@class="irwQRTitle"]/text()').extract_first()).group(0)
            quarter = re.search(r'\D+', year_div.xpath('.//a/span[@class="irwQRTitle"]/text()').extract_first()).group(0).rstrip()
            href = year_div.xpath('//div[@class="panel-body"]/ul/li/a[contains(text(), "Earnings Release") or contains(text(), "Press Release")]/@href').extract_first()
            if '../' in href:
              href = 'https://investor.kelloggs.com' + year_div.xpath('//div[@class="panel-body"]/ul/li/a[contains(text(), "Earnings Release") or contains(text(), "Press Release")]/@href').extract_first().split('..')[1]
            self.doc_mapping[year][quarter].setdefault('er', href)

        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))  # noqa

    
    #def parse(self, response):  # follow drop down menue for different years
        years = list(range(0, 151))#151 # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'https://investor.kelloggs.com/News/4133514/NewsData?pageIndex={}'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//div[contains(@class, "TableRowItem")]')
          for aux in auxs:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('.//div[@class="prDateCol col-sm-2"]/div/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('.//div[@class="col-sm-10"]/h4/a/text()').extract_first()
              item['DOCLINK']= aux.xpath('.//div[@class="col-sm-10"]/h4/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://investor.kelloggs.com'
              aux_url = aux.xpath('.//div[@class="col-sm-10"]/h4/a/@href').extract_first()
              
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bABOUT\s*Kellogg\s*Company\b)(.|\s)*|(\bABOUT.Kellogg.Company\b)(.|\s)*' #|(\bABOUT\s*L\s*BRANDS\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="col-xs-12"]//text()[not(ancestor::h1 or ancestor::div[@class="irwFilePageDate"])][not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            title = item['HEADLINE']
            quarter_match = re.search(r'Reports\s*\d{4}\s*(First|Second|Third|Fourth)\s*Quarter', item['HEADLINE'])
            if quarter_match:
                quarter = re.search(r'(First|Second|Third|Fourth)\s*Quarter', item['HEADLINE']).group(0)
                year = re.search(r'\d{4}', item['HEADLINE']).group(0)
                item['file_urls'] = [self.doc_mapping[year][quarter].get('er')]
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="irwFilePageBody"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                  item['DESCRIPTION'] = 'FEHLER'
                  yield item
                else:
                    yield item
            else:
                yield item
       
       