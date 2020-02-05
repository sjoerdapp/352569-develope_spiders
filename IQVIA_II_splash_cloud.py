import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
#from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

class BHGE(scrapy.Spider):
    name = "IQVIA_II_9900204ARV002"
    #handle_httpstatus_list = [404]
    #custom_settings = {
    #     'JOBDIR' : 'None',
    #     'FILES_STORE' : 's3://sp5001/PAY_II_6333000ARV002/',
    #    }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
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
    
    def start_requests(self):
        urls = ['https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[1,2,2019]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[20,11,2018]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[1,8,2018]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[17,5,2018]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[18,4,2018]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[15,3,2018]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[27,11,2018]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[15,9,2017]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                'https://www.iqvia.com/newsroom#t=Corporate&f:pdate=[5,5,2017]&f:ptype=[Article,News,Press%20release,Media%20coverage]',
                ]        ]
        for url in urls:
            url = 'https://www.willistowerswatson.com/en/press#first={}&sort=%40displayz45xdate%20descending'
            request = SplashRequest(url=url, splash_headers={'Authorization': basic_auth_header('535209af07354fbbb4110611b27f7504', '')}, args={'wait': 0.5, 'timeout':15}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/201,00101 Firefox/62.0'}, callback=self.parse)
            yield request
        #yield SplashRequest(
        #    url='https://www.willistowerswatson.com/en/press#first=10&sort=%40displayz45xdate%20descending',
        #    callback=self.parse,
        #)

    def parse(self, response):
          auxs = response.xpath('//div[@class="CoveoResultList"]/div/a')
          for aux in auxs:
              item = {
                      'PUBSTRING': aux.xpath('./div[@class="coveo-date"]/text()').extract_first(),
                      'HEADLINE': aux.xpath('./div[@class="coveo-title"]/p/text()').extract_first(),
                      'DOCLINK': aux.xpath('./@href').extract_first(),
                      }
              url= aux.xpath('./@href').extract_first()
              request = scrapy.Request(url=url, callback=self.parse_details)
              request.meta['item'] = item
              yield request
        
    def parse_details(self, response):
        item = response.meta['item']
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['Textbody'] = re.sub(r'(\bAbout\s*Willis\s*Towers\s*Watson\b)(.|\s)* | (\bAbout.Wiilis.Towers.Watson\b)(.|\s)*','' ," ".join(response.xpath('//div [@class="article-wrapper"]/article/section//text()').extract()))
        item['url'] = response.url
        yield item
       
       


        
            