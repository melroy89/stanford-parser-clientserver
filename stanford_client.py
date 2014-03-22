#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2014 by Melroy van den Berg
"""
Stanford Parser Client Example
"""
__author__ = "Melroy van den Berg <melroy@melroy.org>"
__version__ = "0.1"

import sys
import Pyro4

PYRO_NAME = "PYRONAME:stanford.server"

wordList = ['Hello', ',', 'my', 'name', 'is', 'Melroy']
try:
	# Connect to the Stanford Server
	server=Pyro4.Proxy(PYRO_NAME)
	# Sent the request to the server
	tree = server.parse(wordList)
	print tree
except Pyro4.errors.CommunicationError, e:
	print "Can't connect to Stanford Parser Server. Is the server running?"
	print "Error: ", e
except Pyro4.errors.NamingError, e:
	print "Can't connect to Stanford Parser Server. Is the server running?"
	print "Error: ", e
