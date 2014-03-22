#!/usr/bin/env jython
# -*- coding: utf-8 -*-
# Copyright 2014 by Melroy van den Berg
"""
Stanford Parser Server running on localhost

Requirements
------------
	- Jython >= 2.7 (http://www.jython.org/downloads.html)
	- Pyro4 (https://github.com/irmen/Pyro4)

"""
__author__ = "Melroy van den Berg <melroy@melroy.org>"
__version__ = "0.1"

import socket
from select import cpython_compatible_select as select
import sys
import Pyro4.core
import Pyro4.naming
from stanford_interface import StanfordParser

PYRO_NAME = 'stanford.server'

Pyro4.config.SERVERTYPE="thread" # Thread pool based
#Pyro4.config.SERVERTYPE="multiplex" # Select/poll based
hostname="localhost" #socket.gethostname()

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

print("initializing services... servertype=%s" % Pyro4.config.SERVERTYPE)
# start a name server (only with a broadcast server when NOT running on localhost)
nameserverUri, nameserverDaemon, broadcastServer = Pyro4.naming.startNS(host=hostname)
  
print("got a Nameserver, uri=%s" % nameserverUri)
print("ns daemon location string=%s" % nameserverDaemon.locationStr)
print("ns daemon sockets=%s" % nameserverDaemon.sockets)
if broadcastServer:
	print("bc server socket=%s (fileno %d)" % (broadcastServer.sock, broadcastServer.fileno()))
  
# create a Pyro daemon
pyrodaemon=Pyro4.core.Daemon(host=hostname)
print("daemon location string=%s" % pyrodaemon.locationStr)
print("daemon sockets=%s" % pyrodaemon.sockets)
  
# register a server object with the daemon
serveruri=pyrodaemon.register(StanfordHelpParser())
print("server uri=%s" % serveruri)
  
# register it with the embedded nameserver directly
nameserverDaemon.nameserver.register(PYRO_NAME,serveruri)
  
print("Stanford Server is running...")
  
# below is our custom event loop.
while True:
	# create sets of the socket objects we will be waiting on
	# (a set provides fast lookup compared to a list)
	nameserverSockets = set(nameserverDaemon.sockets)
	pyroSockets = set(pyrodaemon.sockets)
	rs=[]
	if broadcastServer:
		rs=[broadcastServer]  # only the broadcast server is directly usable as a select() object
	rs.extend(nameserverSockets)
	rs.extend(pyroSockets)
	rs,_,_ = select(rs,[],[],2)
	eventsForNameserver=[]
	eventsForDaemon=[]
	for s in rs:
		if s is broadcastServer:
			broadcastServer.processRequest()
		elif s in nameserverSockets:
			eventsForNameserver.append(s)
		elif s in pyroSockets:
			eventsForDaemon.append(s)
	if eventsForNameserver:
		nameserverDaemon.events(eventsForNameserver)
	if eventsForDaemon:
		pyrodaemon.events(eventsForDaemon)

nameserverDaemon.close()
if broadcastServer:
	broadcastServer.close()
pyrodaemon.close()

