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
    i, w  = 1, 1
    cursor = db.cursor()
    cursor.execute("SELECT imid, filename, desc, tags FROM images;")
    images = cursor.fetchall()

    for image in images:
        imid  = str(image[0])  # Holy crap it took me forever to realize I need to explicity make
        words = {}             # this a string!
        file  = normalize(image[1])
        desc  = normalize(image[2])
        tags  = normalize(image[3])
        sstr  = f"{file} {desc} {tags}".split(' ')

        cursor.execute("UPDATE images SET wCount=? WHERE imid=? AND (wCount IS NULL OR wCount<>?);", 
                       (len(sstr), imid, len(sstr),))
        for word in sstr:
            if word not in blacklist:
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
        
        for word, count in words.items():
            if w % 500 == 0:
                db.commit()
                print(f"Indexing {(i/len(images))*100:.2f}% complete.")
            cursor.execute("SELECT * FROM crawler WHERE word = ?;", (word,))
            result = cursor.fetchone()
            if result:
                linked = json.loads(result[2])
                linked[imid] = count
                cursor.execute("UPDATE crawler SET linked=? WHERE wid=?;", 
                                   (json.dumps(linked), result[0],))
            else:
                linked = {imid: count}
                cursor.execute("INSERT OR IGNORE INTO crawler (word, linked) VALUES (?, ?);",
                               (word, json.dumps(linked),))
            w += 1
        i += 1
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
            linked = json.loads(cursor.execute(qWord, (term,)).fetchone()[0])
            if linked:
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