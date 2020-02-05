import scrapy
import re
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
import json
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### Advanced Micro Devices Inc. 2|2
### 2nd spider Newsroom
### classic get
### back to 20130102

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = 'AMD_II_2110000ARV002'
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/AMD_II_2110000ARV002/',
         'USER_AGENT' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    #start_urls = ['http://ir.amd.com/'] 

    
    def start_requests(self):
    #def parse(self, response):  # follow drop down menue for different years
         years = list(range(0, 46)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         cookies = {'pmuser_country': 'ch',
                    'c_slidebox_lists': '',
                    '_gcl_au': '1.1.329745309.1557748288',
                    'fonce_current_user': '1',
                    '_ga': 'GA1.2.1863769081.1557748288',
                    '_gid': 'GA1.2.1427955687.1557748288',
                    'tc_ptidexpiry': '1620820288207',
                    'tc_ptid': '1OetyHOWHN8Biz5DVBh77L',
                    '_fbp': 'fb.1.1557748288527.1546486949',
                    'visitor_id659533': '80980240',
                    'visitor_id659533-hash': '6ad1ed109efbc462e9f79e60bb17fd5c977ffd693e45994cb95e77278baa5b9ed8d60f823c82dc9114f9e9d2bde9821f0cab43a0',
                    'fonce_current_day': '1,2019-05-14',
                    'cookieCompliance': 'true',
                    '__atuvc': '16%7C20',
                    'c_rurl': 'https%3A//www.amd.com/en/corporate/newsroom/press-releases/',
                    '_gat_UA-55985825-1': '1',
                    'tc_q': 'tcptid%3D1OetyHOWHN8Biz5DVBh77L%26tcttid%3D42VIQ7m5j6E4lqXhcDEieH%26tcctid%3D1JXiAmQKQQ4KoMoYwSIaCi%26tcvc%3DLink%2520Click%26tcect%3D1557836075050%26tcvv%3Dhttps%253A%252F%252Fwww.amd.com%252Fen%252Fcorporate%252Fnewsroom%252Fpress-releases%26tcvr%3D%26tcvt%3Dundefined%26tclv%3Dundefined%26tcectz%3D-120%26tcep%3DWin32%26site_id%3Damd_prod%26content_title%3DPress%2520Release%2520Search%2520%257C%2520AMD%26event_udf10%3D%252Fwww.amd.com%252Fen%252Fcorporate%252Fnewsroom%252Fpress-releases%253Fkeyword%253D%2526page%253D1%26account_id%3DAMD%7Ctcptid%3D1OetyHOWHN8Biz5DVBh77L%26tcttid%3D42VIQ7m5j6E4lqXhcDEieH%26tcctid%3D6NEtpGWVUcmgMuEQKiSaQK%26tcvc%3DPercentage%2520Scrolled%26tcect%3D1557836075167%26tcvv%3Dhttps%253A%252F%252Fwww.amd.com%252Fen%252Fcorporate%252Fnewsroom%252Fpress-releases%26tcvr%3D%26tcvt%3Dundefined%26tclv%3Dundefined%26tcectz%3D-120%26tcep%3DWin32%26site_id%3Damd_prod%26content_title%3DPress%2520Release%2520Search%2520%257C%2520AMD%26event_udf8%3DMax%253A100%2525%257CExit%253A100%2525%26account_id%3DAMD',
                    '_4c_': 'jVHdjtM8EH0V5OvS%2Bv%2BndwgkxAMgLleOPaYRaRzZKflWq777jtN2P1iKllxYnsnxOWfmPJHlACPZM6WMFZoaxQzbkB%2FwWMn%2BiYSpnT%2FbcSoD2ZPDPE91v9sty7L1x7gN%2BbiDcRdymXLxM%2BxGWGrJ2J0K1Pq%2BwAC%2BQiUbEnIEZGBuq7YM667kpULB1sdDyUd4ZyR2EyoS64UHLiNHOyEBCLRHO8YEupPALeIy%2BiPf%2BjEiCZYFEpSysmFV%2B7lJXQ1eGzjTpYf1DOXYCPA64XRE4GXIwQ%2FtGe6jEU6Df3zoIzacVME6pk0wTnQqgOGac9AKTXpNoQngsH0eV7hyOjnWeRl8ApYcTUl3ThqRmHWgmvvPHx6%2BfvnUtmG1MNpRy7YtAiMttw0QMRMSIfnTMJPzhvx3iQhNOCOUNDjCjHlYLWn7EFGa9poV4TZqKiFIgxZ9tEy4mGKCSEOHZUL%2BlU8rxSXqOc6RoC1ifS9e5Kww0jHO9Z9yl%2FT%2B%2FkbYOxbDzeFcTm1rv7uwomHmKyb5ocJriGMICWNA3jdAx%2F%2FX8Q%2Fx3SH4XtLNypqMYtQxQd1dMCZ1xeLYby%2BipXvxdov4F1aDOkophPUvqNf%2FteLn8%2FkZ'
                    }


         for year in years:
             aux_url = 'https://www.amd.com/en/corporate/newsroom/press-releases?keyword=&page={}'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url,
                                  headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
                                           'Upgrade-Insecure-Requests': 1,
                                           'if-none-match': '1557830431'},
                                  cookies= cookies, 
                                  callback=self.parse_next,
                                  dont_filter = True)

    #def parse_month(self, response):  # follow drop down menue for different years
    #     data = json.loads(response.text)
    #     #year = re.findall(r'\d{4}',  response.url)[0]
    #     for month in data['activeMonths']:
    #         aux = 'filter.' + month # built part with filter and month to insert in url
    #         month_url = re.sub(r'months',aux ,response.url) # build request url for respective month
    #         yield scrapy.Request(url=month_url, callback=self.parse_next)
    
    def parse_next(self, response):
        auxs = response.xpath('//div[@class="view-content"]/div[@class="views-row"]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./article/div[@class="node__content"]//time/text()').extract_first()
            item['HEADLINE']= aux.xpath('./article/h4/a/span/text()').extract_first()
            item['DOCLINK']= aux.xpath('./article/h4/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./article/div[@class="node__content"]//time/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./article/h4/a/span/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./article/h4/a/@href').extract_first(),
            #        }
            base_url = 'https://www.amd.com'
            aux_url = aux.xpath('./article/h4/a/@href').extract_first()
            
            if '.pdf' in aux_url.lower() or 'static-files' in aux_url.lower():
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
        name_regex = r'xxx'#(This\s*(earnings\s*|press\s*)?release\s*may\s*contain\s*Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*AMD\b)(.|\s)* | (\bAbout.AMD\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        if '.pdf' in response.url.lower() or 'external.file' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//main/div[@class="container"]//div[contains(@class, "field field--name-body")]//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item    
    #def parse_details(self, response):
    #    item = response.meta['item']
    #    #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*AMD\b)(.|\s)* | (\bAbout.AMD\b)(.|\s)*','' ," ".join(response.xpath('//main/div[@class="container"]//div[contains(@class, "field field--name-body")]//text()').extract()))
    #    item['DOCLINK'] = response.url
    #    #if not item['DESCRIPTION']:
    #    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Corning\b)(.|\s)* | (\bAbout.Corning.Incorporated\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="module_body"]//text()').extract()))
    #    #   
    #    yield item



            