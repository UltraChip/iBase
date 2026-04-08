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

### How to Use
The first thing you'll probably want to do is run an initial scan of your images in order to generate the actual database. You can do this by running:

    $ python3 ibase.py -s

Be aware that if you have a lot of images the scan could take an **EXTREMELY LONG TIME**. For reference: I had about 76,000 pictures and the initial scan took about 5 days. But once the scan is complete you should have a fully populated sqlite3 database with information about all your pictures. Once the initial database is populated re-running the scan will add any new images that you've added since the last scan.

For basic keyword searches of the database you can use iBase itself with the -f parameter. For example, to search for images that contain apples you could enter:

    $ python3 ibase.py -f apple

The search is case-insensitive.

For more sophisticated queries you are free to search the database directly with sqlite3's native command line utility or any other DB utility you choose.

Eventually, you are likely going to delete or move images in your album. When this happens, you will want to run a purge operation on the database to remove records which are no longer accurate.

    $ python3 ibase.py -p

There will be many times when you'll want to perform a complete synchronization of the database. In other words, purge records for no-longer-present files while also adding records for new ones. This can be accomplished with iBase's sYnc function;

    $ python3 ibase.py -y

For a full rundown on the rest of the command-line arguments available to you look at the [complete arguments table](docs/args.md) in the docs directory.

### Database Schema
Full details on the database schema can be found in [docs/database.md](docs/database.md).

### Configuration
Full details on the configuration of iBase can be found in [docs/config.md](docs/config.md).