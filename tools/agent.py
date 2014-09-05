# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# agent class
# parallel programming and execution
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

import threading
import time
import os
from datetime import date, timedelta
import shutil
import random
import Queue
from sfproject import SfProject
import hashlib
from database import Database

class Agent(threading.Thread):

	resultList = Queue.Queue()
	resultListLock = threading.Lock() 
	projectList = Queue.Queue()
	projectListLock = threading.Lock() 
	terminate = False

	def __init__ (self, threadId): #, project, startDate, endDate):
		threading.Thread.__init__(self)
		self.threadId = threadId
		#self.projectName = project["name"]
		#self.projectUrl = project["remoteUrl"]
		#self.projectLoc = project["localeUrl"]
		#self.projectRcs = project["rcs"]
		#self.startDate = startDate
		#self.endDate = endDate
		print "starting %i" % (self.threadId)
		
	def run(self):
		while True:
			if Agent.terminate:
				print "terminating %i" % (self.threadId)
				break

			if not Agent.projectList.empty():
				# fetch project from project list
				currentProject = Agent.projectList.get()
				projectName = currentProject.getProjectName()
				print "(%i) fetched project %s" % (self.threadId, projectName)

				# fetched from project list with success
				Agent.projectList.task_done()

				# do something
				# - retrieve project data from sourceforge
				currentProject = self.retrieveProjectData(currentProject)

				# - with updated location
				projectRcs = currentProject.getRcs()
				projectLoc = currentProject.getLocalUrl()

				projectStartDate = currentProject.getStartDate()
				projectEndDate = currentProject.getEndDate()
				print "range: %s to %s" % (projectStartDate.isoformat(), projectEndDate.isoformat())

				currentDate = projectStartDate
				while currentDate < projectEndDate:
					print projectName, currentDate

					# retrieve local evaluation results
					localResultList = self.evaluateProjectData (projectName, currentDate, projectRcs, projectLoc)

					for localResultListEntry in localResultList:
						resultListEntry = Database()
						resultListEntry.setName(projectName)
						resultListEntry.setId(currentProject.getProjectId())
						resultListEntry.setHash(localResultListEntry["fingerprint"])
						resultListEntry.setFilename(localResultListEntry["filename"])
						resultListEntry.setDate(currentDate)
						resultListEntry.setLineNumber(localResultListEntry["line"])
						resultListEntry.setWeighting(0)
						resultListEntry.setExclusion(0)
					
						#Agent.resultListLock.acquire()
						Agent.resultList.put(resultListEntry)
						print "(%i) stored result for %s" % (self.threadId, projectName)
						#Agent.resultListLock.release()

					currentDate += timedelta(hours=24)

				# clean up
				self.cleanup(projectLoc)
		return 

	def retrieveProjectData(self, projectData):
		# retrieve project code from sourceforge

		projectName = projectData.getProjectName()
		projectRcs = projectData.getRcs()

		# call:
		# rsync -av SCM.code.sf.net::p/PROJECTNAME/MOUNTPOINT[.git] .
		# rsync -av PROJECTNAME.cvs.sourceforge.net::cvsroot/PROJECTNAME/* .
		# rsync -av rsync://PROJECTNAME.cvs.sourceforge.net/cvsroot/PROJECTNAME/* .
		#
		rsyncOptions = "-avz"

		# cvs
		if projectRcs == "cvs":
			source = "rsync://" + projectName + ".cvs.sf.net/cvsroot/" + projectName + "/*"

		# svn
		if projectRcs == "svn":
			source = projectName + ".svn.sourceforge.net::svn/" + projectName + "/*"

		# define targets
		target = "/tmp/" + projectName
		call = "rsync " + rsyncOptions + " " + source + " " + target

		print "calling: " + call
		os.system(call)
		
		# update locale project target
		projectData.setLocalUrl(target)

		return projectData

	def cleanup(self, directory):
		if directory:
			# cleanup - remove temporary instance
			print ("removing " + directory)
			shutil.rmtree(directory)
		return

	def evaluateProjectData(self, currentProjectName, currentDate, currentProjectRcs, currentProjectLoc):

		# init empty resultList
		localResultList = []

		# set list of files
		temporaryFileList = []

		print "evaluating " + currentProjectName + " (" + currentDate.isoformat() + ") ..."
		tmpDir = "/tmp/" + currentProjectName + '-' + currentDate.isoformat()
		print ("creating: " + tmpDir)
		os.mkdir(tmpDir)
		# - create locale instance for the given date
		#   (extract from svn or cvs)
		# cvs:
		if currentProjectRcs == "cvs":
			command = 'cvs -d ' + currentProjectLoc + ' co -D "' + currentDate.isoformat() + '" -d ' + tmpDir + ' ' + currentProjectName

		# svn:
		if currentProjectRcs == "svn":
			command = "svn co -r {" + currentDate.isoformat() + "} " + "file:///" + currentProjectLoc + " " + tmpDir

		print ("calling: " + command)
		os.system(command)

		# create file list
		for root, subFolders, files in os.walk(tmpDir):
			for file in files:
				temporaryFileList.append(os.path.join(root,file))

		print temporaryFileList

		# - search by file
		for currentFile in temporaryFileList:

			# read currentFile
			content = open(currentFile).readlines()
			fullContent = "".join(content)

			# calculate fingerprint for that file
			fingerprint = hashlib.sha256(fullContent).hexdigest()

			# set result entry
			resultEntry = {
				"filename": currentFile,
				"line": 0,
				"fingerprint": fingerprint
			}

			# print result
			print resultEntry
			
			# save result
			localResultList.append(resultEntry)

			# calculate line-by-line fingerprint
			lineNo = 1
			for currentLine in content:
				fingerprint = hashlib.sha256(currentLine).hexdigest()
				
				# add result entry
				resultEntry = {
					"filename": currentFile,
					"line": lineNo,
					"fingerprint": fingerprint
				}

				lineNo += 1

				# print result
				print resultEntry
			
				# save result
				localResultList.append(resultEntry)

		# - remove temporary, locale instance
		print ("removing " + tmpDir)
		shutil.rmtree(tmpDir)

		return localResultList


