# iBase
## A simple command-line utility for catalogging large numbers of unorganized images.

### Intro
iBase is a simple command-line utility designed to catalog large numbers of unorganized pictures. It's meant for those of us who having been hording random photographs and other images on our computers for years and have lost track of what we actually have. The end result is a nice, easy-to-search sqlite3 database containing information about every picture you've scanned.

In addition to tracking other image properties (such as detected duplicate images), iBase uses your local ollama server to add LLM-generated descriptions and search tags to the database. 

### Prerequisites
- Python 3
- SQLite3
- An accessible Ollama server equipped with a model that can process image input, such as Gemini 3
- The Ollama Python module
- The tabulate Python module

### Installation
1. Clone this repository to your local computer.
2. Set up your config file by editing sample.conf and saving it as iBase.conf. At minimum, you'll want to set:
- "albumRoot" to whatever the root directory for your images is
- "llmHost" to point to your Ollama server, and
- "llmModel" to point to a model that can process image input.

### How to Use
The first thing you'll probably want to do is run an initial scan of your images in order to generate the actual database. You can do this by running:

    $ python3 ibase.py -s

Be aware that if you have a lot of images the scan could take an **EXTREMELY LONG TIME**. For reference: I had about 76,000 pictures and the initial scan took about 5 days. But once the scan is complete you should have a fully populated sqlite3 database with information about all your pictures. Once the initial database is populated re-running the scan will add any new images that you've added since the last scan.

For basic keyword searches of the database you can use iBase itself with the -f parameter. For example, to search for images that contain apples you could enter:

    $ python3 ibase.py -f apple

The search is case-insensitive.

For more sophisticated queries you are free to search the database directly with sqlite3's native command line utility or any other DB utility you choose. 

### Database Schema
The database schema is pretty straightforward. There is only a single table, named "images", which has the following columns:

| Column   | Data Type           | Description |
|----------|---------------------|-------------|
| imid     | INTEGER PRIMARY KEY | Unique ID number for each image |
| filename | TEXT UNIQUE         | The full file name and path of the image |
| hash     | TEXT                | An MD5 hash of the image. Used for indentifying duplicate images |
| dupeOf   | TEXT                | If iBase detects an image is a duplicate of others, the IMIDs of those images are stored here |
| susDOS   | TEXT                | "Suspected Day of Shot". If iBase is able to parse the date/time an image was captured from its file name, it will be recorded here as a UNIX timestamp |
| desc     | TEXT                | An LLM-generated description of the image |
| tags     | TEXT                | An LLM-generated list of search tags. Comma-separated | 

### Configuration
Below are the options available to edit in iBase.conf. The file itself is essentially a JSON object, but with the added benefit that inline comments are supported. 

| Option    | Example Setting    | Description |
|-----------|--------------------|-------------|
| albumRoot | /home/bob/Pictures | The root directory where your pictures are kept. iBase will scan this directory and any nested directories within in. |
| dbfile    | ./iBase.db         | The path and name of the generated database file. |
| logfile   | ./iBase.log        | The path and name of the log file. |
| loglevel  | ERROR              | The verbosity level of the logging system. Recommend either ERROR for just error messages or INFO for full verbosity. |
| llmHost   | localhost:11434    | The host and port of your Ollama server. |
| llmModel  | gemma3:12b         | The LLM model to use for scanning. | 
| llmTries  | 3                  | The number of times iBase will attempt to call Ollama for a given image before erroring out and moving on. |

### Command-line Parameters
This section will probably get updated regularly as new features are added, but this is the list of what command-line options are available.

| Short | Long | Description |
|----|--------------|-------------|
| -h | --help       | Show usage information and exit. |
| -r | --album-root | Override the default album root directory. |
| -s | --scan       | Recursively scan all images in the album root and add any new images to the database. |
| -f | --find       | Basic keyword search of the database. |