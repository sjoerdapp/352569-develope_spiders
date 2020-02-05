import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

#### UPDATES
### scrape first 5 pages with 4 News each (last 20 news)

### Omnicom Group Inc 2|2
### this spider agency news
### 1st spider scrapes Omnicom News, 2nd spider Agency news
### first get headline request
### next get press release lists
### go along pages using page# and callback._#
### descriptions come with json request with the Getpressrelease source
### need to use workflow id to access content
### back to 20130522

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "Omnicom_II_1367000ARV002"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Omnicom_II_1367000ARV002/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    #start_urls = ['http://www.omnicomgroup.com/newsroom/'] 
    def start_requests(self):
        headers = {
           'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
           'Connection': 'keep-alive',
           #'Content-Length': '316',
           #'Content-Type': 'application/json; charset=UTF-8',
           #'Cookie': '_ga=GA1.2.9377599.1549202778; _gid=GA1.2.1210191223.1549202778; cookieAccept=true; _gat=1',
            #'Host': 'investor.twitterinc.com',
           #'Origin': 'https://ir.sbasite.com',
           'Referer': 'http://www.omnicomgroup.com/newsroom/',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
           #'X-NewRelic-ID': 'VQYBUlRVChABXFNXBAcCXw==',
           'X-Requested-With': 'XMLHttpRequest',
          }
        s_url = 'http://www.omnicomgroup.com/umbraco/api/newsroom/getarticles'
        yield scrapy.Request(s_url, method='GET', headers=headers, callback=self.parse)
    
    def parse(self, response):  # follow drop down menue for different years
        body = response.body
        dats = json.loads(body.decode("utf-8"))
        for dat in dats['Agency']:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['PressReleaseDate']
            item['HEADLINE']= dat['Headline']
            item['DOCLINK']= dat['LinkToDetailPage']
            
            base_url = 'http://www.omnicomgroup.com'
            aux_url = dat['LinkToDetailPage']
            url= base_url + aux_url
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request

        #for dat in dats[ 'Omnicom']:
        #    item = SwisscomIvCrawlerItem()
        #    item['PUBSTRING'] = dat['PressReleaseDate']
        #    item['HEADLINE']= dat['Headline']
        #    item['DOCLINK']= dat['LinkToDetailPage']
        #    
        #    base_url = 'http://www.omnicomgroup.com'
        #    aux_url = dat['LinkToDetailPage']
        #    url= base_url + aux_url
        #    request = scrapy.Request(url=url, callback=self.parse_details)
        #    request.meta['item'] = item
        #    yield request
