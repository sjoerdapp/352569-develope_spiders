import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Baker hugehes a Genereal Electric Comapny 2|2
### Post request
### Html comes in json response body
### DESCRIPTION: selector with or expression as both nodes are on the same level need structure to get everything
### goes back to 20170703


class BHGE(scrapy.Spider):
    name = "BHGE_II_2025300ARV002"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/BHGE_II_2025300ARV002/',
        }
    #handle_httpstatus_list = [404]
    #custom_settings = {
        #'ROBOTSTXT_OBEY':'False',
        #'USER_AGENT': "'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
        #}
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    start_urls = ['https://www.bhge.com/newsroom']
    #count = 0
    
    def parse(self, response):
    #def start_requests(self):
        auxs = response.xpath('//ul[contains(@class, "card-slider")]/li')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//div[@class="date"]/text()').extract_first()
            item['HEADLINE']= aux.xpath('.//h2/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//h2/a/@href').extract_first()

            base_url = 'https://www.bhge.com/'
            aux_url = aux.xpath('.//h2/a/@href').extract_first()
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


    
        headers = {
            #'accept': 'application/json, text/javascript, */*; q=0.01'
            #'CSRF-Token': 'undefined',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 
            'origin': 'https://www.bhge.com',
            'Referer': 'https://www.bhge.com/newsroom',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
            }

        data = {
            'view_name' : 'dyamic_cards_with_filters',
            'view_display_id': 'block_1',
            'view_args': 'dyamic_cards_with_filters/109541/0/1582816',
            #'view_path': '/views/ajax',
            'view_path': '/newsroom',
            'view_base_path': '',
            'view_dom_id': 'f950b72b00e43adae46270566a492b3f57f151aabf50c40403c6e0ad493a26b5',
            'pager_element': '0',
            'type': 'news_item',
            'field_categories_target_id': 'All',
            'year': 'all',
            'page': '0',
            '_drupal_ajax': '1',
            'ajax_page_state[theme]': 'bhge',
            'ajax_page_state[theme_token]': '',
            'ajax_page_state[libraries]': 'bhge/global-styling,bhge_dynamic_filter_comp/bhge-video-popup,bhge_dynamic_filter_comp/bhge-views-counter,bhge_dynamic_filter_comp/bhge-youtube-popup,bhge_marketo/marketo,calendar/calendar.theme,classy/base,classy/messages,core/drupal.date,core/drupal.date,core/html5shiv,core/normalize,paragraphs/drupal.paragraphs.unpublished,seven/global-styling,views/views.ajax,views/views.ajax,views/views.module,views/views.module,views_infinite_scroll/views-infinite-scroll,views_infinite_scroll/views-infinite-scroll' ,
            }
        for num in range(0,12):  # loop iterating over different pages of ajax request
            data['page'] = str(num)
            s_url = 'https://www.bhge.com/views/ajax?_wrapper_format=drupal_ajax'
            yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse_next )
    
    def parse_next(self, response):
        dat = json.loads(response.text)  # load jason response from post request
        body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        for quote in quotes:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = quote.xpath('./div[@class="views-field views-field-created"]/span[@class="field-content"]/text()').extract_first()
            item['HEADLINE']= quote.xpath('./div[@class="views-field views-field-title"]/span[@class="field-content"]/a/text()').extract_first()
            item['DOCLINK']= quote.xpath('./div[@class="views-field views-field-title"]/span[@class="field-content"]/a/@href').extract_first()
            #item = {
            #          'PUBSTRING': quote.xpath('./div[@class="views-field views-field-created"]/span[@class="field-content"]/text()').extract_first(),
            #          'HEADLINE': quote.xpath('./div[@class="views-field views-field-title"]/span[@class="field-content"]/a/text()').extract_first(),
            #          'DOCLINK': quote.xpath('./div[@class="views-field views-field-title"]/span[@class="field-content"]/a/@href').extract_first(),
            #          }
            base_url = 'https://investors.bhge.com'
            aux_url = quote.xpath('normalize-space(./div[@class="views-field views-field-title"]/span[@class="field-content"]/a/@href)').extract_first()
            
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
        name_regex = r'(\bAbout.BHGE\b)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout.Baker.Hughes\b)(.|\s)*| (\bAbout\s*Baker\s*Hughes\b)(.|\s)*'
        #head_regex = r"(Investor\s*Contact:\s*ht(.*)version.\s*)"
        #item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="content"]//section[@data-component="c24-body-text"]//text() |//div[@class="content"]//div[@class="wysiwyg-copy"]//text()').extract()), flags=re.IGNORECASE)
        item['DESCRIPTION'] =  re.sub(name_regex,'' ," ".join(response.xpath('//div[@class= "wysiwyg-copy"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] =  re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "wysiwyg-copy")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                  item['DESCRIPTION'] = 'FEHLER'
                  yield item
            else:
                  yield item
        else:
            yield item                



        
            