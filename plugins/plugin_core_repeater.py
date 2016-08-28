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
# StormForce Repeater Plugin                      #
###################################################

from plugin_core_base import PluginBase
from smq_shared import MQ


###########
# Classes #
###########
class Plugin(PluginBase):
	def __init__(self, filename, database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		self.MQ_DURABLE = True # Fixed
		self.MQ_EXCHANGE_NAME = "Exchange.To.Repeater"
		self.MQ_EXCHANGE_TYPE = "topic" # Fixed
		self.MQ_HOSTNAME = "localhost"
		self.MQ_NO_ACK_MESSAGES = False # Fixed
		self.MQ_PASSWORD = "guest"
		self.MQ_PORT = 5672
		self.MQ_REPLY_TO = "" # Fixed
		self.MQ_ROUTING_KEY = "" # Fixed
		self.MQ_USERNAME = "guest"
		self.MQ_VIRTUAL_HOST = "/"
		
		
		mq_routing_key = "events.#"
		
		PluginBase.__init__(self, filename, "Repeater", database_server, database_database, database_username, database_password, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to)
		
		self.mqc = MQ(self.MQ_HOSTNAME, self.MQ_PORT, self.MQ_USERNAME, self.MQ_PASSWORD, self.MQ_VIRTUAL_HOST, self.MQ_EXCHANGE_NAME, self.MQ_EXCHANGE_TYPE, self.MQ_ROUTING_KEY, self.MQ_DURABLE, self.MQ_NO_ACK_MESSAGES, self.MQ_REPLY_TO, None)
	
	def onEventReceived(self, basic_deliver, properties, body):
		PluginBase.onEventReceived(self, basic_deliver, properties, body)
		
		
		self.log.info("Re-transmitting message onto the repeater...")
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
	
	def writeXMLSettings(self):
		PluginBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("PluginRepeater")
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
			
			
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()
