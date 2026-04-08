#!/bin/python3

## IMAGE-BASE (iBASE)
## K. Chaconas
##
## Iterates over an image library and leverages LLMs to build a searchable database of descriptions
## for each image. 


# IMPORTS AND CONSTANTS
import os
import shutil
import sqlite3
import ollama
import hashlib
import datetime
import time
import argparse
import logging
import logging.config
import random
from tabulate import tabulate
from PIL import Image

import lib.sengine as sengine
import lib.tui as tui
from lib.configManager import loadConfig

cfile = './iBase.conf'


# FUNCTIONS
def buildFileList(albumRoot):
    # Builds a list of image files by iterating over all the contents of albumRoot, including
    # subdirectories.
    imageTypes = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")
    fileList = []

    for root, dirs, files in os.walk(albumRoot):
        for file in files:
            if file.endswith(imageTypes):
                filename = (os.path.join(root, file))
                fileList.append(os.fsdecode(os.fsencode(filename)))  # Normalizes the filename so
                                                                     # that the DB doesn't choke on
                                                                     # unparseable characters.
    return fileList

def initDB(filename):
    # Initializes the sqlite database which keeps track of images and their descriptions
    if not os.path.exists(filename):
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        tab_images = """CREATE TABLE images (
                        imid     INTEGER PRIMARY KEY,
                        filename TEXT UNIQUE,
                        hash     TEXT,
                        dupeOf   TEXT,
                        susDOS   TEXT,
                        desc     TEXT,
                        tags     TEXT,
                        width    INTEGER,
                        height   INTEGER,
                        fSize    INTEGER,
                        wCount   INTEGER,
                        freeText TEXT);"""
        tab_crawler = """CREATE TABLE crawler (
                         wid    INTEGER PRIMARY KEY,
                         word   TEXT,
                         linked TEXT);"""
        cursor.execute(tab_images)
        cursor.execute(tab_crawler)
        cursor.close()
        db.commit()
        db.close()
    return

def buildHash(filename):
    # Creates an MD5 hash of the given file, the same hash that would be returned if you had run
    # an md5sum command on it manually. 
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            hashObj = hashlib.md5()
            for chunk in iter(lambda: f.read(4096), b""):
                hashObj.update(chunk)
        return hashObj.hexdigest()
    else:
        logging.error(f"buildHash: File Not Found: {filename}")
        quit()

def scanDB(db, aRoot):
    # Recursively scans all the images in albumRoot in order to categorize them and store their
    # info in the database
    logging.info("SCANNING MODE")
    cursor  = db.cursor()
    i       = 1
    dPrompt = "In one or two sentences please describe what you see in this image. Provide ONLY the description and nothing else."
    tPrompt = "Please generate one to five comma-separated tag words that apply to this image. Provide ONLY the tags and nothing else."

    logging.info("Building file list...")
    files = buildFileList(aRoot)
    logging.info(f"Detected {len(files): ,} files.")

    for file in files:
        if i % 10000 == 0:
            pct = i/len(files)
            print(f"Progress: {pct:.2%}%")
        if i % 100 == 0:
            db.commit()

        susDos = parseDate(file)
        fSize  = os.path.getsize(file)

        try:
            if not entryExists(file, db):
                hashVal = buildHash(file)
                dupeOf  = findDupes(hashVal, db)
                desc    = callAI(file, dPrompt)
                tags    = callAI(file, tPrompt).upper()
                try:
                    with Image.open(file) as img:
                        width, height = img.size
                except Exception as e:
                    width, height = 0, 0
                    logging.error(f"Unable to open {file} for size assessment.")
                    logging.error(e)

                cursor.execute("INSERT OR IGNORE INTO images " \
                               "(filename, hash, dupeOf, susDOS, desc, tags, width, height, fSize) " \
                                "VALUES (?,?,?,?,?,?,?,?,?);", (file, hashVal, dupeOf, susDos, desc, tags, width, height, fSize))
                logging.info(f"Added {os.path.basename(file)} ({hashVal}) to the database.")
            else:
                cursor.execute("UPDATE images SET susDOS=?, fSize=? WHERE filename=?;", (susDos, fSize, file))
        except Exception as e:
            logging.error(f"Unable to process {file}!")
            logging.error(f"Error: {e}")
        i += 1

    db.commit()
    logging.info("SCAN COMPLETE.")
    cursor.close()
    return

def callAI(file, prompt):
    # Generates an LLM description for the given file using the ollama server.
    tries = 0
    while tries < conf['llmTries']:
        try:
            client   = ollama.Client(host=conf['llmHost'])
            response = client.chat(model=conf['llmModel'], messages=[{"role": "user", "content": prompt, "images": [file],}])
            return response['message']['content']
        except Exception as e:
            tries += 1
            if tries == conf['llmTries']:
                logging.error(e)
    logging.error(f"Tried {conf['llmTries']} times for file {os.path.basename(file)} but failed.")
    return "LLM Not Reachable"

def entryExists(filename, db):
    # Checks to see if a given file name already exists in the database.
    cursor = db.cursor()
    cursor.execute("SELECT imid FROM images WHERE filename=?", (filename,))
    imid = cursor.fetchone()
    cursor.close()
    if imid:
        return True
    else:
        return False

