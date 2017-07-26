# -*- coding: utf-8 -*-
import os, json, datetime, re, csv
from shutil import copyfile
from lxml import etree
from unicodedata import normalize

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

def readDate(target_date):
#	print(target_date)
	if len(target_date) == 4:
		format = '%Y'
	elif len(target_date) == 6:
		if target_date[4:6] == '00':
			format = '%Y00'
		elif int(target_date[4:6]) <= 12:
			format = '%Y%m'
		else:
			format = '%Y%d'
	elif len(target_date) == 8:
		if target_date[6:] == '00' and target_date[4:6] == '00':
			format = '%Y0000'
		elif target_date[4:6] == '00' and target_date[6:] != '00':
			format = '%Y00%d'
		elif target_date[6:] == '00':
			if int(target_date[4:6]) <= 12:
				format = '%Y%m00'
			else:
				format = '%Y%d00'
		else:
			if int(target_date[4:6]) <= 12:
				format = '%Y%m%d'
			else:
				format = '%Y%d%m'
	else:
		if len(target_date) > 8:
			return readDate(target_date[:8])
		elif len(target_date) > 6:
			return readDate(target_date[:6])
		elif len(target_date) > 4:
			format = '%Y'
		elif len(target_date) > 2:
			format = '%y'

	print(target_date)
	return datetime.datetime.strptime(target_date,format)

def extractDate(text_string):
	print("EXTRACTING DATE")
	print(text_string)
	year_results = re.search(r'[12][890][0-9][0-9]',text_string)
	year = None
	if year_results:
		year = year_results.group(0)
		print(year_results.group(0))

	month = None
	month_results = re.search(ur'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)',normalize('NFC',(text_string.lower().decode('utf-8') if type(text_string) is str else text_string.lower())))
	months = {u'janvier': '01',u'février': '02',u'mars': '03',u'avril': '04',u'mai': '05',u'juin': '06',u'juillet': '07',u'août': '08',u'septembre': '09',u'octobre': '10',u'novembre': '11',u'décembre': '12'}
	if month_results:
		month = months[month_results.group(0)]
		print(month_results.group(0))
	else:
		month = '00'

	thirty_one_day_re = r' (1er|[1-9]|[12][0-9]|3[01]) '
	thirty_day_re = r' (1er|[1-9]|[12][0-9]|30) '
	twenty_nine_day_re = r' (1er|[1-9]|[12][0-9]) '

	day = None
	if month in ['01','03','05','07','08','10','12']:
		day_result = re.search(thirty_one_day_re,text_string)
	elif month in ['04','06','09','11']:
		day_result = re.search(thirty_day_re,text_string)
	else:
		day_result = re.search(twenty_nine_day_re,text_string)

	if day_result:
		print(day_result.group(0).strip(' '))
		day = day_result.group(0).strip(' ')
		if day == '1er':
			day = '01'
		elif len(day) == 1:
			day = '0' + day
	else:
		day = '00'

	if type(year) is unicode:
		year = year.encode('utf-8')

	if type(day) is unicode:
		day = day.encode('utf-8')
	
	if not year:
		return None
	else:
		return readDate(year+month+day).date().isoformat()

def extractVolumeNumber(text_string):
	volume_result = re.search(r'(vol|n)\. ([0-9]|[ivx])*,',text_string)
	if volume_result:
		print(volume_result.group(0))
		volume_number = volume_result.group(0)[volume_result.group(0).find('.')+2:-1]
		return volume_number
	else:
		return None

def getPages(text_string):
	page_results = re.search(r'p\. ([0-9]*:)?[0-9]+-?[0-9]*(, ([0-9]*:)?[0-9]+-?[0-9]*)*',text_string)
	if page_results:
		page_results_string = page_results.group(0)[3:]

		first_dash = page_results_string.find('-')
		first_colon = page_results_string.find(':')
		first_comma = page_results_string.find(',')

		#cases:
		#p. #:#  		X
		#p. #:#- 		X
		#p. #:#, 		X
		#p. #-			X
		#p. #,			X
		#p. #    		X
		#Null cases     X

		if first_dash < 0 and first_colon < 0 and first_comma < 0:
			first_page = page_results_string
		if first_colon > 0 and ((first_colon < first_dash or first_colon < first_comma) or (first_dash < 0 and first_comma < 0)):
			if (first_comma < 0 and first_dash > 0) or (first_dash > 0 and first_dash < first_comma):
				first_page = page_results_string[first_colon+1:first_dash]
			elif (first_dash < 0 and first_comma > 0) or (first_comma > 0 and first_comma < first_dash):
				first_page = page_results_string[first_colon+1:first_comma]
			else:
				first_page = page_results_string[first_colon+1:]
		elif first_colon < 0 or (first_dash > 0 and first_dash < first_colon) or (first_comma > 0 and first_comma < first_colon):
			if (first_dash < first_comma and first_dash > 0) or (first_dash > 0 and first_comma < 0):
				first_page = page_results_string[:first_dash]
			elif (first_comma < first_dash and first_comma > 0) or (first_comma > 0 and first_dash < 0):
				first_page = page_results_string[:first_comma]
		else:
			first_page = None

		last_dash = page_results_string.rfind('-')
		last_colon = page_results_string.rfind(':')
		last_comma = page_results_string.rfind(',')

		#cases:
		# -#
		# , #
		# , #:#

		if last_dash < 0 and last_colon < 0 and last_comma < 0:
			last_page = None
		elif last_dash >= first_dash and last_dash > last_colon and last_dash > last_comma:
			last_page = page_results_string[last_dash+1:]
		elif last_comma >= first_comma and last_comma > last_dash:
			if last_colon > last_comma:
				last_page = page_results_string[last_colon+1:]
			else:
				last_page = page_results_string[last_comma+2:]
		else:
			last_page = None

		return first_page, last_page

	return None, None

