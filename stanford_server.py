#!/usr/bin/env jython
# -*- coding: utf-8 -*-
# Copyright 2014 by Melroy van den Berg
"""
Stanford Parser Server

Requirements
------------
	- Jython >= 2.7 (http://www.jython.org/downloads.html)
	- Pyro4 (https://github.com/irmen/Pyro4)

"""
__author__ = "Melroy van den Berg <melroy@melroy.org>"
__version__ = "0.1"

import os
import Pyro4
from stanford_interface import StanfordParser
Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

PYRO_NAME = 'stanford.server'

class StanfordHelpParser(object):
	"""
	Helper class around the StanfordParser class
	"""

	def __init__(self):
		"""
		Setup the Stanford Parser
		"""
		# Jar file should be set inside the stanford_lib.py or add it manually to the class path
		self.parser = StanfordParser(parser_file='./englishPCFG.ser.gz')

	def parse(self, wordList):
		"""
		Parse the word list
		"""
		sentenceObject = self.parser.parse_wordlist(wordList)	
		return str(sentenceObject.get_parse())

parser=StanfordHelpParser()

daemon=Pyro4.Daemon()					# make a Pyro daemon
ns=Pyro4.locateNS()						# find the name server
uri=daemon.register(parser)				# register the parser object as a Pyro object
ns.register(PYRO_NAME, uri)				# register the object

print "Stanford Server is running on %s with the proxy name: %s." % (str(uri).split("@")[1], str(PYRO_NAME))

daemon.requestLoop()                  # start the event loop of the server to wait for calls

