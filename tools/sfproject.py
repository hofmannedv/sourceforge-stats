# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# sfProject class
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

from datetime import date

class SfProject:
	def __init__(self, projectName, projectId):
		"init a SfProject object"
		self.setProjectName (projectName)
		self.setProjectId (projectId)
		self.initProjectDependencyList()
		self.remoteUrl = ""
		self.localUrl = ""
		self.rcs = ""
		self.startDate = date(1995,1,1)
		self.endDate = date.today()
		self.weighting = ""
		return

	def setProjectName (self, projectName):
		"set project name"
		self.projectName = projectName
		return

	def getProjectName (self):
		"get project name"
		return self.projectName

	def hasProjectName (self, projectName):
		"if project name is similar to the requested one"
		return self.projectName == projectName
		
	def setProjectId (self, projectId):
		"set project id"
		self.projectId = projectId
		return

	def hasProjectId (self, projectId):
		"if project id is similar to the requested one"
		return self.projectId == projectId

	def getProjectId (self):
		"get project id"
		return self.projectId

	def getProjectDependencyList (self):
		"give back the list of project dependencies"
		return self.projectDependencyList

	def addProjectDependencyEntry (self, entry):
		"add a new project dependency"
		self.projectDependencyList.append(entry)
		return

	def countProjectDependencyEntries (self):
		"count the list of project dependencies"
		return len(self.projectDependencyList)

	def removeProjectDependencyEntry (self, entry):
		"remove the given entry from the list"
		self.projectDependencyList.remove(entry)
		return

	def initProjectDependencyList (self):
		"initiate the dependency list"
		self.projectDependencyList = []
		return

	def setRemoteUrl (self, remoteUrl):
		"set the remote project url"
		self.remoteUrl = remoteUrl
		return

	def getRemoteUrl (self):
		"give back the remote project url"
		return self.remoteUrl

	def setLocalUrl (self, localUrl):
		"set the local project url"
		self.localUrl = localUrl
		return

	def getLocalUrl (self):
		"give back the local project url"
		return self.localUrl

	def setRcs (self, rcs):
		"save the projects revision control system"
		self.rcs = rcs
		return

	def getRcs (self):
		"give back the projects revision control system"
		return self.rcs

	def setStartDate (self, startDate):
		"set the projects start date"
		self.startDate = startDate
		return

	def getStartDate (self):
		"list the projects start date"
		return self.startDate

	def setEndDate (self, endDate):
		"set the projects end date"
		self.endDate = endDate
		return

	def getEndDate (self):
		"list the projects end date"
		return self.endDate
