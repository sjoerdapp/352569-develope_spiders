import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
 
### IHS Markit Ltd 1|1 
### classic get request, 
### pubstring has to be extracted from detail page 
### goes back to 20040112


class BHGE(scrapy.Spider):
    name = "IHS_Mark_9900188ARV001"
    #handle_httpstatus_list = [404]
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/IHS_Mark_9900188ARV001/',
        }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    start_urls = ['https://news.ihsmarkit.com/news-releases']
    #count = 0
    
       
    def parse(self, response):
        #body= json.loads(response.text)  # load jason response from post request
        quotes = response.xpath('//div[@class="pane-content"]//div[@class="item-list"]//div[@class="view-inner-wrapper"]//span[@class="field-content title"]')
        #quotes = Selector(text=body).xpath('//div[@class="view-all-right"]') # define html body content as reference for the selector
        for quote in quotes:
            item = SwisscomIvCrawlerItem()
            #item['PUBSTRING'] = quote.xpath('./td[1][not(contains(text(), "Date"))]/text()').extract_first(),
            item['HEADLINE']=  quote.xpath('./a/text()').extract_first()
            item['DOCLINK']=  quote.xpath('./a/@href').extract_first()
            
            base_url = 'https://news.ihsmarkit.com'
            url= base_url + quote.xpath('./a/@href').extract_first()
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request

        # follow pagination link
        next_page_url = response.xpath('//div[@class="item-list"]//ul[@class="pager"]//li[@class="pager-next"]/a/@href').extract_first()
        if next_page_url:
            aux_url = 'https://news.ihsmarkit.com'
            next_page_url = aux_url + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse)   

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*IHS\s*Markit\b)(.|\s)*|(\bAbout.IHS.Markit\b)(.|\s)*|(\bAbout\s*Markit\b)(.|\s)*' 
        item['PUBSTRING'] = response.xpath('//div[@class="panel-pane pane-node-date"]/div[@class="pane-content"]/text()').extract_first()
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "fieldpressreleasesubheadline")]//text()|//div[@class="panel-pane pane-pr-body"]/div[@class="pane-content"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        pdf_link = response.xpath('//div[@class="panel-pane pane-pr-body"]//div[@class="pane-content"]//p[contains(text(), "To read the release in its entirety")]/a/@href').extract_first()
        #yield item
        if pdf_link and pdf_link != 'https://www.markiteconomics.com/Public/Release/PressReleases':
            item['file_urls'] = [pdf_link]
            item['DESCRIPTION'] = ''
            yield item
        else: 
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
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



        
            