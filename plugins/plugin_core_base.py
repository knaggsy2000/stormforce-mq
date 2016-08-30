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

from danlog import DanLog
from smq_shared import Database, MQ


###########
# Classes #
###########
class PluginBase():
	def __init__(self, plugin_filename, plugin_name, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		from datetime import datetime, timedelta
		from xml.dom import minidom
		
		import json
		import os
		import threading
		import time
		
		
		self.ENABLED = False
		
		self.MQ_RX_ENABLED = True
		
		self.PLUGIN_FILENAME = "{0}.py".format(plugin_filename)
		self.PLUGIN_NAME = plugin_name
		
		
		self.datetime = datetime
		self.db = Database(database_server, database_database, database_username, database_password)
		self.json = json
		self.log = DanLog("Plugin{0}".format(self.PLUGIN_NAME))
		self.minidom = minidom
		self.mq = MQ(mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to, self.onEventReceived)
		self.os = os
		self.running = False
		self.threading = threading
		self.time = time
		self.timedelta = timedelta
		
		
		self.XML_SETTINGS_FILE = self.os.path.join("plugins", "{0}.xml".format(plugin_filename))
		
		
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
	
	def constructMessage(self, event_name, details):
		h = {
			"PluginFilename": self.PLUGIN_FILENAME,
			"PluginName": self.PLUGIN_NAME,
			"EventName": event_name
		}
		
		
		return [h, self.json.dumps(details)]
	
	def ifNoneReturnZero(self, strinput):
		if strinput is None:
			return 0
		
		else:
			return strinput
	
	def onEventReceived(self, basic_deliver, properties, body):
		self.log.debug("Starting...")
	
	def readXMLSettings(self):
		self.log.debug("Starting...")
	
	def start(self):
		self.log.debug("Starting...")
		
		
		if self.ENABLED and self.MQ_RX_ENABLED:
			t = self.threading.Thread(target = self.mq.start)
			t.setDaemon(1)
			t.start()
	
	def stop(self):
		self.log.debug("Starting...")
		
		
		if self.ENABLED and self.MQ_RX_ENABLED:
			self.mq.stop()
	
	def writeXMLSettings(self):
		self.log.debug("Starting...")
