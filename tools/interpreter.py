# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# command line interpreter class
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

import sys
import cmd
import csv
import time
from datetime import date
from agent import Agent
from database import Database
import libxml2
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom
from sfproject import SfProject

# interpreter class
class Interpreter (cmd.Cmd):
	"command line interpreter class"

	def __init__(self, projectFile, keywordsFile, databaseFile):
		cmd.Cmd.__init__(self)
		# define command-line prompt
		self.prompt = 'sfr > '

		# define list data
		self.projectList = []
		self.keywordsList = []
		self.databaseList = []
		self.projectFile = projectFile
		self.keywordsFile = keywordsFile
		self.databaseFile = databaseFile

		# define search period
		self.startDate = date(1995,1,1)
		self.endDate = date.fromtimestamp(time.time())
		print "setting search range from %s to %s" % (self.startDate.isoformat(), self.endDate.isoformat())
		print " "

		# read projectFile
		with open(projectFile, 'rb') as csvfile:
			projectReader = csv.reader(csvfile, delimiter=',')
			for row in projectReader:
				projectEntry = SfProject(row[0], 0)
				projectEntry.setRemoteUrl(row[1])
				projectEntry.setLocalUrl(row[2])
				projectEntry.setRcs(row[3])
				self.projectList.append(projectEntry)
				print "added project %s" % (projectEntry.getProjectName())

		# print status message
		print "loaded %i projects" % (len(self.projectList))
		print " "

		# read keywords
		self.keywordsList = open(keywordsFile).readlines()

		# print status message
		for keyword in self.keywordsList:
			print "added keyword %s " % (keyword)
		print "loaded %i keywords" % (len(self.keywordsList))
		print " "

		# read database file
		self.readDatabase()

		# print status message
		print "loaded %i database entries" % (len(self.databaseList))

	#def preloop(self):
	#	print "(we are in the preloop function)" # this will be called before terminal.cmdloop() begins
	
	#def postloop(self):
	#	print "(we are in the postloop function)" # this will be called when terminal.cmdloop() exits
	
	def do_quit(self, line):
		"quit sfr"
		
		self.do_exit(line)

		# return True to terminate
		return True
	
	def do_exit(self, line):
		"quit sfr"
		
		# terminate agents
		Agent.terminate = True

		# clear queues
		# - projectList queue
		while not Agent.projectList.empty():
			p = Agent.projectList.get()
			print "(c) removing project entry %s " % (p.getProjectName())
			Agent.projectList.task_done()

		# - resultList queue
		while not Agent.resultList.empty():
			currentResultEntry = Agent.resultList.get()
			print "(c) removing result entry %s " % (currentResultEntry.getName())

			# update database
			self.updateDatabase(currentResultEntry)

			Agent.resultList.task_done()

		# concatenate threads
		Agent.projectList.join()
		Agent.resultList.join()

		# save database
		self.writeDatabase()

		# return True to terminate
		return True

	def do_addproject(self, line):
		"add the project to the list of projects"
		if line:
			elements = line.split()
			projectName, projectRemoteUrl, projectLocalUrl, projectRcs = "", "", "", ""
			
			projectName = elements[0]
			if len(elements) > 1:
				projectRemoteUrl = elements[1]
			if len(elements) > 2:
				projectLocalUrl = elements[2]
			if len(elements) > 3:
				projectRcs = elements[3]
			
			projectEntry = SfProject(projectName, 0)
			projectEntry.setRemoteUrl(projectRemoteUrl)
			projectEntry.setLocalUrl(projectLocalUrl)
			projectEntry.setRcs(projectRcs)
			self.projectList.append(projectEntry)
			
			print "added project %s (%s, %s, %s) to the list" % (projectName, projectRemoteUrl, projectLocalUrl, projectRcs)
		return 

	def do_removeproject(self, line):
		"remove the project to the list of projects"
		if line:
			for entry in self.projectList:
				projectName = entry.getProjectName()
				if line == projectName:
					self.projectList.remove(entry)
					print "removed project %s from the list" % (projectName)
					break
		return 

	def do_listprojects(self, line):
		"output the list of projects"
		for entry in self.projectList:
			projectName = entry.getProjectName()
			projectRemoteUrl = entry.getRemoteUrl()
			projectLocalUrl = entry.getLocalUrl()
			projectRcs = entry.getRcs()
			print "%s (%s, %s, %s)" % (projectName, projectRemoteUrl, projectLocalUrl, projectRcs)
		return 
	
	def do_projectexists(self, line):
		"if project is part of the project list"
		for entry in self.projectList:
			projectName = entry.getProjectName()
			projectRemoteUrl = entry.getRemoteUrl()
			projectLocalUrl = entry.getLocalUrl()
			projectRcs = entry.getRcs()
			if line == projectName:			
				print "%s (%s, %s, %s)" % (projectName, projectRemoteUrl, projectLocalUrl, projectRcs)
		return

	def do_countprojects(self, line):
		"count the number of projects"
		print "the project list contains %i project entries" % (len(self.projectList))
		return 

	def do_saveprojects(self, line):
		"save the project list"
		with open(self.projectFile, 'wb') as csvfile:
			projectWriter = csv.writer(csvfile, delimiter=',')
			for entry in self.projectList:
				projectWriter.writerow(entry.getProjectName(), entry.getRemoteUrl(), entry.getLocalUrl(), entry.getRcs())
		# print status message
		print "saved %i projects to %s" % (len(self.projectList), self.projectFile)
		print " "

		return

	def do_clearprojects(self, line):
		"clear the project list"
		self.projectList = []
		print "the project list was cleared, and is empty, now"
		return

	#def do_sortprojects(self, line):
	#	"sorts the project list in alphabetical order"
	#	self.projectList = sorted(self.projectList, key=lambda project: project["name"])
	#	print "projects are sorted"
	#	return

	def do_listkeywords(self, line):
		"output the list of keywords"
		for entry in self.keywordsList:
			print "%s " % (entry)
		return 

	def do_clearkeywords(self, line):
		"clear the keywords list"
		self.keywordsList = []
		print "the keywords list was cleared, and is empty, now"
		return

	def do_sortkeywords(self, line):
		"sorts the keyword list in alphabetical order"
		self.keywordsList = sorted(self.keywordsList)
		print "keywords are sorted"
		return

	def do_countkeywords(self, line):
		"count the number of keywords"
		print "the keyword list contains %i keyword entries" % (len(self.keywordsList))
		return 

	def do_savekeywords(self, line):
		"save the keywords list"
		
		open(self.keywordsFile, 'wb').writelines(self.keywordsList)
		# print status message
		print "saved %i keywords to %s" % (len(self.keywordsList), self.keywordsFile)
		print " "

		return

	def do_addkeyword(self, line):
		"add keyword to the keywords list"
		if not line:
			print "keyword missing"
		else:
			self.keywordsList.append(line)
			print "%s added to keyword list" % (line)
		return

	def do_removekeyword(self, line):
		"remove the given keyword from the keywords list"
		if not line:
			print "keyword missing"
		else:
			if line in self.keywordsList:
				self.keywordsList.remove(line)
			else:
				print "keyword %s not in keyword list" % (line)
		return

	def do_keywordexists(self, line):
		"looks if keyword is in keyword list"
		if line in self.keywordsList:
			print "%s found in keywords list" % (line)
		else:
			print "%s not found in keywords list" % (line)
		return

	def do_displaysearchperiod(self, line):
		"show the search period"
		print "start date: %s" % (self.startDate.isoformat())
		print "end date: %s" % (self.endDate.isoformat())
		return

	def do_setstartdate(self, line):
		"set a new start date"
		if line:
			year, month, day = line.split()
			self.startDate = date(int(year),int(month),int(day))
			print "start date set to %s" % (self.startDate.isoformat())
		else:
			print "no valid date given"
		return

	def do_setenddate(self, line):
		"set a new end date"
		if line:
			year, month, day = line.split()
			self.endDate = date(int(year),int(month),int(day))
			print "end date set to %s" % (self.endDate.isoformat())
		else:
			print "no valid date given"
		return

	def do_getqueue(self, line):
		while not Agent.resultList.empty():
			result = Agent.resultList.get()
			Agent.resultList.task_done()
			print result.getProjectName()
		return

	def do_evaluateproject(self, line):
		"evaluate the named project"
		if not line:
			print "no project specified"
		else:

			desiredProjects = line.split()
			print line
			for projectName in desiredProjects:
				for projectEntry in self.projectList:
					if projectName == projectEntry.getProjectName():
						# project found in list
						# add time range -- start, and end date
						projectEntry.setStartDate(self.startDate)
						projectEntry.setEndDate(self.endDate)
						print "added project %s" % (projectName)
						Agent.projectList.put(projectEntry)

		return

	def readDatabase(self):
		# read database file
		doc = libxml2.parseFile(self.databaseFile)

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
				self.databaseList.append(databaseEntry)
				print "Entry: %s, %s" % (databaseEntry.getName(), databaseEntry.getHash())
			child = child.next
	    
		# free memory
		doc.freeDoc()

		return

	def writeDatabase(self):

		# create xml structure
		rootNode = Element('entrylist')

		# attach node by node
		for databaseEntry in self.databaseList:
			entryNode = SubElement(rootNode, 'entry')

			nameNode = SubElement(entryNode, 'name')
			nameNode.text = databaseEntry.getName()

			idNode = SubElement(entryNode, 'id')
			idNode.text = databaseEntry.getId()

			dateNode = SubElement(entryNode, 'date')
			dateNode.text = databaseEntry.getDate()

			hashNode = SubElement(entryNode, 'hash')
			hashNode.text = databaseEntry.getHash()

			filenameNode = SubElement(entryNode, 'filename')
			filenameNode.text = databaseEntry.getFilename()

			linenumberNode = SubElement(entryNode, 'linenumber')
			linenumberNode.text = databaseEntry.getLineNumber()

			weightNode = SubElement(entryNode, 'weight')
			weightNode.text = databaseEntry.getWeighting()

			exclusionNode = SubElement(entryNode, 'exclusion')
			exclusionNode.text = databaseEntry.getExclusion()

		roughString = ElementTree.tostring(rootNode, 'utf-8')
		reparsed = minidom.parseString(roughString)
		niceXML = reparsed.toprettyxml(indent="  ")

		# write xml to database file
		open(self.databaseFile, 'wb').writelines(niceXML)
		return

	def updateDatabase(self, resultEntry):

		# adjust data format
		currentDate = resultEntry.getDate().isoformat()
		resultEntry.setDate(currentDate)

		# adjust id
		# currentId = resultEntry.getId()
		currentId = len(self.databaseList) + 1
		resultEntry.setId(str(currentId))

		# adjust line number
		currentLinenumber = resultEntry.getLineNumber()
		resultEntry.setLineNumber(str(currentLinenumber))

		# adjust weight value
		currentWeight = resultEntry.getWeighting()
		resultEntry.setWeighting(str(currentWeight))

		# adjust exclusion value
		currentExclusion = resultEntry.getExclusion()
		resultEntry.setExclusion(str(currentExclusion))

		if not resultEntry in self.databaseList:
			# add new entry
			self.databaseList.append(resultEntry)
			#print "Entry: %s, %s" % (resultEntry.getName(), resultEntry.getHash())

		return
