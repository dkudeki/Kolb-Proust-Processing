import os
from shutil import copyfile

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
	path_elements = file_path.split('/')
#	print(path_elements)

	built_path = path_elements[0] + '/'

	for index in range(1,len(path_elements)-1):
		if not os.path.exists(built_path + path_elements[index]):
			os.makedirs(built_path + path_elements[index])

		built_path += path_elements[index] + '/'

	if copy:
		copyfile('tei'+file_path[file_path.find('/'):],file_path)
	elif file_contents:
		with open(file_path,'w') as writefile:
			writefile.write(file_contents)


def traverseFullTree(processor):
	rootdir = 'tei'
	results_folder, results_folder_name = makeOutputFolder('json',None)

	for root, dirs, files in os.walk(rootdir):
		for name in files:
			if '.xml' in name:
				if 'dc.xml' in name:
					writeNewFile(results_folder_name+root[3:]+'/'+name,copy=True)
				else:
					writeNewFile(results_folder_name+root[3:]+'/'+name[:-3]+'.json',file_contents=processor(root+'/'+name))

traverseFullTree(None)