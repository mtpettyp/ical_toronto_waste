#/usr/bin/env python

import csv, time, os, errno
from datetime import datetime, timedelta

#title           :iCalTOWaste.py
#description     :Create ical and gmail calendar files for city of toronto curbside garbage collection
#author          :eric partington
#date            :2016/07/27
#version         :0.1
#usage           :python iCalTOWaste.py
#notes           :
#python_version  :
#==============================================================================

#global variables
CALENDAR_OUTPUT_DIR = 'FinalCalendars/'
CSV_OUTPUT_DIR = 'CSVCalendars/'
ICS_OUTPUT_DIR = 'ICSCalendars/'

INPUT_DATE_FORMAT = '%m/%d/%y'
CSV_DATE_FORMAT = '%m-%d-%y'
ICS_DATE_FORMAT = '%Y%m%d'


CSV_OUT_PATH = CALENDAR_OUTPUT_DIR+CSV_OUTPUT_DIR
ICS_OUT_PATH = CALENDAR_OUTPUT_DIR+ICS_OUTPUT_DIR

CALENDAR_INPUT_NAME = 'Calendars.csv'
#dict for unqiue pickup days
PICKUP_DAYS = []

#==================================

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
		#print '#Path exists: '+path
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def make_sure_input_exists(file):
    try:
        os.path.exists(file)
		#print '#File exists: '+file
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

#output CSV File blanks with headers for the collection days of the week
#creates a blank file for each collection day in the master file (column 0)
def MakeFiles():
    print "# Creating template files for each pickup date in input file ##"
    global PICKUP_DAYS

    #check for output directory created
    make_sure_path_exists(CALENDAR_OUTPUT_DIR)
    make_sure_input_exists(CALENDAR_INPUT_NAME)
    print "#Input File and Output directories exist"
    #open the file
    input_file = open(CALENDAR_INPUT_NAME, 'rU')
    data = csv.reader(input_file,delimiter=',')

    #create the template header for the new calendar csv files
    subject = ["Subject"]
    startDate = ["Start Date"]
    allDay = ["All Day Event"]
    description = ["Description"]
    new_line = subject + startDate + allDay + description

    #grab only the unique pickup days from the first column
    for line in data:
    	#print line[0]
    	if line[0] not in PICKUP_DAYS:
    		PICKUP_DAYS.append(line[0])

    #iterate over the unique days to create the template files
    for day in PICKUP_DAYS:
        if day == 'Calendar':
        	#skip this item as its just the header line
        	print "skipping header"
        else:
            #write the template files by pickup day
			print '#Writing template file for '+CSV_OUT_PATH+day
			csv.writer(open((CSV_OUT_PATH+day +'.csv'), 'w')).writerow(new_line)
            #print day

			#file headers for ics files
			print '#Writing template file for '+ICS_OUT_PATH+day
			with open(ICS_OUT_PATH+day +'.ics', 'w') as f:
				f.write('BEGIN:VCALENDAR\n')
				f.write('VERSION:2.0\n')
				f.write('CALSCALE:GREGORIAN\n')
				f.write('METHOD:PUBLISH\n')
				f.write('X-WR-CALNAME:'+day+' Waste Pickup\n')
				f.write('X-WR-TIMEZONE:America/Toronto\n')
				f.write('X-WR-CALDESC:\n')

	input_file.close()

#Write Solid Waste Calendars to file to csv
def WriteCal():
	print "# Writing calendar files for each pickup date in input file ##"
	#read the Calendars.csv file as input
	input_file = open(CALENDAR_INPUT_NAME, 'rU')
	data = csv.reader(input_file)

	for line in data:
		#split the input file into elements
		[Calendar,WeekStarting,GreenBin,Garbage,Recycling,Yardwaste,ChristmasTree] = line

		if Calendar == "Calendar":
			print "#skipping header"
			#skip first line as that is header
			data.next()
		else:
			#date formate was changed in the files from 2012
			#2012 format
			#MondayNight,9/2/2012,M,0,M,0,0
			#2016 format
			#MondayNight,01-04-16,M,0,M,0,0

			#day = datetime.datetime.strptime(WeekStarting, '%m/%d/%Y')
			#%m - zero padded month
			#%d - zero padded day
			#%y - year without the century
			day = datetime.strptime(WeekStarting, INPUT_DATE_FORMAT)
			#calendars are provided starting with a weekStarting datetime
			#there is the letter in the dict below that maps the pickup day on the week of service
			#so for instance if the pickup date was thursday, tht would be marked with an R
			#so to get the actual pickup date of the week you would need to add the weekstarting and the day of the week to get the date

			dw = {"M": 7, "T":8, "W":9, "R":10, "F":11, "S":12}
			#mark the calendar appointment as allDay
			#may try to change this to 7am as that is when the city wants curbside garbage out by.
			allDay = ["True"]
			if ChristmasTree != "0":
			    subject = ["Christmas Tree/Garbage Day"]
			    description = ["Garbage and Green Bin waste, Christmas tree collection occurs Today. When placing your tree out for collection, please remove all decorations, tinsel, etc and do not place out in any type of bag"]
			    startDate = day + timedelta(dw[ChristmasTree] - day.weekday())
			    startDate = [datetime.strftime(startDate, CSV_DATE_FORMAT)]
			elif Recycling != "0":
			    subject = ["Recycling Day"]
			    description = ["Recycling and Green Bin - More information on what can be recycled click here: http://www.toronto.ca/garbage/bluebin.htm"]
			    startDate = day + timedelta(dw[Recycling] - day.weekday())
			    startDate = [datetime.strftime(startDate, CSV_DATE_FORMAT)]
			elif Garbage != "0" and ChristmasTree == "0":
			    subject = ["Garbage Day"]
			    description = ["Garbage, Yard and Green Bin - Basic sorting information here: http://app.toronto.ca/wes/winfo/search.do"]
			    startDate = day + timedelta(dw[Garbage] - day.weekday())
			    startDate = [datetime.strftime(startDate, CSV_DATE_FORMAT)]

			new_line = subject + startDate + allDay + description
			#append the contents to the file template created above
			csv.writer(open((CSV_OUT_PATH+Calendar +'.csv'), 'a')).writerow(new_line)
			#print Calendar
			#print new_line
	print "# Finished writing CSV calendars ##"
	input_file.close()

