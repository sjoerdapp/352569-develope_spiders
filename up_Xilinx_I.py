# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### scrape actual year, if more than 20 news, cut off

### Xilinx Inc 1|2
### 1st spider Investor press releases, 2nd spider news
### 1st spider mixed with  pdfs
### get request for different years, 
### back to 20060104

class QuotessSpider(scrapy.Spider):
    name = 'XIL_I_1063400ARV001'
    start_urls = ['http://investor.xilinx.com/press-releases?b28b0971_year%5Bvalue%5D=2018&op=Filter&b28b0971_widget_id=b28b0971&form_build_id=form-iMCd89KhFsnmHwrkHvxw_P9P3iIsBxYP0xYwwqUu92s&form_id=widget_form_base']
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/XIL_I_1063400ARV001/',
        }
    
    def parse(self, response):  # follow drop down menue for different years
         years = list(range(2019, 2021)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'http://investor.xilinx.com/press-releases?b28b0971_year%5Bvalue%5D={}&op=Filter&b28b0971_widget_id=b28b0971&form_build_id=form-iMCd89KhFsnmHwrkHvxw_P9P3iIsBxYP0xYwwqUu92s&form_id=widget_form_base'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    def parse_next(self, response):
        auxs = response.xpath('//div[@class="nir-widget--list"]/article')
        if len(auxs) > 20:
            auxs = auxs[0:20]

        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//div[contains(@class, "date-time")]//text()').extract_first()
            item['HEADLINE']= aux.xpath('./a[2]/text()').extract_first()
            item['DOCLINK']= aux.xpath('./a[2]/@href').extract_first()

            base_url = 'http://investor.xilinx.com'
            aux_url = aux.xpath('./a[2]/@href').extract_first()

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


            #aux_url = aux.xpath('.//div[@class="nir-widgets-file-link"]/a/@href').extract_first()
            #if aux_url.startswith('http'):
            #    item_url= aux_url
            #    item['file_urls'] = [item_url]
            #    item['PUBSTRING'] = aux.xpath('./div[@class="nir-widget--field nir-widget--news--date-time"]/text()').extract_first()
            #    item['HEADLINE']= aux.xpath('./a/text()').extract_first()
            #    item['DOCLINK']= item_url
            #    item['DESCRIPTION'] = ''
            #    yield item
#
#            #else:
#            #    base_url = 'http://investor.xilinx.com'
#            #    item_url= base_url + aux_url
#            #    item['file_urls'] = [item_url]
#            #    item['PUBSTRING'] = aux.xpath('./div[@class="nir-widget--field nir-widget--news--date-time"]/text()').extract_first()
#            #    item['HEADLINE']= aux.xpath('./a/text()').extract_first()
#            #    item['DOCLINK']= item_url
#            #    item['DESCRIPTION'] = ''
            #    yield item
                
            
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Xilinx\b)(.|\s)* | (\bAbout.Xilinx\b)(.|\s)*'
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
            #item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains( @class, "main-content")]/p//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "main-block")]/article//div[@class= "node__content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item



       






















