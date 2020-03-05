

### script to update spiders on scrapy cloud using Update Sourcefile CSV

import csv
import requests
import re
import json

APIKEY ='9c97ff0f27ed491fbc1c33a3dbf856e3'
start = 420 # number after which spider should be started, starts with 0 (includes first argument)
stop = 29 ## range of how many spiders should be updated # spiders = figure+1 as python counts zero
with open ('//?/C:/Users/chris/strique/scraping/US/UpdateSource/UPDATE_SOURCES_V2_2020-03-04.csv') as file:
	SourcesList = csv.DictReader(file, delimiter=';')
	get_spider_list = json.loads(requests.get('https://app.scrapinghub.com/api/spiders/list.json?project=352569', auth=("9c97ff0f27ed491fbc1c33a3dbf856e3", '')).text)
	SpiderList =get_spider_list['spiders']
	project = '352569'
	#print(SpiderLis180
	#print(SpiderList[0]['id'])
	#print(SourcesList)#spiders = 
	count_start = 0
	count_stop = 0
	for row in SourcesList:
	#	#print(row)
	#	#if count >5 :
	#	#	break
		#count += 1
		spider_ID = row['SOURCE_COMP_ID']
		count_start += 1
		if count_start > start:
			if count_stop > stop:
				break
			count_stop += 1  
			#print(type(spiderList))
			for spider in SpiderList: 
				spider_name = spider['id']
				#print(spider_name)
				if spider_ID in spider_name:
					data = {
					'project' : project, 
					'spider' : spider_name,
					}
					url = 'https://app.scrapinghub.com/api/run.json'
					run_spider = requests.post('https://app.scrapinghub.com/api/run.json', data = data, auth=("9c97ff0f27ed491fbc1c33a3dbf856e3", '') )
					print(spider_name)
	#	#r = requests.get('https://app.scrapinghub.com/api/spiders/list.json?project=376964', auth=("9c97ff0f27ed491fbc1c33a3dbf856e3", ' '))
#
#
#		#'GET https://app.scrapinghub.com/api/spiders/list.json?project=376964'
#
#		# curl -u APIKEY: https://app.scrapinghub.com/api/run.json -d project=123 -d spider=spider_name -d units=2 -d add_tag=sometag -d spiderarg1=example -d job_settings='{ "setting1": "value1", "setting2": "value2" }'
#		#_
		#curl -u 9c97ff0f27ed491fbc1c33a3dbf856e3: https://app.scrapinghub.com/api/spiders/list.json?project=352569