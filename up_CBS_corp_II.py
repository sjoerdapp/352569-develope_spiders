import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### take news from actual year, if there are more than 20, take first 20

### CBS Corporation Class 2|2
### 2nd spider general News Page
### normal get request, has to follow pagination links for each year
### Date hast to be constructed 
### 

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "CBS_corp_II_2186600ARV002"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/CBS_corp_II_2186600ARV002/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['https://www.cbscorporation.com/news/'] 

    
    def parse(self, response):  # follow drop down menue for different years
         years = list(range(2019, 2020)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://www.cbscorporation.com/news/?cyear={}'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_next)

    #def parse_month(self, response):  # follow drop down menue for different years
    #     data = json.loads(response.text)
    #     #year = re.findall(r'\d{4}',  response.url)[0]
    #     for month in data['activeMonths']:
    #         aux = 'filter.' + month # built part with filter and month to insert in url
    #         month_url = re.sub(r'months',aux ,response.url) # build request url for respective month
    #         yield scrapy.Request(url=month_url, callback=self.parse_next)
    
    def parse_next(self, response):
        auxs = response.xpath('//div[@class="posts-layout"]/article')
        if len(auxs) > 20:
            auxs = response.xpath('//div[@class="posts-layout"]/article')[0:20]

        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('.//div[@class="news-date-info"]//span[1]//text()').extract_first()  +' '+aux.xpath('.//div[@class="news-date-info"]//span[2]//text()').extract_first() + ' '+ aux.xpath('.//div[@class="news-date-info"]//span[3]//text()').extract_first()
            item['HEADLINE']= aux.xpath('.//h2/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('.//h2/a/@href').extract_first()
            #item = {
            #        'PUBSTRING': aux.xpath('./td//div[@class="field__item"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./td/a[2]/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./td/a[2]/@href').extract_first(),
            #        }
            base_url = 'https://www.cbscorporation.com'
            aux_url = aux.xpath('.//h2/a/@href').extract_first()
            
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

        next_page_url = response.xpath('//div[@class="nav-links"]/div[@class="nav-previous"]/a/@href').extract_first()
        if next_page_url:
            if '/3' in next_page_url:
                return
            yield scrapy.Request(url=next_page_url, callback=self.parse_next)
        

        
    def parse_details(self, response):
        item = response.meta['item']
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item   
        else:
            if '/static-files' in response.url.lower():
                item['file_urls'] = [response.url]
                item['DOCLINK'] = response.url 
                item['DESCRIPTION'] = ''   
                yield item
            else:
                
                #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
                item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bDISCLOSURE\s*NOTICE:?\b)(.|\s)*|(\bDisclosure\s*Notice\b)(.|\s)*|(\bAbout\s*CBS\s*Corporation\b)(.|\s)*|(\bAbout.CBS.Corporation\b)(.|\s)*','' ," ".join(response.xpath('//div[contains(@class,"latestnews-content")]/*[not(self::style or self::script or descendant::style or descendant::script)]//text()[not(ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                item['DOCLINK'] = response.url
                #yield item
                if not item['DESCRIPTION']:
                    item['DESCRIPTION'] = re.sub(r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bDISCLOSURE\s*NOTICE:?\b)(.|\s)*|(\bDisclosure\s*Notice\b)(.|\s)*|(\bAbout\s*CBS\s*Corporation\b)(.|\s)*|(\bAbout.CBS.Corporation\b)(.|\s)*','' ," ".join(response.xpath('//article[contains(@class, "full node")]/*[not( descendant::div[contains(@class, "border-left")] or self::style or self::script or descendant::style or descendant::script)]//text()[not(ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
                #    item['file_urls'] = [response.url]
                #    item['DOCLINK'] = response.url
                    yield item
                else:
                    yield item


            