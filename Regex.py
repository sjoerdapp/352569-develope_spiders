


re.search(r'January(.*)(?=—)|February(.*)(?=—)|March(.*)(?=—)|April(.*)(?=—)|May(.*)(?=—)|June(.*)(?=—)|July(.*)(?=—)|August(.*)(?=—)|September(.*)(?=—)|October(.*)(?=—)|November(.*)(?=—)|December(.*)(?=—)', aux.xpath('.//div[@class="catItemBody"]//p/text()').extract_first(), re.IGNORECASE).group(0),