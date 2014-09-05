# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# sourceforge retriever
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

import sys
import os
import getopt
import csv
from sfproject import SfProject
from database import Database
import libxml2
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom

# define subroutines

def help():
	"displays help message"
	print ("""
usage: sfr [<option>] <input file> <database file> <relations file>

options:
 --help, -H    : display this help
 --version, -V : display release information
 --quiet, -Q   : no transformation messages
 --verbose, -v : be more precise and see more messages
 input file    : file with the projects to evaluate
 database file : file with the hashed lines of code
 relation file : file with the project relationss
""")

	return

def readCommandLineOptions():
	"read and evaluate command line options"
	try:
		# evaluate command line parameters starting with parameter 2
		fullCommandLineOptions = sys.argv[1:]
		opts, args = getopt.getopt(fullCommandLineOptions, "VHQv", ["help", "version", "quiet", "verbose"])

		# set default values
		projectFile = ""
		databaseFile = ""
		relationsFile = ""
		quiet = False
		verbose = False

		# print "options: ", opts
		# print "arguments: ", args

		for option,argument in opts:
			if option in ("-H", "--help"):
				help()
				return(1)
			elif option in ("-V", "--version"):
				print "dbx-0.1"
				return(1)
			elif option in ("-Q", "--quiet"):
				quiet = True
			elif option in ("-v", "--verbose"):
				verbose = True
			else:
				assert False, "dbx.py: unhandled option. Exiting. "
				return(1)

		if len(args) == 3:
			projectFile = args[0]
			databaseFile = args[1]
			relationsFile = args[2]
			if not (os.path.isfile(projectFile)):
				print ("dbx.py: given project file (%s) not found" % (projectFile))
				return(1)

			if not (os.path.isfile(databaseFile)):
				print ("dbx.py: given database file (%s) not found" % (databaseFile))
				return(1)
		else:
			print("dbx.py: expected three file names to proceed.")
			help()
			return(1)

	except getopt.GetoptError, err:
		# print error message
		print str(err)
		help()
		return(1)
	return((projectFile, databaseFile, relationsFile, quiet, verbose))

def readDatabase(databaseFile):
	# read database file
	doc = libxml2.parseFile(databaseFile)

	# - get root element
	root = doc.getRootElement()
      
	# - iterate child by child
	child = root.children		# entrylist/entry
	while child is not None:	# 
		subnode = child.children
		databaseEntry = Database()
		while subnode is not None:
			if subnode.type == "element":
				#print subnode.name, subnode.content
				if subnode.name == "name":
					databaseEntry.setName(subnode.content)
				if subnode.name == "id":
					databaseEntry.setId(subnode.content)
				if subnode.name == "hash":
					databaseEntry.setHash(subnode.content)
				if subnode.name == "filename":
					databaseEntry.setFilename(subnode.content)
				if subnode.name == "date":
					databaseEntry.setDate(subnode.content)
				if subnode.name == "linenumber":
					databaseEntry.setLineNumber(subnode.content)
				if subnode.name == "weight":
					databaseEntry.setWeighting(subnode.content)
				if subnode.name == "exclusion":
					databaseEntry.setExclusion(subnode.content)
			subnode = subnode.next
	    
		if databaseEntry.getId():
			databaseList.append(databaseEntry)
			print "Entry: %s, %s" % (databaseEntry.getName(), databaseEntry.getHash())
		child = child.next
	    
	# free memory
	doc.freeDoc()

	return databaseList

def writeRelations(relationList, relationFile):

	# create xml structure
	rootNode = Element('projectlist')

	# attach node by node
	for relationEntry in relationList:
		entryNode = SubElement(rootNode, 'project')

		nameNode = SubElement(entryNode, 'name')
		nameNode.text = relationEntry.getProjectName()

		idNode = SubElement(entryNode, 'id')
		idNode.text = relationEntry.getProjectId()

		releaseNode = SubElement(entryNode, 'release')
		releaseNode.text = ""

		sourceNode = SubElement(entryNode, 'source')
		sourceNode.text = ""
		
		startNode = SubElement(entryNode, 'start')
		startNode.text = relationEntry.getStartDate()

		endNode = SubElement(entryNode, 'end')
		endNode.text = relationEntry.getEndDate()

		dependencyList = relationEntry.getProjectDependencyList()
		for dependencyListItem in dependencyList:
			dependsonNode = SubElement(entryNode, 'dependson')
			dependsonNode.text = dependencyListItem

		weightingNode = SubElement(entryNode, 'weighting')
		weightingNode.text = ""

	roughString = ElementTree.tostring(rootNode, 'utf-8')
	reparsed = minidom.parseString(roughString)
	niceXML = reparsed.toprettyxml(indent="  ")

	# write xml to database file
	open(relationFile, 'wb').writelines(niceXML)
	return

# initiate program
# output welcome message
print """sourceforge and database evaluator (dbx)
(C) 2014 Frank Hofmann (Berlin, Germany) <frank.hofmann@efho.de>
Released under GNU Public License (GPL) \n"""
	
# read and evaluate start parameters
retVal = 0
retVal = readCommandLineOptions()
if retVal == 1:
	# returned with error code 1
	# sth went wrong with the command line options ...
	sys.exit(retVal)

# set command line parameters
projectFile, databaseFile, relationsFile, quiet, verbose = retVal

# define list data
projectList = []
databaseList = []
relationsList = []
hashList = {}

# read projectFile
with open(projectFile, 'rb') as csvfile:
	projectReader = csv.reader(csvfile, delimiter=',')
	for row in projectReader:
		projectEntry = SfProject(row[0], 0)
		projectEntry.setRemoteUrl(row[1])
		projectEntry.setLocalUrl(row[2])
		projectEntry.setRcs(row[3])
		projectList.append(projectEntry)
		print "added project %s" % (projectEntry.getProjectName())

# print status message
print "loaded %i projects" % (len(projectList))
print " "

# read database file
databaseList = readDatabase(databaseFile)

# print status message
print "loaded %i database entries" % (len(databaseList))

# analyze database entries
for databaseEntry in databaseList:
	currentHash = databaseEntry.getHash()
	if not currentHash in hashList:
		# add as a new entry
		hashList[currentHash] = [databaseEntry.getId()]
	else:
		# extend an existing entry
		hashList[currentHash].append(databaseEntry.getId())

print hashList

for hashListEntry in hashList:
	newRelation = []
	nameList = []
	# print hashListEntry
	currentIds = hashList[hashListEntry]
	for databaseEntry in databaseList:
		if databaseEntry.getId() in currentIds:
			currentName = databaseEntry.getName()
			# print databaseEntry.getId(), ": ", currentName
			if not currentName in nameList:
				nameList.append(currentName)
				newRelation.append(databaseEntry)
	
	if len(newRelation) > 1:	
		relationsList.append(newRelation)

outputList = []
for relationEntry in relationsList:
	
	# init output entry with dummy values
	outputEntry = SfProject("dummy", 123)

	entryNo = 1

	for objectEntry in relationEntry:
		if entryNo == 1:
			outputEntry.setProjectName(objectEntry.getName())
			outputEntry.setProjectId(objectEntry.getId())
			outputEntry.setStartDate(objectEntry.getDate())
			outputEntry.setEndDate(objectEntry.getDate())
			entryNo = 0
		else:
			outputEntry.addProjectDependencyEntry (objectEntry.getName())

	outputList.append(outputEntry)

	print "[-] relation:"
	for objectEntry in relationEntry:
		print "    %s (%s)" % (objectEntry.getName(), objectEntry.getDate())
	print " "

writeRelations(outputList, relationsFile)
