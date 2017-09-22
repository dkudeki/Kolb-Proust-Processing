import os, json, csv

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

def getPersonIDsFromCSV():
	person_ids = []

	with open('KolbProustNameData.csv','rU') as readfile:
		headerReader = csv.reader(readfile)
		header = next(headerReader)
		name_reader = csv.DictReader(readfile,header,delimiter=',');
		for name in name_reader:
			person_ids.append(name['KeyCode'])

	return person_ids

def getPersonIDsFromCards():
	person_ids = []

	rootdir = 'tei'
	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if '.json' in name:
				with open(root+SLASH+name,'r') as data_file:
					card = json.load(data_file)

				if 'mentions' in card:
					if type(card['mentions']) is list:
						for mention in card['mentions']:
							if mention['@type'] == 'Person' and mention['@id'][64:] not in person_ids:
								person_ids.append(mention['@id'][64:])

	return sorted(person_ids)

def outputSpreadsheet(rows,person_ids):
	with open('coocurrences.csv','w') as outfile:
		writer = csv.writer(outfile)
		writer.writerow([''] + [unicode(s).encode('utf-8') for s in person_ids])

		for person in person_ids:
			writer.writerow([person] + [('' if p == 0 else p) for p in rows[person]])

def traverseFullTree():
	rootdir = 'tei'
	coocurrence_count = 0

#	person_ids = getPersonIDsFromCSV()
	person_ids = getPersonIDsFromCards()

	column_numbers = {}
	for index in range(0,len(person_ids)):
		column_numbers[person_ids[index]] = index

	rows = {}
	for person in person_ids:
		rows[person] = [0] * len(person_ids)

	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if '.json' in name:
				with open(root+SLASH+name,'r') as data_file:
					card = json.load(data_file)

				if 'mentions' in card:
					if type(card['mentions']) is list:
						for mention in card['mentions']:
							if mention['@type'] == 'Person':
								for other_mention in card['mentions']:
									if other_mention['@type'] == 'Person' and other_mention != mention:
										print(mention['@id'][64:], other_mention['@id'][64:])
										rows[mention['@id'][64:]][column_numbers[other_mention['@id'][64:]]] += 1
										coocurrence_count += 1

	print(person_ids)
	print(len(person_ids))
	outputSpreadsheet(rows,person_ids)
	print(coocurrence_count/2)

#On Windows, the Command Prompt doesn't know how to display unicode characters, causing it to halt when it encounters non-ASCII characters
def setupByOS():
	if os.name == 'nt':
		if sys.stdout.encoding != 'cp850':
		  sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'replace')
		if sys.stderr.encoding != 'cp850':
		  sys.stderr = codecs.getwriter('cp850')(sys.stderr, 'replace')

def main():
	setupByOS()
	traverseFullTree()

main()