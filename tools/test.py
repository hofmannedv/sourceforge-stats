# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# read analyzed data, and stores them in 3d matrics
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

# ---- required modules ----
import datetime
import time
import libxml2
import sys

from dependency import DependencyList
from dependency import Dependency
from sfproject import SfProject

from datacube import Datacube
from datalevel import Datalevel
from dataentry import Dataentry

# ---- subroutines ----

def fromSfProjectToProjectId(sfprojectList, queryName):
	"return the project id for the requested project"
	for sfproject in sfprojectList:
		if sfproject.hasProjectName(queryName):
			# we got a project name ... 
			# ... so return the according project #id
			return sfproject.getProjectId()

	# we did not succeed -- return 0, instead
	return 0

def dateFromTextToInt(datum):
	"converts a date string into an time value"
	# split the date string into single pieces
	year,month,day = datum.split("-")

	# calculate the according time tuple
	return datetime.datetime(int(year),int(month),int(day))

def getProjectData(dataFile):
	"return the project data"

	# -- test data
	#projectData = [
	#["python", 1, "1.6", "http://test.de", [1996, 1997], ["libc"]],
	#["python", 1, "1.7", "http://test.de", [1998, 1999], ["libc", "xslt"]],
	#["python", 1, "1.8", "http://test.de", [1999, 2000], ["xslt"]],
	#["perl", 2, "3.5", "http://data.de", [1997, 2000], ["libc"]],
	#["perl", 2, "3.6", "http://data.de", [2001, 2004], ["libc", "xslt"]],
	#["libc", 3, "1.4.5", "http://irgend.was", [1995, 1997], []],
	#["xslt", 4, "4.2", "http://da.ta", [1996, 1999], []],
	#["x11", 5, "11.4", "http://x.org", [1999, 2002], ["libc","xslt","perl"]],
	#["libssl", 6, "4.1", "http://da.ta", [1998, 2004], ["libc","python"]],
	#["libssl", 6, "4.2", "http://da.ta", [2005, 2006], ["libc","python", "perl"]],
	#["libssl", 6, "4.7", "http://da.ta", [2007, 2008], ["python", "perl"]],
	#["libxml-libxslt-perl", 7, "4.0", "http://da.ta", [2001, 2003], ["perl"]],
	#["libxml-libxslt-perl", 7, "4.1", "http://da.ta", [2004, 2008], ["perl", "xslt"]],
	#["python-libxslt1", 8, "3.2", "http://da.ta", [1998, 2004], ["python", "xslt"]],
	#["xsltproc", 9, "4.0", "http://xslt.proc", [1999, 2000], ["libc", "libxml-libxslt-perl"]]
	#]
      
	# start with an empty project list
	 projectData = []

	# load project sources as xml data
	doc = libxml2.parseFile(dataFile)
	
	# get root element
	root = doc.getRootElement()

	# iterate child by child
	child = root.children		# projectlist
	while child is not None:		# project
		subnode = child.children	# node value
		
		# assume: empty project entry
		# set default values
		projectEntry = []
		projectName = ""
		projectId = 0
		projectRelease = ""
		projectSource = ""

		# assume: empty dependency list
		dependencyList = []
		timerangeList = []

		# read all subnodes until we finished
		while subnode is not None:
			# evaluate element nodes, only
			if subnode.type == "element":
				#print subnode.name, subnode.content
				if subnode.name == "name":
					projectName = subnode.content
				if subnode.name == "id":
					projectId = int(subnode.content)
				if subnode.name == "release":
					projectRelease = subnode.content
				if subnode.name == "source":
					projectSource = subnode.content
				if subnode.name == "start":
					timerangeList = [dateFromTextToInt(subnode.content)] + timerangeList
				if subnode.name == "end":
					timerangeList = timerangeList + [dateFromTextToInt(subnode.content)]
				if subnode.name == "dependson":
					dependencyList.append(subnode.content)
			subnode = subnode.next
		
		# in case we have a valid project id, create a new project entry
		if projectId:
			projectEntry = [projectName,projectId,projectRelease,projectSource,timerangeList,dependencyList]
			projectData.append(projectEntry)
	    
		# continue with the next xml node
		child = child.next
		
	# free memory
	doc.freeDoc()

	#print projectData
	return projectData
      
# ---- main program ----
# evaluate command line parameters starting with parameter 2
fullCommandLineOptions = sys.argv[1:]
if fullCommandLineOptions == []:
	print "parameter missing: xml data input file"
	sys.exit(1)

# extract data file
dataFile = fullCommandLineOptions[0]

# retrieve data
projectData = getProjectData(dataFile)

# initiate time measurement
testStart1 = time.clock()

