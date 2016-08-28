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
# StormForce SXR Plugin                           #
###################################################

from plugin_core_base import PluginBase
from smq_shared import Database
from twisted.web import xmlrpc



###########
# Classes #
###########
class Plugin(PluginBase):
	def __init__(self, filename, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		PluginBase.__init__(self, filename, "SXR", database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to)
		
		
		from twisted.internet import defer, reactor
		from twisted.web import resource, server
		
		
		self.twisted_internet_defer = defer
		self.twisted_internet_reactor = reactor
		self.twisted_web_resource = resource
		self.twisted_web_server = server
		
		
		self.MQ_RX_ENABLED = False
		
		self.SERVER_PORT = 7397
	
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
						
					elif key == "ServerPort":
						self.SERVER_PORT = int(val)
	
	def start(self):
		PluginBase.start(self)
		
		
		if self.ENABLED:
			self.log.info("Configuring XMLRPC server...")
			
			f = XRXMLRPCFunctions(self.db, self.log)
			xmlrpc.addIntrospection(f)
			
			s = self.twisted_web_resource.Resource()
			s.putChild("xmlrpc", f)
			
			
			self.log.info("Starting XMLRPC server...")
			
			self.twisted_internet_reactor.listenTCP(self.SERVER_PORT, self.twisted_web_server.Site(s))
			
			t = self.threading.Thread(target = self.twisted_internet_reactor.run, args = (False,))
			t.setDaemon(1)
			t.start()
	
	def stop(self):
		PluginBase.stop(self)
		
		
		if self.ENABLED:
			self.twisted_internet_reactor.stop()
	
	def writeXMLSettings(self):
		PluginBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("PluginSXR")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("ServerPort", str(self.SERVER_PORT))
			settings.appendChild(var)
			
			
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()

class XRXMLRPCFunctions(xmlrpc.XMLRPC):
	def __init__(self, db, log):
		xmlrpc.XMLRPC.__init__(self)
		
		
		from twisted.internet import threads
		from xml.dom import minidom
		from StringIO import StringIO
		
		import gzip
		import xmlrpclib
		
		
		self.db = db
		self.gzip = gzip
		self.log = log
		self.minidom = minidom
		self.stringio = StringIO
		self.twisted_internet_threads = threads
		self.xmlrpclib = xmlrpclib
	
	def compressData(self, data):
		dio = self.stringio()
		
		com = self.gzip.GzipFile(fileobj = dio, mode = "wb", compresslevel = 9)
		com.write(data)
		com.close()
		
		return self.xmlrpclib.Binary(dio.getvalue())
	
	
	def xmlrpc_fieldCounter(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT kVm FROM tblEFM100ElectricFieldStrength ORDER BY ID DESC LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("kVm", str(row[0]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_fieldCounter.help = "Returns the electric field strength from the Boltek EFM-100."
	xmlrpc_fieldCounter.signature = [["SXRDataSet[kVm]", "none"]]
	
	
	def xmlrpc_lastHourOfStrikesByMinute(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT Minute, StrikeAge, NumberOfStrikes FROM vwLD250StrikesSummaryByMinute ORDER BY Minute", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("Minute", str(row[0]))
				var.setAttribute("StrikeAge", str(row[1]))
				var.setAttribute("NumberOfStrikes", str(row[2]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_lastHourOfStrikesByMinute.help = "Returns the number of strikes in the last hour grouped per minute, the strike age is represented in minutes."
	xmlrpc_lastHourOfStrikesByMinute.signature = [["SXRDataSet[Minute, StrikeAge, NumberOfStrikes]", "none"]]
	
	
	def xmlrpc_serverDetails(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT ServerStarted, ServerApplication, ServerCopyright, ServerVersion, StrikeCopyright FROM tblServerDetails LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				self.log.info("Row...")
				var = xmldoc.createElement("Row")
				var.setAttribute("ServerStarted", str(row[0]))
				var.setAttribute("ServerApplication", str(row[1]))
				var.setAttribute("ServerCopyright", str(row[2]))
				var.setAttribute("ServerVersion", str(row[3]))
				var.setAttribute("StrikeCopyright", str(row[4]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_serverDetails.help = "Returns specific details about the server StormForce XR is running on."
	xmlrpc_serverDetails.signature = [["SXRDataSet[ServerStarted, ServerApplication, ServerCopyright, ServerVersion, StrikeCopyright]", "none"]]
	
	
	def xmlrpc_serverUptime(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT DATE_PART('epoch', ServerStarted) AS ServerStartedUT FROM tblServerDetails LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("ServerStartedUT", str(row[0]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_serverUptime.help = "Returns the server started date in UNIX timestamp format."
	xmlrpc_serverUptime.signature = [["SXRDataSet[ServerStartedUT]", "none"]]
	
	
	def xmlrpc_strikeCounter(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT CloseMinute, CloseTotal, NoiseMinute, NoiseTotal, StrikesMinute, StrikesTotal, StrikesOutOfRange FROM tblStrikeCounter LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("CloseMinute", str(row[0]))
				var.setAttribute("CloseTotal", str(row[1]))
				var.setAttribute("NoiseMinute", str(row[2]))
				var.setAttribute("NoiseTotal", str(row[3]))
				var.setAttribute("StrikesMinute", str(row[4]))
				var.setAttribute("StrikesTotal", str(row[5]))
				var.setAttribute("StrikesOutOfRange", str(row[6]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_strikeCounter.help = "Returns the strike counters."
	xmlrpc_strikeCounter.signature = [["SXRDataSet[CloseMinute, CloseTotal, NoiseMinute, NoiseTotal, StrikesMinute, StrikesTotal, StrikesOutOfRange]", "none"]]
	
	
	def xmlrpc_strikePersistence(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT DISTINCT StrikeAge, X, Y, X - 300 AS RelativeX, Y - 300 AS RelativeY, DateTimeOfStrike FROM vwLD250StrikesPersistence ORDER BY DateTimeOfStrike ASC", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("StrikeAge", str(row[0]))
				var.setAttribute("X", str(row[1]))
				var.setAttribute("Y", str(row[2]))
				var.setAttribute("RelativeX", str(row[3]))
				var.setAttribute("RelativeY", str(row[4]))
				var.setAttribute("DateTimeOfStrike", str(row[5]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_strikePersistence.help = "Returns the persistence data based on the current time minus one hour, remember that depending on the server settings the X,Y co-ords maybe using uncorrected strike factors (default is to use corrected strike factors).  The relative values are based on the centre of the map and the strike age is represented in seconds."
	xmlrpc_strikePersistence.signature = [["SXRDataSet[StrikeAge, X, Y, RelativeX, RelativeY, DateTimeOfStrike]", "none"]]
	
	
	def xmlrpc_tracStatus(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT Version, Active, NumberOfStorms AS NoOfStorms, MostActive, MostActiveDistance, Closest, ClosestDistance, Width FROM tblTRACStatus LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("Version", str(row[0]))
				var.setAttribute("Active", str(row[1]))
				var.setAttribute("NoOfStorms", str(row[2]))
				var.setAttribute("MostActive", str(row[3]))
				var.setAttribute("MostActiveDistance", str(row[4]))
				var.setAttribute("Closest", str(row[5]))
				var.setAttribute("ClosestDistance", str(row[6]))
				var.setAttribute("Width", str(row[7]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_tracStatus.help = "Returns the status of the TRAC engine."
	xmlrpc_tracStatus.signature = [["SXRDataSet[Version, Active, NoOfStorms, MostActive, MostActiveDistance, Closest, ClosestDistance, Width]", "none"]]
	
	
	def xmlrpc_tracStorms(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT X, Y, XOffset, YOffset, Name, Intensity, Distance FROM tblTRACStorms ORDER BY ID", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("X", str(row[0]))
				var.setAttribute("Y", str(row[1]))
				var.setAttribute("XOffset", str(row[2]))
				var.setAttribute("YOffset", str(row[3]))
				var.setAttribute("Name", str(row[4]))
				var.setAttribute("Intensity", str(row[5]))
				var.setAttribute("Distance", str(row[6]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_tracStorms.help = "Returns the storms TRAC is monitoring for drawing on-screen."
	xmlrpc_tracStorms.signature = [["SXRDataSet[X, Y, XOffset, YOffset, Name, Intensity, Distance]", "none"]]
	
	
	def xmlrpc_unitStatus(self):
		self.log.debug("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected, ReceiverLost FROM vwUnitStatus ORDER BY Hardware", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("Hardware", str(row[0]))
				var.setAttribute("SquelchLevel", str(row[1]))
				var.setAttribute("UseUncorrectedStrikes", str(row[2]))
				var.setAttribute("CloseAlarm", str(row[3]))
				var.setAttribute("SevereAlarm", str(row[4]))
				var.setAttribute("ReceiverLastDetected", str(row[5]))
				var.setAttribute("ReceiverLost", str(row[6]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_unitStatus.help = "Returns information about the Boltek LD-250 and Boltek EFM-100."
	xmlrpc_unitStatus.signature = [["SXRDataSet[Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected, ReceiverLost]", "none"]]
