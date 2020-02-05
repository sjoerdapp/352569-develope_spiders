import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Digital Realty Trust 1|1
### classic post with payload and json
### goes back to 20041104

class BHGE(scrapy.Spider):
    name = "DigReal_9900101ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/DigReal_9900101ARV001/',
        }
    
    def start_requests(self):
        headers = {           
            'Cookie': 'Cookie: _gcl_au=1.1.318713842.1548109382; _biz_sid=64bde7; _fbp=fb.1.1548109382354.1750803567; _biz_uid=763be9ab75d94327b701ee0313740eee; _biz_flagsA=%7B%22Version%22%3A1%2C%22XDomain%22%3A%221%22%7D; _ga=GA1.2.984834625.1548109383; _gid=GA1.2.1939606624.1548109383; _ga=GA1.3.984834625.1548109383; _gid=GA1.3.1939606624.1548109383; bpazaws52gukakzc__ctrl0_ctl42_uccaptcha=mqynJ0ej+GQoWZhDBPQOsHFyD0pYcj94uv7w4Pjmgek9zkzP4N0AkrCbCcIhbJ0K9eTUuqkE6gUhbKHbf2IE+XbgI/NI1REs1qcDwte2ypxxUyGMeUzvwDg9hg0s68k/ZPUu+9wvDAnlgpo9PBIf6g==; _biz_nA=6; _biz_pendingA=%5B%5D; _gali=newsYear',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            #'Cookie': '_ga=GA1.2.1216204916.1547660679',
            #'Host': 'investor.twitterinc.com',
            'Origin': 'https://investor.digitalrealty.com',
            'Referer': 'https://investor.digitalrealty.com/news-and-events/news/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseBodyType":0,"pressReleaseSelection":3,"pressReleaseCategoryWorkflowId":"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0","excludeSelection":1,"year":2018}
        for year in list(range(2004, 2020)):  # loop iterating over different pages of ajax request
            data['year'] = year
            s_url = 'https://investor.digitalrealty.com/Services/PressReleaseService.svc/GetPressReleaseList'
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
            base_url = 'https://investor.digitalrealty.com'
            aux_url = dat['LinkToDetailPage']
            
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bSafe\s*Harbor\s*Statement\b)(.|\s)*|(\bAbout\s*Digital\s*Realty\b)(.|\s)* |(\bAbout.Digital.Realty\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="module_body"]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            pdf_url = 'https:' + response.xpath('//div[@class="module_links"]/a/@href').extract_first()
            item['file_urls'] = [pdf_url]
            item['DOCLINK'] = pdf_url
            item['DESCRIPTION'] = ''
            yield item
        else:
            yield item



        
            