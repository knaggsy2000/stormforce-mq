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
# StormForce MQ Server                            #
###################################################
# Version:     v0.2.0                             #
###################################################

from danlog import DanLog
from smq_shared import Database, MQ


###########
# Classes #
###########
class SMQExtensible():
	def __init__(self, path, name):
		import os
		import sys
		
		
		self.name = name
		self.os = os
		self.path = path
		self.plugin = None
		self.sys = sys
		
	def start(self):
		self.sys.path.append("hardware")
		self.sys.path.append("plugins")
		
	def stop(self):
		if self.plugin is not None:
			self.plugin.stop()

class SMQExtensibleAsProcess():
	def __init__(self, path, name):
		import os
		import subprocess
		
		
		self.name = name
		self.os = os
		self.path = path
		self.plugin = None
		self.subprocess = subprocess
		
	def start(self):
		self.plugin = self.subprocess.Popen(["python", self.os.path.join(self.path, self.name)])
		
	def stop(self):
		if self.plugin is not None:
			self.plugin.terminate()

class SMQHardware(SMQExtensible):
	def start(self):
		SMQExtensible.start(self)
		
		
		self.plugin = __import__("{0}".format(self.os.path.splitext(self.name)[0])).Hardware()
		self.plugin.start()

class SMQHardwareAsProcess(SMQExtensibleAsProcess):
	def start(self):
		SMQExtensibleAsProcess.start(self)

class SMQPlugin(SMQExtensible):
	def start(self):
		SMQExtensible.start(self)
		
		
		self.plugin = __import__("{0}".format(self.os.path.splitext(self.name)[0])).Plugin()
		self.plugin.start()

class SMQPluginAsProcess(SMQExtensibleAsProcess):
	def start(self):
		SMQExtensibleAsProcess.start(self)

