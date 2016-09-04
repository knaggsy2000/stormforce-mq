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
	def __init__(self):
		self.MQC_DURABLE = True # Fixed
		self.MQC_EXCHANGE_NAME = "Exchange.To.Repeater"
		self.MQC_EXCHANGE_TYPE = "topic" # Fixed
		self.MQC_HOSTNAME = "localhost"
		self.MQC_NO_ACK_MESSAGES = False # Fixed
		self.MQC_PASSWORD = "guest"
		self.MQC_PORT = 5672
		self.MQC_REPLY_TO = "" # Fixed
		self.MQC_ROUTING_KEY = "" # Fixed
		self.MQC_USERNAME = "guest"
		self.MQC_VIRTUAL_HOST = "/"
		
		
		PluginBase.__init__(self)
		
		self.MQ_ROUTING_KEY = "events.#"
		
		
		self.mqc = MQ(self.MQC_HOSTNAME, self.MQC_PORT, self.MQC_USERNAME, self.MQC_PASSWORD, self.MQC_VIRTUAL_HOST, self.MQC_EXCHANGE_NAME, self.MQC_EXCHANGE_TYPE, self.MQC_ROUTING_KEY, self.MQC_DURABLE, self.MQC_NO_ACK_MESSAGES, self.MQC_REPLY_TO, None)
	
	def getScriptPath(self):
		return self.os.path.realpath(__file__)
	
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
						self.MQC_HOSTNAME = val
						
					elif key == "MQPort":
						self.MQC_PORT = int(val)
						
					elif key == "MQUsername":
						self.MQC_USERNAME = val
						
					elif key == "MQPassword":
						self.MQC_PASSWORD = val
						
					elif key == "MQVirtualHost":
						self.MQC_VIRTUAL_HOST = val
						
					elif key == "MQExchangeName":
						self.MQC_EXCHANGE_NAME = val
	
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
			var.setAttribute("MQHostname", str(self.MQC_HOSTNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQPort", str(self.MQC_PORT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQUsername", str(self.MQC_USERNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQPassword", str(self.MQC_PASSWORD))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQVirtualHost", str(self.MQC_VIRTUAL_HOST))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("MQExchangeName", str(self.MQC_EXCHANGE_NAME))
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
