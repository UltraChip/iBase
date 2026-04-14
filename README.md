# iBase
## A simple command-line utility for catalogging large numbers of unorganized images.

### Intro
iBase is a simple command-line utility designed to catalog large numbers of unorganized pictures. It's meant for those of us who having been hording random photographs and other images on our computers for years and have lost track of what we actually have. The end result is a nice, easy-to-search sqlite3 database containing information about every picture you've scanned.

In addition to tracking other image properties (such as detected duplicate images), iBase uses your local ollama server to add LLM-generated descriptions and search tags to the database. 

### Prerequisites
- Python 3
- SQLite3
- An accessible Ollama server equipped with a model that can process image input, such as gemma3
- The Ollama Python module
- The tabulate Python module
- The simple-term-menu Python module

### Installation
1. Clone this repository to your local computer.
2. Set up your config file by editing sample.conf and saving it as iBase.conf. At minimum, you'll want to set:
- "albumRoot" to whatever the root directory for your images is
- "llmHost" to point to your Ollama server, and
- "llmModel" to point to a model that can process image input.

### First Use
The first thing you'll probably want to do is run an initial scan of your images in order to generate the actual database. You can do this by running:

    $ python3 ibase.py -s

Be aware that if you have a lot of images the scan could take an **EXTREMELY LONG TIME**. For reference: I had about 76,000 pictures and the initial scan took about 5 days. But once the scan is complete you should have a fully populated sqlite3 database with information about all your pictures. Once the initial database is populated re-running the scan will add any new images that you've added since the last scan.

After the initial scan, you'll likely want to build the search index. This can be accomplished by either performing a full sync (see below) or by running:

    $ python3 ibase.py -i

Eventually, you are likely going to delete or move images in your album. When this happens, you will want to run a purge operation on the database to remove records which are no longer accurate.

    $ python3 ibase.py -p

There will be many times when you'll want to perform a complete synchronization of the database. In other words, purge records for no-longer-present files,add records for new files, and rebuild the search index to account for all the changes. This can be accomplished with iBase's sYnc function;

    $ python3 ibase.py -y

For a full rundown on the rest of the command-line arguments available to you look at the [complete arguments table](docs/args.md) in the docs directory.

### Using the TUI for image search and lookup
If you run iBase without any command line parameters like so:

    $ python3 ibase.py

...you will be presented with a TUI menu that allows you to easily look up images, either directly if you happen to know the image's IMID number or via search engine. 

The TUI will allow you to view the key metadata associated with the image, add additional notes to the database, and open up the image itself for viewing.

### Database Schema
Full details on the database schema can be found in [docs/database.md](docs/database.md).

### Configuration
Full details on the configuration of iBase can be found in [docs/config.md](docs/config.md).