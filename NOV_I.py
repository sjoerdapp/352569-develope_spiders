# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### National Oilwell Varco Inc 1|2
### 1st spider IR Press releases, 2nd spider News
### classic get
### back to 20150227


class QuotessSpider(scrapy.Spider):
    name = 'NOV_I_3176900ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/NOV_I_3176900ARV001/',
        }
    start_urls = ['https://investors.nov.com/news-releases']
    
    def parse(self, response):  # follow drop down menue for different years
         years = response.xpath('//div[@class="nir-widget--form"]//select//text()').extract()
         del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://investors.nov.com/news-releases?a89c091f_year%5Bvalue%5D={}&op=Filter&a89c091f_widget_id=a89c091f&form_build_id=form-o6U8VccBDtRaXh_CzVv_zQqtrrbVALDevvRB5o6qdB4&form_id=widget_form_base'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)
    
    def parse_next(self, response):
        auxs = response.xpath('//table//tr')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//td/div[@class="nir-widget--field nir-widget--news--date-time"]/text()').extract_first()# cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux.xpath('.//td/div[@class="nir-widget--field nir-widget--news--headline"]//a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//td/div[@class="nir-widget--field nir-widget--news--headline"]/a/@href').extract_first()
            

            #item = {
            #        'PUBSTRING': aux.xpath('.//td/div[@class="nir-widget--field nir-widget--news--date-time"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('.//td/div[@class="nir-widget--field nir-widget--news--headline"]//a/text()').extract_first(),
            #        'DOCLINK': aux.xpath('.//td/div[@class="nir-widget--field nir-widget--news--headline"]/a/@href').extract_first(),
            #        }
            base_url = 'https://investors.nov.com'
            aux_url = aux.xpath('.//td/div[@class="nir-widget--field nir-widget--news--headline"]/a/@href').extract_first()

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
           

        # follow pagination link vianext page url
        #next_page_url = response.xpath('//li[@class="pager-next"]/a/@href').extract_first()     
        #next_page_url = response.urljoin(next_page_url)
        #yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*NOV\b)(.|\s)*|(\bAbout.NOV\b)(.|\s)*'
        #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
        #re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ,test) regex to cut out about apache
        #item['Textbody'] = " ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text()').extract()) join connects scraped lists
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="node__content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item
       
       






















