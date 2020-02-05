import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### take last 20 news of each page/url

### Mettler Toledo International 2|2
### 1 spider IR 2nd  spider Press Rleases have to scrape all tabs to miss nothing
### normal get request but content comes in json
### original source nur javascript 
### some pubstirngs are randomly empty....
### goes back to 20130311

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "Mettler_II_3215800ARV002"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/Mettler_II_3215800ARV002/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = [
        'https://www.mt.com/us/en/home/supportive_content/press-releases/jcr:content/standardpar/listoverview.listOverviewSrch.p.all.json',
        'https://www.mt.com/us/en/home/supportive_content/press-releases/jcr:content/standardpar/listoverview.listOverviewSrch.a.all.json',
        'https://www.mt.com/us/en/home/supportive_content/press-releases/jcr:content/standardpar/listoverview.listOverviewSrch.i.all.json',
        'https://www.mt.com/us/en/home/supportive_content/press-releases/jcr:content/standardpar/listoverview.listOverviewSrch.w.all.json',
        ] 

    
    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(1997, 2020)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://mt.gcs-web.com/news-releases?field_nir_news_date_value%5Bmin%5D={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)
#
    #def parse_month(self, response):  # follow drop down menue for different years
    #     data = json.loads(response.text)
    #     #year = re.findall(r'\d{4}',  response.url)[0]
    #     for month in data['activeMonths']:
    #         aux = 'filter.' + month # built part with filter and month to insert in url
    #         month_url = re.sub(r'months',aux ,response.url) # build request url for respective month
    #         yield scrapy.Request(url=month_url, callback=self.parse_next)
    
    def parse(self, response):
        body = json.loads(response.text) 
        body_rows = body['rows']
        if len(body_rows) > 20:
            body_rows = body_rows[0:20]


        for dat in body_rows:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = dat['jsDate']
            item['HEADLINE']= dat['title']
            item['DOCLINK']= dat['href']
            #item = {
            #        'PUBSTRING': aux.xpath('./td//div[@class="field__item"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./td/a[2]/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./td/a[2]/@href').extract_first(),
            #        }
            base_url = 'https://www.mt.com'
            aux_url = dat['href']
            
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
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
            item['DESCRIPTION'] = re.sub(r'(\bMETTLER\s*TOLEDO\s*is\s*a\s*leading\s*global\s*supplier\b)(.|\s)* | (\bAbout.Mettler.Toledo\b)(.|\s)*','' ," ".join(response.xpath('//div[@id="mainContent"]//text()[not(self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not item['PUBSTRING']:
                item['PUBSTRING'] = re.split('—', ''.join(re.split('(\d+\s*—)', re.split('Switzerland\s*—', item['DESCRIPTION'])[-1])[0:2]))[0]
                if 'Greifensee' in item['PUBSTRING']:
                    item['PUBSTRING'] = re.split('(\d+\s*—|–)', re.split('Greifensee, (Switzerland\s*)?—?', item['DESCRIPTION'], 1)[-1])[0]
           
            if not item['DESCRIPTION']: 
                item['DESCRIPTION'] = re.sub(r'(\bMETTLER\s*TOLEDO\s*is\s*a\s*leading\s*global\s*supplier\b)(.|\s)* | (\bAbout.Mettler.Toledo\b)(.|\s)*','' ," ".join(response.xpath('//div[@id="main_layer"]//div[@class="text parbase section"]//text()[not(self::style or self::script or ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                yield item
            else:   
                yield item



            