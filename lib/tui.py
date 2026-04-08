#!/bin/python3

## IBASE DISPLAY ENGINE LIBRARY
##
## Various helper functions for generating TUI elements on the screen.


# IMPORTS AND CONSTANTS
import sqlite3
import datetime
import os
from time import sleep
from tkinter import Image
from simple_term_menu import TerminalMenu
from PIL import Image


# FUNCTIONS
def mainmenu(db, conf):
    # Main TUI menu.
    while True:
        os.system('clear')
        buildHeader(f"iBase version {conf['VERSION']}")
        options = [ "Direct IMID lookup",
                    "Search by keyword",
                    "Quit" ]
        menu = TerminalMenu(options)
        choice = menu.show()
        if choice == 0:
            imid = input("Which IMID? ")
            imidMenu(db, imid)
        elif choice == 1:
            searchTerm = input("Search term: ")
            searchMenu(db, searchTerm)
        elif choice == 2:
            return

def imidMenu(db, imid):
    # TUI for displaying a single record based on IMID.
    cursor = db.cursor()
    record = cursor.execute("SELECT imid, filename, susDOS, dupeOf, desc, tags, width, height, fSize" /
                            " FROM images WHERE imid=?;", (imid,)).fetchone()
    
    if record:
        while True:
            os.system('clear')
            printRecord(record)
            buildHeader(f"IMID Lookup")
            options = [ "Open image",
                        "Go back" ]
            menu = TerminalMenu(options)
            choice = menu.show()
            if choice == 0:
                try:
                    with Image.open(record[1]) as pic:
                        pic.show()
                except:
                    pass
            elif choice == 1:
                cursor.close()
                return
    else:
        print("Bad IMID!")
        sleep(2)
        return

def buildHeader(content, delim="="):
    # Builds a header string.
    try:
        width = os.get_terminal_size().columns
    except:
        width = 100
    padCount = width - (len(content) + 4)
    print(f"== {content} " + (delim * padCount))
    return

def printRecord(record):
    # Prints the information from a single database record. Assumes record is a list of ALL columns
    # in the images table, in order.
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
    print(f"Search tags: {record[5]}\n")

    return


# MAIN (Except not really)
if __name__ == "__main__":
    print("This is a library of functions for displaying information on the screen. It is not " /
          "meant to be run directly.")