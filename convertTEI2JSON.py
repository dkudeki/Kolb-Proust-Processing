import os, json, datetime
from shutil import copyfile
from lxml import etree

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

def readDate(target_date):
	if len(target_date) == 4:
		format = '%Y'
	elif target_date[6:] == '00' and target_date[4:6] == '00':
		format = '%Y0000'
	elif target_date[6:] == '00':
		format = '%Y%m00'
	else:
		format = '%Y%m%d'
	return datetime.datetime.strptime(target_date,format)

def generateCitation(bibl_root):
	new_citation = {}
	new_titles = bibl_root.xpath('.//title')
	for title in new_titles:
		new_types = title.xpath('./@type')
		new_levels = title.xpath('./@level')
		if ('es' in new_types or 're' in new_types) or 'a' in new_levels:
			new_citation['headline'] = title.xpath('./text()')[0]
			new_citation['@type'] = 'Text'
		else:
			new_citation['name'] = title.xpath('./text()')[0]
			new_citation['@type'] = 'CreativeWork'


	return new_citation

def processTEIFile(tei_file):
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
		pass
	else:
		#chronology
		output_card['@id'] = root.xpath('/TEI/@xml:id')[0]
		output_card['@type'] = 'Dataset'
		output_card['author'] = { '@type': 'Person', '@id': 'http://viaf.org/viaf/44300868'}
		output_card['inLanguage'] = 'fr'
		output_card['temporalCoverage'] = readDate(root.xpath('//head/date/@value')[0]).date().isoformat()
		
		output_card['mentions'] = map((lambda x: { '@type': 'CreativeWork', 'title': x }),root.xpath('//div1//p/title/text()') + root.xpath('//div1//note/title/text()'))
		if len(output_card['mentions']) == 1:
			output_card['mentions'] = output_card['mentions'][0]
		elif len(output_card['mentions']) == 0:
			del output_card['mentions']

#		print(tei_file,root.xpath('//div1//bibl'))
		output_card['citation'] = map(generateCitation,root.xpath('//div1//bibl'))
	#	if len(output_card['citation']) == 1:
	#		output_card['citation'] = output_card['citation'][0]
	#	elif len(output_card['citation']) == 0:
	#		del output_card['citation']


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


def traverseFullTree(processorFunction):
	rootdir = 'tei'
	results_folder, results_folder_name = makeOutputFolder('json',None)

	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if '.xml' in name:
				if 'dc.xml' in name:
					writeNewFile(results_folder_name+root[3:]+SLASH+name,copy=True)
				else:
					writeNewFile(results_folder_name+root[3:]+SLASH+name[:-3]+'json',file_contents=processorFunction(root+SLASH+name))

def main():
	traverseFullTree(processTEIFile)

main()