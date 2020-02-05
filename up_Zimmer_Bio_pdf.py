import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### download news of actual year, breack after first two pages, hence 20 news

### Zimmer Biomet 1|1
### All description urls as pdf. think about using text as well
### back to 20010716




class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "ZimBio_4187000ARV001"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/ZimBio_4187000ARV001/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['http://investor.zimmerbiomet.com'] 

    
    def parse(self, response):  # follow drop down menue for different years
        years = list(range(2019, 2021)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #years.append('archive')
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'http://investor.zimmerbiomet.com/news-and-events/news/{}'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_page)

    def parse_page(self, response):  # follow drop down menue for different years
        page_aux = response.xpath('//li[@class="pagerlink"]/a/@href').extract()
        if page_aux:
            help_url = 'http://investor.zimmerbiomet.com'
            page_aux = [help_url + s for s in page_aux]  # ad base url to relative url
            page_aux.insert(0, response.url+'?page=1')
            pages = page_aux
            #year = re.findall(r'\d{4}',  response.url)[0]
            for page in pages:
                if 'page=3' in page:
                    break
                #aux = 'filter.' + month # built part with filter and month to insert in url
                #page_url = page # build request url for respective page
                yield scrapy.Request(url=page, callback=self.parse_next)
        else:
            url = response.url +'?page=1'
            yield scrapy.Request(url=url, callback=self.parse_next)


    
    def parse_next(self, response):
        auxs = response.xpath('//table//tr[not(self::*[@class="trHeaders"] or descendant::*[@class="trHeaders"] )]')
        for aux in auxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./th[@class="pr-date-field"]/text()[2]').extract_first() # cuts out the part berfore the date as well as the /n at the end of the string
            item['HEADLINE']= aux.xpath('./td[@class="pr-title-field"]/a//text()[not(ancestor::span)]').extract_first()
            item['DOCLINK']= aux.xpath('./td[@class="pr-title-field"]/a/@href').extract_first()
            
            base_url = 'http://investor.zimmerbiomet.com'
            aux_url = aux.xpath('./td[@class="pr-title-field"]/a/@href').extract_first()
            
            if not item['HEADLINE']:
                item['DOCLINK']= aux.xpath('./td[@class="pr-document-field"]/a/@href').extract_first()
                item['HEADLINE']= aux.xpath('./td[@class="pr-title-field"]/text()[2][not(ancestor::span)]').extract_first()
                base_url = 'http://investor.zimmerbiomet.com'
                aux_url = aux.xpath('./td[@class="pr-document-field"]/a/@href').extract_first()
            
            if 'pdf' in aux_url.lower():
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
        name_regex = r'(About\s*Zimmer\s*Founded\s*in\s*1927)(.|\s)*|(About\s*Zimmer\s*Holdings)(.|\s)*|(About\s*the\s*Company\s*Founded)(.|\s)*|(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(Zimmer\s*Safe\s*Harbor\s*Statement)(.|\s)*|(\bAbout\s*Zimmer\s*Biomet\b)(.|\s)*|(\bAbout.Zimmer.Biomet\b)(.|\s)*'##(Forward(.|\s*)Looking\s*Statements)(.|\s)*|
        if 'pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
            #item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains( @class, "main-content")]/p//text()[not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DESCRIPTION'] = re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class,"pr-headline")]/hl2//text()|//div[contains(@class,"release-body")]//text()[not(ancestor::h2 or ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE)
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item



            