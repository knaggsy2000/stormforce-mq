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
# StormForce LD-350 Hardware                      #
###################################################

from hardware_core_base import HardwareBase
from smq_shared import SentenceDevice


###########
# Classes #
###########
class Hardware(HardwareBase):
	def __init__(self, filename, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		self.CLOSE_DISTANCE = 15
		
		self.LD350_BITS = 8
		self.LD350_NAME = "Boltek LD-350"
		self.LD350_PARITY = "N"
		self.LD350_PORT = "/dev/ttyu0"
		self.LD350_SQUELCH = 0
		self.LD350_SPEED = 9600
		self.LD350_STOPBITS = 1
		self.LD350_USE_UNCORRECTED_STRIKES = False
		
		self.MAP_MATRIX_CENTRE = (300, 300)
		
		
		mq_routing_key = "{0}.core.ld350".format(mq_routing_key)
		
		HardwareBase.__init__(self, self.LD350_NAME, filename, "LD350", database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to)
	
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
						
					elif key == "LD350Bits":
						self.LD350_BITS = int(val)
						
					elif key == "LD350Parity":
						self.LD350_PARITY = val
						
					elif key == "LD350Port":
						self.LD350_PORT = val
						
					elif key == "LD350Squelch":
						self.LD350_SQUELCH = int(val)
						
					elif key == "LD350Speed":
						self.LD350_SPEED = int(val)
						
					elif key == "LD350StopBits":
						self.LD350_STOPBITS = int(val)
						
					elif key == "LD350UseUncorrectedStrikes":
						self.LD350_USE_UNCORRECTED_STRIKES = self.cBool(val)
						
					elif key == "CloseDistance":
						self.CLOSE_DISTANCE = int(val)
	
	def sentenceRX(self, sentence):
		self.log.debug("Starting...")
		
		
		try:
			myconn = []
			self.db.connectToDatabase(myconn)
			
			sentence = sentence.replace("\r", "").replace("\n", "")
			star_split = sentence.split("*")
			
			
			if sentence.startswith(self.device.LD_NOISE):
				# Noise
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET NoiseMinute = NoiseMinute + %(N)s, NoiseTotal = NoiseTotal + %(N)s", {"N": 1}, myconn):
					self.log.warn("Unable to write the noise minute into the database.")
					
				else:
					m = self.constructMessage(self.device.LD_NOISE, {})
					self.mq.publishMessage(m[1], headers = m[0])
				
			elif sentence.startswith(self.device.LD_STATUS):
				# Status update
				if len(star_split) == 2:
					data_split = star_split[0].split(",")
					
					if len(data_split) == 6:
						close_strikes = int(data_split[1])
						total_strikes = int(data_split[2])
						close_alarm = self.cBool(data_split[3])
						severe_alarm = self.cBool(data_split[4])
						gps_heading = float(data_split[5])
						
						
						# Update the alarm status
						if not self.db.executeSQLCommand("UPDATE tblUnitStatus SET CloseAlarm = %(CloseAlarm)s, SevereAlarm = %(SevereAlarm)s, ReceiverLastDetected = LOCALTIMESTAMP WHERE Hardware = %(Hardware)s", {"CloseAlarm": close_alarm, "SevereAlarm": severe_alarm, "Hardware": self.LD350_NAME}, myconn):
							self.log.warn("Unable to update the database with the unit status.")
							
						else:
							m = self.constructMessage(self.device.LD_STATUS, {"close_strikes": close_strikes, "total_strikes": total_strikes, "close_alarm": close_alarm, "severe_alarm": severe_alarm, "gps_heading": gps_heading})
							self.mq.publishMessage(m[1], headers = m[0])
				
			elif sentence.startswith(self.device.LD_STRIKE):
				# Strike
				if len(star_split) == 2:
					data_split = star_split[0].split(",")
					
					if len(data_split) == 4:
						strike_distance_corrected = int(data_split[1])
						strike_distance = int(data_split[2])
						strike_angle = float(data_split[3])
						strike_type = "CG"
						strike_polarity = ""
						
						# Use a bit of trignonmetry to get the X,Y co-ords
						#
						#        ^
						#       /|
						#      / |
						#  H  /  | O
						#    /   |
						#   /    |
						#  / )X  |
						# /-------
						#     A
						new_distance = 0.
						
						if self.LD350_USE_UNCORRECTED_STRIKES:
							new_distance = strike_distance
							
						else:
							new_distance = strike_distance_corrected
						
						o = self.math.sin(self.math.radians(strike_angle)) * float(new_distance)
						a = self.math.cos(self.math.radians(strike_angle)) * float(new_distance)
						
						screen_x = int(self.MAP_MATRIX_CENTRE[0] + o)
						screen_y = int(self.MAP_MATRIX_CENTRE[1] + -a)
						
						
						if not self.db.executeSQLCommand("INSERT INTO tblLD350Strikes(X, Y, DateTimeOfStrike, CorrectedStrikeDistance, UncorrectedStrikeDistance, StrikeAngle, StrikeType, StrikePolarity) VALUES(%(X)s, %(Y)s, LOCALTIMESTAMP, %(CorrectedStrikeDistance)s, %(UncorrectedStrikeDistance)s, %(StrikeAngle)s, %(StrikeType)s, %(StrikePolarity)s)", {"X": screen_x, "Y": screen_y, "CorrectedStrikeDistance": strike_distance_corrected, "UncorrectedStrikeDistance": strike_distance, "StrikeAngle": strike_angle, "StrikeType": "CG", "StrikePolarity": ""}, myconn):
							self.log.warn("Unable to write the strike into the database.")
							
						else:
							m = self.constructMessage(self.device.LD_STRIKE, {"screen_x": screen_x, "screen_y": screen_y, "strike_distance_corrected": strike_distance_corrected, "strike_distance": strike_distance, "strike_angle": strike_angle, "strike_type": strike_type, "strike_polarity": strike_polarity})
							self.mq.publishMessage(m[1], headers = m[0])
						
						
						if new_distance <= 300.:
							if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesMinute = StrikesMinute + %(N)s, StrikesTotal = StrikesTotal + %(N)s", {"N": 1}, myconn):
								self.log.warn("Unable to write the strike into the database.")
							
							
							if new_distance <= self.CLOSE_DISTANCE:
								if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseMinute = CloseMinute + %(N)s, CloseTotal = CloseTotal + %(N)s", {"N": 1}, myconn):
									self.log.warn("Unable to write the close strike into the database.")
							
						else:
							if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesOutOfRange = StrikesOutOfRange + %(N)s", {"N": 1}, myconn):
								self.log.warn("Unable to write the out of range strike into the database.")
			
			self.db.disconnectFromDatabase(myconn)
			
		except Exception, ex:
			self.log.error("An error has occurred while receiving the sentence.")
			self.log.error(ex)
	
	def start(self):
		HardwareBase.start(self)
		
		
		if self.ENABLED:
			self.log.info("Setting up EFM-350...")
			
			self.device = LD350(self.log, self.LD350_PORT, self.LD350_SPEED, self.LD350_BITS, self.LD350_PARITY, self.LD350_STOPBITS, self.LD350_SQUELCH, self.sentenceRX)
			
			
			myconn = []
			self.db.connectToDatabase(myconn)
			
			
			##########
			# Tables #
			##########
			self.log.info("Creating tables...")
			
			
			# tblLD350Strikes
			self.log.debug("TABLE: tblLD350Strikes")
			self.db.executeSQLCommand(self.db.createTableSQLString("tblLD350Strikes"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "X", "smallint"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "Y", "smallint"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "DateTimeOfStrike", "timestamp"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "CorrectedStrikeDistance", "decimal(6,3)"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "UncorrectedStrikeDistance", "decimal(6,3)"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "StrikeType", "varchar(2)"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "StrikePolarity", "varchar(1)"), conn = myconn)
			self.db.executeSQLCommand(self.db.addColumnSQLString("tblLD350Strikes", "StrikeAngle", "decimal(4,1)"), conn = myconn)
			
			
			self.db.executeSQLCommand("INSERT INTO tblUnitStatus(Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected) VALUES(%(Hardware)s, %(SquelchLevel)s, %(UseUncorrectedStrikes)s, %(CloseAlarm)s, %(SevereAlarm)s, NULL)", {"Hardware": self.LD350_NAME, "SquelchLevel": self.LD350_SQUELCH, "UseUncorrectedStrikes": self.LD350_USE_UNCORRECTED_STRIKES, "CloseAlarm": False, "SevereAlarm": False}, myconn)
			
			
			
			#########
			# Views #
			#########
			self.log.info("Creating views...")
			
			
			self.db.executeSQLCommand("DROP VIEW IF EXISTS vwLD350StrikesPersistence CASCADE", conn = myconn)
			self.db.executeSQLCommand("DROP VIEW IF EXISTS vwLD350StrikesSummaryByMinute CASCADE", conn = myconn)
			
			self.log.debug("VIEW: vwLD350StrikesPersistence")
			self.db.executeSQLCommand("""CREATE VIEW vwLD350StrikesPersistence AS
SELECT ID, X, Y, DateTimeOfStrike, CAST(EXTRACT(epoch from (LOCALTIMESTAMP - DateTimeOfStrike)) AS smallint) AS StrikeAge
FROM tblLD350Strikes
WHERE DateTimeOfStrike >= LOCALTIMESTAMP - INTERVAL '1 HOUR' AND DateTimeOfStrike >= (SELECT ServerStarted FROM tblServerDetails LIMIT 1)""", conn = myconn)
		
			self.log.debug("VIEW: vwLD350StrikesSummaryByMinute")
			self.db.executeSQLCommand("""CREATE VIEW vwLD350StrikesSummaryByMinute AS
SELECT CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp) AS Minute, ((CAST(EXTRACT(epoch from (CAST(to_char(LOCALTIMESTAMP, 'YYYY/MM/DD HH24:MI:00') AS timestamp) - CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp))) AS smallint)) / 60) AS StrikeAge, COUNT(ID) AS NumberOfStrikes
FROM vwLD350StrikesPersistence
GROUP BY CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp), ((CAST(EXTRACT(epoch from (CAST(to_char(CAST(to_char(LOCALTIMESTAMP, 'YYYY/MM/DD HH24:MI:00') AS timestamp), 'YYYY/MM/DD HH24:MI:00') AS timestamp) - CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp))) AS smallint)) / 60)""", conn = myconn)
			
			
			
			###########
			# Indices #
			###########
			self.log.info("Indices...")
			
			self.log.debug("INDEX: tblLD350Strikes_X_Y")
			self.db.executeSQLCommand(self.db.createIndexSQLString("tblLD350Strikes_X_Y", "tblLD350Strikes", "X, Y"), conn = myconn)
			
			self.log.debug("INDEX: tblLD350Strikes_DateTimeOfStrike")
			self.db.executeSQLCommand(self.db.createIndexSQLString("tblLD350Strikes_DateTimeOfStrike", "tblLD350Strikes", "DateTimeOfStrike"), conn = myconn)
			
			
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
			settings = xmldoc.createElement("HardwareLD350")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD350Port", str(self.LD350_PORT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD350Speed", str(self.LD350_SPEED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD350Bits", str(self.LD350_BITS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD350Parity", str(self.LD350_PARITY))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD350StopBits", str(self.LD350_STOPBITS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD350Squelch", str(self.LD350_SQUELCH))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD350UseUncorrectedStrikes", str(self.LD350_USE_UNCORRECTED_STRIKES))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("CloseDistance", str(self.CLOSE_DISTANCE))
			settings.appendChild(var)
			
			
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()