class SMQServer():
	def __init__(self):
		from datetime import datetime
		from xml.dom import minidom
		
		import os
		import sys
		import threading
		import time
		
		
		self.db = None # Initialised in main()
		self.datetime = datetime
		self.hardware = []
		self.log = DanLog("SMQServer")
		self.minidom = minidom
		self.os = os
		self.plugins = []
		self.sys = sys
		self.threading = threading
		self.time = time
		
		
		self.DB_VERSION = 1000
		
		self.HARDWARE_AS_PROCESS = False
		
		self.MQ_DURABLE = True # Fixed
		self.MQ_EVENTS_HARDWARE = "events.hardware"
		self.MQ_EVENTS_PLUGIN = "events.plugin"
		self.MQ_EXCHANGE_NAME = "StormForce.MQ.Server"
		self.MQ_EXCHANGE_TYPE = "topic" # Fixed
		self.MQ_HOSTNAME = "localhost"
		self.MQ_NO_ACK_MESSAGES = False # Fixed
		self.MQ_PASSWORD = "guest"
		self.MQ_PORT = 5672
		self.MQ_REPLY_TO = "" # Fixed
		self.MQ_ROUTING_KEY = "" # Fixed
		self.MQ_USERNAME = "guest"
		self.MQ_VIRTUAL_HOST = "/"
		
		self.PLUGINS_AS_PROCESS = False
		self.POSTGRESQL_DATABASE = "stormforce_mq"
		self.POSTGRESQL_PASSWORD = ""
		self.POSTGRESQL_SERVER = "localhost"
		self.POSTGRESQL_USERNAME = "stormforce"
		
		self.XML_SETTINGS_FILE = "smqserver-settings.xml"
	
	def cBool(self, value):
		if str(value).lower() in ("true", "1"):
			return True
			
		elif str(value).lower() in ("false", "0"):
			return False
			
		else:
			raise Exception("Value cannot be converted to boolean.")
	
	def exitProgram(self):
		self.log.info("Exiting...")
		
		
		self.sys.exit(0)
	
	def ifNoneReturnZero(self, strinput):
		if strinput is None:
			return 0
		
		else:
			return strinput
	
	def iif(self, testval, trueval, falseval):
		if testval:
			return trueval
		
		else:
			return falseval
	
	def main(self):
		self.log.debug("Starting...")
		
		
		print """
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
"""
		self.log.info("")
		self.log.info("StormForce MQ - Server")
		self.log.info("======================")
		self.log.info("Checking settings...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.warn("The XML settings file doesn't exist, create one...")
			
			self.xmlSettingsWrite()
			
			
			self.log.info("The XML settings file has been created using the default settings.  Please edit it and restart the server once you're happy with the settings.")
			
			exitProgram()
			
		else:
			self.log.info("Reading XML settings...")
			
			self.xmlSettingsRead()
			
			# This will ensure it will have any new settings in
			if self.os.path.exists("{0}.bak".format(self.XML_SETTINGS_FILE)):
				self.os.unlink("{0}.bak".format(self.XML_SETTINGS_FILE))
				
			self.os.rename(self.XML_SETTINGS_FILE, "{0}.bak".format(self.XML_SETTINGS_FILE))
			self.xmlSettingsWrite()
		
		
		self.log.info("Setting up database...")
		self.db = Database(self.POSTGRESQL_SERVER, self.POSTGRESQL_DATABASE, self.POSTGRESQL_USERNAME, self.POSTGRESQL_PASSWORD)
		
		self.updateDatabase()
		
		
		self.log.info("Creating extensible settings...")
		self.xmlExtensibleWrite("hardware")
		self.xmlExtensibleWrite("plugins")
		
		
		self.log.info("Configuring plugins...")
		
		for root, dirs, files in self.os.walk("plugins", topdown = False):
			files.sort()
			
			for f in files:
				fs = self.os.path.splitext(f)
				
				if fs[0] <> "plugin_core_base" and fs[1] == ".py":
					try:
						self.log.info("Configuring plugin {0}...".format(f))
						
						
						p = None
						
						if self.PLUGINS_AS_PROCESS:
							p = SMQPluginAsProcess(root, f)
							
						else:
							p = SMQPlugin(root, f)
						
						p.start()
						
						if self.PLUGINS_AS_PROCESS:
							self.plugins.append(p)
							
							self.log.info("Plugin {0} has been started successfully.".format(f))
							
						else:
							if p.plugin.ENABLED:
								self.plugins.append(p)
								
								self.log.info("Plugin {0} has been started successfully.".format(f))
								
							else:
								self.log.warn("Plugin {0} is currently disabled.".format(f))
						
					except Exception, ex:
						self.log.error("An error has occurred while initialising plugin {0}.".format(f))
						self.log.error(ex)
			
			break
		
		
		self.log.info("Configuring hardware...")
		
		for root, dirs, files in self.os.walk("hardware", topdown = False):
			files.sort()
			
			for f in files:
				fs = self.os.path.splitext(f)
				
				if fs[0] <> "hardware_core_base" and fs[1] == ".py":
					try:
						self.log.info("Configuring hardware {0}...".format(f))
						
						
						p = None
						
						if self.HARDWARE_AS_PROCESS:
							p = SMQHardwareAsProcess(root, f)
							
						else:
							p = SMQHardware(root, f)
						
						p.start()
						
						if self.HARDWARE_AS_PROCESS:
							self.hardware.append(p)
							
							self.log.info("Hardware {0} has been started successfully.".format(f))
							
						else:
							if p.plugin.ENABLED:
								self.hardware.append(p)
								
								self.log.info("Hardware {0} has been started successfully.".format(f))
								
							else:
								self.log.warn("Hardware {0} is currently disabled.".format(f))
						
					except Exception, ex:
						self.log.error("An error has occurred while initialising hardware {0}.".format(f))
						self.log.error(ex)
			
			break
		
		
		self.log.info("Plugins enabled ({:d}): -".format(len(self.plugins)))
		
		for p in self.plugins:
			if self.PLUGINS_AS_PROCESS:
				self.log.info("    {0}".format(p.name))
				
			else:
				self.log.info("    {0}".format(p.plugin.PLUGIN_FILENAME))
		
		
		self.log.info("Hardware enabled ({:d}): -".format(len(self.hardware)))
		
		for p in self.hardware:
			if self.HARDWARE_AS_PROCESS:
				self.log.info("    {0}".format(p.name))
				
			else:
				self.log.info("    {0}".format(p.plugin.PLUGIN_FILENAME))
		
		
		self.log.info("Backgrounding...")
		
		try:
			while len(self.hardware) > 0 or len(self.plugins) > 0:
				self.time.sleep(1.)
			
		except KeyboardInterrupt:
			pass
			
		except Exception, ex:
			self.log.error("An error has occurred while running in the background.")
			self.log.error(ex)
			
		finally:
			self.log.warn("The background loop has stopped.")
			
			
			self.log.warn("Informing hardware to stop...")
			
			for p in self.hardware:
				try:
					if self.HARDWARE_AS_PROCESS:
						self.log.info("Stopping hardware {0}...".format(p.name))
						
					else:
						self.log.info("Stopping hardware {0}...".format(p.plugin.PLUGIN_FILENAME))
					
					p.stop()
					
				except Exception, ex:
					self.log.error("An error has occurred while stopping the hardware.")
					self.log.error(ex)
			
			
			self.log.warn("Informing plugins to stop...")
			
			for p in self.plugins:
				try:
					if self.PLUGINS_AS_PROCESS:
						self.log.info("Stopping plugin {0}...".format(p.name))
						
					else:
						self.log.info("Stopping plugin {0}...".format(p.plugin.PLUGIN_FILENAME))
					
					p.stop()
					
				except Exception, ex:
					self.log.error("An error has occurred while stopping the plugin.")
					self.log.error(ex)
			
			
			self.exitProgram()
	
	def updateDatabase(self):
		self.log.debug("Starting...")
		
		
		myconn = []
		self.db.connectToDatabase(myconn)
		
		
		##########
		# Tables #
		##########
		self.log.info("Creating tables...")
		
		
		# tblSystem
		self.log.debug("TABLE: tblSystem")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblSystem"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblSystem", "DatabaseVersion", "int"), conn = myconn)
		
		rowcount = int(self.ifNoneReturnZero(self.db.danLookup("COUNT(ID)", "tblSystem", "", conn = myconn)))
		
		if rowcount == 0:
			self.db.executeSQLCommand("INSERT INTO tblSystem(DatabaseVersion) VALUES(%(DatabaseVersion)s)", {"DatabaseVersion": 0}, myconn)
		
		
		
		###########
		# Updates #
		###########
		self.log.info("Updating data...")
		
		
		curr_db_version = int(self.ifNoneReturnZero(self.db.danLookup("DatabaseVersion", "tblSystem", "", conn = myconn)))
		
		if curr_db_version < self.DB_VERSION:
			# Update needed
			
			
			
			# Finally, update the db version
			self.db.executeSQLCommand("UPDATE tblSystem SET DatabaseVersion = %(DatabaseVersion)s", {"DatabaseVersion": self.DB_VERSION}, myconn)
		
		self.db.disconnectFromDatabase(myconn)
	
	def xmlExtensibleWrite(self, folder):
		self.log.debug("Starting...")
		
		
		f = self.os.path.join(folder, "smq_extensible.xml")
		
		if self.os.path.exists(f):
			self.os.unlink(f)
		
		if not self.os.path.exists(f):
			xmldoc = self.minidom.Document()
			
			# Create header
			settings = xmldoc.createElement("SMQExtensible")
			xmldoc.appendChild(settings)
			
			# Write each of the details one at a time, makes it easier for someone to alter the file using a text editor
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLServer", str(self.POSTGRESQL_SERVER))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLDatabase", str(self.POSTGRESQL_DATABASE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLUsername", str(self.POSTGRESQL_USERNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLPassword", str(self.POSTGRESQL_PASSWORD))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQDurable", str(self.MQ_DURABLE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQExchangeName", str(self.MQ_EXCHANGE_NAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQExchangeType", str(self.MQ_EXCHANGE_TYPE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQHostname", str(self.MQ_HOSTNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQNoAckMessages", str(self.MQ_NO_ACK_MESSAGES))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQPassword", str(self.MQ_PASSWORD))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQPort", str(self.MQ_PORT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQReplyTo", str(self.MQ_REPLY_TO))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			
			if folder.lower() == "hardware":
				var.setAttribute("MQRoutingKey", str(self.MQ_EVENTS_HARDWARE))
				
			else:
				var.setAttribute("MQRoutingKey", str(self.MQ_EVENTS_PLUGIN))
			
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQUsername", str(self.MQ_USERNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQVirtualHost", str(self.MQ_VIRTUAL_HOST))
			settings.appendChild(var)
			
			
			# Finally, save to the file
			xmloutput = file(f, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()
	
	def xmlSettingsRead(self):
		self.log.debug("Starting...")
		
		
		if self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.parse(self.XML_SETTINGS_FILE)
			
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
						
					elif key == "MQHostname":
						self.MQ_HOSTNAME = val
						
					elif key == "MQPort":
						self.MQ_PORT = int(val)
						
					elif key == "MQUsername":
						self.MQ_USERNAME = val
						
					elif key == "MQPassword":
						self.MQ_PASSWORD = val
						
					elif key == "MQVirtualHost":
						self.MQ_VIRTUAL_HOST = val
						
					elif key == "MQExchangeName":
						self.MQ_EXCHANGE_NAME = val
						
					elif key == "HardwareAsProcess":
						self.HARDWARE_AS_PROCESS = self.cBool(val)
						
					elif key == "PluginsAsProcess":
						self.PLUGINS_AS_PROCESS = self.cBool(val)
						
					else:
						self.log.warn("XML setting attribute \"{0}\" isn't known.  Ignoring...".format(key))
	
	def xmlSettingsWrite(self):
		self.log.debug("Starting...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			
			# Create header
			settings = xmldoc.createElement("SMQServer")
			xmldoc.appendChild(settings)
			
			# Write each of the details one at a time, makes it easier for someone to alter the file using a text editor
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLServer", str(self.POSTGRESQL_SERVER))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLDatabase", str(self.POSTGRESQL_DATABASE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLUsername", str(self.POSTGRESQL_USERNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLPassword", str(self.POSTGRESQL_PASSWORD))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQHostname", str(self.MQ_HOSTNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQPort", str(self.MQ_PORT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQUsername", str(self.MQ_USERNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQPassword", str(self.MQ_PASSWORD))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQVirtualHost", str(self.MQ_VIRTUAL_HOST))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQExchangeName", str(self.MQ_EXCHANGE_NAME))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("HardwareAsProcess", str(self.HARDWARE_AS_PROCESS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PluginsAsProcess", str(self.PLUGINS_AS_PROCESS))
			settings.appendChild(var)
			
			
			# Finally, save to the file
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()



########
# Main #
########
if __name__ == "__main__":
	l = None
	
	try:
		l = DanLog("Main")
		l.info("Preparing...")
		
		smq = SMQServer()
		smq.main()
		smq = None
		
	except Exception, ex:
		if l is not None:
			l.fatal(str(ex))
			
		else:
			print "Exception: {0}".format(ex)
