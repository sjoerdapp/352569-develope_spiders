# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 23:30:54 2018

@author: Winchr01
"""

import scrapy
import re

class QuotessSpider(scrapy.Spider):
    name = '2020400ARV001_appachecorpcom'
    #start_urls = ['http://www.apachecorp.com/LatestFromApacheLoader.aspx?FeedID=8&Offset=0&Limit=500&SessionID=0.10923292219441927']
    start_urls = ['http://www.apachecorp.com/LatestFromApacheLoader.aspx?FeedID=8&Offset=0&Limit=30&SessionID=0.10923292219441927']
    

    def parse(self, response):
          #auxs = response.xpath('//tr[@class="rss-item"]')
          #auxs = response.xpath('/descendant::tr[@class="rss-item"]')
          for aux in response.xpath('//descendant::tr[@class="rss-item"]'):
              item = {
                      'Date': aux.xpath('./td[@class="v date"]/a/text()').extract_first(), # ./ is important; // does not work
                      'Header': aux.xpath('./td[@class="v title"]/a/text()').extract_first(),
                      'url': aux.xpath('./td[@class="v date"]/a/@href').extract_first(),
                      }
              url = aux.xpath('./td[@class="v date"]/a/@href').extract_first()
              request = scrapy.Request(url=url, callback=self.parse_details)
              request.meta['item'] = item
              yield request
        
    def parse_details(self, response):
        item = response.meta['item']
        #item['Headline'] = response.xpath('//h1[@class="newstitle"]/text()').extract()
        #re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ,test) regex to cut out about apache
        #item['Textbody'] = " ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text()').extract()) join connects scraped lists
        item['Textbody'] = re.sub(r'(\bAbout.Apache\b)(.|\s)*','' ," ".join(response.xpath('//div[@id="ndq-releasebody"]/div//text() | //div[@class="apache-article"]//text()').extract()))
        #response.css('div.ModuleBody > div > p::text').extract_first()
        item['url'] = response.url
        yield item
       
       