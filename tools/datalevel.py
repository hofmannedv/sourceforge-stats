# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# datalevel class
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

# import numpy as np

class Datalevel:

	def __init__(self, year):
		"init a Datalevel object"
		self.initDatalevel(year)
		return

	def initDatalevel(self, year):
		self.year = year
		self.entries = []
		return
		
	def getYear(self):
		return self.year

	def getEntries(self):
		return self.entries

	def getNumberOfEntries(self):
		return len(self.entries)
		
	def hasEntry(self, entry):
		return entry in self.entries
		
	def addEntry(self, newEntry):
		if not self.hasEntry(newEntry):
		      self.entries.append(newEntry)

	def removeEntry(self, entry):
		if self.hasEntry(entry):
		      self.entries.remove(entry)
		      return True
		return False