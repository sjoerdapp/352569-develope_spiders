import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Paychex Inc. 1|2
### post with Formdata (FormRequest)
### 1st spider financial news
### back to 20131206


class BHGE(scrapy.Spider):
    name = "PAY_I_6333000ARV001"
    #handle_httpstatus_list = [404]
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/PAY_I_6333000ARV001/',
        }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            #'Cookie': '_ga=GA1.2.1216204916.1547660679',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.paychex.com',
            'Referer': 'https://www.paychex.com/newsroom/financial-news',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {
            'view_name': 'view_all_paragraph',
            'view_display_id': 'default',
            'view_args': 'newsroom_page/916/',
            'view_path': '/newsroom/financial-news',
            'view_base_path': '', 
            'iew_dom_id': '7c213868faab8562e0bea0a5746c516e903d5d3b4f1875d855f078c2b2f3fa63',
            'pager_element': '0',
            'page': '1',
            '_drupal_ajax': '1',
            'ajax_page_state[theme]': 'paychex',
            'ajax_page_state[theme_token]': '',
            'ajax_page_state[libraries]': 'cog/lib,core/html5shiv,paragraphs/drupal.paragraphs.unpublished,paychex/global_styles,system/base,views/views.ajax,views/views.module,views_infinite_scroll/views-infinite-scroll',
            }

        for num in range(0,6):  # loop iterating over different pages of ajax request; last number not in list anymore
            data['page'] = str(num)
            s_url = 'https://www.paychex.com/views/ajax?_wrapper_format=drupal_ajax'
            yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        dat = json.loads(response.text)  # load jason response from post request
        body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        quotes = Selector(text=body).xpath('//div[@class="view-all-right"]') # define html body content as reference for the selector
        for quote in quotes:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = quote.xpath('.//div[@class="div--type"]/text()').extract_first().split(" - ")[1].split("\n")[0] # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= quote.xpath('.//div[@class="div--title"]/a/text()').extract_first()
            item['DOCLINK']= quote.xpath('.//div[@class="div--title"]/a/@href').extract_first()
            
            base_url = 'https://www.paychex.com'
            aux_url = quote.xpath('.//div[@class="div--title"]/a/@href').extract_first()
            
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
             

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Paychex\b)(.|\s)* | (\bAbout.Paychex\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="cog--mq cog--mq-gutter"]//text()[not(ancestor::div[contains(@class, "newsroom-author field")])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        pdf_test = response.xpath('//div[@class="cog--mq cog--mq-gutter"]/div//a/@href').extract_first() 
        if pdf_test and '.pdf' in pdf_test:
            if pdf_test.startswith('http'):  # checks whether link to pdf is relative of absolute link
                item['file_urls'] = [pdf_test]
                yield item
            else:
                base_url = 'https://www.paychex.com'
                item['file_urls'] = [base_url + pdf_test]
                yield item
        else:    
            yield item               



        
            