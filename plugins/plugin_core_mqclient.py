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
# StormForce MQ Client Plugin                     #
###################################################

from plugin_core_base import PluginBase
from smq_shared import MQ


###########
# Classes #
###########
class Plugin(PluginBase):
	def __init__(self, filename, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		self.MQ_DURABLE = True # Fixed
		self.MQ_EXCHANGE_NAME = "StormForce.MQ.Client"
		self.MQ_EXCHANGE_TYPE = "topic" # Fixed
		self.MQ_HOSTNAME = "localhost"
		self.MQ_NO_ACK_MESSAGES = False # Fixed
		self.MQ_PASSWORD = "guest"
		self.MQ_PORT = 5672
		self.MQ_REPLY_TO = "" # Fixed
		self.MQ_ROUTING_KEY = "" # Fixed
		self.MQ_USERNAME = "guest"
		self.MQ_VIRTUAL_HOST = "/"
		
		self.UPDATE_PERIOD_CAPTURE = 15.
		self.UPDATE_PERIOD_CURRENT_TIME = 1.
		self.UPDATE_PERIOD_EFM100 = 5.
		self.UPDATE_PERIOD_GRAPHS = 60.
		self.UPDATE_PERIOD_LD250 = 1.
		self.UPDATE_PERIOD_STRIKES = 15.
		
		
		mq_routing_key = "events.#"
		
		PluginBase.__init__(self, filename, "MQClient", database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to)
		
		self.mqc = MQ(self.MQ_HOSTNAME, self.MQ_PORT, self.MQ_USERNAME, self.MQ_PASSWORD, self.MQ_VIRTUAL_HOST, self.MQ_EXCHANGE_NAME, self.MQ_EXCHANGE_TYPE, self.MQ_ROUTING_KEY, self.MQ_DURABLE, self.MQ_NO_ACK_MESSAGES, self.MQ_REPLY_TO, None)
		self.running = False
	
	def onEventReceived(self, basic_deliver, properties, body):
		PluginBase.onEventReceived(self, basic_deliver, properties, body)
		
		
		self.log.info("Re-transmitting message onto the client exchange...")
		self.mqc.publishMessage(body, headers = properties.headers, routing_key = basic_deliver.routing_key)
		
		
		self.mq.ackMessage(basic_deliver.delivery_tag)
	
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
						
					elif key == "UpdatePeriodCapture":
						self.UPDATE_PERIOD_CAPTURE = float(val)
						
					elif key == "UpdatePeriodCurrentTime":
						self.UPDATE_PERIOD_CURRENT_TIME = float(val)
						
					elif key == "UpdatePeriodEFM100":
						self.UPDATE_PERIOD_EFM100 = float(val)
						
					elif key == "UpdatePeriodGraphs":
						self.UPDATE_PERIOD_GRAPHS = float(val)
						
					elif key == "UpdatePeriodLD250":
						self.UPDATE_PERIOD_LD250 = float(val)
						
					elif key == "UpdatePeriodStrikes":
						self.UPDATE_PERIOD_STRIKES = float(val)
	
	def run(self):
		self.log.debug("Starting...")
		
		
		capture_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CAPTURE)
		efm100_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_EFM100)
		graphs_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_GRAPHS)
		ld250_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_LD250)
		strikes_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_STRIKES)
		time_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CURRENT_TIME)
		
		while self.running:
			t = self.datetime.now()
			
			try:
				if t >= capture_wait:
					m = self.constructMessage("TRAC", {"number_of_storms": number_of_storms})
					self.mq.publishMessage(m[1], headers = m[0])
				
			except Exception, ex:
				self.log.error("An error occurred while running the capture.")
				self.log.error(ex)
				
			finally:
				capture_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CAPTURE)
			
			
			try:
				if t >= efm100_wait:
					m = self.constructMessage("TRAC", {"number_of_storms": number_of_storms})
					self.mq.publishMessage(m[1], headers = m[0])
				
			except Exception, ex:
				self.log.error("An error occurred while running the EFM-100.")
				self.log.error(ex)
				
			finally:
				efm100_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_EFM100)
			
			
			try:
				if t >= graphs_wait:
					m = self.constructMessage("TRAC", {"number_of_storms": number_of_storms})
					self.mq.publishMessage(m[1], headers = m[0])
				
			except Exception, ex:
				self.log.error("An error occurred while running the graphs.")
				self.log.error(ex)
				
			finally:
				graphs_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_GRAPHS)
			
			
			try:
				if t >= ld250_wait:
					m = self.constructMessage("TRAC", {"number_of_storms": number_of_storms})
					self.mq.publishMessage(m[1], headers = m[0])
				
			except Exception, ex:
				self.log.error("An error occurred while running the LD-250.")
				self.log.error(ex)
				
			finally:
				ld250_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_LD250)
			
			
			try:
				if t >= strikes_wait:
					m = self.constructMessage("TRAC", {"number_of_storms": number_of_storms})
					self.mq.publishMessage(m[1], headers = m[0])
				
			except Exception, ex:
				self.log.error("An error occurred while running the capture.")
				self.log.error(ex)
				
			finally:
				strikes_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_STRIKES)
			
			
			try:
				if t >= time_wait:
					m = self.constructMessage("TRAC", {"number_of_storms": number_of_storms})
					self.mq.publishMessage(m[1], headers = m[0])
				
			except Exception, ex:
				self.log.error("An error occurred while running the current time.")
				self.log.error(ex)
				
			finally:
				time_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CURRENT_TIME)
			
			
			self.time.sleep(0.1)
	
	def start(self):
		PluginBase.start(self)
		
		
		if self.ENABLED:
			self.log.info("Starting MQ Client...")
			self.running = True
			
			t = self.threading.Thread(target = self.run)
			t.setDaemon(1)
			t.start()
	
	def stop(self):
		if self.ENABLED:
			self.running = False
	
	def writeXMLSettings(self):
		PluginBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("PluginMQClient")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
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
			var.setAttribute("UpdatePeriodCapture", str(self.UPDATE_PERIOD_CAPTURE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodCurrentTime", str(self.UPDATE_PERIOD_CURRENT_TIME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodEFM100", str(self.UPDATE_PERIOD_EFM100))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodGraphs", str(self.UPDATE_PERIOD_GRAPHS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodLD250", str(self.UPDATE_PERIOD_LD250))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodStrikes", str(self.UPDATE_PERIOD_STRIKES))
			settings.appendChild(var)
			
			
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()
