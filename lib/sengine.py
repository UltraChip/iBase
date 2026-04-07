#!/bin/python3

## IBASE SEARCH ENGINE LIBRARY
##
## Functions needed to search images in the iBase database.


# IMPORTS AND CONSTANTS
import sqlite3
import re
import json
from math import log

blacklist = [ ' ', 'THE', 'A', 'AN', 'OF', 'IN', 'ON', 'IS', 'AND', 'OR', 'JPG', 'JPEG', 'PNG',
              'BULK-DATA', 'PICS', 'ARE', 'WITH', 'FROM', 'HAS' ]


# FUNCTIONS
def crawler(db):
    # Crawler function to index images in the db.
    print("INDEX MODE")
    cursor = db.cursor()
    
    cursor.execute("SELECT word, linked FROM crawler")
    cTable = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
    cursor.execute("SELECT imid, filename, desc, tags, wCount, freeText FROM images;")
    images = cursor.fetchall()
    tImages = len(images)

    for i, image in enumerate(images, 1):
        imid    = str(image[0])
        rawText = f"{image[1]} {image[2]} {image[3]} {image[5]}"
        sstr    = normalize(rawText).split(' ')
        wCount  = len(sstr)
        
        if image[4] != wCount:
            cursor.execute("UPDATE images SET wCount=? WHERE imid=?", (wCount, imid))

        words = {}
        for word in sstr:
            if word not in blacklist and word:
                words[word] = words.get(word, 0) + 1
        
        for word, count in words.items():
            if word not in cTable:
                cTable[word] = {}
            cTable[word][imid] = count

        if i % 1000 == 0:
            print(f"Indexing {(i/tImages)*100:.2f}% complete.")

    finalCData = [(word, json.dumps(linked)) for word, linked in cTable.items()]
    cursor.execute("DELETE FROM crawler")
    cursor.executemany("INSERT INTO crawler (word, linked) VALUES (?, ?)", finalCData)
    
    db.commit()
    cursor.close()
    print("INDEXING COMPLETE")
    return

def search(query, db):
    # Searches through the database according to query and returns a list of relevant imids,
    # ordered from most to least relevant.
    cursor  = db.cursor()
    sTable  = {}
    terms   = normalize(query).split(' ')
    tImages = cursor.execute("SELECT COUNT(*) FROM images;").fetchone()[0]
    qWord   = "SELECT linked FROM crawler WHERE word=?;"
    qCount  = "SELECT wCount FROM images  WHERE imid=?;"

    for term in terms:
        if term not in blacklist:
            dLinked = cursor.execute(qWord, (term,)).fetchone()
            if dLinked:
                linked = json.loads(dLinked[0])
                for image, count in linked.items():
                    wCount = cursor.execute(qCount, (image,)).fetchone()[0]
                    tf     = linked[image] / wCount
                    idf    = log(tImages / len(linked))
                    sTable[image] = sTable.get(image, 0) + (tf * idf)

    cursor.close()
    return sorted(sTable, key=sTable.get, reverse=True)

def normalize(content):
    # Takes in text content and normalizes it so that all extraneous characters are stripped away,
    # whitespace is flattened, and text is uppered.
    cNoChars   = re.sub(r'[^a-zA-Z0-9-]', ' ', content)
    cflattened = re.sub(r' +', ' ', cNoChars)
    normalized = cflattened.upper().strip()
    return normalized


# MAIN
if __name__ == "__main__":
    print("iBase Search Engine Library - not meant to be run as a standalone script.")
    quit()