# start with an empty project list
projectList = []
for projectEntry in projectData:

	# extract project information from the project data list
	projectName, projectId, projectVersion, projectUrl, projectTimePeriod, projectDependencies = projectEntry

	# check the project list for a project with a similar id
	# assume that we did not find it, yet
	found = False
	for sfproject in projectList:
		if projectId == sfproject.getProjectId():
			found = True
			break

	if not found:
		# create a new project list entry
		sfproject = SfProject(projectName, projectId)

	# set up dependency object	
	dependency = Dependency()
	dependency.setTimePeriodStart(projectTimePeriod[0])
	dependency.setTimePeriodEnd(projectTimePeriod[1])
	dependency.setVersion(projectVersion)
	dependency.setUrl(projectUrl)
	for dep in projectDependencies:
		dependency.addDependency(dep)
	
	sfproject.addProjectDependencyEntry(dependency)
	if not found:
		projectList.append(sfproject)

testEnde1 = time.clock()		
		
#print "number of projects: ", len(projectList)
#for sfproject in projectList:
	#print "--"
	#print "name:    ", sfproject.getProjectName()
	#print "id:      ", sfproject.getProjectId()
	#pdl = sfproject.getProjectDependencyList()
	#for listItem in pdl:
		#print "deps:    ", listItem.getTimePeriodStart(), "-", listItem.getTimePeriodEnd(), ": ", listItem.getDependencies()
		#print "url:     ", listItem.getUrl()
		#print "version: ", listItem.getVersion()

#print "duration %1.8f seconds" % (testEnde1 - testStart1)

testStart2 = time.clock()
# create datacube
dataCube = Datacube()
# start with an empty list of data levels
dataLevelList = []
for sfproject in projectList:
	pdl = sfproject.getProjectDependencyList()
	for listItem in pdl:
		timePeriodStart = listItem.getTimePeriodStart()
		timePeriodEnd = listItem.getTimePeriodEnd()
		
		# verify datalevel existance
		# if not available -- create according data level entry
		currentTime = timePeriodStart
		while currentTime <= timePeriodEnd:
			dataLevelList.append(currentTime)
			currentTime = currentTime + datetime.timedelta(days=1)
	      
#print timePeriodStart
#print timePeriodEnd
#print dataLevelList

# fill the datacube with the according levels
for timeValue in dataLevelList:
	dataLevel = Datalevel(timeValue)
	dataCube.addLevel(dataLevel)

# take the list of projects and its dependencies, and store it in the cube
for sfproject in projectList:
	id1 = sfproject.getProjectId()
	pdl = sfproject.getProjectDependencyList()
	#sfprojectName = sfproject.getProjectName()
	for listItem in pdl:
	      timePeriodStart = listItem.getTimePeriodStart()
	      timePeriodEnd = listItem.getTimePeriodEnd()
	      deps = listItem.getDependencies()
	      for depsEntry in deps:
			#print depsEntry	
			for dependingProject in projectList:
			      if dependingProject.hasProjectName(depsEntry):
				    id2 = dependingProject.getProjectId()
				    dataEntry = Dataentry(id1, id2)
				    dataLevelList = dataCube.getLevels()
				    for dataLevel in dataLevelList:
						if dataLevel.getYear >= timePeriodStart:
							if dataLevel.getYear <= timePeriodEnd:
								dataLevel.addEntry(dataEntry)
				    dataCube.setLevels(dataLevelList)

testEnde2 = time.clock()
print "duration %1.8f seconds" % (testEnde2 - testStart2)

print "Levels: ", dataCube.getNumberOfLevels()

for dataLevel in dataCube.getLevels():
	numberOfEntries = dataLevel.getNumberOfEntries()
	dataEntries = dataLevel.getEntries()
	print "year:", dataLevel.getYear()
	print "cont:", numberOfEntries
	for dataEntry in dataEntries:
	    print dataEntry.getEntry()
	print "-----"

# define query data		
queryData = [
	["python", "perl", "1997-01-01"],
	["libc", "a2kmp", "2005-12-12"],
	["libc", "x11", "1995-01-01"]
]

testStart3 = time.clock()

# send query
for query in queryData:
	queryFrom, queryTo, queryDate = query
	queryDate = dateFromTextToInt(queryDate)

	projectIdFrom = fromSfProjectToProjectId(projectList, queryFrom)
	projectIdTo = fromSfProjectToProjectId(projectList, queryTo)
	print "analyzing", queryFrom, "(", projectIdFrom, ") ->", queryTo, "(", projectIdTo, ") :", queryDate
	if dataCube.isDependency(projectIdFrom, projectIdTo, queryDate):
	      print "-> match!"

# print output
testEnde3 = time.clock()
print "duration %1.8f seconds" % (testEnde3 - testStart3)
