import scrapy
import re
import json
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header
from scrapy.selector import Selector
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### latest 20 news
### 

### Microchip Technology Incorporate 2|3
### Financial Press Releases
### only PDFs therefore last spider
### get request, all news come in ona page as json
### extracts json list out of script element on page
### back to 20110505

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "Mic_Tech_III_1202700ARV003"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Mic_Tech_III_1202700ARV003/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = [
                'https://www.microchip.com/documentlisting/financial-press-releases',
                 ] 

    
    def parse(self, response): 
        auxs = json.loads(response.xpath('//script[contains(., "json")]/text()').extract_first().split('"Docs": ')[1].rsplit(']')[0]+']') ## extracts json list out of script element on page
        base_url = 'https://www.microchip.com/'
        for aux in auxs[0:20]:
            item = SwisscomIvCrawlerItem()
            item['file_urls'] = [base_url + aux['Url']]
            item['PUBSTRING'] = aux['CreationDate']
            item['HEADLINE']= re.split(r'.\d{6,}', aux['Title'])[0]
            item['DOCLINK']= base_url + aux['Url']
            item['DESCRIPTION'] = ''
            yield item
            #item = {
            #        'PUBSTRING': aux.xpath('./following-sibling::div[@data-label="Date"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./a/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./a/@href').extract_first(),
            #        }
            #base_url = 'https://www.microchip.com'
            #url= base_url + aux.xpath('./a/@href').extract_first()
            #request = scrapy.Request(url=url, callback=self.parse_details)
            #request.meta['item'] = item
            #yield request

           # else:
           #     item = SwisscomIvCrawlerItem()
           #     item['file_urls'] = [url]
           #     item['PUBSTRING'] = dat['date'][0]['date']
           #     item['HEADLINE']= dat['Headline']
           #     item['DOCLINK']= url
           #     yield item 
   
        
    #def parse_details(self, response):
    #    item = response.meta['item']
    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Microchip\s*Technology\b)(.|\s)* | (\bAbout.Micropchip.Technology\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="col-md-12"]//div[@class="subHeadLine"]//text() | //div[@id="pressContent"]//text()').extract()))
    #    item['DOCLINK'] = response.url
    #    yield item
    #    #if not item['DESCRIPTION']:
    #    #    item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Nucor\b)(.|\s)* | (\bAbout.Nucor\b)(.|\s)*','' ," ".join(Selector(text=content).xpath('//p/text()').extract()))
    #    #    yield item
    #    #else: 
    #    #    yield item



            