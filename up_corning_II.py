import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### scrape last 3 moth of actual year

### Corning Inc. 2|2
### first spider IR page second News
### both come in json file
### back to 20040708


class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "CORN_II_2052300ARV002"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/CORN_II_2052300ARV002/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types[]=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page=2&q=&facets[prod-ember-content][]=field_content_tags:name&fetch_fields[prod-ember-content][]=created&fetch_fields[prod-ember-content][]=field_content_tags:name&fetch_fields[prod-ember-content][]=field_pr_body:value&fetch_fields[prod-ember-content][]=field_pr_body:summary&fetch_fields[prod-ember-content][]=field_pr_subheadline&fetch_fields[prod-ember-content][]=field_pr_click_through&fetch_fields[prod-ember-content][]=field_publish_date&fetch_fields[prod-ember-content][]=field_press_note&fetch_fields[prod-ember-content][]=search_api_metatag_description&fetch_fields[prod-ember-content][]=sticky&fetch_fields[prod-ember-content][]=title&fetch_fields[prod-ember-content][]=type&fetch_fields[prod-ember-content][]=url&search_fields[prod-ember-content][]=title^3&search_fields[prod-ember-content][]=field_keyword_search_boost^5&search_fields[prod-ember-content][]=field_device_subheadline&search_fields[prod-ember-content][]=field_processor_number&search_fields[prod-ember-content][]=field_product_private_part_num&search_fields[prod-ember-content][]=field_product_public_part_num&search_fields[prod-ember-content][]=search_api_language&search_fields[prod-ember-content][]=search_api_metatag_title&search_fields[prod-ember-content][]=search_api_metatag_description&search_fields[prod-ember-content][]=search_api_metatag_abstract&search_fields[prod-ember-content][]=search_api_metatag_keywords^2&search_fields[prod-ember-content][]=search_api_viewed&search_fields[prod-ember-content][]=search_api_aggregation_1&search_fields[prod-ember-content][]=search_api_access_node&search_fields[prod-ember-content][]=attachments_field_person_downloadable_bio&search_fields[prod-ember-content][]=attachments_field_pr_document&search_fields[prod-ember-content][]=attachments_field_document_file_private&search_fields[prod-ember-content][]=body:value&search_fields[prod-ember-content][]=body:summary&search_fields[prod-ember-content][]=field_blog_teaser_image:alt&search_fields[prod-ember-content][]=field_blog_main_image:alt&search_fields[prod-ember-content][]=field_private_tags:name&search_fields[prod-ember-content][]=field_blog_video:title&search_fields[prod-ember-content][]=field_pr_body:value&search_fields[prod-ember-content][]=field_pr_body:summary&search_fields[prod-ember-content][]=field_pr_subheadline:value&search_fields[prod-ember-content][]=field_device_description:value&search_fields[prod-ember-content][]=field_device_image:alt&search_fields[prod-ember-content][]=field_dev_processor_ref:field_processor_number&search_fields[prod-ember-content][]=field_document_description:value&search_fields[prod-ember-content][]=field_video_description:value&search_fields[prod-ember-content][]=field_video_description:summary&search_fields[prod-ember-content][]=field_product_brand:name&search_fields[prod-ember-content][]=field_product_description:value&search_fields[prod-ember-content][]=field_product_description:summary&search_fields[prod-ember-content][]=field_product_segment:name&search_fields[prod-ember-content][]=field_product_type:name&filters[prod-ember-content][type]=press_release&filters[prod-ember-content][language]=en&per_page=18&sort_direction[prod-ember-content]=desc&sort_field[prod-ember-content]=field_publish_date']

    
    def parse(self, response):  # follow drop down menue for different years
         years = list(range(2019, 2021)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
         #del years[0]  # delets first element "NULL" from list of years
         for year in years:
             aux_url = 'https://www.corning.com/content/corning/worldwide/en/about-us/news-events/news-releases/_jcr_content/par/newslisting_ba04.months.{}.json'
             year_url = [aux_url.format(year)][0]
             yield scrapy.Request(url=year_url, callback=self.parse_month)

    def parse_month(self, response):  # follow drop down menue for different years
         data = json.loads(response.text)
         #year = re.findall(r'\d{4}',  response.url)[0]
         for month in data['activeMonths'][-3: ]:
             aux = 'filter.' + month # built part with filter and month to insert in url
             month_url = re.sub(r'months',aux ,response.url) # build request url for respective month
             yield scrapy.Request(url=month_url, callback=self.parse_next)
    
    def parse_next(self, response):
        data = json.loads(response.text)
        #data_aux = data['records']['prod-ember-content']
        for prod in data:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = prod['publishDate']
            item['HEADLINE']= prod['longTitle']
            item['DOCLINK']= prod['cta']
            #item = {
            #    'PUBSTRING': prod['publishDate'],
            #    'HEADLINE' : prod['longTitle'],
            #    'DOCLINK' : prod['cta'],
            #    }
            
            base_url = 'https://www.corning.com'
            aux_url = prod['cta']
            
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
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*Corning\s*Incorporated\b)(.|\s)*| (\bAbout.Corning.Incorporated\b)(.|\s)*'
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[@class="event-des-container"]//text()[not(ancestor::div[@class="box__right"] or ancestor::div[@class="date-container"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
        item['DOCLINK'] = response.url
        if not re.search('[a-zA-Z]', item['DESCRIPTION']):
            item['DESCRIPTION'] = ''
            yield item
        else:
            yield item



            