def generateChronologyCitation(bibl_root,linked_names):
	new_citation = {}
	new_titles = bibl_root.xpath('.//title')
	title_counter = 0
	new_author = bibl_root.xpath('.//author/name/@key')
	if new_author:
		new_citation['author'] = { '@type': 'Person', '@id': 'catalogdata.library.illinois.edu/lod/entries/Persons/kp/' + new_author[0] }

	for title in new_titles:
		new_types = title.xpath('./@type')
		new_levels = title.xpath('./@level')
#		if ('es' in new_types or 're' in new_types) or 'a' in new_levels:
#			new_citation['headline'] = title.xpath('./text()')[0]
#			new_citation['@type'] = 'Text'
#		else:
#			new_citation['name'] = title.xpath('./text()')[0]
#			new_citation['@type'] = 'CreativeWork'

		if title_counter > 0:
			print("Multiple Titles")
			text_data = max([ x.strip() for x in bibl_root.xpath('./text()') ],key=len)
			if 'j' in new_levels:
				new_citation['isPartOf'] = { '@type': 'PublicationIssue' }
				new_citation['isPartOf']['name'] = title.xpath('./text()')[0]
				print(new_citation['isPartOf']['name'])
				date_created = extractDate(text_data)
				if date_created:
					new_citation['isPartOf']['dateCreated'] = date_created
				volume_number = extractVolumeNumber(text_data)
				if volume_number:
					new_citation['isPartOf']['issueNumber'] = volume_number
			else:
				new_citation['isPartOf'] = { '@type': 'PublicationVolume' }
				date_published = extractDate(text_data)
				if date_published:
					new_citation['isPartOf']['datePublished'] = date_published
				volume_number = extractVolumeNumber(text_data)
				if volume_number:
					new_citation['isPartOf']['volumeNumber'] = volume_number
			
			page_start, page_end = getPages(text_data)
			if page_start:
				new_citation['isPartOf']['pageStart'] = page_start
			if page_end:
				new_citation['isPartOf']['pageEnd'] = page_end
		else:
			new_citation['@type'] = 'CreativeWork'
			if ('es' in new_types or 're' in new_types) or 'a' in new_levels:
				new_citation['headline'] = title.xpath('./text()')[0]
			else:
				new_citation['name'] = title.xpath('./text()')[0]

		title_counter += 1

	return new_citation

def generateBibCitation(bibl_root,linked_names):
	new_citation = {}
	new_titles = bibl_root.xpath('.//title')
	title_counter = 0
	new_author = bibl_root.xpath('.//author/name/@key')
	if new_author:
		new_citation['author'] = { '@type': 'Person', '@id': 'catalogdata.library.illinois.edu/lod/entries/Persons/kp/' + new_author[0] }
	else:
		new_authors = bibl_root.xpath('.//author/name/text()')
		if new_authors:
			for author in new_authors:
				if author in linked_names[1]:
					new_citation['author'] = { '@type': 'Person', '@id': 'catalogdata.library.illinois.edu/lod/entries/Persons/kp/' + linked_names[0][linked_names[1].index(author)] }
					print("FOUND AUTHOR IN CITATION")
					print(author)
					print(linked_names[0][linked_names[1].index(author)])


	dates = bibl_root.xpath('./date/@when')
	new_citation['dateCreated'] = readDate(dates[0]).date().isoformat()

	for title in new_titles:
		new_types = title.xpath('./@type')
		new_levels = title.xpath('./@level')

		if title_counter > 0:
			print("Multiple Titles")
			text_data = max([ x.strip() for x in bibl_root.xpath('./text()') ],key=len)

			if 'j' in new_levels:
				new_citation['isPartOf'] = { '@type': 'PublicationIssue' }
				new_citation['isPartOf']['name'] = title.xpath('./rs/text()')[0]

				new_issue_number = bibl_root.xpath('./biblScope[@type="issue"]/text()')
				if new_issue_number:
					new_citation['isPartOf']['issueNumber'] = new_issue_number[0]

				pub_place = bibl_root.xpath('./pubPlace/text()')
				if pub_place:
					new_citation['locationCreated'] = pub_place[0]

				new_publisher = bibl_root.xpath('./publisher/text()')
				if new_publisher:
					new_citation['publisher'] = new_publisher[0]

				new_date_published = bibl_root.xpath('./date/@when')
				if new_date_published:
					new_citation['datePublished'] = readDate(new_date_published[0]).date().isoformat()

