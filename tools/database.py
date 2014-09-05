# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# xml database class
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

import libxml2

# xml database class
class Database (object):
	"database class for xml storage"

	def __init__(self):
		self.name = ""
		self.id = 0
		self.hash = ""
		self.filename = ""
		self.date = ""
		self.linenumber = -1
		self.weighting = 0
		self.exclusion = False
		return

	def getName(self):
		"return the unix project name"
		return self.name

	def setName(self, unixname):
		"set the unix project name"
		self.name = unixname
		return

	def getId(self):
		"return the data entry id"
		return self.id

	def setId(self, value):
		"set the data entry id"
		self.id = value
		return

	def getHash(self):
		"return the data hash value"
		return self.hash

	def setHash(self, hashValue):
		"set the data hash value"
		self.hash = hashValue
		return

	def getLineNumber(self):
		"return the line number"
		return self.linenumber

	def setLineNumber(self, value):
		"set the line number"
		self.linenumber = value
		return

	def getFilename(self):
		"return the file name"
		return self.filename

	def setFilename(self, filename):
		"set the file name"
		self.filename = filename
		return

	def getDate(self):
		"return the date value"
		return self.date

	def setDate(self, value):
		"set the date value"
		self.date = value
		return

	def getWeighting(self):
		"return the entry weighting"
		return self.weighting

	def setWeighting(self, value):
		"set the weighting"
		self.weighting = value
		return

	def getExclusion(self):
		"return the exclusion information"
		return self.exclusion

	def setExclusion(self, value):
		"set the exclusion value"
		self.exclusion = value
		return