class LD350(SentenceDevice):
	#
	# LD sentence key:
	#
	# <bbb.b> = bearing to strike 0-359.9 degrees
	# <ccc>   = close strike rate 0-999 strikes/minute
	# <ca>    = close alarm status (0 = inactive, 1 = active)
	# <cs>    = checksum
	# <ddd>   = corrected strike distance (0-300 miles)
	# <hhh.h> = current heading from GPS/compass
	# <sa>    = severe alarm status (0 = inactive, 1 = active)
	# <ldns1> = lightning network 1 connection state
	# <ldns2> = lightning network 2 connection state
	# <sss>   = total strike rate 0-999 strikes/minute
	# <uuu>   = uncorrected strike distance (0-300 miles)
	def __init__(self, log, port, speed, bits, parity, stopbits, squelch = 0, trigger_sub = None):
		SentenceDevice.__init__(self, port, speed, bits, parity, stopbits, trigger_sub)
		
		
		self.log = log
		self.squelch = int(squelch)
		
		self.LD_NOISE  = "$WIMLN" # $WIMLN*<cs>
		self.LD_STATUS = "$WIMSU" # $WIMSU,<ccc>,<sss>,<ca>,<sa>,<ldns1>,<ldns2>,<hhh.h>*<cs>
		self.LD_STRIKE = "$WIMLI" # $WIMLI,<ddd>,<uuu>,<bbb.b>*<cs>
		
		
		# Setup everything we need
		self.log.info("Initialising LD-350...")
		
		self.setupUnit(port, speed, bits, parity, stopbits)
		self.start()
	
	def setupUnit(self, port, speed, bits, parity, stopbits):
		self.log.debug("Running...")
		
		
		import serial
		
		
		self.serial = serial.Serial()
		self.serial.baudrate = speed
		self.serial.bytesize = bits
		self.serial.parity = parity
		self.serial.port = port
		self.serial.stopbits = stopbits
		self.serial.timeout = 10.
		self.serial.writeTimeout = None
		self.serial.xonxoff = None
		
		self.serial.open()
		
		self.serial.flushInput()
		self.serial.flushOutput()
		
		
		# Attempt to set the squelch
		self.log.info("Setting squelch...")
		
		
		ok = False
		
		for x in xrange(0, 3):
			self.serial.write("SQ{:d}\r".format(self.squelch))
			self.serial.flush()
			
			o = self.serial.readline().replace("\r", "").replace("\n", "")
			
			if o.startswith(":SQUELCH {:d} (0-100)".format(self.squelch)):
				ok = True
				break
		
		if not ok:
			self.log.warn("The squelch doesn't appear to have been set.")
