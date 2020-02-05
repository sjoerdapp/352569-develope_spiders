import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from swisscom_IV_crawler.items import SwisscomIvCrawlerItem

### UPDATES
### scrap top 3 news + 15 most actual, total 18 news

### NetApp Inc 1|1
### 1 spider Newsroom All Reseases
### normal get request and all pdfs
### goes back 20041220 -> base page goes back to 2002 however most links after 2002 are broken
### no working links afer 2004
### also page only goes backt to 2016 in chrome
### only 1 page per year
### most links after 2008 are broken

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "net_app_1415200ARV001"
    custom_settings = {
         'JOBDIR' : 'None',
         'FILES_STORE' : 's3://352569/net_app_1415200ARV001/',
        }
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    start_urls = ['https://www.netapp.com/us/company/news/press-releases.aspx?year=all',
    #'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year=2015',
    #'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year=2014',
    #'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year=2013',
    #'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year=2012',
    #'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year=2011',
    #'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year=2010',
    #'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year=2009'] 
    ]
    #def start_requests(self):  # follow drop down menue for different years
    #     years = list(range(1, 23)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.netapp.com/us/company/news/press-releases.aspx?page={}'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse)
    
    def parse(self, response):  # follow drop down menue for different years
        auxxs = response.xpath('//a[contains(@class, "flex__item")]')
        for auxx in auxxs:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = auxx.xpath('.//p/text()').extract_first()
            item['HEADLINE']= auxx.xpath('.//h3/text()').extract_first()
            item['DOCLINK']= auxx.xpath('./@href').extract_first()
            
            base_url = 'https://www.netapp.com'
            auxx_url = item['DOCLINK']
            
            url= base_url + auxx_url
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request

        auxs = response.xpath('//table//tr[not(ancestor::thead)]')
        for aux in auxs[0:15]:
            item = SwisscomIvCrawlerItem()
            item['PUBSTRING'] = aux.xpath('./td/text()').extract_first()
            item['HEADLINE']= aux.xpath('./th/a/text()').extract_first()
            item['DOCLINK']= aux.xpath('./th/a/@href').extract_first()
            if not item['DOCLINK']:
                continue
            #item = {
            #        'PUBSTRING': aux.xpath('./td//div[@class="field__item"]/text()').extract_first(),
            #        'HEADLINE': aux.xpath('./td/a[2]/text()').extract_first(),
            #        'DOCLINK': aux.xpath('./td/a[2]/@href').extract_first(),
            #        }
            base_url = 'https://www.netapp.com'
            aux_url =  item['DOCLINK']

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

        #years = list(range(2002, 2019)) # fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        ##del years[0]  # delets first element "NULL" from list of years
        #for year in years:
        #    aux_url = 'https://www.netapp.com/us/company/news/press-releases.aspx?page=1&year={}'
        #    year_url = [aux_url.format(year)][0]
        #    yield scrapy.Request(url=year_url, callback=self.parse_next)

    #def parse_month(self, response):  # follow drop down menue for different years
    #     data = json.loads(response.text)
    #     #year = re.findall(r'\d{4}',  response.url)[0]
    #     for month in data['activeMonths']:
    #         aux = 'filter.' + month # built part with filter and month to insert in url
    #         month_url = re.sub(r'months',aux ,response.url) # build request url for respective month
    #         yield scrapy.Request(url=month_url, callback=self.parse_next)
    
    
        
    def parse_details(self, response):
        item = response.meta['item']
        name_regex = r'(Forward(.|\s*)Looking\s*Statements)(.|\s)*|(\bAbout\s*NetApp\b)(.|\s)* | (\bAbout.NetApp\b)(.|\s)*'
        if '.pdf' in response.url.lower():
            item['file_urls'] = [response.url]
            item['DOCLINK'] = response.url
            item['DESCRIPTION'] = ''
            yield item
        else:
            #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
            item['DESCRIPTION'] =  re.sub(r'(View\s*Financial\s*Tables\s*\(\s*PDF\s*\))','', re.sub(name_regex,'' ," ".join(response.xpath('//div[contains(@class, "n-articles")]//text()[not(ancestor::h1)][not(ancestor::b[@class="dateline"])][not(ancestor::div[@class="box__right"] or self::style or self::script or  ancestor::style or ancestor::script or ancestor::p[@id="news-body-cta"] or ancestor::div[@id="bwbodyimg"])]').extract()), flags=re.IGNORECASE))
            item['DOCLINK'] = response.url
            if not re.search('[a-zA-Z]', item['DESCRIPTION']):
                item['DESCRIPTION'] = 'FEHLER'
                yield item
            else:
                yield item


            