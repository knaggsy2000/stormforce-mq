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
# StormForce Strike Counters Plugin               #
###################################################

from plugin_core_base import PluginBase


###########
# Classes #
###########
class Plugin(PluginBase):
	def __init__(self, filename, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		mq_routing_key = "{0}.core.strikecounters".format(mq_routing_key)
		
		PluginBase.__init__(self, filename, "StrikeCounters", database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to)
		
		
		self.MQ_RX_ENABLED = False
	
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
		
		
		one_sec = self.datetime.now() + self.timedelta(seconds = 1)
		
		while self.running:
			t = self.datetime.now()
			
			if t >= one_sec:
				try:
					myconn = []
					self.db.connectToDatabase(myconn)
					
					
					if (t.hour == 0 and t.minute == 0):
						# New day, reset grand counters
						self.log.info("New day has started, resetting grand counters...")
						
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseTotal = %(N)s, NoiseTotal = %(N)s, StrikesTotal = %(N)s, StrikesOutOfRange = %(N)s", {"N": 0}, myconn):
							self.log.warn("Unable to write the zero noise total into the database.")
					
					if t.second == 0:
						# Reset the per minute counters
						self.log.info("New minute has started, resetting minute counters...")
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseMinute = %(N)s, NoiseMinute = %(N)s, StrikesMinute = %(N)s", {"N": 0}, myconn):
							self.log.warn("Unable to write the zero noise minute into the database.")
						
						
						# Reset counters if excessive
						self.log.info("New minute has started, resetting counters if excessive...")
						
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesMinute = %(StrikesMinute)s WHERE StrikesMinute > %(MaxStrikes)s", {"StrikesMinute": 0, "MaxStrikes": 999}, myconn):
							self.log.warn("Unable to write the zero excessive strike minute into the database.")
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET NoiseMinute = %(NoiseMinute)s WHERE NoiseMinute > %(MaxNoise)s", {"NoiseMinute": 0, "MaxNoise": 999}, myconn):
							self.log.warn("Unable to write the zero excessive noise minute into the database.")
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesOutOfRange = %(StrikesOutOfRange)s WHERE StrikesOutOfRange > %(MaxOOR)s", {"StrikesOutOfRange": 0, "MaxOOR": 999}, myconn):
							self.log.warn("Unable to write the zero excessive strike out of range into the database.")
						
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseTotal = %(CloseTotal)s WHERE CloseTotal > %(MaxClose)s", {"CloseTotal": 0, "MaxClose": 999999}, myconn):
							self.log.warn("Unable to write the zero excessive close total into the database.")
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET NoiseTotal = %(NoiseTotal)s WHERE NoiseTotal > %(MaxNoise)s", {"NoiseTotal": 0, "MaxNoise": 999999}, myconn):
							self.log.warn("Unable to write the zero excessive noise total into the database.")
						
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesTotal = %(StrikesTotal)s WHERE StrikesTotal > %(MaxStrikes)s", {"StrikesTotal": 0, "MaxStrikes": 999999}, myconn):
							self.log.warn("Unable to write the zero excessive strike total into the database.")
					
					
					# Send out the current counters out
					self.log.info("Sending out the current counters...")
					
					
					rows = self.db.executeSQLQuery("SELECT CloseMinute, CloseTotal, NoiseMinute, NoiseTotal, StrikesMinute, StrikesTotal, StrikesOutOfRange FROM tblStrikeCounter LIMIT 1", conn = myconn)
					
					for row in rows:
						m = self.constructMessage("StrikeCounters", {"CloseMinute": row[0], "CloseTotal": row[1], "NoiseMinute": row[2], "NoiseTotal": row[3], "StrikesMinute": row[4], "StrikesTotal": row[5], "StrikesOutOfRange": row[6]})
						self.mq.publishMessage(m[1], headers = m[0])
						break
					
					
					self.db.disconnectFromDatabase(myconn)
				
				except Exception, ex:
					self.log.error("An error occurred while updating the strike counters.")
					self.log.error(ex)
					
				finally:
					one_sec = self.datetime.now() + self.timedelta(seconds = 1)
			
			
			self.time.sleep(0.1)
	
	def start(self):
		PluginBase.start(self)
		
		
		if self.ENABLED:
			self.log.info("Starting stike counters...")
			self.running = True
			
			
			myconn = []
			self.db.connectToDatabase(myconn)
			
			
			##########
			# Tables #
			##########
			self.log.info("Creating tables...")
			
			
			# tblStrikeCounter
			self.log.debug("TABLE: tblStrikeCounter")
			self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikeCounter CASCADE", conn = myconn)
			self.db.executeSQLCommand("CREATE TABLE tblStrikeCounter(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
			self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN CloseMinute int", conn = myconn)
			self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN CloseTotal int", conn = myconn)
			self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN NoiseMinute int", conn = myconn)
			self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN NoiseTotal int", conn = myconn)
			self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN StrikesMinute int", conn = myconn)
			self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN StrikesTotal int", conn = myconn)
			self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN StrikesOutOfRange int", conn = myconn)
			
			self.db.executeSQLCommand("INSERT INTO tblStrikeCounter(CloseMinute, CloseTotal, NoiseMinute, NoiseTotal, StrikesMinute, StrikesTotal, StrikesOutOfRange) VALUES(%(N)s, %(N)s, %(N)s, %(N)s, %(N)s, %(N)s, %(N)s)", {"N": 0}, myconn)
			
			
			self.db.disconnectFromDatabase(myconn)
			
			
			
			t = self.threading.Thread(target = self.run)
			t.setDaemon(1)
			t.start()
	
	def stop(self):
		PluginBase.stop(self)
		
		
		if self.ENABLED:
			self.running = False
	
	def writeXMLSettings(self):
		PluginBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("PluginStrikeCounters")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
			settings.appendChild(var)
			
			
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()
