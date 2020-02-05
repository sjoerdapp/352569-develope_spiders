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
### take last 20 news

### Newmont Mining corporation 1|1
### classic post with payload and json
### back to 20050103
class BHGE(scrapy.Spider):
    name = "New_Min_2128600ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/New_Min_2128600ARV001/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': '_ga=GA1.2.1924729719.1550162660; _gid=GA1.2.286262920.1550162660; _hjIncludedInSample=1; bpazaws52gukakzc__ctrl0_ctl54_uccaptcha=7XEFCJDzq/BNQWiuSisNmk4YnJ2/1xQLS4K/hyIfEoc4qgw5m39W4OwLpWSROVqjSNWME+fpDsWb65cvxciOzlz7sscVEec81at6QwLTlOC29Vg1RVqiHAPrWABXWlKD5zdcBolfByUad3OLEmNqzg==; bpazaws52gukakzc__ctrl0_ctl63_uccaptcha=p+sAHHhSBVXSUXXkVxCu2xdRxmDjgtH28LIKdj6qkjoYFC+ok9jRkUwbm7W9fkj1tpsMSvlQGsOrtGF48+GCTmrFKcSpuvZZtwMo+iPUEOJBHQoZotieKXlNFkgmM66Q5d+CxdfFs6uLsCiVGTShbQ==; __unam=2bd4467-168ece50440-5684d44b-14; _dc_gtm_UA-5171119-1=1',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.newmont.com',
            'Referer': 'https://www.newmont.com/newsroom/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        #data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","pressReleaseBodyType":0,"pressReleaseSelection":3,"excludeSelection":1,"year":2018}
        data ={"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","ItemCount":10,"StartIndex":0,"Signature":"","TagList":["corporate"]},"year":-1,"pressReleaseSelection":3,"pressReleaseBodyType":3,"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0"}
        for year in list(range(0, 12, 10)):  # loop iterating over different pages of ajax request
            data["serviceDto"]['StartIndex'] = year
            s_url = 'https://www.newmont.com/Services/PressReleaseService.svc/GetPressReleaseList'
            yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
        #for num in range(0,11):  # loop iterating over different pages of ajax request
        #    data['page'] = str(num)
        #    s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
        #    yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        #quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        for dat in body['GetPressReleaseListResult']:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['PressReleaseDate']
            item['HEADLINE']= dat['Headline']
            item['DOCLINK']= dat['LinkToDetailPage']
            #item = {
            #          'PUBSTRING': dat['PressReleaseDate'],
            #          'HEADLINE': dat['Headline'],
            #          'DOCLINK': dat['LinkToDetailPage'],
            #          }
            base_url = 'https://www.newmont.com'
            aux_url = dat['LinkToDetailPage']
            if aux_url.startswith('http'):
                url = aux_url
                if ".pdf" not in url.lower(): # make url all lowercase so match is not casinsensitive anymore
                    request = scrapy.Request(url=url, callback=self.parse_details, dont_filter=True)
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
            else:  
                url = base_url + aux_url
                if ".pdf" not in url.lower(): # make url all lowercase so match is not casinsensitive anymore
                    request = scrapy.Request(url=url, callback=self.parse_details, dont_filter=True)
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
        name_regex = r'(Cautionary(.|\s*)Statement\s*:)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Newmont\b)(.|\s)* |(\bAbout.Newmont.Mining.Corporation\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="q4default"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        #yield item
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="ModuleBody"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()[not(ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            #yield item
            if not item['DESCRIPTION']:
                ht = 'https:'
                url = ht + response.xpath('//div[@class="ModuleLinks"]/a/@href').extract_first() 
                item['file_urls'] = [url]
                item['DOCLINK'] = url
                item['DESCRIPTION'] = ''
                yield item
            elif not re.search('[a-zA-Z]', item['DESCRIPTION']):
                ht = 'https:'
                url = ht + response.xpath('//div[@class="ModuleLinks"]/a/@href').extract_first() 
                item['file_urls'] = [url]
                item['DOCLINK'] = url
                item['DESCRIPTION'] = ''
                yield item

            else:
                yield item

        else:     
            yield item
           



        
            