# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# Dependency classes
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

class Dependency:
	def __init__(self):
		"init a Dependency object"
		self.timePeriodStart = 0
		self.timePeriodEnd = 0
		self.url = ""
		self.version = ""
		self.depends = DependencyList()
		self.rdepends = DependencyList()
		return

	# set and get time range ----
	def setTimePeriodStart (self, value):
		self.timePeriodStart = value
		return

	def setTimePeriodEnd (self, value):
		self.timePeriodEnd = value
		return

	def getTimePeriodStart (self):
		return self.timePeriodStart

	def getTimePeriodEnd (self):
		return self.timePeriodEnd

	# set and get url ----
	def setUrl (self, value):
		self.url = value
		return

	def getUrl (self):
		return self.url

	# set and get version ----
	def setVersion (self, value):
		self.version = value
		return

	def getVersion (self):
		return self.version

	# set and change dependencies ----
	def addDependency (self, dependency):
		if not self.hasDependency (dependency):
			self.depends.addItem(dependency)
		return

	def removeDependency (self, dependency):
		if self.hasDependency (dependency):
			self.depends.removeItem (dependency)
		return

	def hasDependency (self, dependency):
		return self.depends.hasItem (dependency)

	def clearDependency (self):
		self.depends.clearItemList()

	def getDependencies (self):
		return self.depends.getItemList ()

	# set and change rdependencies ----
	def addRDependency (self, dependency):
		if not self.hasRDependency (dependency):
			self.rdepends.addItem(dependency)
		return

	def removeRDependency (self, dependency):
		if self.hasRDependency (dependency):
			self.rdepends.removeItem (dependency)
		return

	def hasRDependency (self, dependency):
		return self.rdepends.hasItem (dependency)

	def clearRDependency (self):
		self.rdepends.clearItemList()

	def getRDependencies (self):
		return self.rdepends.getItemList ()

class DependencyList:
	def __init__(self):
		self.itemList = []
		return

	def addItem (self, item):
		if not self.hasItem (item):
			self.itemList.append(item)
		return

	def removeItem (self, item):
		if self.hasItem (item):
			self.itemList.remove (item)
		return

	def hasItem (self, item):
		return item in self.itemList

	def clearItemList (self):
		self.itemList = []
		return

	def getItemList (self):
		return self.itemList
