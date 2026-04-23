#!/bin/python3

## IBASE DISPLAY ENGINE LIBRARY
##
## Various helper functions for generating TUI elements on the screen.


# IMPORTS AND CONSTANTS
import sqlite3
import datetime
import os
import random
import lib.sengine as sengine
from time import sleep
from tkinter import Image
from simple_term_menu import TerminalMenu
from PIL import Image
from math import floor


# FUNCTIONS
def mainmenu(db, conf, vers):
    # Main TUI menu.
    while True:
        os.system('clear')
        buildHeader(f"iBase version {vers}")
        options = [ "Direct IMID lookup",
                    "Search by keyword",
                    "Random draw",
                    "",
                    "Quit" ]
        menu = TerminalMenu(options, skip_empty_entries=True)
        choice = menu.show()
        if choice == 0:
            imid = input("Which IMID? ")
            imidMenu(db, imid)
        elif choice == 1:
            searchTerm = input("Search term: ")
            searchMenu(db, searchTerm, conf)
        elif choice == 2:
            draw(db)
        elif choice == 4:
            return

def imidMenu(db, imid):
    # TUI for displaying a single record based on IMID.
    cursor = db.cursor()
    cursor.execute("SELECT imid, filename, susDOS, dupeOf, desc, tags, width, height, fSize, " \
                   "freeText FROM images WHERE imid=?;", (imid,))
    record = list(cursor.fetchone())
    
    if record:
        while True:
            os.system('clear')
            printRecord(record)
            buildHeader(f"IMID Lookup")
            options = [ "Open image",
                        "Add/edit description",
                        "",
                        "Go back" ]
            menu = TerminalMenu(options, skip_empty_entries=True)
            choice = menu.show()
            if choice == 0:
                try:
                    with Image.open(record[1]) as pic:
                        pic.show()
                except:
                    pass
            elif choice == 1:
                notes = input(f"\nEnter additional notes: ")
                cursor.execute("UPDATE images SET freeText=? WHERE imid=?;", (notes, imid))
                record[9] = notes
                db.commit()
            elif choice == 3:
                cursor.close()
                return
    else:
        print("Bad IMID!")
        sleep(2)
        return

def searchMenu(db, searchTerm, conf):
    # TUI for searching records based on a search term.
    records   = []
    cursor    = db.cursor()
    results   = sengine.search(searchTerm, db)[:conf['results']]

    if results:
        for result in results:
            fullRecord = cursor.execute("SELECT imid, filename, desc FROM images WHERE imid = ?",
                                        (result,)).fetchone()
            records.append(fullRecord)
        menuLines = buildRecordLines(records)
        menuLines.append("")
        menuLines.append("Go back")

        while True:
            os.system('clear')
            buildHeader("Search Results")
            menu = TerminalMenu(menuLines, skip_empty_entries=True)
            choice = menu.show()
            if choice == len(menuLines)-1:
                cursor.close()
                return
            else:
                imidMenu(db, results[choice])
    else:
        print("No results found!")
        sleep(2)
        return

def buildRecordLines(records):
    # Creates nicely-formatted menu lines from a list of records.
    recordLines = []
    colOne      = 0
    colTwo      = 0
    colThree    = 0
    try:
        width = (os.get_terminal_size().columns) - 2
    except:
        width = 98

    for record in records:                  # This initial loop just calculates what the column
        if len(str(record[0])) > colOne:    # widths should be. 
            colOne = len(str(record[0]))
        if len(record[1]) > colTwo:
            if len(record[1]) > width / 2:
                colTwo = floor(width / 2)
            else:
                colTwo = len(record[1])
        colThree = width - (colOne + colTwo + 10)
    
    for record in records:
        imid  = str(record[0]).strip()
        fName = record[1].strip()
        desc  = record[2].strip()
        line  = f" {imid:>{colOne}.{colOne}} : {fName:<{colTwo}.{colTwo}} : {desc:<{colThree}.{colThree}}"
        recordLines.append(line)
    return recordLines

def buildHeader(content, delim="="):
    # Builds a header string.
    try:
        width = os.get_terminal_size().columns
    except:
        width = 100
    padCount = width - (len(content) + 4)
    print(f"\n" * 5)
    print(f"== {content} " + (delim*padCount) + "\n")
    return

def printRecord(record):
    # Prints the information from a single database record. Assumes record is a list containing 
    # the imid, filename, susDOS, dupeOf, desc, tags, width, height, fSize, and freeText fields IN
    # THAT ORDER.
    try:
        tstamp = datetime.datetime.fromtimestamp(float(record[2])).strftime('%B %d, %Y at %H:%M:%S')
    except:
        tstamp = ""

    print(f"\n\nIMID      #{record[0]}\n")
    print(f"Filename:   {record[1]}")
    print(f"File Size:  {(record[8]/1024):.2f} KB")
    print(f"Resolution: {record[6]} x {record[7]}\n")
    print(f"Suspected Day of Shot: {tstamp}")
    print(f"Suspected Duplicates:  {record[3]}\n")
    print(f"Description:\n    {record[4]}\n")
    print(f"Additional Notes:\n    {record[9]}\n")
    print(f"Search tags: {record[5]}\n")

    return

def draw(db):
    # Draw a random image from the database
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM images;")
    total = cursor.fetchone()[0]

    pick = random.randint(1, total)
    cursor.execute("SELECT imid FROM images ORDER BY imid LIMIT 1 OFFSET (? - 1);", (pick,))
    imid = cursor.fetchone()[0]
    imidMenu(db, imid)
    return


# MAIN (Except not really)
if __name__ == "__main__":
    print("This is a library of functions for displaying information on the screen. It is not " /
          "meant to be run directly.")