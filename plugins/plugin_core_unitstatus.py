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
# StormForce Unit Status Plugin                   #
###################################################

from plugin_core_base import PluginBase


###########
# Classes #
###########
class Plugin(PluginBase):
	def __init__(self):
		PluginBase.__init__(self)
		
		
		self.MQ_ROUTING_KEY = "{0}.core.unitstatus".format(self.MQ_ROUTING_KEY)
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
	
	def run(self):
		self.log.debug("Starting...")
		
		
		five_sec = self.datetime.now() + self.timedelta(seconds = 5)
		
		while self.running:
			t = self.datetime.now()
			
			if t >= five_sec:
				try:
					myconn = []
					self.db.connectToDatabase(myconn)
					
					rows = self.db.executeSQLQuery("SELECT Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected, ReceiverLost FROM vwUnitStatus ORDER BY Hardware", conn = myconn)
					
					self.db.disconnectFromDatabase(myconn)
					
					
					ret = []
					
					for row in rows:
						ret.append({"Hardware": row[0], "SquelchLevel": row[1], "UseUncorrectedStrikes": row[2], "CloseAlarm": row[3], "SevereAlarm": row[4], "ReceiverLastDetected": str(row[5]), "ReceiverLost": row[6]})
					
					
					# Send out the current counters out
					self.log.info("Sending out the unit status...")
					
					m = self.constructMessage("UnitStatus", ret)
					self.mq.publishMessage(m[1], headers = m[0])
					
				
				except Exception, ex:
					self.log.error("An error occurred while updating the strike counters.")
					self.log.error(ex)
					
				finally:
					five_sec = self.datetime.now() + self.timedelta(seconds = 5)
			
			
			self.time.sleep(0.1)
	
	def start(self, use_threading = True):
		PluginBase.start(self, use_threading)
		
		
		if self.ENABLED:
			self.log.info("Starting unit status...")
			
			if use_threading:
				t = self.threading.Thread(target = self.run)
				t.setDaemon(1)
				t.start()
				
			else:
				self.run()
	
	def stop(self):
		PluginBase.stop(self)
		
		
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
		
		
		# tblUnitStatus
		self.log.debug("TABLE: tblUnitStatus")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblUnitStatus CASCADE", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblUnitStatus(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN Hardware varchar(20)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN SquelchLevel smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN UseUncorrectedStrikes boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN CloseAlarm boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN SevereAlarm boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN ReceiverLastDetected timestamp", conn = myconn)
		
		
		
		#########
		# Views #
		#########
		self.log.info("Creating views...")
		
		
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwUnitStatus CASCADE", conn = myconn)
		
		
		self.log.debug("VIEW: vwUnitStatus")
		self.db.executeSQLCommand("""CREATE VIEW vwUnitStatus AS
SELECT ID, Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected, (CASE WHEN ReceiverLastDetected IS NULL THEN TRUE ELSE (CASE WHEN EXTRACT(epoch from (LOCALTIMESTAMP - ReceiverLastDetected)) >= 5 THEN TRUE ELSE FALSE END) END) AS ReceiverLost
FROM tblUnitStatus""", conn = myconn)
		
		
		self.db.disconnectFromDatabase(myconn)
	
	def writeXMLSettings(self):
		PluginBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("PluginUnitStatus")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
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
