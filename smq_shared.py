#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008-2012, 2014, 2016, Daniel Knaggs - 2E0DPK/M6DPK     #
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
# StormForce Shared                               #
###################################################

from danlog import DanLog


###########
# Classes #
###########
class Database():
	def __init__(self, server, database, username, password):
		from datetime import datetime
		
		import psycopg2
		
		
		self.datetime = datetime
		self.log = DanLog("Database")
		self.psycopg2 = psycopg2
		
		
		self.POSTGRESQL_DATABASE = database
		self.POSTGRESQL_PASSWORD = password
		self.POSTGRESQL_SERVER = server
		self.POSTGRESQL_USERNAME = username
	
	def addColumnSQLString(self, table, column_name, column_type):
		self.log.debug("Starting...")
		
		
		return """
DO $$
	BEGIN
		BEGIN
			ALTER TABLE %s ADD COLUMN %s %s;
			
		EXCEPTION WHEN duplicate_column THEN
			-- Nothing
		END;
	END
$$
""" % (table, column_name, column_type)
	
	def createTableSQLString(self, table):
		self.log.debug("Starting...")
		
		
		return """
DO $$
	BEGIN
		BEGIN
			CREATE TABLE %s(ID bigserial PRIMARY KEY);
			
		EXCEPTION WHEN duplicate_table THEN
			-- Nothing
		END;
	END
$$
""" % table
	
	def createIndexSQLString(self, name, table, columns, conn = []):
		self.log.debug("Starting...")
		
		
		return """
DO $$
	BEGIN
		IF NOT EXISTS (
				SELECT c.relname
				FROM pg_class c
				INNER JOIN pg_namespace n ON n.oid = c.relnamespace
				WHERE c.relname = lower('%s') AND n.nspname = 'public' AND c.relkind = 'i'
			) THEN
			
			CREATE INDEX %s ON %s (%s);
		END IF;
	END
$$
""" % (name, name, table, columns)
	
	def connectToDatabase(self, conn = []):
		self.log.debug("Starting...")
		
		
		newconn = self.psycopg2.connect(database = self.POSTGRESQL_DATABASE, host = self.POSTGRESQL_SERVER, user = self.POSTGRESQL_USERNAME, password = self.POSTGRESQL_PASSWORD)
		newconn.autocommit = True
		newconn.set_isolation_level(self.psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
		
		if len(conn) > 0:
			for item in conn:
				item = None
			
			del conn
		
		conn.append(newconn)
	
	def danLookup(self, strfield, strtable, strwhere, parameters = (), conn = []):
		self.log.debug("Starting...")
		
		
		if len(conn) >= 1:
			strsql = ""
			
			if strwhere == "":
				strsql = "SELECT %s FROM %s LIMIT 1" % (strfield, strtable)
				
			else:
				strsql = "SELECT %s FROM %s WHERE %s LIMIT 1" % (strfield, strtable, strwhere)
			
			strsql = strsql.replace("?", """%s""") # "?" doesn't seem to work, work around it
			
			
			try:
				cur = conn[0].cursor()
				cur.execute(strsql, parameters)
				
				row = cur.fetchone()
				
				if row is not None:
					row = row[0]
					
				else:
					row = None
				
				cur.close()
				
				return row
				
			except Exception, ex:
				self.log.error(str(ex))
				
				return None
			
		else:
			self.log.warn("Connection has not been passed.")
			
			return None
	
	def disconnectFromDatabase(self, conn = []):
		self.log.debug("Starting...")
		
		
		if len(conn) == 1:
			conn[0].close()
			conn[0] = None
	
	def executeSQLCommand(self, strsql, parameters = (), conn = []):
		self.log.debug("Starting...")
		
		
		if len(conn) >= 1:
			try:
				strsql = strsql.replace("?", """%s""") # "?" doesn't seem to work, work around it
				
				
				cur = conn[0].cursor()
				cur.execute(strsql, parameters)
				cur.close()
				
				return True
				
			except Exception, ex:
				self.log.error(str(ex))
				self.log.debug(str(strsql))
				
				return False
			
		else:
			self.log.warn("Connection has not been passed.")
			
			return None
	
	def executeSQLQuery(self, strsql, parameters = (), conn = []):
		self.log.debug("Starting...")
		
		
		if len(conn) >= 1:
			try:
				strsql = strsql.replace("?", """%s""") # "?" doesn't seem to work, work around it
				
				
				cur = conn[0].cursor()
				cur.execute(strsql, parameters)
				
				rows = cur.fetchall()
				
				cur.close()
				
				return rows
				
			except Exception, ex:
				self.log.error(str(ex))
				
				return None
			
		else:
			self.log.warn("Connection has not been passed.")
			
			return None
	
	def sqlDateTime(self):
		self.log.debug("Starting...")
		
		
		t = self.datetime.now()
		
		return str(t.strftime("%Y/%m/%d %H:%M:%S"))

class MQ():
	def __init__(self, hostname = "localhost", port = 5672, username = "guest", password = "guest", virtual_host = "/", exchange_name = "", exchange_type = "topic", routing_key = "", durable = True, no_ack = False, reply_to = "", message_callback = None):
		from datetime import datetime
		
		import pika
		import time
		import uuid
		
		
		self.channel = None
		self.connection = None
		self.consumer_tag = None
		self.datetime = datetime
		self.log = DanLog("MQ")
		self.onMessageReceived = message_callback
		self.pika = pika
		self.time = time
		self.uuid = uuid
		
		
		self.MQ_DURABLE = durable
		self.MQ_EXCHANGE_NAME = exchange_name
		self.MQ_EXCHANGE_TYPE = exchange_type
		self.MQ_HOSTNAME = hostname
		self.MQ_NO_ACK_MESSAGES = no_ack
		self.MQ_PASSWORD = password
		self.MQ_PORT = port
		self.MQ_QUEUE_NAME = ""
		self.MQ_REPLY_TO = reply_to
		self.MQ_ROUTING_KEY = routing_key
		self.MQ_USERNAME = username
		self.MQ_VIRTUAL_HOST = virtual_host
		
		
		self.parameters = self.pika.ConnectionParameters(self.MQ_HOSTNAME, self.MQ_PORT, self.MQ_VIRTUAL_HOST, self.pika.PlainCredentials(self.MQ_USERNAME, self.MQ_PASSWORD))
	
	def ackMessage(self, delivery_tag):
		self.log.debug("Starting...")
		
		
		if self.channel is not None:
			self.channel.basic_ack(delivery_tag = delivery_tag)
	
	def consume(self):
		self.log.debug("Starting...")
		
		
		self.channel.basic_qos(prefetch_count = 1)
		self.channel.add_on_cancel_callback(self.onConsumerCancelled)
		
		self.consumer_tag = self.channel.basic_consume(self.onMessage, queue = self.MQ_QUEUE_NAME)
	
	def onCancelOK(self, frame):
		self.log.debug("Starting...")
		
		
		self.channel.close()
	
	def onChannelClose(self, channel, reply_code, reply_text):
		self.log.debug("Starting...")
		
		
		self.connection.close()
	
	def onChannelOpen(self, channel):
		self.log.debug("Starting...")
		
		
		self.channel = channel
		self.channel.add_on_close_callback(self.onChannelClose)
		self.channel.exchange_declare(self.onExchangeDeclareOK, exchange = self.MQ_EXCHANGE_NAME, type = self.MQ_EXCHANGE_TYPE, durable = self.MQ_DURABLE)
	
	def onConnectionClose(self):
		self.log.debug("Starting...")
		
		
		self.stop()
	
	def onConnectionOpen(self, conn):
		self.log.debug("Starting...")
		
		
		self.connection.add_on_close_callback(self.onConnectionClose)
		self.connection.channel(on_open_callback = self.onChannelOpen)
	
	def onConsumerCancelled(self, method_frame):
		self.log.debug("Starting...")
		
		
		if self.channel:
			self.channel.close()
	
	def onExchangeBindOK(self, frame):
		self.log.debug("Starting...")
		
		
		self.consume()
	
	def onExchangeDeclareOK(self, frame):
		self.log.debug("Starting...")
		
		
		self.channel.queue_declare(self.onQueueDeclareOK, exclusive = True)
	
	def onMessage(self, channel, basic_deliver, properties, body):
		self.log.debug("Starting...")
		
		
		if self.onMessageReceived is not None:
			self.onMessageReceived(basic_deliver, properties, body)
	
	def onQueueDeclareOK(self, frame):
		self.log.debug("Starting...")
		
		
		self.MQ_QUEUE_NAME = frame.method.queue
		
		self.channel.queue_bind(self.onExchangeBindOK, exchange = self.MQ_EXCHANGE_NAME, queue = self.MQ_QUEUE_NAME, routing_key = self.MQ_ROUTING_KEY)
	
	def publishMessage(self, message, content_type = "text/plain", headers = None, message_id = None, correlation_id = None, reply_to = None, routing_key = None, declare = True):
		self.log.debug("Starting...")
		
		
		if correlation_id is None:
			correlation_id = "{0}:{1}".format(self.datetime.now().strftime("%Y%m%d%H%M%S%f"), self.uuid.uuid4())
		
		if reply_to is None:
			reply_to = self.MQ_REPLY_TO
		
		if routing_key is None:
			routing_key = self.MQ_ROUTING_KEY
		
		
		conn = self.pika.BlockingConnection(self.parameters)
		chan = conn.channel()
		
		if declare:
			chan.exchange_declare(exchange = self.MQ_EXCHANGE_NAME, type = self.MQ_EXCHANGE_TYPE, durable = self.MQ_DURABLE)
		
		
		p = self.pika.BasicProperties(content_type = content_type, headers = headers, delivery_mode = 2, correlation_id = correlation_id, reply_to = reply_to, message_id = message_id)
		chan.basic_publish(exchange = self.MQ_EXCHANGE_NAME, routing_key = routing_key, body = message, properties = p)
		
		conn.close()
		
		
		return correlation_id
	
	def start(self):
		self.log.debug("Starting...")
		
		
		self.connection = self.pika.SelectConnection(self.parameters, self.onConnectionOpen)
		self.connection.ioloop.start()
	
	def stop(self):
		self.log.debug("Starting...")
		
		
		if self.consumer_tag is not None:
			self.channel.basic_cancel(self.onCancelOK, self.consumer_tag)
		
		self.connection.ioloop.stop()

class SentenceDevice():
	def __init__(self, port, speed, bits, parity, stopbits, trigger_sub = None):
		import threading
		import time
		
		
		self.log = DanLog("SentenceDevice")
		self.serial = None
		self.thread = None
		self.thread_alive = False
		self.threading = threading
		self.time = time
		self.trigger = trigger_sub
		
		self.SENTENCE_END = "\n"
		self.SENTENCE_START = "$"
	
	def dispose(self):
		self.log.debug("Starting...")
		
		
		self.thread_alive = False
		
		if self.serial is not None:
			self.serial.close()
			self.serial = None
	
	def rxThread(self):
		self.log.debug("Starting...")
		
		
		buffer = bytearray()
		
		while self.thread_alive:
			extracted = None
			
			
			bytes = self.serial.inWaiting()
			
			if bytes > 0:
				self.log.info("%d bytes are waiting in the serial buffer." % bytes)
				
				
				# Ensure we're thread-safe
				lock = self.threading.Lock()
				
				with lock:
					try:
						buffer.extend(self.serial.read(bytes))
						
					except Exception, ex:
						self.log.error(str(ex))
			
			x = buffer.find(self.SENTENCE_START)
			
			if x <> -1:
				y = buffer.find(self.SENTENCE_END, x)
				
				if y <> -1:
					self.log.info("A sentence has been found in the buffer.")
					
					
					y += len(self.SENTENCE_END)
					
					# There appears to be complete sentence in there, extract it
					extracted = str(buffer[x:y])
			
			
			if extracted is not None:
				# Remove it from the buffer first
				newbuf = str(buffer).replace(extracted, "", 1)
				
				buffer = bytearray()
				buffer.extend(newbuf)
				
				
				# Now trigger any events
				if self.trigger is not None:
					self.log.info("Triggering sentence subroutine...")
					
					
					self.trigger(extracted)
					
				else:
					self.log.warn("Trigger subroutine not defined, cannot raise sentence event.")
			
			self.time.sleep(0.01)
	
	def setupUnit(self, port, speed, bits, parity, stopbits):
		self.log.debug("Starting...")
		
		
		import serial
		
		
		self.serial = serial.Serial()
		self.serial.baudrate = speed
		self.serial.bytesize = bits
		self.serial.parity = parity
		self.serial.port = port
		self.serial.stopbits = stopbits
		self.serial.timeout = 10.
		self.serial.writeTimeout = None
		self.serial.xonxoff = False
		
		self.serial.open()
		
		self.serial.flushInput()
		self.serial.flushOutput()
	
	def start(self):
		self.log.debug("Starting...")
		
		
		self.thread_alive = True
		
		self.thread = self.threading.Thread(target = self.rxThread)
		self.thread.setDaemon(1)
		self.thread.start()
