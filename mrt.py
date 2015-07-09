# 	movie-recognize-tool
# 	The MIT License (MIT)
# 	Copyright (c) 2015 Marc Szymkowiak 'Ezak91' marc.szymkowiak91@googlemail.com
#
# 	Permission is hereby granted, free of charge, to any person obtaining a copy
# 	of this software and associated documentation files (the "Software"), to deal
# 	in the Software without restriction, including without limitation the rights
# 	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# 	copies of the Software, and to permit persons to whom the Software is
# 	furnished to do so, subject to the following conditions:
# 	The above copyright notice and this permission notice shall be included in all
# 	copies or substantial portions of the Software.
# 	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# 	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# 	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# 	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# 	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# 	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# 	SOFTWARE.

from urllib2 import Request, urlopen
from datetime import datetime
import ConfigParser
import json
import sys
import os
import re

def initial():
	global log
	global newline
	global archiveOutput
	global imdbID
	global apiKey
	global language
	global filenameFormat
	global movieTitle
	global releaseYear
	global fileName
	global startupPath
	global move
	global destinationPath
	startupPath = os.path.dirname(os.path.abspath(sys.argv[0]))
	newline = '\n'
	openlog()
	writelog("Start MRT")
	writelog("Scriptpath: " + startupPath)
	readConf()

def readConf():
	global apiKey
	global language
	global filenameFormat
	global startupPath
	global destinationPath
	global move
	writelog("Read mrt.conf")
	config = ConfigParser.RawConfigParser()
	config.read(startupPath+'/mrt.conf')
	apiKey = config.get('TMDB', 'key')
	language = config.get('TMDB', 'language')
	filenameFormat = config.get('MRT', 'format')
	move = config.get('MRT','move')
	destinationPath = config.get('MRT','destinationpath')


	writelog("Apikey: "+apiKey)
	writelog("Language: "+language)
	writelog("Format: "+filenameFormat)
	writelog("Move: "+move)
	writelog("Destinationpath: "+destinationPath)

def openlog():
	global log
	global startupPath
	log = open(startupPath+'/mrt.log','w')

def writelog( message ):
	global log
	print(message)
	log.write(message + '\n')	

def closelog():
	log.close()

def checkparam():
	global archiveOutput
	if (len(sys.argv) < 4):		
		writelog("Not enough arguments (download.id, download.name, download.file, archive.output)")
		return False
	else:
		writelog("Read arguments")
		downloadID = sys.argv[1]
		downloadName = sys.argv[2]
		archiveOutput = sys.argv[3]
		writelog("ID: " + downloadID + newline + "Name: " + downloadName + newline + "Outputdirectory: " + archiveOutput);
		return True

def findNFO():
	global archiveOutput
	if os.path.isdir(archiveOutput):
		fileExtensions = ['nfo']
		for root, dirs, files in os.walk(archiveOutput, topdown=False):
			for nfo in files:
				if nfo[-3:] in fileExtensions:
					writelog("Found NFO " + root + nfo)
					parseNFO(root+"/"+nfo)
					return True
	else:
		writelog("Directory " + archiveOutput + " doesn't exist")
		return False

def parseNFO(nfoFile):
	global imdbID
	nfoString = open(nfoFile, 'r').read()
	movieID = re.search('tt\d{5,7}',nfoString)
	if movieID is not None:
		imdbID = movieID.group(0)
		writelog("Found IMDB ID: " + imdbID)
		return True
	else:
		return False

def readTMDBData():
	global imdbID
	global language
	headers = { 'Accept': 'application/json'}
	requestUrl = 'http://api.themoviedb.org/3/find/'+imdbID+'?external_source=imdb_id&api_key='+apiKey+'&language='+language
	request = Request(requestUrl, headers=headers)
	writelog("Request-Url: "+requestUrl)
	response_body = urlopen(request).read()
	getMovietitle(response_body)

def getMovietitle(jsonData):
    data = json.loads(jsonData)
    global movieTitle
    global releaseYear
    movieTitle = data['movie_results'][0]['title']
    datestring = data['movie_results'][0]['release_date']
    dt = datetime.strptime(datestring, '%Y-%m-%d')
    releaseYear = dt.year

def findMovie():
	global fileName
	fileExtensions = ['mkv','avi','mp4','ts','mpg']
	for root, dirs, files in os.walk(archiveOutput, topdown=False):
		for movieFile in files:
			if movieFile[-3:] in fileExtensions and not "sample" in movieFile:
				writelog("Found movie " + root + "/" + movieFile)
				fileName = root+"/"+movieFile
				return True			
	writelog("No movie found in " + root)
	return False

def renameMovie():
	global fileName
	global movieTitle
	global filenameFormat
	global releaseYear
	global newFileName
	newFilename = filenameFormat.replace("%t",movieTitle.encode('utf-8'))
	newFilename = newFilename.replace("%y",str(releaseYear))
	name, fileExtension = os.path.splitext(fileName)
	newFileName = os.path.dirname(fileName) + "/" + newFilename + fileExtension
	os.renames(fileName, newFileName)
	if os.path.isfile(newFileName):
		writelog("Successful rename movie from "+fileName+" to "+newFileName)
		return True
	else:
		writelog("Failed to rename movie from "+fileName+" to "+newFileName)
		return False

def moveMovie():
	global move
	global destinationPath
	global newFileName
	if move == "True":
		destinationFile = destinationPath+"/"+os.path.basename(newFileName)
		print("newFilename: "+newFileName)
		print("destinationFile:"+destinationFile)
		os.rename(newFileName, destinationFile)
		writelog("Copy movie from "+newFileName+" to "+destinationFile)

def addToMuhvieh()
	

def main():
	initial()
	if checkparam():
		if findNFO():
			if findMovie():
				readTMDBData()
				renameMovie()
				moveMovie()
	writelog("End")
	closelog()

main()