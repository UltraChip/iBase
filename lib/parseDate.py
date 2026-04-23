#!/bin/python3

## IBASE DATE PARSER LIBRARY
##
## Functions used to aid in parsing out date and time information from filenames. Mainly used to 
## calculate "Suspected Day of Shot" (susDoS) values. 


# IMPORTS AND CONSTANTS
import re
import os
import time
import logging
from datetime import datetime


# FUNCTIONS
def parseDate(fName):
    # Main function - takes in a filename, does preliminary analysis to determine if it's using a 
    # recognizable pattern, then farms the name out to a helper function for parsing. Note that 
    # tList is a list of time elements consisting of 4-char Year, 2-char Month, 2-char Day, 2-char
    # hour, and 2-char minute IN THAT ORDER.
    file = os.path.basename(fName)

    if re.match("^[a-zA-Z]{3}_", file) and len(file) > 20 and file[4].isdigit():
        tList = threeScore(file)
    elif re.match("^Screenshot from", file):
        tList = screenshotFrom(file)
    elif re.match("^signal-", file):
        tList = signal(file)
    elif re.match("^Screenshot_", file) and len(file) > 28:
        tList = screenshotScore(file)
    else:
        return ""

    try:
        iList  = [int(t) for t in tList]
        dto    = datetime(iList[0], iList[1], iList[2], iList[3], iList[4])
        tstamp = time.mktime(dto.timetuple())
    except Exception as e:
        #logging.info(f"parseDate failure on {fName}. Leaving susDOS blank.")
        tstamp = ""

    return str(tstamp)

def threeScore(file):
    # Parses out the date if the filename is of the pattern where it starts with three letters
    # followed by an underscore.
    tList = []
    tList.append(file[4:8])
    tList.append(file[8:10])
    tList.append(file[10:12])
    tList.append(file[13:15])
    tList.append(file[15:17])
    return tList

def screenshotFrom(file):
    # Parses out the date if the filename starts with "Screenshot from"
    sFile = file[16:-4]
    tList = re.split(r'\s|-', sFile)
    return tList

def screenshotScore(file):
    # Parses out the date if the filename starts with "Screenshot_"
    tList = []
    sFile = file[11:-6]
    if sFile[4] == "-":
        tList = sFile.split("-")[:5]
    else:
        tList.append(sFile[0:4])
        tList.append(sFile[4:6])
        tList.append(sFile[6:8])
        tList.append(sFile[9:11])
        tList.append(sFile[11:13])
    return tList

def signal(file):
    # Parses out the date if the file came from the Signal messaging app.
    sFile = file[7:22]
    tList = sFile.split('-')
    tList.append(tList[3][-2:])
    tList[3] = tList[3][:2]
    return tList

def highResScreenShot(file):
    # Parses out the date if the filename starts with "HighResScreenshot_"
    sFile = file[18:-4]
    t1 = sFile[:10].split('-')
    t2 = sFile[11:16].split('-')
    return t1 + t2

# MAIN (Except not really)
if __name__ == "__main__":
    print("This is a library of functions for parsing out susDoS values. It is not meant to be " /
          "run directly.")