# -*- coding: utf-8 -*-
import os, json

if os.name == 'nt':
	SLASH = '\\'
else:
	SLASH = '/'

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

def buildNewOutput(output_directory):
	core_name = output_directory[output_directory.rfind('/')+1:]
	with open(output_directory + '/' + core_name + '.ttl.graph','w') as graph_write_file:
		graph_write_file.write('http://localhost:8890/DAV/')

	output_text = 'PREFIX schema: <http://http://schema.org/>\n\n'
	with open(output_directory + '/' + core_name + '.ttl','w') as write_file:
		write_file.write(output_text.encode('utf-8'))

	return output_directory + '/' + core_name + '.ttl'

def outputTurtleFile(write_file,turtle_strings):
	with open(write_file,'a') as output_file:
		for turtle_string in turtle_strings:
			print turtle_string
			output_file.write(turtle_string.encode('utf-8'))

def addCardsToTurtle(read_file):
	with open(read_file,'r') as data_file:
		card = json.load(data_file)
	print(card)
	end_text = ''
	output_text = '\n<' + card['@id'] + '>\n'
	output_text += '\ta\tschema:' + card['@type'] + ' ;\n'
	output_text += '\tschema:temporalCoverage\t' + card['temporalCoverage'] + '^^schema:Date ;\n'

	if 'dateCreated' in card:
		output_text += '\tschema:dateCreated\t' + card['dateCreated'] + '^^schema:Date ;\n'

	if type(card['name']) is list:
		output_text += '\tschema:name\t' + card['name'][0] + ' ;\n'
		output_text += '\tschema:name\t' + card['name'][1] + ' ;\n'
	else:
		output_text += '\tschema:name\t' + card['name'] + ' ;\n'
	output_text += '\tschema:author\t<' + card['author']['@id'] + '> ;\n'

	if 'mentions' in card:
		if type(card['mentions']) is list:
			for instance in card['mentions']:
				if '@id' in instance:
					output_text += '\tschema:mentions\t<' + instance['@id'] + '> ;\n'
				else:
					output_text += '\tschema:mentions\t[\n'
					output_text += '\t\ta\tschema:CreativeWork ;\n'
					output_text += '\t\tschema:name\t' + instance['name'] + ' ;\n'
					output_text += '\t] ;\n'
		else:
			if '@id' in card['mentions']:
				output_text += '\tschema:mentions\t<' + card['mentions']['@id'] + '> ;\n'
			else:
				output_text += '\tschema:mentions\t[\n'
				output_text += '\t\ta\tschema:CreativeWork ;\n'
				output_text += '\t\tschema:name\t' + card['mentions']['name'] + '\n'
				output_text += '\t] ;\n'

	if 'citation' in card:
		if type(card['citation']) is list:
			for citation in card['citation']:
				output_text += '\tschema:citation\t[\n'
				output_text += '\t\ta\tschema:CreativeWork ;\n'
				if 'additionalType' in citation:
					output_text += '\t\tschema:additionalType\t<' + citation['additionalType'] + '> ;\n'
				if 'datePublished' in citation:
					output_text += '\t\tschema:datePublished\t' + citation['datePublished'] + '^^schema:Date ;\n'
				if 'author' in citation:
					output_text += '\t\tschema:author\t<' + citation['author']['@id'] + '> ;\n'
				if 'editor' in citation:
					output_text += '\t\tschema:editor\t<' + citation['editor']['@id'] + '> ;\n'
				if 'name' in citation:
					output_text += '\t\tschema:name\t' + citation['name'] + ' ;\n'
				if 'headline' in citation:
					output_text += '\t\tschema:headline\t' + citation['headline'] + ' ;\n'
				if 'sameAs' in citation:
					output_text += '\t\tschema:sameAs\t<' + citation['sameAs'] + '> ;\n'
				if 'pageStart' in citation:
					output_text += '\t\tschema:pageStart\t' + citation['pageStart'] + ' ;\n'
				if 'pageEnd' in citation:
					output_text += '\t\tschema:pageEnd\t' + citation['pageEnd'] + ' ;\n'

				if 'isPartOf' in citation:
					output_text += '\t\tschema:isPartOf\t[\n'
					output_text += '\t\t\ta\t' + citation['isPartOf']['@type'] + ' ;\n'
					if 'dateCreated' in citation['isPartOf']:
						output_text += '\t\t\tschema:dateCreated\t' + citation['isPartOf']['dateCreated'] + '^^schema:Date ;\n'
					if 'issueNumber' in citation['isPartOf']:
						output_text += '\t\t\tschema:issueNumber\t' + citation['isPartOf']['issueNumber'] + ' ;\n'
					if 'volumeNumber' in citation['isPartOf']:
						output_text += '\t\t\tschema:volumeNumber\t' + citation['isPartOf']['volumeNumber'] + ' ;\n'
					if 'name' in citation['isPartOf']:
						output_text += '\t\t\tschema:name\t' + citation['isPartOf']['name'] + ' ;\n'
					if 'pageStart' in citation['isPartOf']:
						output_text += '\t\t\tschema:pageStart\t' + citation['isPartOf']['pageStart'] + ' ;\n'
					if 'pageEnd' in citation['isPartOf']:
						output_text += '\t\t\tschema:pageEnd\t' + citation['isPartOf']['pageEnd'] + ' ;\n'

					if 'isPartOf' in citation['isPartOf']:
						output_text += '\t\t\tschema:isPartOf\t[\n'
						output_text += '\t\t\t\ta\t' + citation['isPartOf']['isPartOf']['@type'] + ' ;\n'
						if 'name' in citation['isPartOf']['isPartOf']:
							output_text += '\t\t\t\tschema:name\t' + citation['isPartOf']['isPartOf']['name'] + ' ;\n'
						if 'volumeNumber' in citation['isPartOf']['isPartOf']:
							output_text += '\t\t\t\tschema:volumeNumber\t' + citation['isPartOf']['isPartOf']['volumeNumber'] + ' ;\n'
						output_text += '\t\t\t] ;\n'
					output_text += '\t\t] ;\n'

				output_text += '\t] ;\n'
				print citation

	return output_text

def traverseFullTree():
	rootdir = 'tei'
	results_folder, results_folder_name = makeOutputFolder('ttl',None)

	cards_converted = 1
	file_iterator = 1
	turle_strings = []
	specific_write_folder, specific_write_folder_name = makeOutputFolder(results_folder_name + '/' + str(file_iterator),None)

	write_file = buildNewOutput(specific_write_folder_name)
	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if '.json' in name:
				if cards_converted%1000 == 0:
					outputTurtleFile(write_file,turle_strings)
					file_iterator += 1
					turle_strings = []
					specific_write_folder, specific_write_folder_name = makeOutputFolder(results_folder_name + '/' + str(file_iterator),None)
					write_file = buildNewOutput(specific_write_folder_name)

				turle_strings.append(addCardsToTurtle(root+SLASH+name))

				cards_converted += 1

	outputTurtleFile(write_file,turle_strings)
#				writeNewFile(results_folder_name+root[3:]+SLASH+name[:-3]+'json',file_contents=processorFunction(root+SLASH+name,linked_names))

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