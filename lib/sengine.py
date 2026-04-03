#!/bin/python3

## IBASE SEARCH ENGINE LIBRARY
##
## Functions needed to search images in the iBase database.


# IMPORTS AND CONSTANTS
import sqlite3
import re
import json

from configManager import loadConfig
from math import log

conf      = './iBase.conf'
blacklist = [' ', 'THE', 'A', 'AN', 'OF', 'IN', 'ON', 'IS', 'AND', 'OR', 'JPG', 'JPEG', 'PNG',
             'BULK-DATA', 'PICS']


# FUNCTIONS
def crawler(db):
    # Crawler function to index images in the db.
    i, w  = 1, 1
    words = {}
    cursor = db.cursor()
    cursor.execute("SELECT imid, filename, desc, tags FROM images;")
    images = cursor.fetchall()

    for image in images:
        imid = image[0]
        file = normalize(image[1])
        desc = normalize(image[2])
        tags = normalize(image[3])
        sstr = f"{file} {desc} {tags}".split(' ')

        cursor.execute("UPDATE images SET wCount=? WHERE imid=? AND wCount<>?;", 
                       (len(sstr), imid, len(sstr),))
        for word in sstr:
            if word not in blacklist:
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
        
        for word in words:
            if w % 500 == 0:
                cursor.commit()
                print(f"Indexing {i/len(images):.2f}% complete.")
            cursor.execute("SELECT * FROM crawler WHERE word = ?;", (word,))
            result = cursor.fetchone()
            if result:
                linked = json.loads(result[3])
                if imid in linked and linked[imid] != words[word]:
                    linked[imid] = words[word]
                    score = sum(linked.values())
                    cursor.execute("UPDATE crawler SET score=?, linked=? WHERE wid=?;", 
                                   (score, json.dumps(linked), result[0],))
            else:
                linked = {imid: words[word]}
                score  = words[word]
                cursor.execute("INSERT OR IGNORE INTO crawler (word, score, linked) VALUES (?, ?, ?);",
                               (word, score, json.dumps(linked ),))
            w += 1
        i += 1
    cursor.commit()
    cursor.close()
    return

def search(query, db):
    # Searches through the database according to query and returns a list of relevant imids,
    # ordered from most to least relevant.
    cursor  = db.cursor()
    sTable  = {}
    terms   = normalize(query).split(' ')
    tImages = cursor.execute("SELECT COUNT(*) FROM images;").fetchone()[0]
    qWord   = "SELECT score, linked FROM crawler WHERE word=?;"
    qCount  = "SELECT wCount        FROM images  WHERE imid=?;"

    for term in terms:
        if term not in blacklist:
            word   = cursor.execute(qWord, (term,)).fetchone()
            wScore = word[0]
            linked = json.loads(word[1])
            for image in linked:
                wCount = cursor.execute(qCount, (image,)).fetchone()[0]
                tf     = linked[image] / wCount
                idf    = log(tImages / len(linked))
                rScore = tf * idf
                sTable[image] = rScore

    return imids

def normalize(content):
    # Takes in text content and normalizes it so that all extraneous characters are stripped away,
    # whitespace is flattened, and text is uppered.
    cNoChars   = re.sub(r'[^a-zA-Z0-9-]', ' ', content)
    cflattened = re.sub(r' +', ' ', cNoChars)
    normalized = cflattened.upper().strip()
    return normalized

# INITIALIZATION


# MAIN
if __name__ == "__main__":
    print("iBase Search Engine Library - not meant to be run as a standalone script.")
    quit()