def findDupes(h, db):
    # Checks to see if there are any duplicate hashes already logged in the database. If yes, then
    # return a list of duplicate imids.
    imids = ""
    cursor = db.cursor()
    cursor.execute("SELECT imid FROM images WHERE hash=?", (h,))
    results = cursor.fetchall()
    cursor.close()

    for result in results:
        if imids == "":
            imids = result[0]
        else:
            imids = f"{imids}, {result[0]}"

    return imids

def parseDate(lfile):
    # If the filename has a recognizable naming convention based on the date/time the photo was
    # taken, parse the timestamp out and note it down as the "Suspected Day of Shot (DoS)".
    file = os.path.basename(lfile)
    try:
        if file[:4] == "PXL_":
            year   = int(file[4:8])
            month  = int(file[8:10])
            day    = int(file[10:12])
            hour   = int(file[13:15])
            minute = int(file[15:17])

            dto = datetime.datetime(year, month, day, hour, minute, tzinfo=datetime.timezone.utc)
            tstamp = time.mktime(dto.timetuple())
            return str(tstamp)
    except:
        logging.error(f"parseDate failure on {lfile}. Leaving susDOS blank.")
    return ""

def searchDB(db, searchterm):
    # Search the database for images that match the search term
    cursor  = db.cursor()
    table   = [["IMID", "File Path", "Description"]]
    results = sengine.search(searchterm, db)[:conf['results']]

    if results:
        for image in results:
            record = cursor.execute("SELECT imid, filename, desc FROM images WHERE imid=?;", 
                                    (image,)).fetchone()
            table.append([record[0], record[1], record[2]])
        print(tabulate(table, headers='firstrow', tablefmt='grid', maxcolwidths=[None, 30, 50]))
    quit()
    return

def draw(db):
    # Draw a random image from the database
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM images;")
    total = cursor.fetchone()[0]

    pick = random.randint(1, total)
    cursor.execute("SELECT imid, filename, susDOS, dupeOf, desc, tags, width, height, fSize FROM images " \
                   "ORDER BY imid LIMIT 1 OFFSET (? - 1);", (pick,))
    record = cursor.fetchone()
    tui.printRecord(record)

    try:
        with Image.open(record[1]) as pic:
            pic.show()
    except:
        pass

    quit()
    return

def purgeDB(db):
    # Iterates through the database and purges the record of any file which no longer exists.
    logging.info("PURGE MODE")
    cursor = db.cursor()

    shutil.copy(conf['dbfile'], f"{conf['dbfile']}.backup")
    logging.info(f"Backed up database to {conf['dbfile']}.backup")

    cursor.execute("SELECT imid, filename FROM images;")
    results = cursor.fetchall()
    for row in results:
        if not os.path.exists(row[1]):
            cursor.execute("DELETE FROM images WHERE imid=?;", (row[0],))
            logging.info(f"Removed IMID #{row[0]:<7} ({row[1]})")
    cursor.close()
    db.commit()
    logging.info("PURGE COMPLETE")
    return

if __name__ == "__main__":
    # INITIALIZATION
    conf  = loadConfig(cfile)
    aRoot = conf['albumRoot']

    Image.MAX_IMAGE_PIXELS = None  # Disables PIL's compression bomb detection

    logging.config.dictConfig({    # This block silences log spam from imported modules so that only
        'version': 1,              # my own log messages get recorded.
        'disable_existing_loggers': True,
    })
    logging.basicConfig(
        level=conf['loglevel'],
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(conf['logfile'], mode='a'),
            logging.StreamHandler()])
    logging.info("INIT - Logger")

    initDB(conf['dbfile'])
    db = sqlite3.connect(conf['dbfile'])
    logging.info(f"INIT - Database")

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--album-root", help="Override the default album root in the config file")
    parser.add_argument("-s", "--scan", action="store_true", help="Scan for updates to the database")
    parser.add_argument("-f", "--find", help="Image search")
    parser.add_argument("-p", "--purge", action="store_true", help="Iterate through the database and purge records for files which no longer exist.")
    parser.add_argument("-i", "--index", action="store_true", help="Refresh the search index")
    parser.add_argument("-y", "--sync", action="store_true", help="Perform a full database sync (purge, scan, and re-index)")
    parser.add_argument("-d", "--draw", action="store_true", help="Draw a random image out of the database. For fun!")
    args = parser.parse_args()
    logging.info("INIT - Argument Parsing")


    # MAIN
    if args.album_root:
        aRoot = args.album_root
    elif args.scan:
        scanDB(db, aRoot)
        print("HAVE A NICE DAY 😎")
    elif args.find:
        searchDB(db, args.find)
    elif args.purge:
        purgeDB(db)
        print("HAVE A NICE DAY 😎")
        quit()
    elif args.index:
        sengine.crawler(db)
        print("HAVE A NICE DAY 😎")
        quit()
    elif args.sync:
        logging.info("FULL SYNC - Will perform a purge, scan, and re-index.")
        purgeDB(db)
        scanDB(db, aRoot)
        sengine.crawler(db)
        print("SYNC COMPLETE. HAVE A NICE DAY 😎")
    elif args.draw:
        draw(db)
    else:
        tui.mainmenu(db, conf)
    
    db.close()
    quit()

