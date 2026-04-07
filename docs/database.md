# iBase Database Schema
The database schema is pretty straightforward. There are two tables in the database:
- images : Stores the bulk of the collected metadata for each scanned pictures
- crawler : Stores the search word index which drives iBase's search engine

### Table: images
| Column   | Data Type           | Description |
|----------|---------------------|-------------|
| imid     | INTEGER PRIMARY KEY | Unique ID number for each image |
| filename | TEXT UNIQUE         | The full file name and path of the image |
| hash     | TEXT                | An MD5 hash of the image. Used for indentifying duplicate images |
| dupeOf   | TEXT                | If iBase detects an image is a duplicate of others, the IMIDs of the suspected duplicates are stored here |
| susDOS   | TEXT                | "Suspected Day of Shot". If iBase is able to parse the date/time an image was captured from its file name, it will be recorded here as a UNIX timestamp |
| desc     | TEXT                | An LLM-generated description of the image |
| tags     | TEXT                | An LLM-generated list of search tags. Comma-separated |
| width    | INTEGER             | The width of the image in pixels |
| height   | INTEGER             | The height of the image in pixels |
| fSize    | INTEGER             | The size of the image in bytes |
| wCount   | INTEGER             | The total number of unique words associated with the image. Used by the search engine for calculating relevance scores. |
|freeText  | TEXT                | A description field similar to desc, but reserved for human-provided descriptions as opposed to LLM-generated. |

### Table: crawler
| Column | Data Type           | Description |
|--------|---------------------|-------------|
| wid    | INTEGER PRIMARY KEY | Unique identifier for each word in the database |
| word   | TEXT                | The actual word |
| linked | TEXT                | A JSON-encoded list of each image that contains this word. |

### Linked List Structure:
The list of images associated ("linked") with a given search word is encoded as a JSON array, where each element is a key:value pair representing the image (represented by its imid number) and the frequency of that word in the image's metadata. 

As an example, let's say a given word shows up in image \#123's metadata 6 times, in image \#456's metadata 3 times, and image \#789's metadata 27 times. The resulting value of linked would be:

    { '123':6, '456':3, '789':27 }

**NOTE**: Notice the quotation marks surrounding the imids. Even though they are numbers they get encoded in linked as strings. 