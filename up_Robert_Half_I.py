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

### UPDATES
### latest 20 news

### Robert half International Inc. 1|2
### 1st spider Investor Press Releases, 2nd spider News Releases
### normal get, ernas come with seperate page and are connected via dictonary
### back to 20050118


class QuotessSpider(scrapy.Spider):
    name = 'Robert_Half_I_4690000ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Robert_Half_I_4690000ARV001/',
        }

    start_urls = ['https://www.roberthalf.com/investor-center/quarterly-earnings-releases#']

    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.doc_mapping = defaultdict(lambda: defaultdict(lambda: {}))

    def parse(self, response):
        for aux in response.xpath('//table//tr[@class="qer-historical"][not(ancestor::thead)]'):
            text = aux.xpath('./td[@class="views-field views-field-field-end-date"]/*/text()').extract_first()
            year = re.search(r'\d{4}', text).group(0)
            quarter = re.search(r'\d{2}/', text).group(0)
            #if 'and Full Year' in quarter: # get rid of 'and full year' if neccessary
            #  quarter = re.split(r' and', text.split('Reports ')[1])[0]
            
            href = 'https://www.roberthalf.com' + aux.xpath('./td[@class="views-field views-field-field-financial-document"]/a/@href').extract_first()
            self.doc_mapping[year][quarter].setdefault('er', href)

        self.logger.info('doc mapping: {}'.format(json.dumps(self.doc_mapping, indent=4)))
    
        #start_urls = ['https://www.roberthalf.com/investor-center/financial-news?items_per_page=All']
        #def parse(self, response):  # follow drop down menue for different years
        #     years = list(range(0, 151)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #     #del years[0]  # delets first element "NULL" from list of years
        #     for year in years:
        #         aux_url = 'https://investor.kelloggs.com/News/4133514/NewsData?pageIndex={}'
        #         year_url = [aux_url.format(year)][0]
        yield scrapy.Request(url='https://www.roberthalf.com/investor-center/financial-news?items_per_page=All', callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.xpath('//table//tr')
          for aux in auxs[0:20]:
              item = SwisscomIvCrawlerItem()
              item['PUBSTRING'] = aux.xpath('./td[contains(@class, "date")]/text()').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
              item['HEADLINE']= aux.xpath('./td[contains(@class, "title-1")]/text()').extract_first()
              item['DOCLINK']= aux.xpath('./td[contains(@class, "title")]/a/@href').extract_first()
              #item = {
              #        'PUBSTRING': aux.xpath('./p[@class="news-card-date"]//text()').extract()[1],
              #        'HEADLINE': aux.xpath('.//h3[@class="news-card-title"]/a//text()').extract_first(),
              #        'DOCLINK': aux.xpath('.//h3[@class="news-card-title"]/a/@href').extract_first(),
              #        }
              base_url = 'https://www.roberthalf.com'
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Founded\s*in\s*1948.\s*Robert\s*Half\s*(International\s*)?(Inc.\s*)?(\(RHI\)\s*)?is)(.|\s)*|(Founded\s*in\s*1948.\s*Robert\s*Half.\s*is\s*the\s*World.)(.|\s)*|(Founded\s*in\s*1948.\s*Robert\s*Half\s*(International\s*)?(Inc.\s*)?.\s*the world.s\s*first\s*and\s*largest\s*specialized\s*staffing\s*firm.\s*is\s*a)(.|\s)*|(Founded\s*in\s*1948.\s*Robert\s*Half\s*(International\s*)?(Inc.\s*)?(\(RHI\)\s*)?(.|\s*)the world.s\s*first\s*and\s*largest\s*specialized\s*staffing\s*firm.\s*is\s*a)(.|\s)*'
        #name_regex_2=r'(\bAbout\s*Unum\b)(.|\s)*|(\bAbout.Unum\b)(.|\s)*|(\bABOUT.UNUM\b)(.|\s)*'
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//main//div[@class="content"]//div[@class="clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            #item['DESCRIPTION'] = re.sub(name_regex_2,'' , item['DESCRIPTION'])
            item['DOCLINK'] = response.url
            title = item['HEADLINE']
            release_match = re.search(r'ANNOUNCES.SCHEDULE', item['HEADLINE'])
            #if release_match:
            #  text_aux = re.search(r'release\s*(.*)\d{4}.earnings', item['DESCRIPTION']).group(0)
            #  quarter_match = title.split('FOR ')[1].split(' EARNINGS')[0]               
            #  quarter = {
            #    'FIRST-QUARTER': '03/',
            #    'SECOND-QUARTER': '06/',
            #    'THIRD-QUARTER': '09/',
            #    'FOURTH-QUARTER': '12/',
#
#            #  }.get(quarter_match)
#            #  year = re.search(r'\d{4}', text_aux).group(0)
            #  item['file_urls'] = [self.doc_mapping[year][quarter].get('er')]
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
       
       