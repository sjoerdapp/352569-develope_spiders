

### script to update spiders on scrapy cloud using Update Sourcefile CSV

import csv
import requests
import re

APIKEY ='9c97ff0f27ed491fbc1c33a3dbf856e3'
with open ('UpdateSource/UPDATE_SOURCES_V2_2019-03-23.csv') as file:
	SourcesList = csv.DictReader(file)
	spiders = 

	for row in SourceList:
		spider_ID = row['SOURCE_COMP_ID']
		get_spider_list = requests.get('https://app.scrapinghub.com/api/spiders/list.json?project=352569', auth=("9c97ff0f27ed491fbc1c33a3dbf856e3", '')).json()
		spiderList =get_spider_list['spiders']
			for spider_name in spiderList['id']: 
				if re.match('spider_ID', spider_name):
					print(spider_name)

		



		#r = requests.get('https://app.scrapinghub.com/api/spiders/list.json?project=376964', auth=("9c97ff0f27ed491fbc1c33a3dbf856e3", ' '))
#
#
#		#'GET https://app.scrapinghub.com/api/spiders/list.json?project=376964'
#
#		# curl -u APIKEY: https://app.scrapinghub.com/api/run.json -d project=123 -d spider=spider_name -d units=2 -d add_tag=sometag -d spiderarg1=example -d job_settings='{ "setting1": "value1", "setting2": "value2" }'
#		#_
		#curl -u 9c97ff0f27ed491fbc1c33a3dbf856e3: https://app.scrapinghub.com/api/spiders/list.json?project=352569