#
        #cat_ids = ["1cb807d2-208f-4bc3-9133-6a9ad45ac3b0",
        #         " Agency ad93ec78-aeb6-42ec-8e84-5e43a4716272"] # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        cat_id = 'ad93ec78-aeb6-42ec-8e84-5e43a4716272'
        aux_url = 'http://omnicom.q4web.com/feed/PressRelease.svc/GetPressReleaseList?CategoryId={}&apiKey=B5595FEB4174416297055DC1E4CE1676&callback=angular.callbacks._0&includeTags=true&pageNumber=0&pageSize=4&pressReleaseDateFilter=1'
        cat_url = [aux_url.format(cat_id)][0]
        yield scrapy.Request(url=cat_url, callback=self.parse_next)

    #def parse_month(self, response):  # follow drop down menue for different years
    #     data = json.loads(response.text)
    #     #year = re.findall(r'\d{4}',  response.url)[0]
    #     for month in data['activeMonths']:
    #         aux = 'filter.' + month # built part with filter and month to insert in url
    #         month_url = re.sub(r'months',aux ,response.url) # build request url for respective month
    #         yield scrapy.Request(url=month_url, callback=self.parse_next)
    
    def parse_next(self, response):
        body = response.body
        dats = json.loads(re.split('._\d+?\(',body.decode("utf-8"))[1].rsplit(');', 1)[0])
        for dat in dats['GetPressReleaseListResult']:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['PressReleaseDate']
            item['HEADLINE']= dat['Headline']
            item['DOCLINK']= dat['LinkToDetailPage']
            #item = {
            #        'PUBSTRING': aux.xpath('./td//div[@class="field__item"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./td/a[2]/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./td/a[2]/@href').extract_first(),
            #        }
            base_url = 'http://omnicom.q4web.com/feed/PressRelease.svc/GetPressReleaseItem?apiKey=B5595FEB4174416297055DC1E4CE1676&callback=angular.callbacks._0&languageId=1&workflowId={}'
            aux_url = dat['WorkflowId']
            url = [base_url.format(aux_url)][0]
            request = scrapy.Request(url=url, callback=self.parse_details_II)
            request.meta['item'] = item
            yield request
            #if '.pdf' in aux_url.lower():
            #    if aux_url.startswith('http'):
            #        url= aux_url
            #        item['file_urls'] = [url]
            #        item['DOCLINK'] = url
            #        yield item
            #    
            #    else:
            #        url= base_url + aux_url
            #        item['file_urls'] = [url]
            #        item['DOCLINK'] = url
            #        yield item
            #else:
            #    if aux_url.startswith('http'):
            #        url= aux_url
            #        request = scrapy.Request(url=url, callback=self.parse_details)
            #        request.meta['item'] = item
            #        yield request
            #        
            #    
            #    else:
            #        url= base_url + aux_url
            #        request = scrapy.Request(url=url, callback=self.parse_details)
            #        request.meta['item'] = item
            #        yield request

        if len(dats['GetPressReleaseListResult']) == 4:
            #next_url = 'http://omnicom.q4web.com/feed/PressRelease.svc/GetPressReleaseList?CategoryId=ad93ec78-aeb6-42ec-8e84-5e43a4716272&apiKey=B5595FEB4174416297055DC1E4CE1676&callback=angular.callbacks._{}&includeTags=true&pageNumber={}&pageSize=4&pressReleaseDateFilter=1'
            next_url_I = re.split('\d+?&includeTags',response.url )[0]
            next_url_II = re.split('\d+?&pageSize',re.split('callbacks._\d+?&',response.url )[1] )[0]
            next_page =str(int(response.url.split('pageNumber=')[1].split('&page')[0]) +1)
            next_page_check= int(response.url.split('pageNumber=')[1].split('&page')[0])
            if next_page_check > 4:
                return
            next_callback = str(int(response.url.split('callbacks._')[1].split('&include')[0]) +1)
            next_page_url = next_url_I +next_callback + '&' + next_url_II + next_page + '&pageSize=4&pressReleaseDateFilter=1'
            #next_page_url =[next_url.format(next_page)][0]
            request = scrapy.Request(url=next_page_url, callback=self.parse_next)
            yield request


    def parse_details(self, response):
        item = response.meta['item']
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
            item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(About Omnicom Public Relations Group)|(\bAbout\s*Omnicom\b)(.|\s)* | (\bAbout.Omnicom.Group\b)(.|\s)*','' ," ".join(response.xpath('//div[contains(@class, "article-content")]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()[not(ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags= re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(About Omnicom Public Relations Group)|(\bAbout\s*Omnicom\b)(.|\s)* | (\bAbout.Omnicom.Group\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="q4default"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()[not(ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags= re.IGNORECASE)
                yield item
            else:
                yield item

    def parse_details_II(self, response):
        item = response.meta['item']
        body = response.body
        dats = json.loads(re.split('callbacks._\d\(',body.decode("utf-8"))[1].rsplit(');', 1)[0])  ## split secont part from right
        item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(About Omnicom Public Relations Group)|(\bAbout\s*Omnicom\b)(.|\s)* | (\bAbout.Omnicom.Group\b)(.|\s)*','' ," ".join(Selector(text=dats['GetPressReleaseItemResult']['Body']).xpath('//div[@class="xn-content"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()[not(ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags= re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(About Omnicom Public Relations Group)|(\bAbout\s*Omnicom\b)(.|\s)* | (\bAbout.Omnicom.Group\b)(.|\s)*','' ," ".join(Selector(text=dats['GetPressReleaseItemResult']['Body']).xpath('//div[@class="q4default"]//text()[not(self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags= re.IGNORECASE)
            if not item['DESCRIPTION']:
                item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(About Omnicom Public Relations Group)|(\bAbout\s*Omnicom\b)(.|\s)* | (\bAbout.Omnicom.Group\b)(.|\s)*','' ," ".join(Selector(text=dats['GetPressReleaseItemResult']['Body']).xpath('//p//text()[not(self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags= re.IGNORECASE)
                if not item['DESCRIPTION']:
                    item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(About Omnicom Public Relations Group)|(\bAbout\s*Omnicom\b)(.|\s)* | (\bAbout.Omnicom.Group\b)(.|\s)*','' ," ".join(Selector(text=dats['GetPressReleaseItemResult']['Body']).xpath('//span[@class="ccbnTxt"]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()[not(ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags= re.IGNORECASE)
                    if not item['DESCRIPTION']:
                        item['file_urls'] = [dats['GetPressReleaseItemResult']['DocumentPath']]
                        item['DOCLINK'] = response.url
                        item['DESCRIPTION'] = '' 
                        yield item
                    else:
                        yield item 
                else:  
                    yield item 
            else:
                yield item
        else:
            yield item

            