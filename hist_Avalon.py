import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Avalonbay Communities 1|1
### post request formdata -> only very little formdata
### back to 20020531

class BHGE(scrapy.Spider):
    name = "AVA_3034500ARV001"
    #handle_httpstatus_list = [404]
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/AVA_3034500ARV001/',
        }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    def start_requests(self):
        headers = {
            #'accept': 'application/json, text/javascript, */*; q=0.01'
            #'CSRF-Token': 'undefined',
            'accept': '*/*',
            #'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 
            'origin': 'http://investors.avalonbay.com',
            'Referer': 'http://investors.avalonbay.com/News',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            }

        data = {
            'pageIndex': '0'
            #'view_name' : 'dyamic_cards_with_filters',
            #'view_display_id': 'block_1',
            #'view_args': 'dyamic_cards_with_filters/109541/0/1582816',
            #'view_path': '/views/ajax',
            #'view_base_path': '',
            #'view_dom_id': 'f950b72b00e43adae46270566a492b3f57f151aabf50c40403c6e0ad493a26b5',
            #'pager_element': '0',
            #'type': 'news_item',
            #'field_categories_target_id': 'All',
            #'year': 'all',
            #'page': '1',
            #'_drupal_ajax': '1',
            #'ajax_page_state[theme]': 'bhge',
            #'ajax_page_state[theme_token]': '',
            #'ajax_page_state[libraries]': 'bhge/global-styling,bhge_dynamic_filter_comp/bhge-video-popup,bhge_dynamic_filter_comp/bhge-views-counter,bhge_dynamic_filter_comp/bhge-youtube-popup,bhge_marketo/marketo,calendar/calendar.theme,classy/base,classy/messages,core/drupal.date,core/drupal.date,core/html5shiv,core/normalize,paragraphs/drupal.paragraphs.unpublished,seven/global-styling,views/views.ajax,views/views.ajax,views/views.module,views/views.module,views_infinite_scroll/views-infinite-scroll,views_infinite_scroll/views-infinite-scroll' ,
            }

        for num in range(0,73):  # loop iterating over different pages of ajax request
            data['pageIndex'] = str(num)
            s_url = 'http://investors.avalonbay.com/News/103145/NewsData?pageIndex=0'
            yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        #dat = json.loads(response.text)  # load jason response from post request
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        quotes = response.xpath('//div[@class="col-sm-10"]')  # define html body content as reference for the selector
        for quote in quotes:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = quote.xpath('.//div[@class="irwPRDate"]/text()').extract_first()
            item['HEADLINE']= quote.xpath('./h4/a/text()').extract_first()
            item['DOCLINK']= quote.xpath('.//div[@class="irwPRSummary irwHidden"]/a/@href').extract_first()
            #item = {
            #          'PUBSTRING': quote.xpath('.//div[@class="irwPRDate"]/text()').extract_first(),
            #          'HEADLINE': quote.xpath('.//div[@class="irwPRSummary irwHidden"]/p/text()').extract_first(),
            #          'DOCLINK': quote.xpath('.//div[@class="irwPRSummary irwHidden"]/a/@href').extract_first(),
            #          }
            base_url = 'http://investors.avalonbay.com'
            aux_url = quote.xpath('.//div[@class="irwPRSummary irwHidden"]/a/@href').extract_first()
            
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout.AvalonBay.Communities\b)(.|\s)*'
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="irwFilePageBody"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item               



        
            