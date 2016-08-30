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
# StormForce EFM-100 Hardware                     #
###################################################

from hardware_core_base import HardwareBase
from smq_shared import SentenceDevice


###########
# Classes #
###########
class Hardware(HardwareBase):
	def __init__(self, filename, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		self.CLOSE_DISTANCE = 15
		
		self.EFM100_BITS = 8
		self.EFM100_NAME = "Boltek EFM-100"
		self.EFM100_PARITY = "N"
		self.EFM100_PORT = "/dev/ttyu0"
		self.EFM100_SPEED = 9600
		self.EFM100_STOPBITS = 1
		
		
		mq_routing_key = "{0}.core.efm100".format(mq_routing_key)
		
		HardwareBase.__init__(self, self.EFM100_NAME, filename, "EFM100", database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to)
	
	def readXMLSettings(self):
		HardwareBase.readXMLSettings(self)
		
		
		if self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.parse(self.XML_SETTINGS_FILE)
			
			myvars = xmldoc.getElementsByTagName("Setting")
			
			for var in myvars:
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					if key == "Enabled":
						self.ENABLED = self.cBool(val)
						
					elif key == "EFM100Bits":
						self.EFM100_BITS = int(val)
						
					elif key == "EFM100Parity":
						self.EFM100_PARITY = val
						
					elif key == "EFM100Port":
						self.EFM100_PORT = val
						
					elif key == "EFM100Speed":
						self.EFM100_SPEED = int(val)
						
					elif key == "EFM100StopBits":
						self.EFM100_STOPBITS = int(val)
	
	def sentenceRX(self, sentence):
		self.log.debug("Starting...")
		
		
		try:
			myconn = []
			self.db.connectToDatabase(myconn)
			
			sentence = sentence.replace("\r", "").replace("\n", "")
			star_split = sentence.split("*")
			
			
			if sentence.startswith(self.device.EFM_POSITIVE) or sentence.startswith(self.device.EFM_NEGATIVE):
				data_split = star_split[0].split(",")
				
				if len(data_split) == 2:
					electric_field_level = data_split[0]
					fault_present = self.cBool(data_split[1])
					
					
					efl = float(electric_field_level.replace("$", ""))
					
					if not self.db.executeSQLCommand("INSERT INTO tblEFM100ElectricFieldStrength(DateTimeOfMeasurement, kVm) VALUES(LOCALTIMESTAMP, %(kVm)s)", {"kVm": efl}, myconn):
						self.log.warn("Failed to write out the field strength to the database.")
						
					else:
						m = None
						
						if sentence.startswith(self.device.EFM_POSITIVE):
							m = self.constructMessage(self.device.EFM_POSITIVE, {"ElectricFieldLevel": efl, "FaultPresent": fault_present})
							
						elif sentence.startswith(self.device.EFM_NEGATIVE):
							m = self.constructMessage(self.device.EFM_NEGATIVE, {"ElectricFieldLevel": efl, "FaultPresent": fault_present})
						
						self.mq.publishMessage(m[1], headers = m[0])
					
					
					if not self.db.executeSQLCommand("UPDATE tblUnitStatus SET SevereAlarm = %(SevereAlarm)s, ReceiverLastDetected = LOCALTIMESTAMP WHERE Hardware = %(Hardware)s", {"SevereAlarm": fault_present, "Hardware": self.EFM100_NAME}, myconn):
						self.log.warn("Unable to update the database with the unit status.")
			
			self.db.disconnectFromDatabase(myconn)
			
		except Exception, ex:
			self.log.error("An error has occurred while receiving the sentence.")
			self.log.error(ex)
	
	def start(self):
		HardwareBase.start(self)
		
		
		if self.ENABLED:
			self.log.info("Setting up EFM-100...")
			
			self.device = EFM100(self.EFM100_PORT, self.EFM100_SPEED, self.EFM100_BITS, self.EFM100_PARITY, self.EFM100_STOPBITS, self.sentenceRX)
			
			
			myconn = []
			self.db.connectToDatabase(myconn)
			
			
			##########
			# Tables #
			##########
			self.log.info("Creating tables...")
			
			
			# tblEFM100ElectricFieldStrength
			self.log.debug("TABLE: tblEFM100ElectricFieldStrength")
			self.db.executeSQLCommand(self.db.createTableSQLString("tblEFM100ElectricFieldStrength"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblEFM100ElectricFieldStrength", "DateTimeOfMeasurement", "timestamp"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblEFM100ElectricFieldStrength", "kVm", "decimal(4,2)"), conn = myconn)
			
			
			self.db.executeSQLCommand("INSERT INTO tblUnitStatus(Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected) VALUES(%(Hardware)s, %(SquelchLevel)s, %(UseUncorrectedStrikes)s, %(CloseAlarm)s, %(SevereAlarm)s, NULL)", {"Hardware": self.EFM100_NAME, "SquelchLevel": 0, "UseUncorrectedStrikes": False, "CloseAlarm": False, "SevereAlarm": False}, myconn)
			
			
			
			###########
			# Indices #
			###########
			self.log.info("Indices...")
			
			self.log.debug("INDEX: tblEFM100ElectricFieldStrength_DateTimeOfMeasurement")
			self.db.executeSQLCommand(self.db.createIndexSQLString("tblEFM100ElectricFieldStrength_DateTimeOfMeasurement", "tblEFM100ElectricFieldStrength", "DateTimeOfMeasurement"), conn = myconn)
			
			
			self.db.disconnectFromDatabase(myconn)
	
	def stop(self):
		HardwareBase.stop(self)
		
		
		if self.ENABLED and self.device is not None:
			self.device.dispose()
			self.device = None
	
	def writeXMLSettings(self):
		HardwareBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("HardwareEFM100")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Port", str(self.EFM100_PORT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Speed", str(self.EFM100_SPEED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Bits", str(self.EFM100_BITS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Parity", str(self.EFM100_PARITY))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100StopBits", str(self.EFM100_STOPBITS))
			settings.appendChild(var)
			
			
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()

class EFM100(SentenceDevice):
	def __init__(self, port, speed, bits, parity, stopbits, trigger_sub = None):
		SentenceDevice.__init__(self, port, speed, bits, parity, stopbits, trigger_sub)
		
		
		self.log = DanLog("EFM100")
		
		self.EFM_NEGATIVE = "$-"
		self.EFM_POSITIVE = "$+"
		
		
		# Setup everything we need
		self.log.info("Initialising EFM-100...")
		
		self.setupUnit(port, speed, bits, parity, stopbits)
		self.start()
