import requests
import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
#from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

class BHGE(scrapy.Spider):
    name = "WT_wat_9900062ARV001"
    #handle_httpstatus_list = [404]
    #custom_settings = {
    #     'JOBDIR' : 'None',
    #     'FILES_STORE' : 's3://sp5001/PAY_II_6333000ARV002/',
    #    }
    #api_url = 'http://quotes.toscrape.com/api/quotes?page={}'
    #start_urls = [api_url.format(1)]
    #start_urls = ['https://www.swisscom.ch/en/about/news/archive.html']
    #count = 0
    
    def start_requests(self):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset="UTF-8"',
            'Cookie': 'ga=GA1.2.457028218.1549013158; _gid=GA1.2.1122027351.1549013158; _gcl_au=1.1.2142990333.1549013158; shotgun#lang=en; ASP.NET_SessionId=4zz0dxiclzso4fzc1ccxd2u3; SC_ANALYTICS_GLOBAL_COOKIE=0e7997d23437461a8a6faa93ba2fc65e|True; coveorest#lang=en; visitor=f5edb1dd-96b2-4dc9-8838-0701ce655475; coveo_visitorId=f5edb1dd-96b2-4dc9-8838-0701ce655475; OptanonConsent=landingPath=NotLandingPage&datestamp=Fri+Feb+01+2019+10%3A29%3A23+GMT%2B0100+(Mitteleurop%C3%A4ische+Normalzeit)&version=3.6.15&groups=1%3A1&AwaitingReconsent=false; OptanonAlertBoxClosed=2019-02-01T09:29:23.372Z',
            'Origin': 'https://www.iqvia.com',
            'Referer': 'https://www.iqvia.com/newsroom',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            }

        data = {            
            #'actionsHistory': [{"name":"Query","time":"\"2019-02-01T09:26:29.323Z\"","internalTime":1549013189323},{"name":"PageView","value":"2BA2A71A50404C31AC67CB197FA9D522","time":"\"2019-02-01T09:26:28.490Z\"","internalTime":1549013188490},{"name":"PageView","value":"3DBF787E2BB04484A9D89D4531882A6D","time":"\"2019-02-01T09:26:09.029Z\"","internalTime":1549013169029}],
            'referrer': 'https://www.iqvia.com/',
            'visitorId': 'f5edb1dd-96b2-4dc9-8838-0701ce655475',
            'isGuestUser': False,
            'aq': '(@fpublishz32xdate17102<=2019/02/01) ((@syssource=="Coveo_Shotgun_live_index - Prod") (@fz95xlanguage17102=="en") (@fz95xlatestversion17102=="1") (@fcontentz32xtype17102==("News","Press Release")) ((NOT @fid17102==ff98d9927ab94eeda8bc875588ce3ba6))) ((@fisz32xarchived17102==(0))) ((@syssource=="Coveo_Shotgun_live_index - Prod") (@fz95xlanguage17102=="en") (@fz95xlatestversion17102=="1") (@fcontentz32xtype17102==("News","Press Release")) ((NOT @fid17102==ff98d9927ab94eeda8bc875588ce3ba6))) ((@fisz32xarchived17102==(0))(@fisz32xbusinesswirez32xpressz32xrelease17102==1)) (NOT @fz95xtemplate17102==(ADB6CA4F03EF4F47B9AC9CE2BA53FF97,FE5DD82648C6436DB87A7C4210C7413B)) (@syssource=="Coveo_Shotgun_live_index - Prod")',
            'cq': '(@fz95xlanguage17102==en) (@fz95xlatestversion17102==1)',
            'tab': 'Corporate',
            'locale': 'en',
            'maximumAge': 0,
            'firstResult': 10,
            'numberOfResults': 10,
            'excerptLength': 200,
            'enableDidYouMean': False,
            'sortCriteria': '@fpublishz32xdate17102 Descending',
            'queryFunctions': [],
            'rankingFunctions': [],
            'groupBy': [],
            'retrieveFirstSentences': True,
            'timezone': 'Europe/Zurich',
            'enableQuerySyntax': False,
            'enableDuplicateFiltering': False,
            'enableCollaborativeRating': False,
            'debug': False,
            }

        s_url = 'https://www.iqvia.com/coveo/rest/v2/?sitecoreItemUri=2ba2a71a-5040-4c31-ac67-cb197fa9d522&siteName=Shotgun'
                 https://www.willistowerswatson.com/coveo/rest/v2/?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7BE1EB2D45-066F-4F8F-8B9B-049E7918A034%7D%3Flang%3Den%26ver%3D16&siteName=wtw
        #for num in list(range(0,726, 10)):  # loop iterating over different pages of ajax request; last number not in list anymore
        #data['firstResult'] = str(num)
        yield scrapy.Request(s_url, method='GET', body=json.dumps(data), headers=headers, callback=self.parse)
    
    
    def parse(self, response):
        body = json.loads(response.text)  # load jason response from post request
        for dat in body['results']:
            #item = SwisscomIvCrawlerItem()
            item = {
                      'PUBSTRING': dat['raw']['date'],
                      'HEADLINE': dat['Title'],
                      'DOCLINK': dat['clickUri'],
                      }
            #item['PUBSTRING'] = quote.xpath('.//div[@class="div--type"]/text()').extract_first().split(" - ")[1].split("\n")[0], # cuts out the part berfore the date as well as the /n at the end of the string
            #item['HEADLINE']= quote.xpath('.//div[@class="div--title"]/a/text()').extract_first(),
            #item['DOCLINK']= quote.xpath('.//div[@class="div--title"]/a/@href').extract_first(),
            
            #base_url = 'https://www.eversource.com/content'
            url= dat['clickUri'] 
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request   

    def parse_details(self, response):
        item = response.meta['item']
        item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Willis\s*Towers\s*Watson\b)(.|\s)* | (\bAbout.Wiilis.Towers.Watson\b)(.|\s)*','' ," ".join(response.xpath('//div [@class="article-wrapper"]/article/section//text()').extract()))
        item['DOCLINK'] = response.url
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



        
            