shSonos    - sonos control server -

shSonos is a simple sonos control server, mainly based on the brillaint SoCo project (https://github.com/SoCo/SoCo). 
It implements a tcp socket server, wich is controlled through simple commands.
 
Requirements:

python3 (with libraries requests, lxml installed)


Install:

(setup.py coming soon)

1. copy the entire files to your preffered location (writeable)
2. (optional) if you want to start shShonos as background service, edit sonos_server.sh
	2.1 edit DIR variable to /your/path/location
	2.2 edit DAEMON_USER (optional)
	2.3 copy file to /etc/init.d if you want to autostart shShonos on system start
	2.3 chmod +x /path/to/sonos_server.sh
	2.4 ./path/to/sonos_server start
	2.5 (optional) eit sonos_server.py to edit host and port (default: localhost:9999)

3. for raspberry pi user, please follow these instruction prior to point 2:

	sudo apt-get install curl
	sudo apt-get install libxml2-dev libxslt1-dev
	curl http://python-distribute.org/distribute_setup.py | python3
	curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python3
	pip install requests
	pip install lxml

	BE PATIENT! The whole process tooks about 50-60min on the raspberry due to the low system
	performance.

4. testing:
	Because of the server-client design, you're not bound to python to communicate 
	with the sonos server instance. For simplicity, you can use the included sonos_client.py.

	chmod +x /path/to/sonos_client.py
 	

first implemented commands (more coming soon):

	refresh quick

		* quick refresh of sonos speakers in the network (online status, uid, model name)
		* example: sonos_client.py refresh quick

		server response:

		<result status="True" type="data">
  			<data/>
  			<info></info>
		</result>


	refresh all

		* searches for detailled information of all speakers
		* example: 	sonos_client.py refresh all

		server response:

		<result status="True" type="data">
  			<data/>
  			<info> sonos speaker(s) refreshed.</info>
		</result>

	refresh single {uid, ip, id}

		* collects information of a single sonos speaker by its ip, database id or uid
		* example: 	sonos_client.py single ip 192.168.0.12
				sonos_client.py single uid RINCON_12345678
				sonos_client.py single id 1
		
		server response:

		<result status="True" type="data">
  			<data/>
  			<info>Sonos speaker with id '1' and ip '192.168.178.40' refreshed.</info>
		</result>

	list all [complete,online,offline]
	
		* lists detailed information of all sonos speakers
		* important: the data is database-cached, perform a refresh to get 'live' data
	
		* server response (could be more than one speaker tag)

		<result status="True" type="data">
  			<data>
    				<speaker>
      					<hardware_version>1.8.3.7-2</hardware_version>
      					<id>1</id>
      					<ip>192.168.0.40</ip>
      					<mac_address>00:0E:58:D3:59:22</mac_address>
      					<model>ZPS1</model>
      					<serial_number>00-0E-58-D3-59-22:7</serial_number>
      					<software_version>24.0-71060</software_version>
      					<status>1</status>
      					<uid>RINCON_000E58C3892E215432</uid>
      					<zone_icon>x-rincon-roomicon:living</zone_icon>
      					<zone_name>living room</zone_name>
    				</speaker>
  			</data>
  			<info></info>
		</result>

	list single [ip, id, uid]
	
		* lists detailed information of one sonos speaker
		* server response as above

	speaker mute [on, off, get] {uid} [refresh]

		* gets or sets the speaker's mute status
		* uid: speaker' uid
		* refresh: performs a quick refresh to get speaker's online status (faster server response, 
		  if speaker is offline)

		* server response:

		<result status="True" type="data">
			<data>
   	 			<mute>False</mute>
  			</data>
  			<info></info>
		</result>
		
	speaker statuslight [on, off, get] {uid} [refresh]
		
		* gets or sets the speaker's statuslight
		* uid: speaker' uid
                * refresh: performs a quick refresh to get speaker's online status (faster server response,
                  if speaker is offline)

                * server response:
 
		<result status="True" type="data">
  			<data>
    				<statuslight>True</statuslight>
  			</data>
  			<info></info>
		</result>

	speaker volume [set {0-100}, get] {uid} [refresh]
	
		* gets or sets he speaker's volume
		* uid: speaker' uid
                * refresh: performs a quick refresh to get speaker's online status (faster server response,
                  if speaker is offline)

                * server response:

		<result status="True" type="data">
			<data>
    				<volume>10</volume>
  			</data>
  			<info></info>
		</result>

Full command examples:

	sonos_client.py refresh all
	sonos_client.py list single uid RINCON_1234567890 refresh
	sonos_client.py speaker volume set 15 RINCON_1234567890

More commands coming soon!


You can perform '-h' on any command to see the available options (help description will be added later)

	sonos_client.py speaker mute -h
	
		*server response:

		<result type="exception">
  			<exception>usage: sonos_server.py speaker mute [-h] {on,off,get} device_uid [refresh]

				positional arguments:
  				{on,off,get}  Get or set the speaker' mute status.
  				device_uid    A device uid for a sonos speaker within the sqlite database.
  				refresh       Performs a quick refresh to get online / offline status of the
                		device.

				optional arguments:
				-h, --help    show this help message and exit
			</exception>
  			<info></info>
		</result>

Yes i know, not perfect. A help message is not an exception. This is on of the first things i want to redesign.
	


Any exception is thrown in the following xml syntax:

	<result type="exception">
  		<exception>HTTPConnectionPool(host='192.168.178.40', port=1400): Max retries exceeded with url: /status/zp (Caused by &lt;class 'socket.error'&gt;: [Errno 113] No route to host)</exception>
  		<info></info>
	</result



TO DO:

	* full SoCo command implementation
	* documentation
	* setup.py
	* smarthome.py plugin
	* and many more
 


	
