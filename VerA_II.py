import json
import scrapy
import requests
from scrapy.selector import Selector
import re
from calendar import month_name

### Verisk Analytics 1|3
### 3 spiders 1&2 für press releases 3 für IR
### 1 until 2016, 2 rest as url is different due to archive

class QuotesInfiniteScrollSpider(scrapy.Spider):
    name = "VerA_II_9900044ARV002"
    #api_url = 'https://www.qualcomm.com/swiftype-search/api/v1/public/engines/search.json?document_types%5B%5D=prod-ember-content&engine_key=k8T2zLsHW5wHbpEEk2k9&page={}'
    #api_url_I = [api_url.format(1)]
    #con_url = '&q=&search_fields%5Bprod-ember-content%5D%5B%5D=title%5E3&search_fields%5Bprod-ember-content%5D%5B%5D=field_keyword_search_boost%5E5&search_fields%5Bprod-ember-content%5D%5B%5D=field_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_private_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_public_part_num&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_subheadline&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_language&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_title&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_description&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_abstract&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_metatag_keywords%5E2&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_viewed&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_aggregation_1&search_fields%5Bprod-ember-content%5D%5B%5D=search_api_access_node&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_document_file_private&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_person_downloadable_bio&search_fields%5Bprod-ember-content%5D%5B%5D=attachments_field_pr_document&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_private_tags%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_document_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_brand%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_segment%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_product_type%3Aname&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_video_description%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_body%3Asummary&search_fields%5Bprod-ember-content%5D%5B%5D=field_pr_subheadline%3Avalue&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_teaser_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_main_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_blog_video%3Atitle&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_image%3Aalt&search_fields%5Bprod-ember-content%5D%5B%5D=field_dev_processor_ref%3Afield_processor_number&search_fields%5Bprod-ember-content%5D%5B%5D=field_device_description%3Avalue&filters%5Bprod-ember-content%5D%5Blanguage%5D=en'
    #start_urls = api_url_I[0].join(con_url)
    #start_urls = ['https://www.verisk.com/archived/'] 
    def start_requests(self):
        years = list(range(2014, 2016)) # 1996 fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
        #del years[0]  # delets first element "NULL" from list of years
        for year in years:
            aux_url = 'https://www.verisk.com/archived/{}/?page=1'
            year_url = [aux_url.format(year)][0]
            yield scrapy.Request(url=year_url, callback=self.parse_next)
            
    #def parse(self, response):  # follow drop down menue for different years
    #     years = list(range(2014, 2016)) # 1996 fill in years which should be scraped, always last yeat +1 as upper bound will not be element of the list
    #     #del years[0]  # delets first element "NULL" from list of years
    #     for year in years:
    #         aux_url = 'https://www.verisk.com/archived/{}/?page=1'
    #         year_url = [aux_url.format(year)][0]
    #         yield scrapy.Request(url=year_url, callback=self.parse_next)

    
    def parse_next(self, response):
        auxs = response.xpath('//div[@class="itemList"]//div[@class="itemContainer "]')
        #pattern = "(.*)(?=—)|".join(month_name[1:])  # define regex so it takes everything including month_name and before long dash (?=) means before 
        for aux in auxs:
            #pattern = "(.*)(?= —)|".join(month_name[1:])  # define regex so it takes everything including month_name and before long dash (?=) means before 
            #test = aux.xpath('.//div[@class="catItemBody"]//p/text()').extract_first() # define string Pubstring is cut out
            #Datum = re.search("(.*)(?=—)|".join(month_name[1:]), aux.xpath('.//div[@class="catItemBody"]//p/text()').extract_first(), re.IGNORECASE).group(0) ## extract date from defined string by regex and select first element
            
            item = {
                    #'PUBSTRING': pattern,
                    'PUBSTRING': re.search(r'Jan\.(.*)\d{4}| Feb\.(.*)\d{4}|Aug\.(.*)\d{4}|Sept\.(.*)\d{4}|Oct\.(.*)\d{4}| Nov\.(.*)\d{4}|Dec\.(.*)\d{4}|January(.*)\d{4}|February(.*)\d{4}|March(.*)\d{4}|April(.*)\d{4}|May(.*)\d{4}|June(.*)\d{4}|July(.*)\d{4}|August(.*)\d{4}|September(.*)\d{4}|October(.*)\d{4}|November(.*)\d{4}|December(.*)\d{4}', aux.xpath('.//div[@class="catItemBody"]//p/text()').extract_first(), re.IGNORECASE).group(0),
                    'HEADLINE': aux.xpath('.//h3/a/text()').extract_first(),
                    'DOCLINK': aux.xpath('.//h3/a/@href').extract_first(),
                    }
            base_url = 'https://www.verisk.com'
            url= base_url + aux.xpath('.//h3/a/@href').extract_first()
            request = scrapy.Request(url=url, callback=self.parse_details)
            request.meta['item'] = item
            yield request
        
        # follow pagination link vianext page url
        next_page_url = response.xpath('//div[@class="pagination-container"]//li[@class="PagedList-skipToNext"]/a[contains(text(), ">")]/@href').extract_first()     
        if next_page_url :
            next_page_url = 'https://www.verisk.com' + next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse_next)
    


    def parse_details(self, response):
        item = response.meta['item']
        #item['Headline'] = response.css('span.ModuleTitleText::text').extract()
        item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Verisk\b)(.|\s)* | (\bAbout.Verisk\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="col-md-12 col-md-gutter"]//text()[not(ancestor::h1)]').extract()))
        item['DOCLINK'] = response.url
        if not item['DESCRIPTION']:
            item['DESCRIPTION'] = re.sub(r'(\bAbout\s*Verisk\s*Analytics\b)(.|\s)* | (\bAbout.Verisk.Analytics\b)(.|\s)*','' ," ".join(response.xpath('//div[@class="itemBody"]//text()').extract()))
            yield item 
        else :
            yield item



            