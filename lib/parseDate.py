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
    try:
        if re.match("^[a-zA-Z]{3}_", file):
            tList = threeScore(file)
        elif re.match("^Screenshot from", file):
            tList = screenshotFrom(file)
        elif re.match("^signal-", file):
            tList = signal(file)

        dto    = datetime(tList[0], tList[1], tList[2], tList[3], tList[4])
        tstamp = time.mktime(dto.timetuple())
    except:
        logging.error(f"parseDate failure on {fName}. Leaving susDOS blank.")
        tstamp = ""

    return str(tstamp)

def threeScore(file):
    # Parses out the date if the filename is of the pattern where it starts with three letters
    # followed by an underscore.
    tList = []
    tList.append(int(file[4:8]))
    tList.append(int(file[8:10]))
    tList.append(int(file[10:12]))
    tList.append(int(file[13:15]))
    tList.append(int(file[15:17]))
    return tList

def screenshotFrom(file):
    # Parses out the date if the filename starts with "Screenshot from"
    sFile = file[16:-4]
    tList = re.split(r'\s|-', sFile)
    return tList

def signal(file):
    # Parses out the date if the file came from the Signal messaging app.
    sFile = file[7:22]
    tList = sFile.split('-')
    tList.append(tList[3][-2:])
    tList[3] = tList[3][:2]
    return tList

# MAIN (Except not really)
if __name__ == "__main__":
    print("This is a library of functions for parsing out susDoS values. It is not meant to be " /
          "run directly.")