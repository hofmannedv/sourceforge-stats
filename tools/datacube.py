# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# datacube class
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

class Datacube:

	def __init__(self):
		"init a Datacube object"
		self.initLevels()
		return

	def initLevels(self):
		"init Datacube level list"
		self.levels = []
		return
		
	def getNumberOfLevels(self):
		"count the number of levels"
		return len(self.levels)

	def getLevels(self):
		"return the list of levels"
		return self.levels

	def setLevels(self, newLevels):
		"substitute the current list of levels by a new one"
		self.levels = newLevels
		return
		
	def hasLevel(self, level):
		"does the requested level exist?"
		return level in self.levels
		
	def addLevel(self, newLevel):
		"add a new level to the list"
		if not self.hasLevel(newLevel):
		      self.levels.append(newLevel)

	def removeLevel(self, level):
		"remove the given level of the list"
		if self.hasLevel(level):
		      self.levels.remove(level)
		      return True
		return False
		
	def isDependency(self, projectId1, projectId2, queryYear):
		"verify a project dependency in the given year"
		for dataLevel in self.levels:
		      year = dataLevel.getYear()
		      if year == queryYear:
			    listOfEntries = dataLevel.getEntries()
			    for entry in listOfEntries:
				  value = entry.getEntry()
				  if value == (projectId1, projectId2, True):
					  return True
		return False
