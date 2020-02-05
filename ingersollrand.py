import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Ingersoll Rand Plc 1|1
### classic post.payload with json
### some doclincs are pdfs

class BHGE(scrapy.Spider):
    name = "INGR_2097700ARV001"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://sp5001/INGR_2097700ARV001/',
        }
    
    def start_requests(self):
        headers = {           
            'Cookie': 's_fid=28FC7A4F102D95B5-31A335B997F16D31; s_cc=true; _fbp=fb.1.1548021474707.806907153; s_gnr=1548021490426-New; s_sq=trane-ir-corp-ingersollrand%252Ctraneirglobalprod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dirc%25253Aglobal%25253Anews%2526link%253DView%252520All%252520News%252520Releases%2526region%253Dpage%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dirc%25253Aglobal%25253Anews%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fir.ingersollrand.com%25252Finvestors%25252Fpress-releases-and-events%25252Fpress-releases%25252Fdefault.aspx%2526ot%253DA; _ga=GA1.2.579428182.1548021493; _gid=GA1.2.1790252220.1548021493; bpazaws52gukakzc__ctrl0_ctl60_uccaptcha=B8OiVP/tudfMCGa1WPXdj0RTkhMOx4tFGGVHJHKivWw4pWEDk82uBXz59FZIfiI75KcnNPdMz+BuAREmlLXfytHcS+tYBi5KUt2FaoIyGm/Fqh38/BC+4RTZTWx6YviPTCaNNzLNb5dAKB3Xkgrllg==; tp=3599; s_ppv=irc%253Ana%253Aus%253Aen%253Awelcome%2520to%2520ingersoll%2520rand%253Anews%2C39%2C39%2C1410',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            #'Cookie': '_ga=GA1.2.1216204916.1547660679',
            #'Host': 'investor.twitterinc.com',
            'Origin': 'http://ir.ingersollrand.com',
            'Referer': '//ir.ingersollrand.com/investors/press-releases-and-events/press-releases/default.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"serviceDto":{"ViewType":"2","ViewDate":"","RevisionNumber":"1","LanguageId":"1","Signature":"","ItemCount":-1,"StartIndex":0,"TagList":[],"IncludeTags":True},"pressReleaseBodyType":3,"pressReleaseCategoryWorkflowId":"00000000-0000-0000-0000-000000000000","pressReleaseSelection":3,"year":2018}
        for year in list(range(2001, 2020)):  # loop iterating over different pages of ajax request
            data['year'] = year
            s_url = 'http://ir.ingersollrand.com/Services/PressReleaseService.svc/GetPressReleaseList'
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
            item = {
                      'PUBSTRING': dat['PressReleaseDate'],
                      'HEADLINE': dat['Headline'],
                      'DOCLINK': dat['LinkToDetailPage'],
                      }
            base_url = 'http://ir.ingersollrand.com'
            url= base_url + dat['LinkToDetailPage']
            if ".pdf" not in url: 
                request = scrapy.Request(url=url, callback=self.parse_details)
                request.meta['item'] = item
                yield request

            else:
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [url]
                item['PUBSTRING'] = dat['PressReleaseDate']
                item['HEADLINE']= dat['Headline']
                item['DOCLINK']= url
                yield item 

    def parse_details(self, response):
        item = response.meta['item']
        item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Ingersoll\s*Rand\b)(.|\s)* |(\bAbout.Ingersoll.Rand\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="q4default"]//text()').extract()))
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Ingersoll\s*Rand\b)(.|\s)* |(\bAbout.Ingersoll.Rand\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="ModuleBody"]//text()').extract()))
            yield item
        else:
            yield item
           



        
            