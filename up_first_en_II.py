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
### first pages latest 20 News
 
### FirstEnergy Corp 2|2 
### 2 scraper 1 für IR 2 für newsroom 
### Newsroom post request mit FormData
### all items come with one querry
### Attention post request uses multipart formdata -> in this case just use normal content tye (not multipart) and send Formdata as dict
### goes back to 20130101

class BHGE(scrapy.Spider):
    name = "First_en_II_2132600ARV002"
    #handle_httpstatus_list = [404]
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/First_en_II_2132600ARV002/',
        }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    start_urls = ['https://www.firstenergycorp.com/content/fecorp/fehome.searcharticles.json']
    #count = 0
    
    #def start_requests(self):
        #headers = {
        #    'Accept': 'application/json, text/javascript, */*; q=0.01',
        #    'Accept-Encoding': 'gzip, deflate, br',
        #    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        #    'Connection': 'keep-alive',
        #    #'Content-Length': '316',
        #    'Content-Type': 'application/json; charset=UTF-8',
        #    'Cookie': 'BIGipServercustweb_ssl_pool=1551920276.47873.0000; JSESSIONID=pds6pyofsv9p1t4nb7jnx3w5p; dtCookie=505ECDB3345E35C4C8E418EAD364CC4A|RkVDb3JwK1Byb2R8MQ; BIGipServerfecorp-ssl-pool=3984616596.47873.0000; _gcl_au=1.1.792872037.1549577043; _ga=GA1.2.664597907.1549577043; _gid=GA1.2.563255784.1549577043',
        #     #'Host': 'investor.twitterinc.com',
        #    'Origin': 'https://www.firstenergycorp.com',
        #    'Referer': 'https://www.firstenergycorp.com/newsroom/news-archive.html',
        #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        #    #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
        #    'X-Requested-With': 'XMLHttpRequest',
        #   }

        #data = {
        #    'fromResourceNode': '/content/fecorp/newsroom/news-archive/jcr:content/mainpar/articlearchive',
        #    #'view_display_id': 'default',
        #    #'view_args': 'newsroom_page/916/',
        #    #'view_path': '/newsroom/financial-news',
        #    #'view_base_path': '', 
        #    #'iew_dom_id': '7c213868faab8562e0bea0a5746c516e903d5d3b4f1875d855f078c2b2f3fa63',
        #    #'pager_element': '0',
        #    #'page': '1',
        #    #'_drupal_ajax': '1',
        #    #'ajax_page_state[theme]': 'paychex',
        #    #'ajax_page_state[theme_token]': '',
        #    #'ajax_page_state[libraries]': 'cog/lib,core/html5shiv,paragraphs/drupal.paragraphs.unpublished,paychex/global_styles,system/base,views/views.ajax,views/views.module,views_infinite_scroll/views-infinite-scroll',
        #    }

        #for num in range(0,6):  # loop iterating over different pages of ajax request; last number not in list anymore
            #data['page'] = str(num)
        #s_url = 'https://www.firstenergycorp.com/content/fecorp/fehome.searcharticles.json'
        #yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body= json.loads(response.text)  # load jason response from post request
        quotes = body['news'][0:20]
        #quotes = Selector(text=body).xpath('//div[@class="view-all-right"]') # define html body content as reference for the selector
        for quote in quotes:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = quote['newsDate']
            item['HEADLINE']= quote['newsDescription']
            item['DOCLINK']= quote['newsLink']
            
            base_url = 'https://www.firstenergycorp.com'
            url= base_url + quote['newsLink']
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
        name_regex = r'(FirstEnergy\s*is\s*a\s*diversified\s*energy\s*company\s*dedicated\s*to\s*safety,\s*reliability\s*)(.|\s)*|(FirstEnergy\s*Corp.\s*\(\s*NYSE\s*:\s*FE\s*\)\s*is\s*dedicated\s*to\s*safety,\s*reliability\s*)(.|\s)*|(FirstEnergy\s*is\s*dedicated\s*to\s*safety,\s*reliability\s*)(.|\s)*|(Forward(.|\s*)Looking\s*Statements\s*:)(.|\s)*|(\bAbout\s*FirstEnergy\b)(.|\s)* | (\bAbout.FirstEnergy\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//span[@class="subtitle"]//text()|//article[@class="module text-module"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//p/text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
        else: 
            yield item
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



        
            