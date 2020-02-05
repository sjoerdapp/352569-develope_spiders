import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Ball Corporation 1|1
### actually 3 pages: News Releases Ball Corp; News Releases Ball Aerospace; News Releases IR
### only scraping last as other 2 have empty detail pages
### history goes back to 19960717


class BHGE(scrapy.Spider):
    name = "Ball_2025700ARV001"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Ball_2025700ARV001/',
        }
    
    start_urls = ['http://phx.corporate-ir.net/phoenix.zhtml?c=115234&p=irol-news&nyo=1'] 
    user_agent = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36']    
    
    def parse(self, response):  # follow drop down menue for different years
         years = list(range(0, 24)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'http://phx.corporate-ir.net/phoenix.zhtml?c=115234&p=irol-news&nyo={}'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

   
    
    def parse_next(self, response):
        auxs = response.xpath('//td[@class="ccbnOutline"]//table//tr[not(@class="ccbnBgTblTtl")]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./td[1]/span/text()').extract_first()
            item['HEADLINE']= aux.xpath('./td[2]/span/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('./td[2]/span/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./td[1]/span/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./td[2]/span/a/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./td[2]/span/a/@href').extract_first(),
            #        }
            base_url = 'http://phx.corporate-ir.net/'
            aux_url = aux.xpath('./td[2]/span/a/@href').extract_first()
            
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
        name_regex = r"""(\bForward.\s*Looking\s*Statements\b)(.|\s)*|(\bAbout.Ball.Corporation\b)(.|\s)*|(\bAbout\s*Ball\s*Corporation\b)(.|\s)* """
        if 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath(' //span[@class="ccbnTxt"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item


        
            