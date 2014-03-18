Fastest Stanford Parser with RPC interface
==========================================
The latest Stanford Parser combined with RPC interface for a server/client feature. It's the fastest Stanford Parser currently available. 

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

Testing
-------
Execute the client example:  ```./stanford_parser_client.py```


Why is this the fastest parser?
-------------------------------
It uses Jython to start-up the Stanford Parser, instead of initalize the Stanford Parser from cratch everytime...

This  peace of software runs a server where the PCFG parser is already initalized. So parsing different sentences is handled more efficiently and quickly.

Copyright &amp; Licence
-----------------------
The code is developed by Melroy van den Berg, inspired by Viktor Pekar. 

Licensed under the Apache License, Version 2.0 (the "License"). See [LICENSE](LICENSE) file.
