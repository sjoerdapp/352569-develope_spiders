# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy


class QuotessSpider(scrapy.Spider):
    name = 'cisco_final'
    start_urls = ['https://investor.cisco.com/investor-relations/news-and-events/news/default.aspx']

    def parse(self, response):
         years = response.css('div.ModuleYearNavContainerInner')
         years = years.css('a.ModuleYearLink::attr(href)').extract()
         for year in years:
             yield scrapy.Request(url=year, callback=self.parse_next)

    def parse_next(self, response):
          auxs = response.css('div.ModuleItemRow')
          for aux in auxs:
              item = {
                      'Date': aux.css('span.ModuleDate::text').extract(),
                      'Header': aux.css('span.ModuleHeadline::text').extract(),
                      'url': aux.css('div.header > a.ModuleHeadlineLink::attr(href)').extract(),
                      }
              url= aux.css('div.header > a.ModuleHeadlineLink::attr(href)').extract_first()
              request = scrapy.Request(url=url, callback=self.parse_details)
              request.meta['item'] = item
              yield request
        
    def parse_details(self, response):
        item = response.meta['item']
        item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['Textbody'] = response.css('div.ModuleBody > div > p::text').extract_first()
        item['url'] = response.url
        yield item
       
       