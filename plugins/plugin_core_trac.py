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
# StormForce TRAC Plugin                          #
###################################################

from plugin_core_base import PluginBase


###########
# Classes #
###########
class Plugin(PluginBase):
	def __init__(self):
		self.TRAC_DETECTION_METHOD = 1
		self.TRAC_SENSITIVITY = 5
		self.TRAC_STORM_WIDTH = 30 # miles
		self.TRAC_UPDATE_TIME = 15. # seconds
		self.TRAC_VERSION = "0.4.1"
		
		
		PluginBase.__init__(self)
		
		
		self.MAP_MATRIX_SIZE = (600, 600)
		self.MQ_ROUTING_KEY = "{0}.core.trac".format(self.MQ_ROUTING_KEY)
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
						
					elif key == "DetectionMethod":
						self.TRAC_DETECTION_METHOD = int(val)
						
					elif key == "Sensitivity":
						self.TRAC_SENSITIVITY = int(val)
						
					elif key == "StormWidth":
						self.TRAC_STORM_WIDTH = int(val)
						
					elif key == "UpdateTime":
						self.TRAC_UPDATE_TIME = int(val)
	
	def run(self):
		self.log.debug("Starting...")
		
		
		trac_wait = self.datetime.now() + self.timedelta(seconds = self.TRAC_UPDATE_TIME)
		
		while self.running:
			t = self.datetime.now()
			
			if t >= trac_wait:
				try:
					myconn = []
					self.db.connectToDatabase(myconn)
					
					trac_result = self.db.executeSQLQuery("SELECT fnTRAC(%(A)s)", {"A": self.TRAC_DETECTION_METHOD}, myconn)
					trac_status = self.db.executeSQLQuery("SELECT Version, Active, NumberOfStorms, MostActive, MostActiveDistance, Closest, ClosestDistance, Width FROM tblTRACStatus LIMIT 1", conn = myconn)
					trac_storms = self.db.executeSQLQuery("SELECT X, Y, XOffset, YOffset, Name, Intensity, Distance FROM tblTRACStorms ORDER BY ID", conn = myconn)
					
					self.db.disconnectFromDatabase(myconn)
					
					
					if trac_status is not None:
						for row in trac_status:
							self.log.info("TRAC has detected {:d} storms.".format(row[2]))
							
							m = self.constructMessage("Status", {"Version": row[0], "Active": row[1], "NumberOfStorms": row[2], "MostActive": row[3], "MostActiveDistance": float(row[4]), "Closest": row[5], "ClosestDistance": float(row[6]), "Width": row[7]})
							self.mq.publishMessage(m[1], headers = m[0])
							break
						
					else:
						self.log.warn("TRAC status failed to run, review any SQL errors.")
					
					
					if trac_storms is not None:
						ret = []
						
						for row in trac_storms:
							ret.append({"X": row[0], "Y": row[1], "XOffset": row[2], "YOffset": row[3], "Name": row[4], "Intensity": row[5], "Distance": float(row[6])})
						
						m = self.constructMessage("Storms", ret)
						self.mq.publishMessage(m[1], headers = m[0])
						
					else:
						self.log.warn("TRAC storms failed to run, review any SQL errors.")
					
				except Exception, ex:
					self.log.error("An error occurred while running TRAC.")
					self.log.error(ex)
					
				finally:
					trac_wait = self.datetime.now() + self.timedelta(seconds = self.TRAC_UPDATE_TIME)
			
			self.time.sleep(0.1)
	
	def start(self, use_threading = True):
		PluginBase.start(self, use_threading)
		
		
		if self.ENABLED:
			self.log.info("Starting TRAC...")
			self.running = True
			
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
		
		
		# tblTRACDetails
		self.log.debug("TABLE: tblTRACDetails")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblTRACDetails"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "HeaderID", "bigint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "DateTimeOfReading", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "DateTimeOfLastStrike", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "CurrentStrikeRate", "int"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "TotalStrikes", "int"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "Intensity", "varchar(12)"), conn = myconn)
		
		
		# tblTRACGrid
		self.log.debug("TABLE: tblTRACGrid")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblTRACGrid"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACGrid", "X", "smallint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACGrid", "Y", "smallint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACGrid", "Counter", "int"), conn = myconn)
		
		rowcount = int(self.ifNoneReturnZero(self.db.danLookup("COUNT(ID)", "tblTRACGrid", "", conn = myconn)))
		
		if rowcount < 360000:
			self.log.warn("The TRAC grid hasn't been populated (or is invalid), this may take a while to build (%d)..." % rowcount)
			
			
			self.db.executeSQLCommand("""
DO $$
	BEGIN
		DELETE FROM tblTRACGrid;
		
		FOR y IN 0..%d LOOP
			FOR x IN 0..%d LOOP
				INSERT INTO tblTRACGrid(X, Y, Counter) VALUES(x, y, 0);
			END LOOP;
		END LOOP;
	END
$$
""" % (self.MAP_MATRIX_SIZE[1] - 1, self.MAP_MATRIX_SIZE[0] - 1), conn = myconn)
			
		else:
			self.db.executeSQLCommand("UPDATE tblTRACGrid SET Counter = 0 WHERE Counter <> 0", conn = myconn)
		
		
		# tblTRACHeader
		self.log.debug("TABLE: tblTRACHeader")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblTRACHeader"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "GID", "varchar(40)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "CRC32", "varchar(8)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "DateTimeOfDiscovery", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "Bearing", "decimal(10,5)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "Distance", "decimal(10,5)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "DetectionMethod", "smallint"), conn = myconn)
		
		
		# tblTRACStatus
		self.log.debug("TABLE: tblTRACStatus")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblTRACStatus", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblTRACStatus(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Version varchar(6)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN DetectionMethod smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Active boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN NumberOfStorms smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN MostActive varchar(14)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN MostActiveDistance decimal(10,5)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Closest varchar(14)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN ClosestDistance decimal(10,5)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Width smallint", conn = myconn)
		
		self.db.executeSQLCommand("INSERT INTO tblTRACStatus(Version, DetectionMethod, Active, NumberOfStorms, MostActive, MostActiveDistance, Closest, ClosestDistance, Width) VALUES(%(Version)s, %(DetectionMethod)s, %(Active)s, %(NumberOfStorms)s, %(MostActive)s, %(MostActiveDistance)s, %(Closest)s, %(ClosestDistance)s, %(Width)s)", {"Version": self.TRAC_VERSION, "DetectionMethod": self.TRAC_DETECTION_METHOD, "Active": False, "NumberOfStorms": 0, "MostActive": "", "MostActiveDistance": 0, "Closest": "", "ClosestDistance": 0, "Width": self.TRAC_STORM_WIDTH}, myconn)
		
		
		# tblTRACStorms
		self.log.debug("TABLE: tblTRACStorms")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblTRACStorms CASCADE", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblTRACStorms(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN X smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Y smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN XOffset smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN YOffset smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Name varchar(14)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Intensity smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Distance decimal(10,5)", conn = myconn)
		
		
		
		#########
		# Views #
		#########
		self.log.info("Creating views...")
		
		
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwTRACPersistence CASCADE", conn = myconn)
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwTRACStrikesPeak CASCADE", conn = myconn)
		
		self.log.debug("VIEW: vwTRACPersistence")
		self.db.executeSQLCommand("""CREATE VIEW vwTRACPersistence AS
SELECT ID, X, Y, DateTimeOfStrike, EXTRACT(epoch from (LOCALTIMESTAMP - DateTimeOfStrike)) AS StrikeAge
FROM tblLD250Strikes
WHERE DateTimeOfStrike >= LOCALTIMESTAMP - INTERVAL '30 MINUTES' AND DateTimeOfStrike >= (SELECT ServerStarted FROM tblServerDetails LIMIT 1)""", conn = myconn)
		
		self.log.debug("VIEW: vwTRACStrikesPeak")
		self.db.executeSQLCommand("""CREATE VIEW vwTRACStrikesPeak AS
SELECT COUNT(ID) AS StrikeCount, CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp) AS PeakTime, MIN(X) AS MinX, MIN(Y) AS MinY
FROM vwTRACPersistence
GROUP BY CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp)""", conn = myconn)
		
		
		
		#############
		# Functions #
		#############
		self.log.info("Functions...")
		
		
		self.log.debug("FUNCTION: fnTRAC")
		s = """
CREATE OR REPLACE FUNCTION fnTRAC(detectionmethod INT) RETURNS INT AS $$
DECLARE
	strikes_header RECORD;
	strikes_details RECORD;
	trend RECORD;
	
	TRAC_FULL SMALLINT;
	TRAC_HALF SMALLINT;
	TRAC_QUARTER SMALLINT;
	TRAC_SENSITIVITY SMALLINT;
	TRAC_UPDATE_TIME SMALLINT;
	
	x_offset INT;
	y_offset INT;
	offset_x INT;
	offset_y INT;
	
	top_left BIGINT;
	top_right BIGINT;
	bottom_left BIGINT;
	bottom_right BIGINT;
	
	tl INT;
	tr INT;
	bl INT;
	br INT;
	
	new_x INT;
	new_y INT;
	
	o INT;
	a INT;
	
	deg_offset DECIMAL(10,5);
	degx DECIMAL(10,5);
	deg DECIMAL(10,5);
	distance DECIMAL(10,5);
	abs_distance DECIMAL(10,5);
	
	total_count BIGINT;
	
	first_recorded_activity TIMESTAMP;
	last_recorded_activity TIMESTAMP;
	
	current_strike_rate BIGINT;
	peak_strike_rate BIGINT;
	
	guid VARCHAR;
	guid_ss INT;
	crc32 VARCHAR;
	
	intensity_class VARCHAR;
	intensity_trend VARCHAR;
	intensity_trend_symbol VARCHAR;
	
	rises INT;
	falls INT;
	
	average_strike_count DECIMAL(10,5);
	
	diff DECIMAL(10,5);
	
	amount DECIMAL(10,5);
	
	current_name VARCHAR;
	
	tracid BIGINT;
	
	trac_most_active VARCHAR;
	trac_most_active_distance DECIMAL(10,5);
	
	trac_closest VARCHAR;
	trac_closest_distance DECIMAL(10,5);

	corrected_strikes_in_sector BIGINT;
	strikes_in_sector BIGINT;
	storms_found INT;
BEGIN
	-- Populate the variables
	x_offset := 0;
	y_offset := 0;
	storms_found := 0;
	trac_closest_distance := 300.;
	trac_most_active_distance := 0.;
	
	
	-- Populate the "constants"
	TRAC_FULL := (SELECT Width FROM tblTRACStatus LIMIT 1);
	
	IF TRAC_FULL %% 2 > 0 THEN
		TRAC_FULL := TRAC_FULL - 1;
	END IF;
	
	TRAC_HALF := TRAC_FULL / 2;
	TRAC_QUARTER := TRAC_HALF / 2;
	TRAC_SENSITIVITY := 5;
	TRAC_UPDATE_TIME := 1;
	
	RAISE NOTICE 'TRAC detection method is %%', detectionmethod;
	RAISE NOTICE 'TRAC_FULL is %%', TRAC_FULL;
	RAISE NOTICE 'TRAC_HALF is %%', TRAC_HALF;
	RAISE NOTICE 'TRAC_QUARTER is %%', TRAC_QUARTER;
	RAISE NOTICE 'TRAC_SENSITIVITY is %%', TRAC_SENSITIVITY;
	
	
	-- Reset any tables
	UPDATE tblTRACGrid SET Counter = 0 WHERE Counter <> 0;
	UPDATE tblTRACStatus SET Active = FALSE, NumberOfStorms = 0, MostActive = '', MostActiveDistance = 0, Closest = '', ClosestDistance = 0;
	
	DELETE FROM tblTRACStorms;
	
	
	-- Get the unique areas where the strikes are
	DROP TABLE IF EXISTS tmpStrikesHeader;
	
	IF detectionmethod = 0 THEN
		-- Fixed-grid
		CREATE TEMPORARY TABLE tmpStrikesHeader AS
			SELECT div(X, TRAC_FULL) * TRAC_FULL AS X, div(Y, TRAC_FULL) * TRAC_FULL AS Y
			FROM vwTRACPersistence
			GROUP BY div(X, TRAC_FULL) * TRAC_FULL, div(Y, TRAC_FULL) * TRAC_FULL
			HAVING COUNT(ID) >= TRAC_SENSITIVITY
		;
		
	ELSIF detectionmethod = 1 THEN
		-- Freestyle-grid
		CREATE TEMPORARY TABLE tmpStrikesHeader AS
			SELECT DISTINCT X, Y
			FROM vwTRACPersistence
			GROUP BY X, Y
		;
		
	ELSE
		RAISE EXCEPTION 'Unknown TRAC detection method %%.', detectionmethod;
	END IF;
	
	
	FOR strikes_header	IN	SELECT X, Y
							FROM tmpStrikesHeader
							ORDER BY X, Y
						LOOP
		
		IF detectionmethod = 0 THEN
			strikes_in_sector = COALESCE((	SELECT COUNT(ID) - (SELECT SUM(Counter) FROM tblTRACGrid WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL)) AS NoOfStrikes
											FROM vwTRACPersistence
											WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL)
								), 0);
			
		ELSIF detectionmethod = 1 THEN
			strikes_in_sector = COALESCE((	SELECT COUNT(ID) - (SELECT SUM(Counter) FROM tblTRACGrid WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF)) AS NoOfStrikes
											FROM vwTRACPersistence
											WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF)
								), 0);
		END IF;
		
		IF strikes_in_sector = 0 THEN
			RAISE NOTICE 'WARN: Zero strikes where found in the sector.';
		END IF;
		
		corrected_strikes_in_sector := strikes_in_sector;
		
		RAISE NOTICE 'INFO: %% strikes were found within the vicinity of (%%, %%).', strikes_in_sector, strikes_header.X, strikes_header.Y;
		
		
		IF strikes_in_sector >= TRAC_SENSITIVITY THEN
			-- This "sector" may have a storm in it, dig deeper...
			DROP TABLE IF EXISTS tmpStrikesDetails;
			
			IF detectionmethod = 0 THEN
				CREATE TEMPORARY TABLE tmpStrikesDetails AS
					SELECT COUNT(ID) AS NoOfStrikes, (SELECT Counter FROM tblTRACGrid WHERE X = vwTRACPersistence.X AND Y = vwTRACPersistence.Y) AS TrackedStrikes, X, Y
					FROM vwTRACPersistence
					WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y)
					GROUP BY X, Y
				;
				
			ELSIF detectionmethod = 1 THEN
				CREATE TEMPORARY TABLE tmpStrikesDetails AS
					SELECT COUNT(ID) AS NoOfStrikes, (SELECT Counter FROM tblTRACGrid WHERE X = vwTRACPersistence.X AND Y = vwTRACPersistence.Y) AS TrackedStrikes, X, Y
					FROM vwTRACPersistence
					WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF)
					GROUP BY X, Y
				;
			END IF;
			
			
			FOR strikes_details	IN	SELECT NoOfStrikes, TrackedStrikes, X, Y
									FROM tmpStrikesDetails
									ORDER BY X, Y
								LOOP
				
				corrected_strikes_in_sector := corrected_strikes_in_sector - strikes_details.TrackedStrikes;
				
				IF corrected_strikes_in_sector >= TRAC_SENSITIVITY THEN
					UPDATE tblTRACGrid SET Counter = Counter + (strikes_details.NoOfStrikes - strikes_details.TrackedStrikes) WHERE X = strikes_details.X AND Y = strikes_details.Y;
				END IF;
			END LOOP;
			
			DROP TABLE IF EXISTS tmpStrikesDetails;
			
			
			IF corrected_strikes_in_sector >= TRAC_SENSITIVITY THEN
				RAISE NOTICE 'INFO: Deep scan found a storm in (%%, %%).', strikes_header.X, strikes_header.Y;
				
				
				x_offset := 0;
				y_offset := 0;
				storms_found := storms_found + 1;
				
				
				-- Prepare to register the storm
				IF detectionmethod = 0 THEN
					-- No offset required
					offset_x := strikes_header.X;
					offset_y := strikes_header.Y;
					
				ELSIF detectionmethod = 1 THEN
					-- Apply the offset since we search *around* the strike
					offset_x := strikes_header.X - TRAC_HALF;
					offset_y := strikes_header.Y - TRAC_HALF;
				END IF;
				
				top_left := 	(	SELECT COUNT(ID) AS OffsetCount
								FROM vwTRACPersistence
								WHERE (X >= offset_x AND X < offset_x + TRAC_HALF) AND (Y >= offset_y AND Y < offset_y + TRAC_HALF)
							);
				top_right := (	SELECT COUNT(ID) AS OffsetCount
								FROM vwTRACPersistence
								WHERE (X >= offset_x + TRAC_HALF AND X < offset_x + TRAC_FULL) AND (Y >= offset_y AND Y < offset_y + TRAC_HALF)
							);
				bottom_left := (	SELECT COUNT(ID) AS OffsetCount
									FROM vwTRACPersistence
									WHERE (X >= offset_x AND X < offset_x + TRAC_HALF) AND (Y >= offset_y + TRAC_HALF AND Y < offset_y + TRAC_FULL)
								);
				bottom_right :=	(	SELECT COUNT(ID) AS OffsetCount
									FROM vwTRACPersistence
									WHERE (X >= offset_x + TRAC_HALF AND X < offset_x + TRAC_FULL) AND (Y >= offset_y + TRAC_HALF AND Y < offset_y + TRAC_FULL)
								);
				
				total_count := top_left + top_right + bottom_left + bottom_right;
				
				IF total_count <> strikes_in_sector THEN
					RAISE NOTICE 'WARN: The total strike count doesn''t appear match the count in the sector (%%, %%)', total_count, strikes_in_sector;
				END IF;
				
				RAISE NOTICE 'DEBUG: Offset 1 - %% %% %% %%', top_left, top_right, bottom_left, bottom_right;
				
				
				tl := CAST((top_left / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				tr := CAST((top_right / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				bl := CAST((bottom_left / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				br := CAST((bottom_right / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				
				RAISE NOTICE 'DEBUG: Offset 2 - %% %% %% %%', tl, tr, bl, br;
				
				
				-- The greater percentage will make the centre offset to the corner
				x_offset := x_offset + -tl;
				y_offset := y_offset + -tl;
				
				x_offset := x_offset + tr;
				y_offset := y_offset + -tr;
				
				x_offset := x_offset + -bl;
				y_offset := y_offset + bl;
				
				x_offset := x_offset + br;
				y_offset := y_offset + br;
				
				
				-- Apply the offset since we search *around* the strike
				IF detectionmethod = 1 THEN
					x_offset := x_offset + -TRAC_HALF;
					y_offset := y_offset + -TRAC_HALF;
				END IF;
				
				RAISE NOTICE 'DEBUG: Offset 3 - %% %%', x_offset, y_offset;
				
				
				
				------------------------
				-- Register the storm --
				------------------------
				UPDATE tblTRACStatus SET Active = TRUE, NumberOfStorms = NumberOfStorms + 1;
				
				
				-- Calculate the degrees and miles from the X and Y points
				new_x := strikes_header.X + x_offset;
				new_y := strikes_header.Y + y_offset;
				
				o := 0;
				a := 0;
				deg_offset := 0;
				
				IF (new_x >= 0 and new_x < 300) and (new_y >= 0 and new_y < 300) THEN
					-- Top left
					o := 300 - new_x;
					a := 300 - new_y;
					
					deg_offset := 270;
					
				ELSIF (new_x >= 300 and new_x < 600) and (new_y >= 0 and new_y < 300) THEN
					-- Top right
					o := new_x - 300;
					a := 300 - new_y;
					
					deg_offset := 0;
					
				ELSIF (new_x >= 0 and new_x < 300) and (new_y >= 300 and new_y < 600) THEN
					-- Bottom left
					o := 300 - new_x;
					a := new_y - 300;
					
					deg_offset := 180;
					
				ELSE
					-- Bottom right
					o := new_x - 300;
					a := new_y - 300;
					
					deg_offset := 90;
				END IF;
				
				
				-- Numbers will be zero based, so add one
				o := o + 1;
				a := a + 1;
				
				RAISE NOTICE 'DEBUG: O = %%, A = %%', o, a;
				
				
				-- Time for a bit of trigonometry
				degx := degrees(atan(o / a));
				deg := degx + deg_offset;
				distance := sqrt(power(o, 2) + power(a, 2));
				abs_distance := abs(distance);
				
				RAISE NOTICE 'DEBUG: Degrees = %%, X = %%, H = %%', deg, degx, distance;
				
				
				-- Gather some stats
				IF detectionmethod = 0 THEN
					first_recorded_activity := (SELECT MIN(DateTimeOfStrike) AS FirstRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL));
					last_recorded_activity := (SELECT MAX(DateTimeOfStrike) AS LastRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL));
					
					current_strike_rate := (SELECT COUNT(ID) FROM vwTRACPersistence WHERE DateTimeOfStrike >= LOCALTIMESTAMP - (TRAC_UPDATE_TIME || ' MINUTES')::INTERVAL AND (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL));
					peak_strike_rate := (SELECT MAX(StrikeCount) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X AND MinX < strikes_header.X + TRAC_FULL) AND (MinY >= strikes_header.Y AND MinY < strikes_header.Y + TRAC_FULL));
					
				ELSIF detectionmethod = 1 THEN
					first_recorded_activity := (SELECT MIN(DateTimeOfStrike) AS FirstRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF));
					last_recorded_activity := (SELECT MAX(DateTimeOfStrike) AS LastRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF));
					
					current_strike_rate := (SELECT COUNT(ID) FROM vwTRACPersistence WHERE DateTimeOfStrike >= LOCALTIMESTAMP - (TRAC_UPDATE_TIME || ' MINUTES')::INTERVAL AND (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF));
					peak_strike_rate := (SELECT MAX(StrikeCount) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X - TRAC_HALF AND MinX < strikes_header.X + TRAC_HALF) AND (MinY >= strikes_header.Y - TRAC_HALF AND MinY < strikes_header.Y + TRAC_HALF));
				END IF;
				
				IF peak_strike_rate = 0 THEN
					peak_strike_rate := current_strike_rate;
				END IF;
				
				guid := encode(digest(concat(strikes_header.X, strikes_header.X + TRAC_FULL, strikes_header.Y, strikes_header.Y + TRAC_FULL, first_recorded_activity), 'sha1'), 'hex');
				
				-- Pick the middle eight characters since we don't have CRC32, we just need it unique for the session
				guid_ss := (length(guid) / 2) - 4;
				crc32 := substring(guid from guid_ss for 8);
				
				RAISE NOTICE 'DEBUG: guid = %%, guid_ss = %%, crc32 = %%', guid, guid_ss, crc32;
				
				
				-- Since we have the strike rate we can determine the classification of the storm
				intensity_class := 'N/A';
				intensity_trend := 'N/A';
				intensity_trend_symbol := '';
				
				If current_strike_rate < 10 THEN
					intensity_class := 'Very Weak';
					
				ELSIF current_strike_rate < 20 THEN
					intensity_class := 'Weak';
					
				ELSIF current_strike_rate < 40 THEN
					intensity_class := 'Moderate';
					
				ELSIF current_strike_rate < 50 THEN
					intensity_class := 'Strong';
					
				ELSIF current_strike_rate < 60 THEN
					intensity_class := 'Very Strong';
					
				ELSE
					intensity_class := 'Severe';
				END IF;
				
				
				-- Calculate the trend by counting the rises and the falls based on the average strike rate, not the best way but can be improved later
				rises := 0;
				falls := 0;
				
				IF detectionmethod = 0 THEN
					average_strike_count := (SELECT SUM(StrikeCount) / COUNT(*) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X AND MinX < strikes_header.X + TRAC_FULL) AND (MinY >= strikes_header.Y AND MinY < strikes_header.Y + TRAC_FULL));
					
				ELSIF detectionmethod = 1 THEN
					average_strike_count := (SELECT SUM(StrikeCount) / COUNT(*) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X - TRAC_HALF AND MinX < strikes_header.X + TRAC_HALF) AND (MinY >= strikes_header.Y - TRAC_HALF AND MinY < strikes_header.Y + TRAC_HALF));
				END IF;
				
				
				DROP TABLE IF EXISTS tmpStrikesTrend;
				
				IF detectionmethod = 0 THEN
					CREATE TEMPORARY TABLE tmpStrikesTrend AS
						SELECT StrikeCount, PeakTime
						FROM vwTRACStrikesPeak
						WHERE (MinX >= strikes_header.X AND MinX < strikes_header.X + TRAC_FULL) AND (MinY >= strikes_header.Y AND MinY < strikes_header.Y + TRAC_FULL)
					;
					
				ELSIF detectionmethod = 1 THEN
					CREATE TEMPORARY TABLE tmpStrikesTrend AS
						SELECT StrikeCount, PeakTime
						FROM vwTRACStrikesPeak
						WHERE (MinX >= strikes_header.X - TRAC_HALF AND MinX < strikes_header.X + TRAC_HALF) AND (MinY >= strikes_header.Y - TRAC_HALF AND MinY < strikes_header.Y + TRAC_HALF)
					;
				END IF;
				
				
				FOR trend	IN	SELECT StrikeCount
								FROM tmpStrikesTrend
								ORDER BY PeakTime
							LOOP
					
					diff := trend.StrikeCount - average_strike_count;
					
					IF diff > 0 THEN
						rises := rises + 1;
						
					ELSIF diff < 0 THEN
						falls := falls + 1;
					END IF;
				END LOOP;
				
				DROP TABLE IF EXISTS tmpStrikesTrend;
				
				
				RAISE NOTICE 'DEBUG: Rises = %%, falls = %%', rises, falls;
				
				
				IF rises > falls THEN
					intensity_trend := 'Intensifying';
					intensity_trend_symbol := '^';
					
				ELSIF falls > rises THEN
					intensity_trend := 'Weakening';
					intensity_trend_symbol := '.';
					
				ELSE
					intensity_trend := 'No Change';
					intensity_trend_symbol := '-';
				END IF;
				
				
				-- Strike rate amount (mainly for the progress bar)
				amount := 0.;
				
				IF current_strike_rate > 50 THEN
					amount := 1.;
					
				ELSE
					amount := current_strike_rate / 50.;
				END IF;
				
				current_name := crc32 || intensity_trend_symbol || current_strike_rate;
				
				RAISE NOTICE 'INFO: Storm name is %%', current_name;
				
				
				-- Make log of the storm in the database
				tracid := COALESCE((SELECT ID FROM tblTRACHeader WHERE GID = guid LIMIT 1), 0);
				
				IF tracid = 0 THEN
					-- Storm not found in database, add new entry
					RAISE NOTICE 'INFO: Storm GUID %% not found in header, creating entry...', guid;
					
					
					INSERT INTO tblTRACHeader(GID, CRC32, DateTimeOfDiscovery, Bearing, Distance, DetectionMethod)
					VALUES(guid, crc32, first_recorded_activity, deg, abs_distance, 1);
					
					
					tracid := COALESCE((SELECT ID FROM tblTRACHeader WHERE GID = guid LIMIT 1));
					
					IF tracid = 0 THEN
						RAISE NOTICE 'WARN: Failed to locate the newly created record for storm ID %%', guid;
					END IF;
				END IF;
				
				-- Double-check
				IF tracid > 0 THEN
					INSERT INTO tblTRACDetails(HeaderID, DateTimeOfReading, DateTimeOfLastStrike, CurrentStrikeRate, TotalStrikes, Intensity)
					VALUES(tracid, LOCALTIMESTAMP, last_recorded_activity, current_strike_rate, total_count, intensity_trend);
				END IF;
				
				
				RAISE NOTICE 'DEBUG: total_count = %%, trac_most_active_distance = %%', total_count, trac_most_active_distance;
				
				IF total_count > trac_most_active_distance THEN
					trac_most_active := current_name;
					trac_most_active_distance := abs_distance;
					
					UPDATE tblTRACStatus SET MostActive = trac_most_active, MostActiveDistance = trac_most_active_distance;
				END IF;
				
				
				RAISE NOTICE 'DEBUG: abs_distance = %%, trac_closest_distance = %%', abs_distance, trac_closest_distance;
				
				IF abs_distance < trac_closest_distance THEN
					trac_closest := current_name;
					trac_closest_distance := abs_distance;
					
					UPDATE tblTRACStatus SET Closest = trac_closest, ClosestDistance = trac_closest_distance;
				END IF;
				
				
				-- Now for client purposes
				INSERT INTO tblTRACStorms(X, Y, XOffset, YOffset, Name, Intensity, Distance)
				VALUES(strikes_header.X, strikes_header.Y, x_offset, y_offset, current_name, amount, abs_distance);
			END IF;
		END IF;
	END LOOP;
	
	
	-- Clean up
	DROP TABLE IF EXISTS tmpStrikesHeader;
	DROP TABLE IF EXISTS tmpStrikesDetails;
	DROP TABLE IF EXISTS tmpStrikesTrend;
	
	
	
	-- Return
	RAISE NOTICE 'TRAC has found %% storms.', storms_found;
	
	RETURN storms_found;
END
$$ LANGUAGE plpgsql;
"""
		self.db.executeSQLCommand(s, conn = myconn)
		
		
		
		###########
		# Indices #
		###########
		self.log.info("Indices...")
		
		self.log.debug("INDEX: tblTRACDetails_HeaderID")
		self.db.executeSQLCommand(self.db.createIndexSQLString("tblTRACDetails_HeaderID", "tblTRACDetails", "HeaderID"), conn = myconn)
		
		
		self.log.debug("INDEX: tblTRACGrid_X_Y")
		self.db.executeSQLCommand(self.db.createIndexSQLString("tblTRACGrid_X_Y", "tblTRACGrid", "X, Y"), conn = myconn)
		
		
		self.db.disconnectFromDatabase(myconn)
	
	def writeXMLSettings(self):
		PluginBase.writeXMLSettings(self)
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.Document()
			settings = xmldoc.createElement("PluginTRAC")
			xmldoc.appendChild(settings)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Enabled", str(self.ENABLED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("DetectionMethod", str(self.TRAC_DETECTION_METHOD))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("Sensitivity", str(self.TRAC_SENSITIVITY))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("StormWidth", str(self.TRAC_STORM_WIDTH))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdateTime", str(self.TRAC_UPDATE_TIME))
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
