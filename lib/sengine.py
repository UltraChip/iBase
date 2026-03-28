#!/bin/python3

## IBASE SEARCH ENGINE LIBRARY
##
## Functions needed to search images in the iBase database.


# IMPORTS AND CONSTANTS
import sqlite3
from configManager import loadConfig

conf      = './iBase.conf'
blacklist = ['THE', 'A', 'AN', 'OF', 'IN', 'ON', 'IS', 'AND', 'OR', 'JPG', 'JPEG', 'PNG',
             'BULK-DATA', 'PICS']


# FUNCTIONS
def crawler(db):
    # Crawler function to index images in the db.
    cursor = db.cursor()
    cursor.execute("SELECT imid, filename, desc, tags FROM images;")
    images = cursor.fetchall()
    words = {}

    for image in images:
        imid = image[0]
        file = normalize(image[1])
        desc = normalize(image[2])
        tags = normalize(image[3])
        sstr = f"{file} {desc} {tags}".split(' ')

        for word in sstr:
            if word not in blacklist:
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
        
        for word in words:
            cursor.execute("SELECT * FROM crawler WHERE word = ?;", (word,))
            result = cursor.fetchone()
            if result:
                linked = decodeLinked(result[3])
                if imid in linked and linked[imid] != words[word]:
                    linked[imid] = words[word]
                    score = sum(linked.values())
                    cursor.execute("UPDATE crawler SET score=?, linked=? WHERE wid=?;", 
                                   (score, encodeLinked(linked), result[0],))

    return

def search(query):
    # Searches through the database according to query and returns a list of relevant imids,
    # ordered from most to least relevant.
    return imids


# INITIALIZATION


# MAIN
if __name__ == "__main__":
    print("iBase Search Engine Library - not meant to be run as a standalone script.")
    quit()