#				new_volume_number = bibl_root.xpath('./biblScope[@type="vol"]/text()')
#				if new_volume_number:
#					print(new_volume_number[0])
			else:
				new_citation['isPartOf'] = { '@type': 'PublicationVolume' }

				new_volume_number = bibl_root.xpath('./biblScope[@type="vol"]/text()')
				if new_volume_number:
					new_citation['isPartOf']['volumeNumber'] = new_volume_number[0]

			new_pages = bibl_root.xpath('./biblScope[@type="pages"]/text()')
			if new_pages:
#				print(new_pages[0])
#				print(getPages(new_pages[0]))
				page_start, page_end = getPages(new_pages[0])
				if page_start:
					new_citation['isPartOf']['pageStart'] = page_start
				if page_end:
					new_citation['isPartOf']['pageEnd'] = page_end

		else:
			new_citation['@type'] = 'CreativeWork'
			if ('es' in new_types or 're' in new_types) or 'a' in new_levels:
				new_citation['headline'] = title.xpath('./rs/text()')[0]
			else:
				new_citation['name'] = title.xpath('./rs/text()')[0]

		title_counter += 1

	return new_citation

def processTEIFile(tei_file,linked_names):
	with open(tei_file,'rb') as infile:
		card = infile.read()

	output_card = {
		'@context': [ 
			'http://schema.org/',
			{
				's': 'http://schema.org/',
				'scp': 'http://ns.library.illinois.edu/scp'
			}
		]
	}
#	print(card)
	root = etree.fromstring(card)

	card_type = tei_file[tei_file.rfind('/')+1:][0]
	if card_type == 's' or card_type == 'p':
		#bibliography
		output_card['@id'] = root.xpath('/TEI/@xml:id')[0]
		output_card['@type'] = 'Dataset'
		output_card['author'] = { '@type': 'Person', '@id': 'http://viaf.org/viaf/44300868'}
		print(output_card['@id'])
#		print(root.xpath('/TEI/teiHeader/fileDesc/titleStmt/title/text()')[1])
#		print(root.xpath('/TEI/teiHeader/fileDesc/editionStmt/edition/date/@when')[0])
		if root.xpath('/TEI/teiHeader/fileDesc/editionStmt/edition/date/@when'):
			output_card['dateCreated'] = readDate(root.xpath('/TEI/teiHeader/fileDesc/editionStmt/edition/date/@when')[0]).date().isoformat()
		elif root.xpath('/TEI/teiHeader/fileDesc/editionStmt/edition/date/@value'):
			output_card['dateCreated'] = readDate(root.xpath('/TEI/teiHeader/fileDesc/editionStmt/edition/date/@value')[0]).date().isoformat()
		if root.xpath('/TEI/text/body/div1/head/date/@when'):
			output_card['temporalCoverage'] = readDate(root.xpath('/TEI/text/body/div1/head/date/@when')[0]).date().isoformat()
		elif root.xpath('/TEI/text/body/div1/head/date/@value'):
			output_card['temporalCoverage'] = readDate(root.xpath('/TEI/text/body/div1/head/date/@value')[0]).date().isoformat()

		output_card['mentions'] = [ { '@type': 'CreativeWork', 'title': x } for x in root.xpath('/TEI/text/body/div2/p/title/rs/text()') + root.xpath('/TEI/text/body/div2/note/title/rs/text()') ]
		output_card['mentions'] += [ { '@type': 'Person', '@id': 'catalogdata.library.illinois.edu/lod/entries/Persons/kp/' + x } for x in root.xpath('/TEI/text/body/div2/p/name/@key') + root.xpath('/TEI/text/body/div2/note/name/@key') if x in linked_names[0] ]
		print(output_card['mentions'])
		if len(output_card['mentions']) == 1:
			output_card['mentions'] = output_card['mentions'][0]
		elif len(output_card['mentions']) == 0:
			del output_card['mentions']

		if 'mentions' in output_card:
			print(output_card['mentions'])

		output_card['citation'] = [ generateBibCitation(y,linked_names) for y in root.xpath('//div2/bibl') + root.xpath('//div2/p/bibl') + root.xpath('//div2/note/bibl') ]
		print(output_card['citation'])
		output_card['citation'] = [ z for z in output_card['citation'] if len(z) > 0 ]
		if len(output_card['citation']) == 1:
			output_card['citation'] = output_card['citation'][0]
		elif len(output_card['citation']) == 0:
			del output_card['citation']

		if 'citation' in output_card:
			print(output_card['@id'])
	else:
		#chronology
		output_card['@id'] = root.xpath('/TEI/@xml:id')[0]
		output_card['@type'] = 'Dataset'
		output_card['author'] = { '@type': 'Person', '@id': 'http://viaf.org/viaf/44300868'}
		output_card['inLanguage'] = 'fr'
		if root.xpath('//head/date/@value'):
			output_card['temporalCoverage'] = readDate(root.xpath('//head/date/@value')[0]).date().isoformat()
		elif root.xpath('//head/date/@when'):
			output_card['temporalCoverage'] = readDate(root.xpath('//head/date/@when')[0]).date().isoformat()
		
		output_card['mentions'] = [ { '@type': 'CreativeWork', 'title': x } for x in root.xpath('//div1//p/title/text()') + root.xpath('//div1//note/title/text()') ]
		output_card['mentions'] += [ { '@type': 'Person', '@id': 'catalogdata.library.illinois.edu/lod/entries/Persons/kp/' + x } for x in root.xpath('//div1//p/name/@key') + root.xpath('//div1//note/name/@key') if x in linked_names[0] ]
