# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Linde plc 1|1
### marger with paxair, daher short history
### normal get request
### goes back to 20181022



class QuotessSpider(scrapy.Spider):
    name = 'Linde_9950726ARV001'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Linde_9950726ARV001/',
        }
    start_urls = ['https://www.lindeplc.com/en/news-media',
                  'https://www.lindeplc.com/en/news-media?s={"p":{"c":2}}'
                   ]
    
    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(2007, 2020))
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.devonenergy.com/news/{}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)
    
    def parse(self, response):
        auxs = response.xpath('//section/article')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./p/text()').extract_first()
            item['HEADLINE']= aux.xpath('./h3/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('./h3/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./p/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./h3/a/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./h3/a/@href').extract_first(),
            #        }
            base_url = 'https://www.lindeplc.com'
            aux_url= aux.xpath('./h3/a/@href').extract_first()
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Linde\s*plc\b)(.|\s)* | (\bAbout.Linde.plc\b)(.|\s)*'
        #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
        #re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ,test) regex to cut out about apache
        #item['Textbody'] = " ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text()').extract()) join connects scraped lists
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="list-container"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item
       
       






















