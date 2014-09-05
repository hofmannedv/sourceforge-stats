# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# dataentry class
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

# import numpy as np

class Dataentry:

	def __init__(self, projectId1, projectId2):
		"init an Entry object"
		self.projectId1 = projectId1
		self.projectId2 = projectId2
		self.setDependency()
		return
	
	def getEntry(self):
		return (self.projectId1, self.projectId2, self.dependency)
	
	def setDependency(self):
		self.dependency = True
		
	def unsetDependency(self):
		self.dependency = False

	def hasDependency(self):
		return self.dependency