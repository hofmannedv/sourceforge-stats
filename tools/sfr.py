# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# sourceforge retriever
# 
# (C) 2014 Frank Hofmann, Berlin, Germany
# Released under GNU Public License (GPL)
# email frank.hofmann@efho.de
# -----------------------------------------------------------

from interpreter import Interpreter
import threading
import sys
import os
from agent import Agent
import getopt

# define subroutines

def help():
	"displays help message"
	print ("""
usage: sfr [<option>] <input file> <keywords file> <database file>

options:
 --help, -H    : display this help
 --version, -V : display release information
 --quiet, -Q   : no transformation messages
 --verbose, -v : be more precise and see more messages
 input file    : file with the projects to evaluate
 keywords file : file with the keywords to search for
 database file : file with the hashed lines of code
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
		keywordsFile = ""
		databaseFile = ""
		quiet = False
		verbose = False

		# print "options: ", opts
		# print "arguments: ", args

		for option,argument in opts:
			if option in ("-H", "--help"):
				help()
				return(1)
			elif option in ("-V", "--version"):
				print "sfr-0.1"
				return(1)
			elif option in ("-Q", "--quiet"):
				quiet = True
			elif option in ("-v", "--verbose"):
				verbose = True
			else:
				assert False, "sfr.py: unhandled option. Exiting. "
				return(1)

		if len(args) == 3:
			projectFile = args[0]
			keywordsFile = args[1]
			databaseFile = args[2]
			if not (os.path.isfile(projectFile)):
				print ("sfr.py: given project file (%s) not found" % (projectFile))
				return(1)

			if not (os.path.isfile(keywordsFile)):
				print ("sfr.py: given keywords file (%s) not found" % (keywordsFile))
				return(1)

			if not (os.path.isfile(databaseFile)):
				print ("sfr.py: given database file (%s) not found" % (databaseFile))
				return(1)
		else:
			print("sfr.py: expected three file names to proceed.")
			help()
			return(1)

	except getopt.GetoptError, err:
		# print error message
		print str(err)
		help()
		return(1)
	return((projectFile, keywordsFile, databaseFile, quiet, verbose))

# initiate program
# output welcome message
print """sourceforge retriever (sfr)
(C) 2014 Frank Hofmann (Berlin, Germany) <frank.hofmann@efho.de>
Released under GNU Public License (GPL) \n"""
	
# read and evaluate start parameters
retVal = 0
retVal = readCommandLineOptions()
if retVal == 1:
	# returned with error code 1
	# sth went wrong with the command line options ...
	sys.exit(retVal)
else:
	# set command line parameters
	projectFile, keywordsFile, databaseFile, quiet, verbose = retVal

# setup worker queue with 5 threads
parallelThreads = 5
activeThreads = [Agent(threadId) for threadId in range(parallelThreads)]
for thread in activeThreads:
	thread.setDaemon(True) 
	thread.start() 

# start command-line interpreter
Interpreter(projectFile, keywordsFile, databaseFile).cmdloop()
