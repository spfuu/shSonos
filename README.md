Overview
-------------------------------
	
The shSonos project is primary a simple (python) sonos control server, mainly based on the brilliant SoCo project https://github.com/SoCo/SoCo). 
It implements a lightweight http server, wich is controlled by simple commands.
 
In addtion , i decided to write a plugin for the fantastic "Smarthome.py Project" to control sonos speakers in a smart home. (https://github.com/mknx/smarthome/)

 
Requirements:
--------------------------------

server:	python3 (with libraries requests)

client-side: nothing special, just send your commands over http or use the plugin to control the speakers within
smarthome.py



Install:
--------------------------------

(setup.py coming soon)

	1. copy the entire files to your preferred location (writeable)


	2. (optional) if you want to start shShonos as background service, edit sonos_server.sh

		* edit DIR variable to /your/path/location

		* edit DAEMON_USER (optional)
		
		* edit LOCALIP and set it to the server's local network ip (e.g. 192.168.0.70)

		* copy file to /etc/init.d if you want to autostart shShonos on system start

		* chmod +x /path/to/sonos_server.sh

		* chmod +x /path/to/sonos_server.py
		
		* ./path/to/sonos_server start

		* (optional) edit sonos_server.py to edit host and port for the http server
		  (default: 0.0.0.0:9999)


	3. for raspberry pi user, please follow these instruction prior to point 2:

		sudo apt-get install curl
		sudo curl http://python-distribute.org/distribute_setup.py | python3
		sudo curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python3
		pip install requests


	BE PATIENT! The whole process takes up to 20-30min on the raspberry due to the low system
	performance.

Testing:
--------------------------------

	Because of the server-client design, you're not bound to python to communicate 
	with the sonos server instance. Open your browser and control your speaker. This project is focused on
	house automation, therefore there is no web interface.

	Most of the commands return a simple "200 - OK" or "400 Bad Request". The return values
	will be send over udp to all subscribed clients. To receive these messages, you must have an UDP port
	open on your client.
	
	To susbscribe your client for this messages, simply type in following command in your browser:
	(this step is not necessary for smarthome.py-plugin user, it's done automatically)

	http://<sonos_server_ip:port>/client/subscribe/<udp_port>    (udp port is your client port)
	
	To unsubscribe:
	
	http://<sonos_server_ip:port>/client/unsubscribe/<udp_port>
	
	After subscription, your client will receive all status updates of all sonos speakers in the network, 
	whether	they were triggerd by you or other clients (iPad, Android) 
	
	Most of the commands need a speaker uid. Just type 
	
		http://<sonos_server_ip:port>/client/list
		
	to get a short overview of your sonos speakers in the network and to retrieve the uid.
		

First implemented commands (more coming soon):
-----------------------------------------------

	volume
	
		set:
		
			http://<sonos_server:port>/speaker/<sonos_uid>/volume/set/<value:0-100>
		
		get:
		
			http://<sonos_server:port>/speaker/<sonos_uid>/volume

		response (udp):
		
			speaker/<sonos_uid>/volume/<value>          (0|1)
		
	mute
		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/mute/set/<value:0|1>
			
		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/mute
			
		response (udp)
			speaker/<sonos_uid>/mute/<value>            (0|1)
	
	led
		set:
				
			http://<sonos_server:port>/speaker/<sonos_uid>/led/set/<value:0|1>
		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/led
		
		response (udp)
		    speaker/<sonos_uid>/led/<value>             (0|1)

	play

	    set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play/set/<value:0|1>

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/play

		response (udp)
			speaker/<sonos_uid>/play/<value>            (0|1)

    pause

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/pause/set/<value:0|1>

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/pause

		response (udp)
			speaker/<sonos_uid>/pause/<value>           (0|1)

    stop

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/stop/set/<value:0|1>

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/stop

		response (udp)
			speaker/<sonos_uid>/stop/<value>            (0|1)


    artist

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/artist

		response (udp)
			speaker/<sonos_uid>/artist/<value>

    track

   		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/track

		response (udp)
			speaker/<sonos_uid>/track/<value>


    streamtype

   		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/streamtype

		response (udp)
			speaker/<sonos_uid>/streamtype/<value>      (radio|music)



	list
		get:

			http://<sonos_server:port>/client/list
		
		response (http)
			
			<html code ....
				uid : rincon_000e58c3892e01400

				ip : 192.168.178.40

				model : ZPS1
				.
				.
			... htmlcode>			
			
TO DO:
--------------------------------

	* full SoCo command implementation
	* documentation
	* setup.py
	* and many more
 


	
