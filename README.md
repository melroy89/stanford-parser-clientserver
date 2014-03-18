Stanford Parser with RPC interface
==================================
The latest Stanford Parser combined with RPC interface for a server/client feature. It's the fastest Stanford Parser currently available. 
Read below why it's the fastest.

Requirements
------------
- Stanford Parser 
- Jython
- Python (needed for the client example only)


Installation
------------
1. Download the Stanford Parser (http://nlp.stanford.edu/downloads/lex-parser.shtml#Download)
2. Unpack the download into a local dir, place the stanford-parser.jar into this folder.
3. Place the englishPCFG.ser.gz file into this folder as well.
4. Start the Stanford server: ```./stanford_parser_server.py```

**NOTE:** the server only accepts a list of words in purpose. Meaning tokenization of sentences/words can be done out-side the server. For example use NLTK for tokenize sentences and words from user input. For more info see: http://www.nltk.org/

Testing
-------
Execute the client example:  ```./stanford_parser_client.py```


Why is this the fastest parser?
-------------------------------
The Stanford Parser server uses Jython to start-up the Stanford Parser.

The server initialize the PCFG parser once, so parsing different sentences is **handled more efficiently and quickly**. Compared with other implementations of Stanford Parser, which initializes the PCFG parser every time from scratch.

Copyright &amp; Licence
-----------------------
The code is developed by Melroy van den Berg, inspired by Viktor Pekar. 

Licensed under the Apache License, Version 2.0 (the "License"). See [LICENSE](LICENSE) file.
