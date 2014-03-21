Stanford Parser Server
======================
This Stanford Parser Server/Client combines the Stanford Parser with a Pyro4 Interface for client-server communication. It's the fastest Stanford Parser currently available. 
Read below why it's the fastest.

Example client is included!

Requirements
------------
- Stanford Parser 
- Jython
- Pyro4 (https://github.com/irmen/Pyro4)
- Serpent (https://github.com/irmen/Serpent)


- Python (needed for the client example only)

**Note:** Be sure you install Pyro4 &amp; Serpent for both Python and Jython.

Installation
------------
0. Be sure you meets all the requirements (see above)
1. Download the Stanford Parser (http://nlp.stanford.edu/downloads/lex-parser.shtml#Download)
2. Unpack the download into a local dir, place the stanford-parser.jar into this folder.
3. Place the englishPCFG.ser.gz file into this folder as well (this file is located in the stanford-parser-x.x.x-models.jar file)
4. In terminal: ```export PYRO_SERIALIZERS_ACCEPTED=pickle```
5. Start the Name server: ```python -m Pyro4.naming```
6. Start the Stanford server: ```./stanford_server.py```

**IMPORTANT NOTE:** The server only accepts a list of words, for a reason! Meaning tokenization of sentences/words can be done out-side the server. For example use NLTK for tokenize sentences and words from user input. For more info see: http://www.nltk.org/

Testing
-------
Execute the client example: ```./stanford_client.py```



Why is this the fastest parser?
-------------------------------
The Stanford Parser server uses Jython to start-up the Stanford Parser.

The server initialize the PCFG parser once, so parsing different sentences is **handled more efficiently and quickly**. Compared with other implementations of Stanford Parser, which initializes the PCFG parser every time from scratch.

Besides that all, Pyro is a very fast &amp; lightweight Python-based Distributed Object Technology.

Copyright &amp; Licence
-----------------------
The code is developed by Melroy van den Berg, inspired by Viktor Pekar. 

Licensed under the Apache License, Version 2.0 (the "License"). See [LICENSE](LICENSE) file.

