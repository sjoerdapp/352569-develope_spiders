import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem
import datetime

### Aptiv PLC 2|2
### spider scraping news room
### zeigt alle news auf einmal 
### hiessen bis 2017/12 Delphi -> daher also exclude About Delphi
### 2nd news room
### classic post
### need to convert digits into dates
### back to 20171205

class BHGE(scrapy.Spider):
    name = "APT_II_5392700ARV002"
    
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/APT_II_5392700ARV002/',
        }
    
    def start_requests(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            #'Content-Length': '316',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'ARRAffinity=bc0cf902d87a0116b3568f9001a1762206b045dfdddbec8796fa2b0eb2a3b0a7; sf-trckngckie=f0717e6c-e38e-49a2-9d59-b684062a7253; _gcl_au=1.1.234716146.1549401821; _ga=GA1.2.475147106.1549401821; _gid=GA1.2.2040596857.1549401821; _fbp=fb.1.1549401821008.2147064948; OptanonConsent=landingPath=NotLandingPage&datestamp=Tue+Feb+05+2019+22%3A24%3A33+GMT%2B0100+(Mitteleurop%C3%A4ische+Normalzeit)&version=3.6.20&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_5255%3A1%2C0_5254%3A1%2C0_5252%3A1%2C101%3A1%2C102%3A1%2C103%3A1%2C104%3A1%2C105%3A1%2C106%3A1%2C107%3A1%2C108%3A1&AwaitingReconsent=false',
             #'Host': 'investor.twitterinc.com',
            'Origin': 'https://www.aptiv.com',
            'Referer': 'https://www.aptiv.com/media/search',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
            'X-Requested-With': 'XMLHttpRequest',
           }

        data = {"Group":"mediaandassets","ItemsPerPage":386,"OrFacets":["newstypes","Tags"],"SearchFields":["Title","Content","Tags"],"Skip":0}
        #for year in list(range(2014, 2020)):  # loop iterating over different pages of ajax request
        #    data['year'] = year
        s_url = 'https://www.aptiv.com/RestApi/st/facet-search/full-site'
        yield scrapy.Request(s_url, method='POST', body=json.dumps(data), headers=headers, callback=self.parse)
        #for num in range(0,11):  # loop iterating over different pages of ajax request
        #    data['page'] = str(num)
        #    s_url = 'https://investor.twitterinc.com/Services/PressReleaseService.svc/GetPressReleaseList'
        #    yield FormRequest(url=s_url, formdata=data, headers=headers, callback=self.parse )
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        #body = dat[-1]['data']  # [-1] selects last element # extract data body with html content from the json response file
        #quotes = Selector(text=body).xpath('//div[@class="views-row"]')  # define html body content as reference for the selector
        for dat in body['Results']:
            item = SwisscomIvCrawlerItem()
            
            timestamp = dat['PublicationDate'].split('e(')[1].split(')')[0]# cuts out the part berfore the date as well as the /n at the end of the string
            your_dt = datetime.datetime.fromtimestamp(int(timestamp)/1000)
            
            item['PUBSTRING'] = your_dt.strftime("%Y-%m-%d %H:%M:%S") 
            item['HEADLINE']= dat['Title']
            item['DOCLINK']= dat['Link']
            #item = {
            #          'PUBSTRING': dat['PublicationDate'].split('e(')[1].split(')')[0],
            #          'HEADLINE': dat['Title'],
            #          'DOCLINK': dat['Link'],
            #          }
            base_url = 'https://www.aptiv.com'
            url = dat['Link']
            if ".pdf" not in url.lower() : # make url all lowercase so match is not casinsensitive anymore
                if '.jpg' in url.lower() or '.png' in url.lower():
                    item['DESCRIPTION'] = dat['Extension']
                    yield item
                else :
                    request = scrapy.Request(url=url, callback=self.parse_details)
                    request.meta['item'] = item
                    yield request

            else:
                item = SwisscomIvCrawlerItem()
                item['file_urls'] = [url]
                item['PUBSTRING'] = your_dt.strftime("%Y-%m-%d %H:%M:%S") 
                item['HEADLINE']= dat['Title']
                item['DOCLINK']= url
                item['DESCRIPTION'] = ''
                yield item 

    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*| (\bAbout\s*Aptiv\b)(.|\s)* |(\bAbout.Aptiv\b)(.|\s)* | (\bAbout\s*Delphi\b)(.|\s)* | (\bAbout.Delphi\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="content"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="articleContent"]//text()[not(ancestor::img)][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                    item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item
    
    #def parse_details(self, response):
    #    item = response.meta['item']
    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Aptiv\b)(.|\s)* |(\bAbout.Aptiv\b)(.|\s)* | (\bAbout\s*Delphi\b)(.|\s)* | (\bAbout.Delphi\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="content"]//text()').extract()))
    #    item['DOCLINK'] = response.url
    #    yield item
    #    #if not item['DESCRIPTION']:
    #    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Aptiv\b)(.|\s)* |(\bAbout.Aptiv\b)(.|\s)* | (\bAbout\s*Delphi\b)(.|\s)* | (\bAbout.Delphi\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="module_body"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()').extract()))
    #    #    yield item
    #    #else:     
    #    #    yield item
           



        
            