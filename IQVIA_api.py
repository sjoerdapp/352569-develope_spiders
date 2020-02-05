import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector

### Iqvia
### some cookies have datatimes -> check if they still work and eventually adjust them
class BHGE(scrapy.Spider):
    name = "IQVIA_check"

    def start_requests(self):
        headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    #'Content-Length': '2515',
                    'Content-Type': 'application/x-www-form-urlencoded; charset="UTF-8"',
                    #'Cookie': 'shotgun#lang=en; ASP.NET_SessionId=etk5isiohdqywhgxfyktknn4; coveorest#lang=en; visitor=6565c385-eb8b-445d-817d-5fb4eb23f979; coveo_visitorId=6565c385-eb8b-445d-817d-5fb4eb23f979; SC_ANALYTICS_GLOBAL_COOKIE=8f837ae60c2c47419c29d4274a0ffa63|True; gsScrollPos-2107=0',
                    #'Host': 'www.iqvia.com',
                    'Origin:https': '//www.iqvia.com',
                    'Referer:https': '//www.iqvia.com/newsroom',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            }

        #data = '''actionsHistory=%5B%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-20T09%3A11%3A42.054Z%5C%22%22%2C%22internalTime%22%3A1550653902054%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-12T20%3A35%3A52.467Z%5C%22%22%2C%22internalTime%22%3A1550003752467%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-12T20%3A35%3A51.355Z%5C%22%22%2C%22internalTime%22%3A1550003751355%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A07%3A09.677Z%5C%22%22%2C%22internalTime%22%3A1549991229678%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A07%3A09.303Z%5C%22%22%2C%22internalTime%22%3A1549991229303%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A06%3A47.420Z%5C%22%22%2C%22internalTime%22%3A1549991207420%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A06%3A46.237Z%5C%22%22%2C%22internalTime%22%3A1549991206237%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T16%3A50%3A34.886Z%5C%22%22%2C%22internalTime%22%3A1549039834886%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T16%3A50%3A34.631Z%5C%22%22%2C%22internalTime%22%3A1549039834631%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%223DBF787E2BB04484A9D89D4531882A6D%22%2C%22time%22%3A%22%5C%222019-02-01T16%3A50%3A25.199Z%5C%22%22%2C%22internalTime%22%3A1549039825199%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A23%3A53.573Z%5C%22%22%2C%22internalTime%22%3A1549027433573%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A23%3A53.439Z%5C%22%22%2C%22internalTime%22%3A1549027433439%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A18%3A18.688Z%5C%22%22%2C%22internalTime%22%3A1549027098688%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A18%3A18.442Z%5C%22%22%2C%22internalTime%22%3A1549027098442%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A17%3A45.956Z%5C%22%22%2C%22internalTime%22%3A1549027065956%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A17%3A45.714Z%5C%22%22%2C%22internalTime%22%3A1549027065714%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A29%3A50.231Z%5C%22%22%2C%22internalTime%22%3A1549020590231%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A29%3A50.065Z%5C%22%22%2C%22internalTime%22%3A1549020590065%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22FF98D9927AB94EEDA8BC875588CE3BA6%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A29%3A47.908Z%5C%22%22%2C%22internalTime%22%3A1549020587908%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A28%3A00.688Z%5C%22%22%2C%22internalTime%22%3A1549020480688%7D%5D&referrer=https%3A%2F%2Fwww.iqvia.com%2Fnewsroom&visitorId=f5edb1dd-96b2-4dc9-8838-0701ce655475&isGuestUser=false&aq=(%40fpublishz32xdate17102%3C%3D2019%2F02%2F20)%20((%40syssource%3D%3D%22Coveo_Shotgun_live_index%20-%20Prod%22)%20(%40fz95xlanguage17102%3D%3D%22en%22)%20(%40fz95xlatestversion17102%3D%3D%221%22)%20(%40fcontentz32xtype17102%3D%3D(%22News%22%2C%22Press%20Release%22))%20((NOT%20%40fid17102%3D%3Db186a4ca58ec4509b7c9a86ee9432a46)))%20((%40fisz32xarchived17102%3D%3D(0)))%20((%40syssource%3D%3D%22Coveo_Shotgun_live_index%20-%20Prod%22)%20(%40fz95xlanguage17102%3D%3D%22en%22)%20(%40fz95xlatestversion17102%3D%3D%221%22)%20(%40fcontentz32xtype17102%3D%3D(%22News%22%2C%22Press%20Release%22))%20((NOT%20%40fid17102%3D%3Db186a4ca58ec4509b7c9a86ee9432a46)))%20((%40fisz32xarchived17102%3D%3D(0))(%40fisz32xbusinesswirez32xpressz32xrelease17102%3D%3D1))%20(NOT%20%40fz95xtemplate17102%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%22Coveo_Shotgun_live_index%20-%20Prod%22)&cq=(%40fz95xlanguage17102%3D%3Den)%20(%40fz95xlatestversion17102%3D%3D1)&tab=Corporate&locale=en&maximumAge=0&firstResult=0&numberOfResults=10&excerptLength=200&enableDidYouMean=false&sortCriteria=%40fpublishz32xdate17102%20Descending&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%5D&retrieveFirstSentences=true&timezone=Europe%2FZurich&enableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false'''

        cookies = {'_ga': 'GA1.2.457028218.1549013158',
                    '_gcl_au': '1.1.2142990333.1549013158',
                    'SC_ANALYTICS_GLOBAL_COOKIE': '0e7997d23437461a8a6faa93ba2fc65e|True',
                    'visitor': 'f5edb1dd-96b2-4dc9-8838-0701ce655475',
                    'coveo_visitorId': 'f5edb1dd-96b2-4dc9-8838-0701ce655475',
                    'OptanonConsent': 'landingPath=NotLandingPage&datestamp=Tue+Feb+12+2019+21%3A35%3A52+GMT%2B0100+(Mitteleurop%C3%A4ische+Normalzeit)&version=3.6.15&groups=1%3A1&AwaitingReconsent=false',
                    'OptanonAlertBoxClosed': '2019-02-12T20:35:52.593Z',
                    'shotgun#lang': 'en',
                    'ASP.NET_SessionId': 'apsvwj1cqyyxc2mxieozj4tk',
                    'coveorest#lang': 'en'}

        # s_url = 'https://httpbin.org/cookies'
        s_url = 'https://www.iqvia.com/coveo/rest/v2/?sitecoreItemUri=2ba2a71a-5040-4c31-ac67-cb197fa9d522&siteName=Shotgun'
        years = list(range(0, 72, 10))
        for year in years:
            data_aux = '''actionsHistory=%5B%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-20T09%3A11%3A42.054Z%5C%22%22%2C%22internalTime%22%3A1550653902054%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-12T20%3A35%3A52.467Z%5C%22%22%2C%22internalTime%22%3A1550003752467%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-12T20%3A35%3A51.355Z%5C%22%22%2C%22internalTime%22%3A1550003751355%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A07%3A09.677Z%5C%22%22%2C%22internalTime%22%3A1549991229678%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A07%3A09.303Z%5C%22%22%2C%22internalTime%22%3A1549991229303%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A06%3A47.420Z%5C%22%22%2C%22internalTime%22%3A1549991207420%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-12T17%3A06%3A46.237Z%5C%22%22%2C%22internalTime%22%3A1549991206237%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T16%3A50%3A34.886Z%5C%22%22%2C%22internalTime%22%3A1549039834886%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T16%3A50%3A34.631Z%5C%22%22%2C%22internalTime%22%3A1549039834631%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%223DBF787E2BB04484A9D89D4531882A6D%22%2C%22time%22%3A%22%5C%222019-02-01T16%3A50%3A25.199Z%5C%22%22%2C%22internalTime%22%3A1549039825199%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A23%3A53.573Z%5C%22%22%2C%22internalTime%22%3A1549027433573%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A23%3A53.439Z%5C%22%22%2C%22internalTime%22%3A1549027433439%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A18%3A18.688Z%5C%22%22%2C%22internalTime%22%3A1549027098688%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A18%3A18.442Z%5C%22%22%2C%22internalTime%22%3A1549027098442%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A17%3A45.956Z%5C%22%22%2C%22internalTime%22%3A1549027065956%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T13%3A17%3A45.714Z%5C%22%22%2C%22internalTime%22%3A1549027065714%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A29%3A50.231Z%5C%22%22%2C%22internalTime%22%3A1549020590231%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%222BA2A71A50404C31AC67CB197FA9D522%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A29%3A50.065Z%5C%22%22%2C%22internalTime%22%3A1549020590065%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22FF98D9927AB94EEDA8BC875588CE3BA6%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A29%3A47.908Z%5C%22%22%2C%22internalTime%22%3A1549020587908%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222019-02-01T11%3A28%3A00.688Z%5C%22%22%2C%22internalTime%22%3A1549020480688%7D%5D&referrer=https%3A%2F%2Fwww.iqvia.com%2Fnewsroom&visitorId=f5edb1dd-96b2-4dc9-8838-0701ce655475&isGuestUser=false&aq=(%40fpublishz32xdate17102%3C%3D2019%2F02%2F20)%20((%40syssource%3D%3D%22Coveo_Shotgun_live_index%20-%20Prod%22)%20(%40fz95xlanguage17102%3D%3D%22en%22)%20(%40fz95xlatestversion17102%3D%3D%221%22)%20(%40fcontentz32xtype17102%3D%3D(%22News%22%2C%22Press%20Release%22))%20((NOT%20%40fid17102%3D%3Db186a4ca58ec4509b7c9a86ee9432a46)))%20((%40fisz32xarchived17102%3D%3D(0)))%20((%40syssource%3D%3D%22Coveo_Shotgun_live_index%20-%20Prod%22)%20(%40fz95xlanguage17102%3D%3D%22en%22)%20(%40fz95xlatestversion17102%3D%3D%221%22)%20(%40fcontentz32xtype17102%3D%3D(%22News%22%2C%22Press%20Release%22))%20((NOT%20%40fid17102%3D%3Db186a4ca58ec4509b7c9a86ee9432a46)))%20((%40fisz32xarchived17102%3D%3D(0))(%40fisz32xbusinesswirez32xpressz32xrelease17102%3D%3D1))%20(NOT%20%40fz95xtemplate17102%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%22Coveo_Shotgun_live_index%20-%20Prod%22)&cq=(%40fz95xlanguage17102%3D%3Den)%20(%40fz95xlatestversion17102%3D%3D1)&tab=Corporate&locale=en&maximumAge=0&firstResult={}&numberOfResults=10&excerptLength=200&enableDidYouMean=false&sortCriteria=%40fpublishz32xdate17102%20Descending&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%5D&retrieveFirstSentences=true&timezone=Europe%2FZurich&enableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false'''
            data = [data_aux.format(year)][0]
            yield scrapy.Request(s_url, method='POST', body=data, headers=headers, cookies=cookies, callback=self.parse)  # noqa

    def parse(self, response):
        #with open('temp.txt', 'wb') as dest:
        #    dest.write(response.body)

        body = json.loads(response.text)  # load jason response from post request
        for dat in body['results']:
            #item = SwisscomIvCrawlerItem()
            item = {
                      'PUBSTRING': dat['raw']['fcreateddatemmmmddyyyy17102'],
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
        item['DESCRIPTION'] = re.sub(r'(\bAbout\s*IQVIA\b)(.|\s)* | (\bAbout.IQVIA\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="col-sm-8"]/h2/text() | //div[@class="col-sm-8"]//div[@class="box-content"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()').extract()))
        item['DOCLINK'] = response.url
        yield item