# iBase Configuration File
Below are the options available to edit in iBase.conf. The file itself is essentially a JSON object, but with the added benefit that inline comments are supported. 

| Option    | Example Setting    | Description |
|-----------|--------------------|-------------|
| albumRoot | /home/bob/Pictures | The root directory where your pictures are kept. iBase will scan this directory and any nested directories within in. |
| dbfile    | ./iBase.db         | The path and name of the generated database file. |
| logfile   | ./iBase.log        | The path and name of the log file. |
| loglevel  | ERROR              | The verbosity level of the logging system. Recommend either ERROR for just error messages or INFO for full verbosity. |
| results   | 10                 | The number of results that should be returned when performing a search. |
| llmHost   | localhost:11434    | The host and port of your Ollama server. |
| llmModel  | gemma3:12b         | The LLM model to use for scanning. | 
| llmTries  | 3                  | The number of times iBase will attempt to call Ollama for a given image before erroring out and moving on. |