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
# StormForce MQ Client                            #
###################################################
# Version:     v0.2.0                             #
###################################################

from danlog import DanLog
from smq_shared import MQ


###########
# Classes #
###########
class SMQClient():
	def __init__(self):
		from datetime import datetime, timedelta
		from xml.dom import minidom
		
		import os
		import sys
		import threading
		import time
		
		
		self.cron_alive = False
		self.cron_thread = None
		self.datetime = datetime
		self.log = DanLog("SMQClient")
		self.minidom = minidom
		self.os = os
		self.sys = sys
		self.threading = threading
		self.time = time
		self.timedelta = timedelta
		self.ui = None
		
		self.CAPTURE_DIRECTORY = "capture"
		self.CAPTURE_FILENAME = "stormforce-mq.png"
		self.CAPTURE_FULL_PATH =  self.os.path.join(self.CAPTURE_DIRECTORY, self.CAPTURE_FILENAME)
		self.CLIENT_VERSION = "0.2.0"
		
		self.DEMO_MODE = False
		
		self.GRAPH_DIRECTORY = "graphs"
		self.GRAPH_MBM_FILENAME = "mbm.png"
		self.GRAPH_MBM_FULL_PATH = self.os.path.join(self.GRAPH_DIRECTORY, self.GRAPH_MBM_FILENAME)
		
		self.MAP_MATRIX_CENTRE = (300, 300)
		self.MAP_MATRIX_SIZE = (600, 600)
		self.MQ_DURABLE = True # Fixed
		self.MQ_EXCHANGE_NAME = "StormForce.MQ.Client"
		self.MQ_EXCHANGE_TYPE = "topic" # Fixed
		self.MQ_HOSTNAME = "localhost"
		self.MQ_NO_ACK_MESSAGES = False # Fixed
		self.MQ_PASSWORD = "guest"
		self.MQ_PORT = 5672
		self.MQ_REPLY_TO = "" # Fixed
		self.MQ_ROUTING_KEY = "events.#" # Fixed
		self.MQ_USERNAME = "guest"
		self.MQ_VIRTUAL_HOST = "/"
		
		self.SHOW_CROSSHAIR = True
		self.SHOW_RANGE_CIRCLES = False
		self.STRIKE_SHAPE = 1
		
		self.TRAC_STORM_WIDTH = 0
		self.TRAC_VERSION = "0.0.0"
		
		self.UPDATE_PERIOD_CAPTURE = 15.
		self.UPDATE_PERIOD_CURRENT_TIME = 1.
		
		self.XML_SETTINGS_FILE = "smqclient-settings.xml"
		
		self.ZOOM_DISTANCE = 300
	
	def cBool(self, value):
		if str(value).lower() in ("true", "1"):
			return True
			
		elif str(value).lower() in ("false", "0"):
			return False
			
		else:
			raise Exception("Value cannot be converted to boolean.")
	
	def cron(self):
		self.log.debug("Starting...")
		
		
		capture_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CAPTURE)
		current_time_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CURRENT_TIME)
		
		while self.cron_alive:
			t = self.datetime.now()
			
			
			# Update current time/date
			if t >= current_time_wait:
				try:
					self.ui.updateTime()
					
				except Exception, ex:
					self.log.error("An error has occurred while updating the current datetime.")
					self.log.error(ex)
					
				finally:
					current_time_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CURRENT_TIME)
			
			
			# Capture
			if t >= capture_wait:
				try:
					self.ui.captureScreen(self.CAPTURE_FULL_PATH)
					
				except Exception, ex:
					self.log.error("An error has occurred while capturing the screen.")
					self.log.error(ex)
					
				finally:
					capture_wait = self.datetime.now() + self.timedelta(seconds = self.UPDATE_PERIOD_CAPTURE)
			
			
			self.time.sleep(0.1)
	
	def exitProgram(self):
		self.log.debug("Starting...")
		
		
		self.cron_alive = False
		
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
		self.log.info("StormForce MQ - Client")
		self.log.info("======================")
		self.log.info("Checking settings...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.warn("The XML settings file doesn't exist, create one...")
			
			self.writeXMLSettings()
			
			
			self.log.info("The XML settings file has been created using the default settings.  Please edit it and restart the client once you're happy with the settings.")
			
			self.exitProgram()
			
		else:
			self.log.info("Reading XML settings...")
			
			self.readXMLSettings()
			
			# This will ensure it will have any new settings in
			if self.os.path.exists("{0}.bak".format(self.XML_SETTINGS_FILE)):
				self.os.unlink("{0}.bak".format(self.XML_SETTINGS_FILE))
				
			self.os.rename(self.XML_SETTINGS_FILE, "{0}.bak".format(self.XML_SETTINGS_FILE))
			self.writeXMLSettings()
		
		
		self.log.info("Creating directories...")
		
		if not self.os.path.exists(self.CAPTURE_DIRECTORY):
			self.os.mkdir(self.CAPTURE_DIRECTORY)
		
		if not self.os.path.exists(self.GRAPH_DIRECTORY):
			self.os.mkdir(self.GRAPH_DIRECTORY)
		
		
		self.log.info("Removing old captures...")
		
		for root, dirs, files in self.os.walk(self.CAPTURE_DIRECTORY, topdown = False):
			for f in files:
				self.os.unlink(self.os.path.join(root, f))
		
		
		self.log.info("Removing old graphs...")
		
		for root, dirs, files in self.os.walk(self.GRAPH_DIRECTORY, topdown = False):
			for f in files:
				self.os.unlink(self.os.path.join(root, f))
		
		
		self.log.info("Creating UI...")
		self.ui = UI(self, self.MQ_HOSTNAME, self.MQ_PORT, self.MQ_USERNAME, self.MQ_PASSWORD, self.MQ_VIRTUAL_HOST, self.MQ_EXCHANGE_NAME, self.MQ_EXCHANGE_TYPE, self.MQ_ROUTING_KEY, self.MQ_DURABLE, self.MQ_NO_ACK_MESSAGES, self.MQ_REPLY_TO)
		
		
		self.log.info("Starting cron...")
		self.cron_alive = True
		
		self.cron_thread = self.threading.Thread(target = self.cron)
		self.cron_thread.setDaemon(1)
		self.cron_thread.start()
		
		
		self.log.info("Starting UI...")
		
		try:
			self.ui.start()
			
		except KeyboardInterrupt:
			self.ui.stop()
			
		except Exception, ex:
			self.log.error(str(ex))
		
		
		self.log.info("Exiting...")
		self.exitProgram()
	
	def readXMLSettings(self):
		self.log.debug("Starting...")
		
		
		if self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.parse(self.XML_SETTINGS_FILE)
			
			myvars = xmldoc.getElementsByTagName("Setting")
			
			for var in myvars:
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					# Now put the correct values to correct key
					if key == "MQHostname":
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
						
					elif key == "DemoMode":
						self.DEMO_MODE = self.cBool(val)
						
					elif key == "StrikeShape":
						self.STRIKE_SHAPE = int(val)
						
					elif key == "ShowCrosshair":
						self.SHOW_CROSSHAIR = self.cBool(val)
						
					elif key == "ShowRangeCircles":
						self.SHOW_RANGE_CIRCLES = self.cBool(val)
						
					elif key == "UpdatePeriodCapture":
						self.UPDATE_PERIOD_CAPTURE = 15.
						
					elif key == "UpdatePeriodCurrentTime":
						self.UPDATE_PERIOD_CURRENT_TIME = 1.
						
					else:
						self.log.warn("XML setting attribute \"%s\" isn't known.  Ignoring..." % key)
	
	def writeXMLSettings(self):
		self.log.debug("Starting...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			
			
			xmldoc = self.minidom.Document()
			
			# Create header
			settings = xmldoc.createElement("SMQClient")
			xmldoc.appendChild(settings)
			
			# Write each of the details one at a time, makes it easier for someone to alter the file using a text editor
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
			var.setAttribute("DemoMode", str(self.DEMO_MODE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("StrikeShape", str(self.STRIKE_SHAPE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("ShowCrosshair", str(self.SHOW_CROSSHAIR))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("ShowRangeCircles", str(self.SHOW_RANGE_CIRCLES))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodCapture", str(self.UPDATE_PERIOD_CAPTURE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodCurrentTime", str(self.UPDATE_PERIOD_CURRENT_TIME))
			settings.appendChild(var)
			
			
			# Finally, save to the file
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()

class SMQGraphs():
	def __init__(self):
		import os
		
		
		self.log = DanLog("MQGraphs")
		self.mpl_available = False
		self.mpl_pyplot = None
		self.numpy = None
		self.os = os
		self.square_font = None
		
		
		try:
			import matplotlib.font_manager
			import matplotlib.pyplot
			import numpy
			
			
			self.mpl_fontman = matplotlib.font_manager
			self.mpl_pyplot = matplotlib.pyplot
			self.numpy = numpy
			self.square_font = self.mpl_fontman.FontProperties(fname = self.os.path.join("ttf", "micron55.ttf"))
			
			self.mpl_available = True
			
		except Exception, ex:
			self.dispose()
			
			self.log.error("Graphs will not be available due to import exception, please ensure \"matplotlib\" and \"numpy\" have been installed.")
			self.log.error(str(ex))
	
	def available(self):
		return self.mpl_available
	
	def dispose(self):
		self.mpl_available = False
		self.mpl_pyplot = None
		self.numpy = None
		self.square_font = None
	
	def lastHourOfStrikesByMinute(self, rows, filename):
		if self.available():
			try:
				plt = self.mpl_pyplot
				
				
				# 316x232
				fig = plt.figure(figsize = (3.16, 2.32))
				ax = fig.add_subplot(111)
				
				for child in ax.get_children():
					if hasattr(child, "set_color"):
						child.set_color("#000000")
				
				
				# Transpose the data
				xdata = []
				ydata = []
				
				for x in xrange(0, 60):
					xdata.append(x)
					ydata.append(0)
				
				for x in rows:
					ydata[int(x["StrikeAge"])] = int(x["NumberOfStrikes"])
				
				
				# Plot the data and alter the graph apperance
				plt.plot(xdata, ydata, marker = None, color = "#00ff00")
				
				
				# Adjust the y-axis min and max range to avoid it from going negative (happens when there is no strikes in the dataset)
				cx = plt.axis()
				
				if float(cx[3]) < 1.:
					plt.axis([int(cx[0]), int(cx[1]), 0, 1])
					
				else:
					plt.axis([int(cx[0]), int(cx[1]), 0, int(cx[3])])
				
				ax.spines["top"].set_color("white")
				ax.spines["bottom"].set_color("white")
				ax.spines["left"].set_color("white")
				ax.spines["right"].set_color("white")
				
				
				# Can't get the font to NOT use antialiasing, so need to make the font slightly better to make it readable
				for tick in ax.xaxis.get_major_ticks():
					tick.label1.set_fontproperties(self.square_font)
				
				for tick in ax.yaxis.get_major_ticks():
					tick.label1.set_fontproperties(self.square_font)
				
				ax.tick_params(axis = "x", colors = "white", labelsize = 7)
				ax.tick_params(axis = "y", colors = "white", labelsize = 7)
				
				plt.savefig(filename, facecolor = "black", edgecolor = "none")
				
			except Exception, ex:
				self.log.error("An error has occurred while generating the graph.")
				self.log.error(str(ex))

class UI():
	def __init__(self, client, mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to):
		from datetime import datetime
		
		import json
		import math
		import os
		import threading
		import time
		
		
		self.client = client
		self.datetime = datetime
		self.json = json
		self.log = DanLog("UI")
		self.math = math
		self.mq = MQ(mq_hostname, mq_port, mq_username, mq_password, mq_virtual_host, mq_exchange_name, mq_exchange_type, mq_routing_key, mq_durable, mq_no_ack, mq_reply_to, self.onMessageReceived)
		self.os = os
		self.threading = threading
		self.time = time
		
		
		self.BACKGROUND = None
		self.CENTRE_X = 300
		self.CENTRE_Y = 300
		self.CLOSE_TEXT_COLOUR = [255, 0, 0]
		self.COLOUR_ALARM_ACTIVE = [255, 0, 0]
		self.COLOUR_ALARM_INACTIVE = [0, 255, 0]
		self.COLOUR_BLACK = [0, 0, 0]
		self.COLOUR_CROSSHAIR = [245, 245, 90]
		self.COLOUR_NEW_STRIKE = [252, 252, 252]
		self.COLOUR_OLD_STRIKE_0 = [255, 100, 0]
		self.COLOUR_OLD_STRIKE_1 = [255, 200, 0]
		self.COLOUR_OLD_STRIKE_2 = [200, 255, 0]
		self.COLOUR_OLD_STRIKE_3 = [150, 255, 0]
		self.COLOUR_OLD_STRIKE_4 = [0, 255, 50]
		self.COLOUR_OLD_STRIKE_5 = [0, 255, 150]
		self.COLOUR_OLD_STRIKE_6 = [0, 200, 200]
		self.COLOUR_OLD_STRIKE_7 = [0, 150, 255]
		self.COLOUR_OLD_STRIKE_8 = [0, 50, 255]
		self.COLOUR_OLD_STRIKE_9 = [50, 50, 255]
		self.COLOUR_OLD_STRIKE_10 = [100, 0, 255]
		self.COLOUR_OLD_STRIKE_11 = [150, 0, 200]
		self.COLOUR_RANGE_25 = [146, 146, 146]
		self.COLOUR_RANGE_50 = [146, 146, 146]
		self.COLOUR_RANGE_100 = [146, 146, 146]
		self.COLOUR_RANGE_150 = [146, 146, 146]
		self.COLOUR_RANGE_200 = [146, 146, 146]
		self.COLOUR_RANGE_250 = [146, 146, 146]
		self.COLOUR_RANGE_300 = [146, 146, 146]
		self.COLOUR_SIDELINE = [255, 255, 255]
		self.COLOUR_WHITE = [255, 255, 255]
		self.COLOUR_YELLOW = [255, 255, 0]
		self.COPYRIGHT_MESSAGE_1 = "StormForce MQ - Client v{0}".format(self.client.CLIENT_VERSION)
		self.COPYRIGHT_MESSAGE_2 = "(c) 2008-2012, 2014, 2016 - Daniel Knaggs"
		self.EFM100_FIELD = (605, 116)
		self.EFM100_FIELD_VALUE = (682, 116)
		self.EFM100_HEADER = (605, 96)
		self.EFM100_RECEIVER = (605, 108)
		self.EFM100_RECEIVER_VALUE = (682, 108)
		self.INFO_SIZE = None
		self.LD250_CLOSE = (764, 20)
		self.LD250_CLOSE_VALUE = (814, 20)
		self.LD250_CLOSE_ALARM = (605, 20)
		self.LD250_CLOSE_ALARM_VALUE = (682, 20)
		self.LD250_HEADER = (605, 0)
		self.LD250_NOISE = (764, 28)
		self.LD250_NOISE_VALUE = (814, 28)
		self.LD250_RECEIVER = (605, 12)
		self.LD250_RECEIVER_VALUE = (682, 12)
		self.LD250_SEVERE_ALARM = (605, 28)
		self.LD250_SEVERE_ALARM_VALUE = (682, 28)
		self.LD250_SQUELCH = (605, 36)
		self.LD250_SQUELCH_VALUE = (682, 36)
		self.LD250_STRIKES = (764, 12)
		self.LD250_STRIKES_VALUE = (814, 12)
		self.LDUNIT_SQUELCH = 0
		self.MANIFESTO_ELECTION = 0
		self.MANIFESTO_PUBLISHED = 1
		self.MANIFESTO_UNPUBLISHED = 2
		self.MAP_MATRIX_CENTRE = (300, 300) # Can be changed if needed
		self.MAP_MATRIX_SIZE = (600, 600) # Ditto
		self.MAP_SIZE = (600, 600) # DO NOT CHANGE!
		self.MAP = self.os.path.join("png", "map-300.png")
		self.NOISE_TEXT_COLOUR = [30, 200, 240]
		self.SCREEN_SIZE = (920, 600)
		self.SHAPE_CIRCLE = 2
		self.SHAPE_PLUS_1 = 3
		self.SHAPE_PLUS_2 = 4
		self.SHAPE_SQUARE = 0
		self.SHAPE_TRIANGLE = 1
		self.SMALL_NUM = 0.000001
		self.SSBT_ENABLED = False
		self.SSBT_HEADER = (605, 240)
		self.SSBT_MANIFESTO = (605, 260)
		self.SSBT_MANIFESTO_VALUE = (682, 260)
		self.SSBT_STATUS = (605, 252)
		self.SSBT_STATUS_VALUE = (682, 252)
		self.STRIKE_GRAPH = (603, 288)
		self.STRIKE_GRAPH_HEADER = (605, 288)
		self.STRIKE_TEXT_COLOUR = [240, 230, 0]
		self.TIME_SIZE = (220, 20)
		self.TIME_TEXT = [668, 572]
		self.TIME_TEXT_COLOUR = [0, 200, 36]
		self.TRAC_CLOSEST = (764, 220)
		self.TRAC_CLOSEST_VALUE = (814, 220)
		self.TRAC_COLOUR = [0, 255, 255]
		self.TRAC_COUNT = (740, 202)
		self.TRAC_FULL = 0
		self.TRAC_HALF = 0
		self.TRAC_GRADIENT_MIN = [0, 255, 0]
		self.TRAC_GRADIENT_MAX = self.TRAC_COLOUR
		self.TRAC_HEADER = (605, 192)
		self.TRAC_MOST_ACTIVE = (605, 220)
		self.TRAC_MOST_ACTIVE_VALUE = (682, 220)
		self.TRAC_QUARTER = 0
		self.TRAC_STATUS = (605, 204)
		self.TRAC_STATUS_VALUE = (682, 204)
		self.TRAC_STORM_WIDTH = 0
		self.TRAC_STORM_WIDTH_TEXT = (605, 228)
		self.TRAC_STORM_WIDTH_VALUE = (682, 228)
		self.TRAC_STORMS = (605, 212)
		self.TRAC_STORMS_VALUE = (682, 212)
		self.TRAC_THIRD = 0
		self.UPTIME_SIZE = (140, 18)
		self.UPTIME_TEXT = [698, 532]
		self.UPTIME_TEXT_COLOUR = [255, 0, 0]
		self.UNIT_SECTION_COLOUR = [255, 200, 0]
		
		
		self.log.info("Starting...")
		
		
		self.alarm_font = None
		self.number_font = None
		self.screen = None
		self.square_font = None
		self.small_number_font = None
		self.time_font = None
		self.uptime_font = None
		
		
		# Updated "constants"
		self.INFO_SIZE = (self.SCREEN_SIZE[0] - self.MAP_SIZE[0], self.MAP_SIZE[1])
		
		self.MINUTE = 60
		self.HOUR = self.MINUTE * 60
		self.DAY = self.HOUR * 24
		
		
		
		# Start setting things up
		import pygame
		import pygame.locals
		
		self.pygame = pygame
		self.pygame_locals = pygame.locals
		
		
		self.pygame.init()
		
		self.screen = self.pygame.display.set_mode(self.SCREEN_SIZE, 0, 32)
		self.pygame.display.set_caption("StormForce MQ - Client v{0}".format(self.client.CLIENT_VERSION))
		
		
		# Fonts
		self.alarm_font = self.pygame.font.Font(self.os.path.join("ttf", "aldo.ttf"), 28)
		self.number_font = self.pygame.font.Font(self.os.path.join("ttf", "lcd2.ttf"), 30)
		self.square_font = self.pygame.font.Font(self.os.path.join("ttf", "micron55.ttf"), 8)
		self.small_number_font = self.pygame.font.Font(self.os.path.join("ttf", "7linedigital.ttf"), 8)
		self.time_font = self.pygame.font.Font(self.os.path.join("ttf", "lcd1.ttf"), 18)
		self.uptime_font = self.pygame.font.Font(self.os.path.join("ttf", "lcd1.ttf"), 18)
		
		
		# Map
		if not self.os.path.exists(self.MAP):
			self.MAP = self.os.path.join("png", "blank.png")
		
		self.BACKGROUND = self.pygame.image.load(self.MAP).convert()
	
	def captureScreen(self, filename):
		self.log.debug("Starting...")
		
		
		self.pygame.image.save(self.screen, filename)
	
	def cBool(self, value):
		if str(value).lower() in ("true", "1"):
			return True
			
		elif str(value).lower() in ("false", "0"):
			return False
			
		else:
			raise Exception("Value cannot be converted to boolean.")
	
	def clearEFM100FieldArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.EFM100_FIELD_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearEFM100ReceiverArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.EFM100_RECEIVER_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250CloseAlarmArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_CLOSE_ALARM_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250CloseArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_CLOSE_VALUE, (120, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250NoiseArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_NOISE_VALUE, (120, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250ReceiverArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_RECEIVER_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250SevereAlarmArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_SEVERE_ALARM_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250SquelchArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_SQUELCH_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250StrikeArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_STRIKES_VALUE, (120, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearSSBTArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.SSBT_STATUS_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearSSBTManifestoArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.SSBT_MANIFESTO_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearStrikeHistoryArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.STRIKE_GRAPH, (316, 232))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTimeArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.TIME_TEXT, self.TIME_SIZE)
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_STATUS_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACClosestArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_CLOSEST_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACMostActiveArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_MOST_ACTIVE_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACStormsArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_STORMS_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACStormWidthArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_STORM_WIDTH_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACVersionArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_HEADER, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearUptimeArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.pygame.Rect(self.UPTIME_TEXT, self.UPTIME_SIZE)
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def disableInput(self):
		self.log.debug("Starting...")
		
		
		self.pygame.event.set_allowed(None)
	
	def enableInput(self):
		self.log.debug("Starting...")
		
		
		self.pygame.event.set_blocked(None)
		self.pygame.event.set_allowed([KEYDOWN, QUIT, VIDEOEXPOSE])
	
	def handleEvents(self):
		self.log.debug("Starting...")
		
		
		self.pygame.key.set_repeat(1000, 100)
		
		while True:
			event = self.pygame.event.wait()
			
			if event.type == self.pygame.locals.QUIT:
				self.client.exitProgram()
			
			elif event.type == self.pygame.locals.KEYDOWN:
				if event.mod & self.pygame.locals.KMOD_CTRL:
					pass
			
				elif event.mod & self.pygame.locals.KMOD_ALT:
					pass
			
				elif event.mod & self.pygame.locals.KMOD_SHIFT:
					pass
				
				else:
					if event.key == self.pygame.locals.K_ESCAPE:
						self.client.exitProgram()
						
					elif event.key == self.pygame.locals.K_INSERT:
						self.log.debug("To do, zoom in.")
						
					elif event.key == self.pygame.locals.K_DELETE:
						self.log.debug("To do, zoom out.")
						
					elif event.key == self.pygame.locals.K_q:
						self.client.exitProgram()
	
	def onMessageReceived(self, basic_deliver, properties, body):
		try:
			if basic_deliver.routing_key == "events.hardware.core.ld250":
				self.log.debug("The message is to do with the LD-250.")
				
				
				b = self.json.loads(body)
				
				if len(b) > 0:
					if properties.headers["EventName"] == "$WIMST":
						# Status
						self.updateLD250ReceiverArea("Active")
						self.updateLD250CloseAlarmArea(self.cBool(b["CloseAlarm"]))
						self.updateLD250SevereAlarmArea(self.cBool(b["SevereAlarm"]))
						self.updateLD250SquelchArea(int(b["SquelchLevel"]))
						
					elif properties.headers["EventName"] == "$WIMLI":
						# Strike
						self.plotStrikeXY(b["ScreenX"] + self.CENTRE_X - (self.MAP_SIZE[0] / 2), b["ScreenY"] + self.CENTRE_Y - (self.MAP_SIZE[1] / 2), self.COLOUR_OLD_STRIKE_0)
				
			elif basic_deliver.routing_key == "events.hardware.core.efm100":
				self.log.debug("The message is to do with the EFM-100.")
				
				
				b = self.json.loads(body)
				
				if len(b) > 0:
					if properties.headers["EventName"] in ["$-", "$+"]:
						# EFL
						self.updateEFM100FieldArea(float(b["ElectricFieldLevel"]))
						
						if not b["FaultPresent"]:
							self.updateEFM100ReceiverArea("Active")
							
						else:
							self.updateEFM100ReceiverArea("Inactive")
				
			elif basic_deliver.routing_key == "events.plugin.core.mqclient":
				self.log.debug("The message is to do with the MQ client.")
				
				
				b = self.json.loads(body)
				
				if properties.headers["EventName"] == "StrikesPersistence":
					# "Clear" the strike area
					self.renderScreen(render_side = False)
					
					
					# Old strikes
					strike_colour = None
					
					x = 0
					y = 0
					
					for row in b:
						if len(row) > 0:
							if int(row["StrikeAge"]) >= 0 and int(row["StrikeAge"]) < 300:
								strike_colour = self.COLOUR_OLD_STRIKE_0
								
							elif int(row["StrikeAge"]) >= 300 and int(row["StrikeAge"]) < 600:
								strike_colour = self.COLOUR_OLD_STRIKE_1
								
							elif int(row["StrikeAge"]) >= 600 and int(row["StrikeAge"]) < 900:
								strike_colour = self.COLOUR_OLD_STRIKE_2
								
							elif int(row["StrikeAge"]) >= 900 and int(row["StrikeAge"]) < 1200:
								strike_colour = self.COLOUR_OLD_STRIKE_3
								
							elif int(row["StrikeAge"]) >= 1200 and int(row["StrikeAge"]) < 1500:
								strike_colour = self.COLOUR_OLD_STRIKE_4
								
							elif int(row["StrikeAge"]) >= 1500 and int(row["StrikeAge"]) < 1800:
								strike_colour = self.COLOUR_OLD_STRIKE_5
								
							elif int(row["StrikeAge"]) >= 1800 and int(row["StrikeAge"]) < 2100:
								strike_colour = self.COLOUR_OLD_STRIKE_6
								
							elif int(row["StrikeAge"]) >= 2100 and int(row["StrikeAge"]) < 2400:
								strike_colour = self.COLOUR_OLD_STRIKE_7
								
							elif int(row["StrikeAge"]) >= 2400 and int(row["StrikeAge"]) < 2700:
								strike_colour = self.COLOUR_OLD_STRIKE_8
								
							elif int(row["StrikeAge"]) >= 2700 and int(row["StrikeAge"]) < 3000:
								strike_colour = self.COLOUR_OLD_STRIKE_9
								
							elif int(row["StrikeAge"]) >= 3000 and int(row["StrikeAge"]) < 3300:
								strike_colour = self.COLOUR_OLD_STRIKE_10
								
							else:
								strike_colour = self.COLOUR_OLD_STRIKE_11
							
							
							# Draw the strike with it's colour
							x = int(row["ScreenX"])
							y = int(row["ScreenY"])
							
							
							self.plotStrikeXY(x + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + self.CENTRE_Y - (self.MAP_SIZE[1] / 2), strike_colour)
					
				elif properties.headers["EventName"] == "StrikesSummaryByMinute":
					g = SMQGraphs()
					
					if g.available():
						g.lastHourOfStrikesByMinute(b, self.client.GRAPH_MBM_FULL_PATH)
						
					else:
						if self.os.path.exists(self.client.GRAPH_MBM_FULL_PATH):
							self.os.unlink(self.client.GRAPH_MBM_FULL_PATH)
					
					g.dispose()
					g = None
					
					
					self.updateStrikeHistoryArea()
				
			elif basic_deliver.routing_key == "events.plugin.core.serverdetails":
				self.log.debug("The message is to do with the server details.")
				
				
				b = self.json.loads(body)
				
				if len(b) > 0:
					self.updateUptime(b["ServerUptime"])
					
					
					server_details = "%s v%s\n%s\n\n%s" % (b["ServerApplication"], b["ServerVersion"], b["ServerCopyright"], b["StrikeCopyright"])
					uc_split = server_details.split("\n")
					
					y_point = 3
					
					for uc_text in uc_split:
						surface = self.square_font.render(uc_text, True, self.COLOUR_BLACK)
						self.screen.blit(surface, [6, y_point])
						
						surface = self.square_font.render(uc_text, True, self.COLOUR_WHITE)
						self.screen.blit(surface, [5, y_point - 1])
						
						y_point += 8
					
					self.pygame.display.update([5, 2, 600, y_point])
				
			elif basic_deliver.routing_key == "events.plugin.core.strikecounters":
				self.log.debug("The message is to do with the strike counters.")
				
				
				b = self.json.loads(body)
				
				if len(b) > 0:
					self.updateLD250CloseArea(int(b["CloseMinute"]), int(b["CloseTotal"]))
					self.updateLD250NoiseArea(int(b["NoiseMinute"]), int(b["NoiseTotal"]))
					self.updateLD250StrikeArea(int(b["StrikesMinute"]), int(b["StrikesTotal"]), int(b["StrikesOutOfRange"]))
				
			elif basic_deliver.routing_key == "events.plugin.core.trac":
				self.log.debug("The message is to do with the TRAC.")
				
				
				b = self.json.loads(body)
				
				if properties.headers["EventName"] == "Status":
					TRAC_STORM_WIDTH = 0
					
					if len(b) > 0:
						self.updateTRACVersionArea(str(b["Version"]))
						self.updateTRACStatus(self.cBool(b["Active"]))
						self.updateTRACStormsArea(int(b["NumberOfStorms"]))
						self.updateTRACClosestArea(str(b["Closest"]))
						self.updateTRACMostActiveArea(str(b["MostActive"]))
						self.updateTRACStormWidthArea(int(b["Width"]))
						
						self.TRAC_STORM_WIDTH = int(b["Width"])
					
					
					if TRAC_STORM_WIDTH % 2 == 0:
						self.TRAC_FULL = int(self.TRAC_STORM_WIDTH)
						
					else:
						self.TRAC_FULL = int(self.TRAC_STORM_WIDTH - 1)
					
					self.TRAC_HALF = self.TRAC_FULL / 2
					self.TRAC_THIRD = self.TRAC_FULL / 3
					self.TRAC_QUARTER = self.TRAC_HALF / 2
					
				elif properties.headers["EventName"] == "Storms":
					for row in b:
						if len(row) > 0:
							x = int(row["X"])
							y = int(row["Y"])
							x_offset = int(row["XOffset"])
							y_offset = int(row["YOffset"])
							name = str(row["Name"])
							intensity = int(row["Intensity"])
							
							
							points = []
							
							if self.client.STRIKE_SHAPE == self.SHAPE_SQUARE:
								points.append([x + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								points.append([x + self.TRAC_FULL + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								points.append([x + self.TRAC_FULL + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + self.TRAC_FULL + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								points.append([x + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + self.TRAC_FULL + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								
							elif self.client.STRIKE_SHAPE == self.SHAPE_TRIANGLE or self.client.STRIKE_SHAPE == self.SHAPE_PLUS_1 or self.client.STRIKE_SHAPE == self.SHAPE_PLUS_2:
								points.append([x + self.TRAC_HALF + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								points.append([x + self.TRAC_FULL + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + self.TRAC_HALF + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								points.append([x + self.TRAC_HALF + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + self.TRAC_FULL + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								points.append([x + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2), y + self.TRAC_HALF + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
								
							elif self.client.STRIKE_SHAPE == self.SHAPE_CIRCLE:
								rect = self.pygame.draw.circle(self.screen, self.TRAC_COLOUR, [int(x + self.TRAC_HALF + x_offset + self.CENTRE_X - (self.MAP_SIZE[0] / 2)), int(y + self.TRAC_HALF + y_offset + self.CENTRE_Y - (self.MAP_SIZE[1] / 2))], self.TRAC_HALF, 1)
							
							
							if (self.client.STRIKE_SHAPE <> self.SHAPE_CIRCLE):
								rect = self.pygame.draw.polygon(self.screen, self.progressBarColour(self.TRAC_GRADIENT_MIN, self.TRAC_GRADIENT_MAX, int(self.TRAC_FULL * intensity), self.TRAC_FULL), points, 1)
							
							self.pygame.display.update(rect)
							
							
							# Draw the intensity as a "progress bar" with the storm ID as well - the CRC32 length will be 40 pixels
							rect = self.pygame.Rect(((x + x_offset + self.TRAC_HALF + self.CENTRE_X - (self.MAP_SIZE[0] / 2)) - 30, y + y_offset + self.TRAC_FULL + 3 + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)), (70, 8))
							
							id_surface = self.square_font.render(name, True, self.COLOUR_BLACK)
							self.screen.blit(id_surface, [(x + x_offset + self.TRAC_HALF + self.CENTRE_X - (self.MAP_SIZE[0] / 2)) - 29, y + y_offset + self.TRAC_FULL + 3 + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
							
							id_surface = self.square_font.render(name, True, self.COLOUR_WHITE)
							self.screen.blit(id_surface, [(x + x_offset + self.TRAC_HALF + self.CENTRE_X - (self.MAP_SIZE[0] / 2)) - 30, y + y_offset + self.TRAC_FULL + 2 + self.CENTRE_Y - (self.MAP_SIZE[1] / 2)])
							
							self.pygame.display.update(rect)
				
				
			else:
				self.log.debug("Unhandled routing key: {0}".format(basic_deliver.routing_key))
			
			
			self.mq.ackMessage(basic_deliver.delivery_tag)
			
		except Exception, ex:
			self.log.error("An error has occurred while processing the received message.")
			self.log.error(ex)
	
	def progressBar(self, position, startcolour, endcolour, value, maxvalue, thickness):
		self.log.debug("Starting...")
		
		
		r_step = 0
		g_step = 0
		b_step = 0
		
		for x in range(0, value):
			if x > maxvalue:
				break
				
			else:
				# Get the next colour
				colour = [min(max(startcolour[0] + r_step, 0), 255), min(max(startcolour[1] + g_step, 0), 255), min(max(startcolour[2] + b_step, 0), 255)]
				
				# Draw the gradient
				rect = self.pygame.Rect([position[0] + x, position[1]], [1, thickness])
				self.pygame.draw.rect(self.screen, colour, rect)
				
				# Increase the colour stepping
				r_step += (endcolour[0] - startcolour[0]) / maxvalue
				g_step += (endcolour[1] - startcolour[1]) / maxvalue
				b_step += (endcolour[2] - startcolour[2]) / maxvalue
	
	def progressBarColour(self, startcolour, endcolour, value, maxvalue):
		self.log.debug("Starting...")
		
		
		r_step = 0
		g_step = 0
		b_step = 0
		colour = self.TRAC_COLOUR
		
		for x in range(0, value):
			if x > maxvalue:
				break
				
			else:
				# Get the next colour
				colour = [min(max(startcolour[0] + r_step, 0), 255), min(max(startcolour[1] + g_step, 0), 255), min(max(startcolour[2] + b_step, 0), 255)]
				
				# Increase the colour stepping
				r_step += (endcolour[0] - startcolour[0]) / maxvalue
				g_step += (endcolour[1] - startcolour[1]) / maxvalue
				b_step += (endcolour[2] - startcolour[2]) / maxvalue
				
		return colour
	
	def plotStrike(self, strikedistance, strikeangle, isold):
		self.log.debug("Starting...")
		
		
		# By using a bit of trignonmetry we can get the missing values
		#
		#       ^
		#      / |
		#  H  /  |
		#    /   | O
		#   /    |
		#  / )X  |
		# /-------
		#     A
		o = self.math.sin(self.math.radians(strikeangle)) * float(strikedistance)
		a = self.math.cos(self.math.radians(strikeangle)) * float(strikedistance)
		
		rect = None
		
		if not isold:
			if self.client.STRIKE_SHAPE == self.SHAPE_SQUARE:
				# We use a 3x3 rectangle to indicate a strike, where (1,1) is the centre (zero-based)
				rect = self.pygame.Rect([(self.CENTRE_X + o) - 1, (self.CENTRE_Y + -a) - 1], [3, 3])
				self.pygame.draw.rect(self.screen, self.COLOUR_NEW_STRIKE, rect)
				
			elif self.client.STRIKE_SHAPE == self.SHAPE_TRIANGLE:
				points = []
				points.append([self.CENTRE_X + o, self.CENTRE_Y + -a])
				points.append([(self.CENTRE_X + o) - 2, (self.CENTRE_Y + -a) - 2])
				points.append([(self.CENTRE_X + o) + 2, (self.CENTRE_Y + -a) - 2])
				
				rect = self.pygame.draw.polygon(self.screen, self.COLOUR_NEW_STRIKE, points)
				
			elif self.client.STRIKE_SHAPE == self.SHAPE_CIRCLE:
				rect = self.pygame.draw.circle(self.screen, self.COLOUR_NEW_STRIKE, [int(self.CENTRE_X + o), int(self.CENTRE_Y + -a)], 2, 0)
			
		else:
			# Draw a 1-pixel blue strike instead
			rect = self.pygame.Rect([(self.CENTRE_X + o) - 1, (self.CENTRE_Y + -a) - 1], [1, 1])
		
		self.pygame.display.update(rect)
	
	def plotStrikeXY(self, x, y, colour):
		self.log.debug("Starting...")
		
		
		rect = None
		
		if self.client.STRIKE_SHAPE == self.SHAPE_SQUARE:
			rect = self.pygame.Rect([x - 1, y - 1], [3, 3])
			self.pygame.draw.rect(self.screen, colour, rect)
			
		elif self.client.STRIKE_SHAPE == self.SHAPE_TRIANGLE:
			points = []
			points.append([x, y])
			points.append([x - 2, y - 2])
			points.append([x + 2, y - 2])
				
			rect = self.pygame.draw.polygon(self.screen, colour, points)
			
		elif self.client.STRIKE_SHAPE == self.SHAPE_CIRCLE:
			rect = self.pygame.draw.circle(self.screen, colour, [int(x), int(y)], 2, 0)
			
		elif self.client.STRIKE_SHAPE == self.SHAPE_PLUS_1 or self.client.STRIKE_SHAPE == self.SHAPE_PLUS_2:
			points = []
			points.append([x - 1, y - 4])
			points.append([x + 1, y - 4])
			points.append([x + 1, y - 1])
			points.append([x + 4, y - 1])
			points.append([x + 4, y + 1])
			points.append([x + 1, y + 1])
			points.append([x + 1, y + 4])
			points.append([x - 1, y + 4])
			points.append([x - 1, y + 1])
			points.append([x - 4, y + 1])
			points.append([x - 4, y - 1])
			points.append([x - 1, y - 1])
			
			if self.client.STRIKE_SHAPE == self.SHAPE_PLUS_1:
				# Have to fill it in like this otherwise it won't draw it correctly
				rect = self.pygame.draw.polygon(self.screen, self.COLOUR_BLACK, points, 1)
				
				self.pygame.draw.line(self.screen, colour, [x, y - 3], [x, y + 3], 1)
				self.pygame.draw.line(self.screen, colour, [x - 3, y], [x + 3, y], 1)
				
			elif self.client.STRIKE_SHAPE == self.SHAPE_PLUS_2:
				rect = self.pygame.draw.polygon(self.screen, colour, points, 1)
		
		self.pygame.display.update(rect)
	
	def renderScreen(self, render_map = True, render_side = True):
		self.log.debug("Starting...")
		
		
		if render_map:
			# Draw the "base" screen
			self.screen.blit(self.BACKGROUND, (0, 0))
		
		if render_side:
			# Side section
			COUNTER_SIZE = [self.INFO_SIZE[0] - 10, 52]
			
			# Top lines
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] - 5], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] - 5], 1)
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 42], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 42], 1)
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 90], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 90], 1)
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 138], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 138], 1)
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 186], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 186], 1)
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 234], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 234], 1)
			
			
			# Starting point
			self.clearLD250CloseAlarmArea()
			self.clearLD250ReceiverArea()
			self.clearLD250SevereAlarmArea()
			self.clearLD250SquelchArea()
			self.clearLD250CloseArea()
			self.clearLD250NoiseArea()
			self.clearLD250StrikeArea()
			
			self.clearEFM100FieldArea()
			self.clearEFM100ReceiverArea()
			
			self.clearTRACArea()
			self.clearTRACMostActiveArea()
			self.clearTRACStormsArea()
			self.clearTRACStormWidthArea()
			
			self.clearSSBTArea()
			self.clearSSBTManifestoArea()
			
			
			self.updateLD250CloseArea(0, 0)
			self.updateLD250NoiseArea(0, 0)
			self.updateLD250StrikeArea(0, 0, 0)
			
			self.updateTRACClosestArea("")
			self.updateTRACMostActiveArea("")
			self.updateTRACStatus(False)
			self.updateTRACStormsArea(0)
			self.updateTRACStormWidthArea(0)
			
			
			# LD-250
			surface = self.square_font.render("LD-250", False, self.UNIT_SECTION_COLOUR)
			self.screen.blit(surface, self.LD250_HEADER)
			
			surface = self.square_font.render("RECEIVER:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.LD250_RECEIVER)
			
			surface = self.square_font.render("CLOSE ALARM:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.LD250_CLOSE_ALARM)
			
			surface = self.square_font.render("SEVERE ALARM:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.LD250_SEVERE_ALARM)
			
			surface = self.square_font.render("SQUELCH:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.LD250_SQUELCH)
			
			surface = self.square_font.render("STRIKES:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.LD250_STRIKES)
			
			surface = self.square_font.render("CLOSE:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.LD250_CLOSE)
			
			surface = self.square_font.render("NOISE:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.LD250_NOISE)
			
			
			# EFM-100
			surface = self.square_font.render("EFM-100", False, self.UNIT_SECTION_COLOUR)
			self.screen.blit(surface, self.EFM100_HEADER)
			
			surface = self.square_font.render("RECEIVER:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.EFM100_RECEIVER)
			
			surface = self.square_font.render("FIELD LEVEL:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.EFM100_FIELD)
			
			
			# We'll set some of values here
			# LD-250
			surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_INACTIVE)
			self.screen.blit(surface, self.LD250_CLOSE_ALARM_VALUE)
			
			surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_INACTIVE)
			self.screen.blit(surface, self.LD250_SEVERE_ALARM_VALUE)
			
			surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_ACTIVE)
			self.screen.blit(surface, self.LD250_RECEIVER_VALUE)
			
			surface = self.square_font.render("%s" % self.LDUNIT_SQUELCH, False, self.COLOUR_ALARM_INACTIVE)
			self.screen.blit(surface, self.LD250_SQUELCH_VALUE)
			
			
			# EFM-100
			surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_ACTIVE)
			self.screen.blit(surface, self.EFM100_RECEIVER_VALUE)
			
			
			# TRAC
			surface = self.square_font.render("TRAC", False, self.UNIT_SECTION_COLOUR)
			self.screen.blit(surface, self.TRAC_HEADER)
			
			surface = self.square_font.render("STATUS:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.TRAC_STATUS)
			
			surface = self.square_font.render("STORMS:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.TRAC_STORMS)
			
			surface = self.square_font.render("MOST ACTIVE:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.TRAC_MOST_ACTIVE)
			
			surface = self.square_font.render("CLOSEST:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.TRAC_CLOSEST)
			
			surface = self.square_font.render("WIDTH:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.TRAC_STORM_WIDTH_TEXT)
			
			
			# SSBT - StormForce Strike Bi/Triangulation
			surface = self.square_font.render("StormForce Strike Bi/Triangulation (SSBT)", False, self.UNIT_SECTION_COLOUR)
			self.screen.blit(surface, self.SSBT_HEADER)
			
			surface = self.square_font.render("STATUS:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.SSBT_STATUS)
			
			surface = self.square_font.render("MANIFESTO:", False, self.COLOUR_WHITE)
			self.screen.blit(surface, self.SSBT_MANIFESTO)
			
			if self.SSBT_ENABLED:
				surface = self.square_font.render("Active", False, self.COLOUR_ALARM_INACTIVE)
				
			else:
				surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_ACTIVE)
				
			self.screen.blit(surface, self.SSBT_STATUS_VALUE)
			
			if self.SSBT_ENABLED:
				self.updateSSBTManifesto(self.MANIFESTO_ELECTION)
			
			
			
			# Side line
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0], 0], [self.MAP_SIZE[0], self.MAP_SIZE[1] * 2], 1)
			self.pygame.draw.line(self.screen, self.COLOUR_RANGE_300, [self.MAP_SIZE[0] + 1, 0], [self.MAP_SIZE[0] + 1, self.MAP_SIZE[1]], 1)
			
			# Time line
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, self.SCREEN_SIZE[1] - 40], [self.SCREEN_SIZE[0], self.SCREEN_SIZE[1] - 40], 1)
			self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, self.SCREEN_SIZE[1] - 80], [self.SCREEN_SIZE[0], self.SCREEN_SIZE[1] - 80], 1)
			
			surface = self.square_font.render("DATETIME", False, self.UNIT_SECTION_COLOUR)
			self.screen.blit(surface, [self.MAP_SIZE[0] + 5, 561])
			
			surface = self.square_font.render("UPTIME", False, self.UNIT_SECTION_COLOUR)
			self.screen.blit(surface, [self.MAP_SIZE[0] + 5, 521])
		
		if render_map:
			# Range circles
			if self.client.SHOW_RANGE_CIRCLES:
				self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_25, [self.CENTRE_X, self.CENTRE_Y], 25, 1)
				self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_50, [self.CENTRE_X, self.CENTRE_Y], 50, 1)
				self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_100, [self.CENTRE_X, self.CENTRE_Y], 100, 1)
				self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_150, [self.CENTRE_X, self.CENTRE_Y], 150, 1)
				self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_200, [self.CENTRE_X, self.CENTRE_Y], 200, 1)
				self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_250, [self.CENTRE_X, self.CENTRE_Y], 250, 1)
				self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_300, [self.CENTRE_X, self.CENTRE_Y], 300, 1)
			
			if self.client.SHOW_CROSSHAIR:
				# Crosshair V
				self.pygame.draw.line(self.screen, self.COLOUR_CROSSHAIR, [self.CENTRE_X, self.CENTRE_Y - 3], [self.CENTRE_X, self.CENTRE_Y + 3], 1)
				
				# Crosshair H
				self.pygame.draw.line(self.screen, self.COLOUR_CROSSHAIR, [self.CENTRE_X - 3, self.CENTRE_Y], [self.CENTRE_X + 3, self.CENTRE_Y], 1)
			
			
			# Copyright text
			#uc_split = "Unknown"
			#
			#try:
			#	s = self.xmlrpclib.ServerProxy(self.client.STORMFORCEXR_SERVER)
			#	data = self.client.extractDataset(s.serverDetails().data)
			#	s = None
			#	
			#	for row in data:
			#		server_details = "%s v%s\n%s\n\n%s" % (str(row["ServerApplication"]), str(row["ServerVersion"]), str(row["ServerCopyright"]), str(row["StrikeCopyright"]))
			#		uc_split = server_details.split("\n")
			#		
			#		break
			#	
			#except Exception, ex:
			#	self.log.error(str(ex))
			#
			#
			#y_point = 3
			#
			#for uc_text in uc_split:
			#	surface = self.square_font.render(uc_text, True, self.COLOUR_BLACK)
			#	self.screen.blit(surface, [6, y_point])
			#	
			#	surface = self.square_font.render(uc_text, True, self.COLOUR_WHITE)
			#	self.screen.blit(surface, [5, y_point - 1])
			#	
			#	y_point += 8
			
			
			surface = self.square_font.render(self.COPYRIGHT_MESSAGE_1, True, self.COLOUR_BLACK)
			self.screen.blit(surface, [6, 580])
			
			surface = self.square_font.render(self.COPYRIGHT_MESSAGE_1, True, self.COLOUR_WHITE)
			self.screen.blit(surface, [5, 579])
			
			
			surface = self.square_font.render(self.COPYRIGHT_MESSAGE_2, True, self.COLOUR_BLACK)
			self.screen.blit(surface, [6, 588])
			
			surface = self.square_font.render(self.COPYRIGHT_MESSAGE_2, True, self.COLOUR_WHITE)
			self.screen.blit(surface, [5, 587])
			
			
			# Range text
			surface = self.square_font.render("Range: %dmiles" % self.client.ZOOM_DISTANCE, True, self.COLOUR_BLACK)
			self.screen.blit(surface, [514, 588])
			
			surface = self.square_font.render("Range: %dmiles" % self.client.ZOOM_DISTANCE, True, self.COLOUR_WHITE)
			self.screen.blit(surface, [513, 587])
		
		
		# Update when done
		self.pygame.display.update()
	
	def start(self):
		self.log.debug("Starting...")
		
		
		self.renderScreen()
		
		t = self.threading.Thread(target = self.mq.start)
		t.setDaemon(1)
		t.start()
		
		self.handleEvents()
	
	def stop(self):
		if self.mq is not None:
			self.mq.stop()
	
	def updateEFM100FieldArea(self, field):
		self.log.debug("Starting...")
		
		
		rect = self.clearEFM100FieldArea()
		
		field_surface = self.square_font.render("%2.2fKV/m" % field, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(field_surface, self.EFM100_FIELD_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateEFM100ReceiverArea(self, status):
		self.log.debug("Starting...")
		
		
		rect = self.clearEFM100ReceiverArea()
		
		colour = None
		
		if status == "Active":
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			colour = self.COLOUR_ALARM_ACTIVE
		
		receive_surface = self.square_font.render(status, False, colour)
		self.screen.blit(receive_surface, self.EFM100_RECEIVER_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250CloseArea(self, close_minute, close_total):
		self.log.debug("Starting...")
		
		
		rect = self.clearLD250CloseArea()
		
		close_surface = self.small_number_font.render("%03d %06d" % (close_minute, close_total), False, self.CLOSE_TEXT_COLOUR)
		self.screen.blit(close_surface, self.LD250_CLOSE_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250CloseAlarmArea(self, status):
		self.log.debug("Starting...")
		
		
		rect = self.clearLD250CloseAlarmArea()
		
		text = ""
		colour = None
		
		
		if status == 0:
			text = "Inactive"
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			text = "Active"
			colour = self.COLOUR_ALARM_ACTIVE
		
		close_surface = self.square_font.render(text, False, colour)
		self.screen.blit(close_surface, self.LD250_CLOSE_ALARM_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250NoiseArea(self, noise_minute, noise_total):
		self.log.debug("Starting...")
		
		
		rect = self.clearLD250NoiseArea()
		
		noise_surface = self.small_number_font.render("%03d %06d" % (noise_minute, noise_total), False, self.NOISE_TEXT_COLOUR)
		self.screen.blit(noise_surface, self.LD250_NOISE_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250ReceiverArea(self, status):
		self.log.debug("Starting...")
		
		
		rect = self.clearLD250ReceiverArea()
		
		if status == "Active":
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			colour = self.COLOUR_ALARM_ACTIVE
		
		receive_surface = self.square_font.render(status, False, colour)
		self.screen.blit(receive_surface, self.LD250_RECEIVER_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250SevereAlarmArea(self, status):
		self.log.debug("Starting...")
		
		
		rect = self.clearLD250SevereAlarmArea()
		
		text = ""
		colour = None
		
		
		if status == 0:
			text = "Inactive"
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			text = "Active"
			colour = self.COLOUR_ALARM_ACTIVE
		
		severe_surface = self.square_font.render(text, False, colour)
		self.screen.blit(severe_surface, self.LD250_SEVERE_ALARM_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250SquelchArea(self, squelch):
		self.log.debug("Starting...")
		
		
		rect = self.clearLD250SquelchArea()
		
		squelch_surface = self.square_font.render("%d" % squelch, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(squelch_surface, self.LD250_SQUELCH_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250StrikeArea(self, strikes_minute, strikes_total, strikes_oor):
		self.log.debug("Starting...")
		
		
		rect = self.clearLD250StrikeArea()
		
		strike_surface = self.small_number_font.render("%03d %06d %03d" % (strikes_minute, strikes_total, strikes_oor), False, self.STRIKE_TEXT_COLOUR)
		self.screen.blit(strike_surface, self.LD250_STRIKES_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateSSBTManifesto(self, status):
		self.log.debug("Starting...")
		
		
		rect = self.clearSSBTManifestoArea()
		
		text = ""
		colour = None
		
		if status == self.MANIFESTO_ELECTION:
			text = "Election"
			colour = self.COLOUR_YELLOW
			
		elif status == self.MANIFESTO_PUBLISHED:
			text = "Published"
			colour = self.COLOUR_ALARM_INACTIVE
			
		elif status == self.MANIFESTO_UNPUBLISHED:
			text = "Unpublished"
			colour = self.COLOUR_ALARM_ACTIVE
		
		ssbt_surface = self.square_font.render(text, False, colour)
		self.screen.blit(ssbt_surface, self.SSBT_MANIFESTO_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateStrikeHistoryArea(self):
		self.log.debug("Starting...")
		
		
		rect = self.clearStrikeHistoryArea()
		surface = None
		
		if self.os.path.exists(self.client.GRAPH_MBM_FULL_PATH):
			g = self.pygame.image.load(self.client.GRAPH_MBM_FULL_PATH).convert()
			self.screen.blit(g, self.STRIKE_GRAPH)
			
			surface = self.square_font.render("STRIKE HISTORY - LAST 60 MINUTES", False, self.UNIT_SECTION_COLOUR)
			
		else:
			surface = self.square_font.render("STRIKE HISTORY - NOT AVAILABLE", False, self.UNIT_SECTION_COLOUR)
		
		self.screen.blit(surface, self.STRIKE_GRAPH_HEADER)
		self.pygame.display.update(rect)
	
	def updateTime(self):
		self.log.debug("Starting...")
		
		
		t = self.datetime.now()
		
		current_time = str(t.strftime("%d/%m/%Y %H:%M:%S"))
		
		rect = self.clearTimeArea()
		time_surface = self.time_font.render(current_time, True, self.TIME_TEXT_COLOUR)
		self.screen.blit(time_surface, self.TIME_TEXT)
		
		self.pygame.display.update(rect)
	
	def updateTRACClosestArea(self, trac_closest):
		self.log.debug("Starting...")
		
		
		rect = self.clearTRACClosestArea()
		
		surface = self.square_font.render("%s" % trac_closest, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_CLOSEST_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACMostActiveArea(self, trac_most_active):
		self.log.debug("Starting...")
		
		
		rect = self.clearTRACMostActiveArea()
		
		surface = self.square_font.render("%s" % trac_most_active, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_MOST_ACTIVE_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACStatus(self, isactive):
		self.log.debug("Starting...")
		
		
		rect = self.clearTRACArea()
		
		text = ""
		colour = None
		
		if not isactive:
			text = "Inactive"
			colour = self.COLOUR_ALARM_INACTIVE
			
		elif isactive:
			text = "Active"
			colour = self.COLOUR_ALARM_ACTIVE
			
		else:
			text = "Busy"
			colour = self.COLOUR_YELLOW
		
		trac_surface = self.square_font.render(text, False, colour)
		self.screen.blit(trac_surface, self.TRAC_STATUS_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACStormsArea(self, trac_storms_total):
		self.log.debug("Starting...")
		
		
		rect = self.clearTRACStormsArea()
		
		surface = self.square_font.render("%d" % trac_storms_total, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_STORMS_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACStormWidthArea(self, storm_width):
		self.log.debug("Starting...")
		
		
		rect = self.clearTRACStormWidthArea()
		
		surface = self.square_font.render("%d" % storm_width, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_STORM_WIDTH_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACVersionArea(self, version):
		self.log.debug("Starting...")
		
		
		rect = self.clearTRACVersionArea()
		
		surface = self.square_font.render("TRAC v%s" % version, False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, self.TRAC_HEADER)
		
		self.pygame.display.update(rect)
	
	def updateUptime(self, uptime):
		self.log.debug("Starting...")
		
		
		days = int(uptime / self.DAY)
		hours = int((uptime % self.DAY) / self.HOUR)
		minutes = int((uptime % self.HOUR) / self.MINUTE)
		seconds = int(uptime % self.MINUTE)
		
		suptime = "%04d:%02d:%02d:%02d" % (days, hours, minutes, seconds)
		
		rect = self.clearUptimeArea()
		uptime_surface = self.uptime_font.render(suptime, True, self.UPTIME_TEXT_COLOUR)
		self.screen.blit(uptime_surface, self.UPTIME_TEXT)
		
		self.pygame.display.update(rect)


########
# Main #
########
if __name__ == "__main__":
	l = None
	
	try:
		l = DanLog("Main")
		l.info("Preparing...")
		
		smq = SMQClient()
		smq.main()
		smq = None
		
	except Exception, ex:
		if l is not None:
			l.fatal(str(ex))
			
		else:
			print "Exception: %s" % str(ex)
