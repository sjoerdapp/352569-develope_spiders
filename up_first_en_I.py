import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### first two pages meaning latest 20 News
 
### FirstEnergy Corp 1|2 
### 2 scraper 1 für IR 2 für newsroom 
### IR  post request mit FormData
### go along pages with form request response is html
### goes back to 

class BHGE(scrapy.Spider):
    name = "First_en_I_2132600ARV001"
    #handle_httpstatus_list = [404]
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/First_en_I_2132600ARV001/',
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
            #'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'dtCookie=505ECDB3345E35C4C8E418EAD364CC4A|RkVDb3JwK1Byb2R8MQ; _gcl_au=1.1.792872037.1549577043; _ga=GA1.2.664597907.1549577043; _gid=GA1.2.563255784.1549577043; _ga=GA1.3.664597907.1549577043; _gid=GA1.3.563255784.1549577043; _gat=1; _gat_newTracker=1',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://investors.firstenergycorp.com',
            'Referer': 'https://investors.firstenergycorp.com/News/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {
            'pageIndex': '0',
            #'view_display_id': 'default',
            #'view_args': 'newsroom_page/916/',
            #'view_path': '/newsroom/financial-news',
            #'view_base_path': '', 
            #'iew_dom_id': '7c213868faab8562e0bea0a5746c516e903d5d3b4f1875d855f078c2b2f3fa63',
            #'pager_element': '0',
            #'page': '1',
            #'_drupal_ajax': '1',
            #'ajax_page_state[theme]': 'paychex',
            #'ajax_page_state[theme_token]': '',
            #'ajax_page_state[libraries]': 'cog/lib,core/html5shiv,paragraphs/drupal.paragraphs.unpublished,paychex/global_styles,system/base,views/views.ajax,views/views.module,views_infinite_scroll/views-infinite-scroll',
            }

        for num in range(0,2):  # loop iterating over different pages of ajax request; last number not in list anymore
            data['pageIndex'] = str(num)
            s_url = 'https://investors.firstenergycorp.com/News/4056944/NewsData'
            yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        #body= json.loads(response.text)  # load jason response from post request
        quotes = response.xpath('//div[contains(@class,"irwLoadingdata irwHasGA irwTableRowItem")]')
        #quotes = Selector(text=body).xpath('//div[@class="view-all-right"]') # define html body content as reference for the selector
        for quote in quotes:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = quote.xpath('.//div[@class="irwPRDate"]/text()').extract_first()
            item['HEADLINE']=  quote.xpath('.//h4/a/text()').extract_first()
            item['DOCLINK']=  quote.xpath('.//h4/a/@href').extract_first()
            
            base_url = 'https://investors.firstenergycorp.com'
            url= base_url + quote.xpath('.//h4/a/@href').extract_first()
            if ".pdf" not in url.lower(): # make url all lowercase so match is not casinsensitive anymore
                request = scrapy.Request(url=url, callback=self.parse_details)
                request.meta['item'] = item
                yield request

            else:
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [url]
                item['PUBSTRING'] = dat['PressReleaseDate']
                item['HEADLINE']= dat['Headline']
                item['DOCLINK']= url
                item['DESCRIPTION'] = ''
                yield item    

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(FirstEnergy\s*Corp.\s*\(\s*NYSE\s*:\s*FE\s*\)\s*is\s*dedicated\s*to\s*safety,\s*reliability\s*)(.|\s)*|(FirstEnergy\s*is\s*dedicated\s*to\s*safety,\s*reliability\s*)(.|\s)*|(Forward(.|\s*)Looking\s*Statements\s*:)(.|\s)*|(\bAbout\s*FirstEnergy\b)(.|\s)* | (\bAbout.FirstEnergy\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="col-xs-12"]//h2//text()|//div[@class="xn-content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = 'FEHLER'
            yield item
        else:
            yield item
        #if not item['DESCRIPTION']:
        #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*FirstEnergy\b)(.|\s)* | (\bAbout.FirstEnergy\b)(.|\s)*','' ," ".join(response.xpath('//p/text()').extract()))
        #    yield item
        #else: 
        #    yield item
        #pdf_test = response.xpath('//div[@class="cog--mq cog--mq-gutter"]/div//a/@href').extract_first() 
        #if pdf_test:
        #    if pdf_test.startswith('http'):  # checks whether link to pdf is relative of absolute link
        #        item['file_urls'] = [pdf_test]
        #        yield item
        #    else:
        #        base_url = 'https://www.paychex.com'
        #        item['file_urls'] = [base_url + pdf_test]
        #        yield item
        #else:    
        #    yield item               



        
            