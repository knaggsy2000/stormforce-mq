#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008-2012, 2014, 2016 Daniel Knaggs - 2E0DPK/M6DPK      #
# All rights reserved.                                                  #
#                                                                       #
# Redistribution and use in source and binary forms, with or without    #
# modification, are permitted provided that the following conditions    #
# are met: -                                                            #
#                                                                       #
#   * Redistributions of source code must retain the above copyright    #
#     notice, this list of conditions and the following disclaimer.     #
#                                                                       #
#   * Redistributions in binary form must reproduce the above copyright #
#     notice, this list of conditions and the following disclaimer in   #
#     the documentation and/or other materials provided with the        #
#     distribution.                                                     #
#                                                                       #
#   * Neither the name of the author nor the names of its contributors  #
#     may be used to endorse or promote products derived from this      #
#     software without specific prior written permission.               #
#                                                                       #
#   * This Software is not to be used for safety purposes.              #
#                                                                       #
#   * You agree and abide the Disclaimer for your Boltek products.      #
#                                                                       #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #
#########################################################################


###################################################
# StormForce Base Plugin                          #
###################################################
import os
import sys

sys.path.append(os.path.join(sys.path[0], ".."))


from danlog import DanLog
from smq_shared import Database, MQ


###########
# Classes #
###########
class PluginBase():
	def __init__(self):
		from datetime import datetime, timedelta
		from xml.dom import minidom
		
		import json
		import os
		import threading
		import time
		
		
		self.ENABLED = False
		
		self.MQ_DURABLE = True
		self.MQ_EXCHANGE_NAME = ""
		self.MQ_EXCHANGE_TYPE = ""
		self.MQ_HOSTNAME = ""
		self.MQ_NO_ACK_MESSAGES = False
		self.MQ_PASSWORD = ""
		self.MQ_PORT = 5672
		self.MQ_REPLY_TO = ""
		self.MQ_ROUTING_KEY = ""
		self.MQ_RX_ENABLED = True
		self.MQ_USERNAME = ""
		self.MQ_VIRTUAL_HOST = "/"
		
		self.POSTGRESQL_DATABASE = ""
		self.POSTGRESQL_PASSWORD = ""
		self.POSTGRESQL_SERVER = ""
		self.POSTGRESQL_USERNAME = ""
		
		
		self.datetime = datetime
		self.json = json
		self.minidom = minidom
		self.os = os
		self.running = False
		self.threading = threading
		self.time = time
		self.timedelta = timedelta
		
		
		self.PLUGIN_FULL_PATH = self.getScriptPath()
		self.PLUGIN_FOLDER = self.os.path.dirname(self.PLUGIN_FULL_PATH)
		self.PLUGIN_FILENAME = self.os.path.basename(self.PLUGIN_FULL_PATH)
		self.PLUGIN_FILENAME_WITHOUT_EXTENSION = self.os.path.splitext(self.PLUGIN_FILENAME)[0]
		self.log = DanLog("Plugin->{0}".format(self.PLUGIN_FILENAME))
		
		
		self.XML_EXTENSIBLE_SETTINGS_FILE = self.os.path.join(self.PLUGIN_FOLDER, "smq_extensible.xml")
		self.readXMLExtensibleSettings()
		
		
		self.XML_SETTINGS_FILE = self.os.path.join(self.PLUGIN_FOLDER, "{0}.xml".format(self.PLUGIN_FILENAME_WITHOUT_EXTENSION))
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.warn("No XML settings have been found for the plugin, creating one...")
			self.writeXMLSettings()
		
		if self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.info("Reading XML settings for the plugin...")
			self.readXMLSettings()
			
			if self.os.path.exists("{0}.bak".format(self.XML_SETTINGS_FILE)):
				self.os.unlink("{0}.bak".format(self.XML_SETTINGS_FILE))
			
			self.os.rename(self.XML_SETTINGS_FILE, "{0}.bak".format(self.XML_SETTINGS_FILE))
			self.writeXMLSettings()
	
	def cBool(self, value):
		if str(value).lower() in ("true", "1"):
			return True
			
		elif str(value).lower() in ("false", "0"):
			return False
			
		else:
			raise Exception("Value cannot be converted to boolean.")
	
	def connect(self):
		self.log.debug("Starting...")
		
		
		self.db = Database(self.POSTGRESQL_SERVER, self.POSTGRESQL_DATABASE, self.POSTGRESQL_USERNAME, self.POSTGRESQL_PASSWORD)
		self.mq = MQ(self.MQ_HOSTNAME, self.MQ_PORT, self.MQ_USERNAME, self.MQ_PASSWORD, self.MQ_VIRTUAL_HOST, self.MQ_EXCHANGE_NAME, self.MQ_EXCHANGE_TYPE, self.MQ_ROUTING_KEY, self.MQ_DURABLE, self.MQ_NO_ACK_MESSAGES, self.MQ_REPLY_TO, self.onEventReceived)
	
	def constructMessage(self, event_name, details):
		h = {
			"PluginFilename": self.PLUGIN_FILENAME,
			"EventName": event_name
		}
		
		
		return [h, self.json.dumps(details)]
	
	def getScriptPath(self):
		raise Exception("Please override this function in the plugin with: -\n\nreturn self.os.path.realpath(__file__)")
	
	def ifNoneReturnZero(self, strinput):
		if strinput is None:
			return 0
		
		else:
			return strinput
	
	def onEventReceived(self, basic_deliver, properties, body):
		self.log.debug("Starting...")
	
	def readXMLExtensibleSettings(self):
		self.log.debug("Starting...")
		
		
		if self.os.path.exists(self.XML_EXTENSIBLE_SETTINGS_FILE):
			xmldoc = self.minidom.parse(self.XML_EXTENSIBLE_SETTINGS_FILE)
			
			myvars = xmldoc.getElementsByTagName("Setting")
			
			for var in myvars:
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					# Now put the correct values to correct key
					if key == "PostgreSQLDatabase":
						self.POSTGRESQL_DATABASE = val
						
					elif key == "PostgreSQLPassword":
						self.POSTGRESQL_PASSWORD = val
						
					elif key == "PostgreSQLServer":
						self.POSTGRESQL_SERVER = val
						
					elif key == "PostgreSQLUsername":
						self.POSTGRESQL_USERNAME = val
						
					elif key == "MQDurable":
						self.MQ_DURABLE = self.cBool(val)
						
					elif key == "MQExchangeName":
						self.MQ_EXCHANGE_NAME = val
						
					elif key == "MQExchangeType":
						self.MQ_EXCHANGE_TYPE = val
						
					elif key == "MQHostname":
						self.MQ_HOSTNAME = val
						
					elif key == "MQNoAckMessages":
						self.MQ_NO_ACK_MESSAGES = self.cBool(val)
						
					elif key == "MQPassword":
						self.MQ_PASSWORD = val
						
					elif key == "MQPort":
						self.MQ_PORT = int(val)
						
					elif key == "MQReplyTo":
						self.MQ_REPLY_TO = val
						
					elif key == "MQRoutingKey":
						self.MQ_ROUTING_KEY = val
						
					elif key == "MQUsername":
						self.MQ_USERNAME = val
						
					elif key == "MQVirtualHost":
						self.MQ_VIRTUAL_HOST = val
						
					else:
						self.log.warn("XML setting attribute \"{0}\" isn't known.  Ignoring...".format(key))
	
	def readXMLSettings(self):
		self.log.debug("Starting...")
	
	def start(self, use_threading = True):
		self.log.debug("Starting...")
		
		
		if self.ENABLED:
			self.connect()
			self.updateDatabase()
			
			if self.MQ_RX_ENABLED:
				if use_threading:
					t = self.threading.Thread(target = self.mq.start)
					t.setDaemon(1)
					t.start()
					
				else:
					self.mq.start()
	
	def stop(self):
		self.log.debug("Starting...")
		
		
		if self.ENABLED and self.MQ_RX_ENABLED:
			self.mq.stop()
	
	def updateDatabase(self):
		self.log.debug("Starting...")
	
	def writeXMLSettings(self):
		self.log.debug("Starting...")
