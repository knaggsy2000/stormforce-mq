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
# StormForce Server Details Plugin                #
###################################################

from plugin_core_base import PluginBase
from smq_shared import MQ


###########
# Classes #
###########
class Plugin(PluginBase):
	def __init__(self):
		self.SERVER_COPYRIGHT = "(c)2008-2012, 2014, 2016 - Daniel Knaggs"
		self.SERVER_NAME = "StormForce MQ"
		self.SERVER_VERSION = "0.2.0"
		self.STRIKE_COPYRIGHT = "Lightning Data (c) 2016 - Daniel Knaggs"
		
		self.UPDATE_PERIOD = 1.
		
		
		PluginBase.__init__(self)
		
		self.MQ_ROUTING_KEY = "{0}.core.serverdetails".format(self.MQ_ROUTING_KEY)
		self.MQ_RX_ENABLED = False
	
	def getScriptPath(self):
		return self.os.path.realpath(__file__)
	
	def readXMLSettings(self):
		PluginBase.readXMLSettings(self)
		
		
		if self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.parse(self.XML_SETTINGS_FILE)
			
			myvars = xmldoc.getElementsByTagName("Setting")
			
			for var in myvars:
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "Enabled":
						self.ENABLED = self.cBool(val)
						
					elif key == "StrikeCopyright":
						self.STRIKE_COPYRIGHT = val
						
					elif key == "UpdatePeriod":
						self.UPDATE_PERIOD = float(val)
	
	def run(self):
		self.log.debug("Starting...")
		
		
		time_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD)
		
		while self.running:
			t = self.datetime.now()
			
			
			if t >= time_wait:
				try:
					myconn = []
					self.db.connectToDatabase(myconn)
					
					rows = self.db.executeSQLQuery("SELECT ServerStarted, DATE_PART('epoch', ServerStarted) AS ServerStartedUT, DATE_PART('epoch', LOCALTIMESTAMP) - DATE_PART('epoch', ServerStarted) AS ServerUptime, ServerApplication, ServerCopyright, ServerVersion, StrikeCopyright FROM tblServerDetails LIMIT 1", conn = myconn)
					
					self.db.disconnectFromDatabase(myconn)
					
					
					# Send out the server details
					self.log.info("Sending out the server details...")
					
					for row in rows:
						m = self.constructMessage("ServerDetails", {"ServerStarted": str(row[0]), "ServerStartedUT": row[1], "ServerUptime": row[2], "ServerApplication": row[3], "ServerCopyright": row[4], "ServerVersion": row[5], "StrikeCopyright": row[6]})
						self.mq.publishMessage(m[1], headers = m[0])
						break
					
				except Exception, ex:
					self.log.error("An error occurred while running the current time.")
					self.log.error(ex)
					
				finally:
					time_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD)
			
			
			self.time.sleep(0.1)
	
	def start(self, use_threading = True):
		PluginBase.start(self, use_threading)
		
		
		if self.ENABLED:
			self.log.info("Starting server details...")
			self.running = True
			
			if use_threading:
				t = self.threading.Thread(target = self.run)
				t.setDaemon(1)
				t.start()
				
			else:
				self.run()
	
	def stop(self):
		if self.ENABLED:
			self.running = False
	
	def updateDatabase(self):
		PluginBase.updateDatabase(self)
		
		
		myconn = []
		self.db.connectToDatabase(myconn)
		
		
		##########
		# Tables #
		##########
		self.log.info("Creating tables...")
		
		
		# tblServerDetails
		self.log.debug("TABLE: tblServerDetails")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblServerDetails CASCADE", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblServerDetails(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerStarted timestamp", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerApplication varchar(20)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerCopyright varchar(100)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerVersion varchar(8)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN StrikeCopyright varchar(100)", conn = myconn)
		
		self.db.executeSQLCommand("INSERT INTO tblServerDetails(ServerStarted, ServerApplication, ServerCopyright, ServerVersion, StrikeCopyright) VALUES(LOCALTIMESTAMP, %(ServerApplication)s, %(ServerCopyright)s, %(ServerVersion)s, %(StrikeCopyright)s)", {"ServerApplication": self.SERVER_NAME, "ServerCopyright": self.SERVER_COPYRIGHT, "ServerVersion": self.SERVER_VERSION, "StrikeCopyright": self.STRIKE_COPYRIGHT}, myconn)
		
		
		self.db.disconnectFromDatabase(myconn)
	
	def writeXMLSettings(self):
		PluginBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("PluginServerDetails")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("StrikeCopyright", str(self.STRIKE_COPYRIGHT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriod", str(self.UPDATE_PERIOD))
			settings.appendChild(var)
			
			
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()



########
# Main #
########
if __name__ == "__main__":
	try:
		p = Plugin()
		p.start(use_threading = False)
		p = None
		
	except Exception, ex:
		print "Exception: {0}".format(ex)
