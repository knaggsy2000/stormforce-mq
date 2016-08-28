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
# StormForce Base Hardware                        #
###################################################

from danlog import DanLog
from smq_shared import Database, MQ


###########
# Classes #
###########
class HardwareBase():
	def __init__(self, hardware_friendly_name, hardware_filename, hardware_name, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		from datetime import datetime
		from xml.dom import minidom
		
		import json
		import math
		import os
		import threading
		import time
		
		
		self.ENABLED = False
		
		self.HARDWARE_FILENAME = "{0}.py".format(hardware_filename)
		self.HARDWARE_FRIENDLY_NAME = hardware_friendly_name
		self.HARDWARE_NAME = hardware_name
		
		
		self.datetime = datetime
		self.device = None
		self.db = Database(database_server, database_database, database_username, database_password)
		self.json = json
		self.log = DanLog("Hardware{0}".format(self.HARDWARE_NAME))
		self.math = math
		self.minidom = minidom
		self.mq = MQ(mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to, None)
		self.os = os
		self.threading = threading
		self.time = time
		
		
		self.XML_SETTINGS_FILE = self.os.path.join("hardware", "{0}.xml".format(hardware_filename))
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.warn("No XML settings have been found for the hardware, creating one...")
			self.writeXMLSettings()
		
		if self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.info("Reading XML settings for the hardware...")
			self.readXMLSettings()
	
	def cBool(self, value):
		if str(value).lower() in ("true", "1"):
			return True
			
		elif str(value).lower() in ("false", "0"):
			return False
			
		else:
			raise Exception("Value cannot be converted to boolean.")
	
	def constructMessage(self, event_name, details):
		h = {
			"HardwareFilename": self.HARDWARE_FILENAME,
			"HardwareName": self.HARDWARE_FRIENDLY_NAME,
			"EventName": event_name
		}
		
		
		return [h, self.json.dumps(details)]
	
	def ifNoneReturnZero(self, strinput):
		if strinput is None:
			return 0
		
		else:
			return strinput
	
	def readXMLSettings(self):
		self.log.debug("Starting...")
	
	def start(self):
		self.log.debug("Starting...")
	
	def stop(self):
		self.log.debug("Starting...")
	
	def writeXMLSettings(self):
		self.log.debug("Starting...")
