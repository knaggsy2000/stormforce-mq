# StormForce MQ - Release v0.2.0 on 04/09/2016

```
Link:         https://github.com/knaggsy2000/stormforce-mq
Code Quality: Alpha - Expect plenty of bugs!

For license and copyright, please see the LICENSE file.
```


## Preface
StormForce MQ (SMQ) is the third generation of the StormForce series of software: -


```
1st Generation: StormForce    - https://github.com/knaggsy2000/stormforce-legacy
2nd Generation: StormForce XR - https://github.com/knaggsy2000/stormforce-xr
3rd Generation: StormForce MQ - https://github.com/knaggsy2000/stormforce-mq
```


Based on the StormForce XR codebase, SMQ uses RabbitMQ (https://www.rabbitmq.com/) as its communication core is designed for real-time notification of strikes, storms, and allows extensibility through the use of plugins (wrote in Python).  The plugins handle both the hardware interface and the extensibility of how the data is handled and is configured with separate XML files (one for each plugin).  When SMQ is started for the first time it will create the XML settings files for everything, you will then need to close SMQ and configure each plugin as required, as by-default they will be disabled.


The core plugins ("plugin_core_*.py") provide the following functionality: -

```
Name:        Base
Filename:    plugin_core_base.py
Routing Key: N/A
Description: Provides the skeleton framework needed for the plugin system

Name:        Debug
Filename:    plugin_core_debug.py
Routing Key: events.#
Description: Provides debug information to the console which is useful for debugging, also useful if you want write your own plugins

Name:        MQ Client
Filename:    plugin_core_mqclient.py
Routing Key: events.#
Description: Provides real-time messages of strikes and storms and broadcasts them for use with the SMQ client - this plugin is based from the repeater plugin codebase

Name:        Repeater
Filename:    plugin_core_repeater.py
Routing Key: events.#
Description: Publishes all the received events onto a different MQ exchange

Name:        Server Details
Filename:    plugin_core_serverdetails.py
Routing Key: events.plugin.core.serverdetails
Description: Provides the functionality which handles the server details

Name:        Strike Counters
Filename:    plugin_core_strikecounters.py
Routing Key: events.plugin.core.strikecounters
Description: Provides the functionality which handles the strike counters and resets them when required

Name:        SXR
Filename:    plugin_core_sxr.py
Routing Key: N/A
Description: Provides an XMLRPC frontend (using the Twisted library) which is 100% compatible with the StormForce XR client.  Requires the Boltek LD-250 hardware plugin

Name:        TRAC
Filename:    plugin_core_trac.py
Routing Key: events.plugin.core.trac
Description: Provides the functionality which handles the tracking of thunderstorms.  Requires the Boltek LD-250 hardware plugin

Name:        Unit Status
Filename:    plugin_core_unitstatus.py
Routing Key: events.plugin.core.unitstatus
Description: Provides the functionality which handles the unit status
```

When writing your own plugins, ensure the filename starts with "plugin_<NAME>" (e.g. "plugin_myplugin") and not "plugin_core", this is to identify the core plugins provided by this project.  The same goes if you decide to use your own routing key, don't use anything which starts with "events.plugin.core" but instead use "events.plugin.<NAME>".  The routing key of "event.plugin" will be passed to the initialisation of the plugin so you can use it to prefix your own or even not use it at all.



The core hardware plugins ("hardware_core_*.py") provides the interface between hardware and SMQ: -

```
Hardware:    N/A
Name:        Base
Filename:    hardware_core_base.py
Routing Key: N/A
Description: Provides the skeleton framework needed for the hardware system

Hardware:    Boltek EFM-100
Name:        EFM100
Filename:    hardware_core_efm100.py
Routing Key: events.hardware.core.efm100
Description: Interfaces with the Boltek EFM-100 and writes the information to the SMQ database, also useful if you want to write your own hardware plugin so SMQ can use it

Hardware:    Boltek LD-250
Name:        LD250
Filename:    hardware_core_ld250.py
Routing Key: events.hardware.core.ld250
Description: Interfaces with the Boltek LD-250 and writes the information to the SMQ database

Hardware:    Boltek LD-350
Name:        LD350
Filename:    hardware_core_ld350.py
Routing Key: events.hardware.core.ld350
Description: *** Currently does not work due to how that unit exposes itself to the operating system ***  Interfaces with the Boltek LD-350 and writes the information to the SMQ database
```

When writing your own hardware plugins, ensure the filename starts with filename "hardware_<NAME>" (e.g. "hardware_myhardware") and not "hardware_core", this is to identify the core hardware provided by this project.  The same goes if you decide to use your own routing key, don't use anything which starts with "events.hardware.core" but instead use "events.hardware.<NAME>".  The routing key of "event.hardware" will be passed to the initialisation of the plugin so you can use it to prefix your own or even not use it at all.


Both the hardware and plugins are provided with their own connection to both the SQL database and to RabbitMQ.  Messages are produced (typically) from the hardware to SMQ's topic exchange with the routing key "events.hardware".  Each of the hardware issue their own events according to the hardware they are providing support for to the plugins, which may use a different or an amended routing key (detailed above) - use the debug plugin to help you determine how you should handle the messages that have been consumed.  The plugins then, if required, react to the messages that have been broadcast - the plugins are required to acknowledge the message once they have finished processing the message.  While hardware would usually only produce the messages, it's also acceptable for the plugins to also produce a message - for example, the TRAC plugin does this to announce once it's ran with the number of storms that have been detected.  Just be careful not to cause a loopback with messages as by default, the same routing key would be used.

Since v0.2.0 both the hardware and the plugins can be ran independently in another Python process either created by the SMQ server or by-hand.  You can enable this feature in the server's XML settings file.  To allow both the hardware and the plugins to run without any parameters, the SMQ server places a "smq_extensible.xml" into both the "hardware" and the "plugins" folders on startup.  If you want to run either the hardware or the plugins on a different box then ensure you also copy the extensible XML file too (after initially configuring and running the SMQ server) as well as ensuring the remote connections to both PostgreSQL and RabbitMQ is accepted from that different box.  At this point in time, if you run either the hardware and/or a plugin as separate process the SMQ server will have it marked as enabled even if not enabled in the XML file.  This will be rectified in a later version.


## Notes (S = server, C = client)
###v0.2.0 - 4th September 2016
>  1. (S) Removed the MQ initialisation from the server as it didn't even use it.
>  2. (S) MQ client plugin no longer fires two threads which both did the same job.
>  3. (S) Fixed the shared MQ class as the "onConnectionClose" callback didn't have the correct arguments.
>  4. (S) Both hardware and plugins now read the settings from a settings XML file placed in the same directory, rather than being passed them - this allows the hardware and plugins to be ran on completely box.
>  5. (S) The initialisation of both the hardware and the plugins are now done in a separate class.
>  6. (S) The plugins can now be started in their own Python process using the "smq_extensible.xml" file (related to point 4) either through the SMQ server or directly via Python.
>  7. (S) The plugins now only connect to MQ and the database if they are enabled.
>  8. (S) The plugin base now has a separate routine for updating the database.  The core plugins have been amended where required.
>  9. (S) The hardware base now has a separate routine for updating the database.  The core hardware have been amended where required.
> 10. (S) The hardware can now be started in their own Python process using the "smq_extensible.xml" file (related to point 4) either through the SMQ server or directly via Python.
> 11. (S) Moved the remaining server details (SQL and variables) from the server and placed into the plugin.
> 12. (S) Fixed the uptime issue sent out by the server.
> 13. (S) Fixed the variable initialisation for the SXR plugin.
> 14. (S) Fixed the variable initialisation for the TRAC plugin.

###v0.1.1 - 30th August 2016
> 1. (S) Fixed issue with strike counters where it incorrectly reset the minute counter every second.
> 2. (S) Removed UI-based events from the MQ client plugin as it doesn't deal with them, the client should.
> 3. (S) New core plugin: unit status.
> 4. (S) Plugins now get initialised before the hardware.
> 5. (S) New core plugin: server details.
> 6. (S) TRAC plugin incorrectly updated its wait time causing it to never run.
> 7. (S) Various plugins weren't serialising correctly to JSON which used types datetime, decimals, etc.  Should be fixed now.
> 8. (C) SMQ UI-based client.

###v0.1.0 - 28th August 2016
> 1. (S) Initial release - no SMQ client (yet).

###v0.0.0 - 20th July 2016
> 1. (S) Development started.


##Usage
On the command line: -

```
% python smq_server.py
% python smq_client.py
```

If you wanted (for example) to run any of the hardware plugins on a different box: -

```
% python hardware/hardware_core_efm100.py
% python hardware/hardware_core_ld250.py
% python hardware/hardware_core_ld350.py
```

The same goes the for the plugins: -

```
% python plugins/plugin_core_debug.py
% python plugins/plugin_core_mqclient.py
% python plugins/plugin_core_repeater.py
% python plugins/plugin_core_serverdetails.py
% python plugins/plugin_core_strikecounters.py
% python plugins/plugin_core_sxr.py
% python plugins/plugin_core_trac.py
% python plugins/plugin_core_unitstatus.py
```

You can also run them from within their own directory too.  If you choose to run some hardware and/or plugins on a separate box, ensure you disable those plugins on the main SMQ server and don't forget to copy the "smq_extensible.xml" file from the appropriate directory to the separate box.  You do not need to run the SMQ server on the separate box to run them, as both the hardware and the plugins are independent.  If you want to run either the hardware and/or the plugins as a separate process on the same box as the SMQ server, enable that option in the server XML settings file.  It will then take care of it for you.


##TRAC Detection Methods

```
0 = Uses a fixed-grid to determine whether the number of strikes exceeds a threshold
1 = Uses a freestyle-grid to determine whether the number of strikes exceeds a threshold (recommended)
```


##Installation
###FreeBSD
Here are the packages I've currently got installed for StormForce MQ to work: -

```
/usr/ports/databases/postgresql95-server/
/usr/ports/databases/postgresql95-client/
/usr/ports/databases/postgresql95-contrib/
/usr/ports/lang/python/
/usr/ports/comms/py-serial/
/usr/ports/databases/py-psycopg2/
/usr/ports/devel/py-game/
/usr/ports/devel/py-pika/
/usr/ports/devel/py-twisted/
/usr/ports/math/py-matplotlib/
```


###Linux
**This section needs updating.**


###MacOS
Untested - But no problems are expected.


###Microsoft Windows
**This section needs updating.**


##PostgreSQL
All that StormForce MQ needs is the actual database and username setup, the tables, views, indices, and functions will be handled by the program itself.

Run the following commands: -

```
 # su pgsql
 $ createdb stormforce_mq
 $ psql stormforce_mq
=# CREATE USER stormforce_user WITH password 'password';
=# GRANT ALL PRIVILEGES ON DATABASE stormforce_mq TO stormforce_user;
=# ALTER DATABASE stormforce_mq OWNER TO stormforce_user;
=# CREATE EXTENSION pgcrypto;
```

Then give StormForce MQ the connection details in the settings XML file.


##RabbitMQ
All that StormForce MQ needs is the username and password setup, the exchange will be configured by the program itself.

I would recommend enabling the web management interface in RabbitMQ and configuring the username and password using that.  This will also give you a more visual interface to RabbitMQ.


Once setup, give StormForce MQ the connection details in the settings XML file.


##FAQ

```
Q. What operating systems does it support?
A. I develop and test StormForce MQ with FreeBSD 10.2, it should work in other POSIX compliant operating systems as well other distros of Linux.

Q. Can I create (port) of StormForce MQ?
A. By all means! Be sure to read the LICENSE first.

Q. I've found a bug! What do I do?
A. Let me know by raising it as an issue so I can fix it in the next version.

Q. I would like a feature that's not in StormForce MQ...
A. I'm currently not accepting feature requests at this stage.

Q. Can StormForce MQ send it's strike data to Blitzortung?
A. Unfortunately this is not possible due the strikes needing microsecond accuracy which the Boltek LD-250 doesn't provide, even when used with a GPS unit.  Egor from Blitzortung informed me of this.
```

##Legal
I am in no way affiliated or in partnership with either Boltek, Google, NASA, Microsoft, or anyone else.
