import json
import scrapy
import re
from scrapy.http import FormRequest
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector



### Iqvia Holdings Inc 4|4
### 4th Newsroom
### complex post with cookies etc.
### some cookies have datatimes -> check if they still work and eventually adjust them
### back to 20161013



class BHGE(scrapy.Spider):
    name = "IQVIA_IV_9900204ARV004"

    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/IQVIA_IV_9900204ARV004/',
        }

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

        cookies = {'_ga': 'GA1.2.1129656068.1578664350',
                   'SC_ANALYTICS_GLOBAL_COOKIE': 'ffe349100a4547ceb7ee85767024ff12|True',
                   'visitor': '3a025215-d8d9-42af-8cbb-5dab6155f853',
                   'coveo_visitorId': '3a025215-d8d9-42af-8cbb-5dab6155f853',
                   'shotgun#lang': 'en',
                   'ASP.NET_SessionId': 'tvvjjfaojuiixbic5ayaebxz',
                   'BIGipServerwww.iqvia.com_http_prod_pool': '3689557154.20992.0000',
                   'coveorest#lang': 'en',
                   '_gid': 'GA1.2.652120050.1579787930',
                   'OptanonConsent': 'isIABGlobal=true&datestamp=Thu+Jan+23+2020+14%3A59%3A35+GMT%2B0100+(Mitteleurop%C3%A4ische+Normalzeit)&version=5.9.0&landingPath=https%3A%2F%2Fwww.iqvia.com%2Fnewsroom&groups=1%3A1%2C2%3A0%2C3%3A0%2C4%3A0%2C0_67250%3A0%2C0_69649%3A0%2C0_68848%3A0%2C0_67254%3A0%2C0_68844%3A0%2C0_67258%3A0%2C0_68840%3A0%2C0_68836%3A0%2C0_68964%3A0%2C0_68960%3A0%2C0_69650%3A0%2C0_69425%3A0%2C0_69648%3A0%2C0_68847%3A0%2C0_67255%3A0%2C0_68843%3A0%2C0_68839%3A0%2C0_68835%3A0%2C0_68963%3A1%2C0_68959%3A0%2C0_67252%3A0%2C0_69647%3A0%2C0_68846%3A0%2C0_67256%3A0%2C0_68842%3A0%2C0_68838%3A0%2C0_68966%3A0%2C0_68834%3A0%2C0_68962%3A0%2C0_69652%3A0%2C0_68849%3A0%2C0_69518%3A0%2C0_69646%3A0%2C0_68845%3A0%2C0_67257%3A1%2C0_68841%3A0%2C0_68837%3A0%2C0_68965%3A0%2C0_68833%3A0%2C0_68961%3A0%2C0_69651%3A0%2C8%3A0%2C101%3A0%2C102%3A0%2C103%3A0%2C104%3A0%2C105%3A0%2C106%3A0%2C107%3A0%2C109%3A0%2C110%3A0%2C111%3A0%2C112%3A0%2C114%3A0%2C115%3A0%2C116%3A0%2C117%3A0%2C118%3A0%2C119%3A0%2C120%3A0%2C121%3A0%2C122%3A0',
                   }

        # s_url = 'https://httpbin.org/cookies'
        s_url = 'https://www.iqvia.com/coveo/rest/v2?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7B2BA2A71A-5040-4C31-AC67-CB197FA9D522%7D%3Flang%3Den%26amp%3Bver%3D4&siteName=Shotgun&authentication'
        years = list(range(0, 200, 10))
        for year in years:
            data_aux = '''actionsHistory=%5B%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222020-01-24T12%3A06%3A44.672Z%5C%22%22%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222020-01-23T13%3A59%3A38.647Z%5C%22%22%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222020-01-18T12%3A52%3A00.668Z%5C%22%22%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222020-01-10T13%3A53%3A45.106Z%5C%22%22%7D%5D&referrer=&visitorId=3a025215-d8d9-42af-8cbb-5dab6155f853&isGuestUser=false&aq=((%40syssource%3D%3D%22Coveo_Shotgun_web_index%20-%20PROD9%22)%20(%40z95xlanguage%3D%3D%22en%22)%20(%40z95xlatestversion%3D%3D%221%22)%20(%40contentz32xtype%3D%3D(%22News%22%2C%22Press%20Release%22)))%20((%40isz32xarchived%3D%3D(0)))%20(%40publishz32xdate%3C%3D2020%2F01%2F24)%20(NOT%20%40z95xtemplate%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))%20(%40syssource%3D%3D%22Coveo_Shotgun_web_index%20-%20PROD9%22)&cq=(%40z95xlanguage%3D%3Den)%20(%40z95xlatestversion%3D%3D1)&searchHub=Newsroom&locale=en&maximumAge=900000&firstResult=0&numberOfResults=12&excerptLength=200&enableDidYouMean=false&sortCriteria=%40publishz32xdate%20Descending&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40pressz32xreleasez32xtype%22%2C%22maximumNumberOfValues%22%3A20%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%2C%7B%22field%22%3A%22%40shotgunz32xtopic%22%2C%22maximumNumberOfValues%22%3A6%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%5D&categoryFacets=%5B%5D&retrieveFirstSentences=true&timezone=UTC&enableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&allowQueriesWithoutKeywords=true'''
            #data = [data_aux.format(year)][0]
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*IQVIA\b)(.|\s)* |(\bAbout.IQVIA\b)(.|\s)*|(\bAbout\s*QuintilesIMS\b)(.|\s)* |(\bAbout.QuintilesIMS\b)(.|\s)*'
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="col-sm-8"]/h2/text() | //div[@class="col-sm-8"]//div[@class="box-content"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()').extract()))
        item['DOCLINK'] = response.url
        yield item