#		output_card['mentions'] += [ { '@type': 'Person', '@id': 'catalogdata.library.illinois.edu/lod/entries/Persons/kp/' + linked_names[0][linked_names[1].index(x)] } for x in root.xpath('//div1//p/name/text()') + root.xpath('//div1//note/name/text()') if x in linked_names[1] ]
		if len(output_card['mentions']) == 1:
			output_card['mentions'] = output_card['mentions'][0]
		elif len(output_card['mentions']) == 0:
			del output_card['mentions']

		output_card['citation'] = [ generateChronologyCitation(y,linked_names) for y in root.xpath('//div1//bibl') ]
		output_card['citation'] = [ z for z in output_card['citation'] if len(z) > 0 ]
		if len(output_card['citation']) == 1:
			output_card['citation'] = output_card['citation'][0]
		elif len(output_card['citation']) == 0:
			del output_card['citation']

		if 'citation' in output_card:
			print(tei_file)


	return json.dumps(output_card,indent=4)

def makeOutputFolder(folder_name,counter):
	try:
		if counter is not None:
			write_folder_name = folder_name + ' (' + str(counter) + ')'
		else:
			write_folder_name = folder_name

		write_folder = os.mkdir(write_folder_name)
		return write_folder, write_folder_name
	except OSError:
		if counter is not None:
			return makeOutputFolder(folder_name,counter+1)
		else:
			return makeOutputFolder(folder_name,0)

def writeNewFile(file_path,copy=False,file_contents=None):
	path_elements = file_path.split(SLASH)
#	print(path_elements)

	built_path = path_elements[0] + SLASH

	for index in range(1,len(path_elements)-1):
		if not os.path.exists(built_path + path_elements[index]):
			os.makedirs(built_path + path_elements[index])

		built_path += path_elements[index] + SLASH

	if copy:
		copyfile('tei'+file_path[file_path.find(SLASH):],file_path)
	elif file_contents:
		with open(file_path,'w') as writefile:
			writefile.write(file_contents)


def traverseFullTree(processorFunction,linked_names):
	rootdir = 'tei'
	results_folder, results_folder_name = makeOutputFolder('json',None)

	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if '.xml' in name:
				if 'dc.xml' in name:
					writeNewFile(results_folder_name+root[3:]+SLASH+name,copy=True)
				else:
					writeNewFile(results_folder_name+root[3:]+SLASH+name,copy=True)
					writeNewFile(results_folder_name+root[3:]+SLASH+name[:-3]+'json',file_contents=processorFunction(root+SLASH+name,linked_names))

def getNameData():
	linked_name_keys = []
	linked_names = []
	with open('KolbProustNameData.csv','rU') as readfile:
		headerReader = csv.reader(readfile)
		header = next(headerReader)
		name_reader = csv.DictReader(readfile,header,delimiter=',');
		for name in name_reader:
			linked_name_keys.append(name['KeyCode'])
			linked_names.append(name['FullName'])

	return [linked_name_keys, linked_names]

def main():
	linked_names = getNameData()
	traverseFullTree(processTEIFile,linked_names)

main()