#writes the ics version of the calendar files for use with ical
def WriteIcs():
	print '# Starting writing .ics calendars ##'

	#read the Calendars.csv file as input
	input_file2 = open(CALENDAR_INPUT_NAME, 'rU')
	data2 = csv.reader(input_file2, delimiter=',')

	#print data2
	for line in data2:
		[Calendar,WeekStarting,GreenBin,Garbage,Recycling,Yardwaste,ChristmasTree] = line
		#print Calendar
		if Calendar == "Calendar":
			print "#skipping header"
			#print Calendar
			#skip first line as that is header
			data2.next()
		else:
			#print 'else '+line[0]
			day = datetime.strptime(WeekStarting, INPUT_DATE_FORMAT)
			#with open("meeting.ics", 'wb') as f:
			dw = {"M": 7, "T":8, "W":9, "R":10, "F":11, "S":12}
			#mark the calendar appointment as allDay
			#may try to change this to 7am as that is when the city wants curbside garbage out by.
			#allDay = ["True"]
			if ChristmasTree != "0":
				subject = "Christmas Tree/Garbage Day"
				description = "Garbage and Green Bin waste, Christmas tree collection occurs Today. When placing your tree out for collection, please remove all decorations, tinsel, etc and do not place out in any type of bag"
				url=""
				startDate = day + timedelta(dw[ChristmasTree] - day.weekday())
				startDate = datetime.strftime(startDate, ICS_DATE_FORMAT)
			elif Recycling != "0":
				subject = "Recycling Day"
				description = "Recycling and Green Bin"
				url="http://www.toronto.ca/garbage/bluebin.htm"
				startDate = day + timedelta(dw[Recycling] - day.weekday())
				startDate = datetime.strftime(startDate, ICS_DATE_FORMAT)
			elif Garbage != "0" and ChristmasTree == "0":
				subject = "Garbage Day"
				description = "Garbage, Yard and Green Bin"
				url = "http://app.toronto.ca/wes/winfo/search.do"
				startDate = day + timedelta(dw[Garbage] - day.weekday())
				startDate = datetime.strftime(startDate, ICS_DATE_FORMAT)

			#append the contents to the file template created above
			with open(ICS_OUT_PATH+Calendar +'.ics', 'a') as f:
			#csv.writer(open((ICS_OUT_PATH+Calendar +'.ics'), 'w')).writerow(calendar_line)
				f.write('BEGIN:VEVENT\n')
				f.write('URL;VALUE=URI:'+url+'\n')
				f.write('DTEND;VALUE=DATE:'+startDate+'\n')
				f.write('SUMMARY:'+subject+'\n')
				f.write('LOCATION:'+Calendar+' Waste Pickup\n')
				f.write('DTSTART;VALUE=DATE:'+startDate+'\n')
				f.write('DESCRIPTION:'+description+'\n')
				f.write('END:VEVENT\n')

			#print 'end '+Calendar

	#we need to close the ics files with the end tags, use the dict that we created at the beginning to do that
	#append one last line to each ics file to complete them
	for calendar_day in PICKUP_DAYS:
		print calendar_day
		#append each file based on the writing path with the ICS_FOOTERS
		with open(ICS_OUT_PATH+calendar_day +'.ics', 'a') as f:
			f.write('END:VCALENDAR')

	print '# Finished writing .ics calendars ##'
#main functions
MakeFiles()
WriteCal()
WriteIcs()