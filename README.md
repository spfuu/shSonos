Release
-------------------------------
v0.1.2  - 2014-01-30

    added command 'track_duration'
    added command 'track_position'
    added command 'seek'

v0.1.1  - 2014-01-29

    bugfix in sonos_command.py

v0.1    - 2014-01-28

    initial release
    setup package


Overview
-------------------------------
	
The shSonos project is primary a simple (python) sonos control server, mainly based on the brilliant SoCo project https://github.com/SoCo/SoCo). 
It implements a lightweight http server, wich is controlled by simple commands.
 
In addition , i decided to write a plugin for the fantastic "Smarthome.py Project" to control sonos speakers in a smart home. (https://github.com/mknx/smarthome/)

 
Requirements:
--------------------------------

server:	python3 (with library requests)

client-side: nothing special, just send your commands over http or use the plugin to control the speakers within
smarthome.py



Install:
--------------------------------


1.SETUP


Under the github folder "server.sonos/dist/" you'll find the actual release as a tar.gz file
Unzip this file with:

    tar -xvf sonos_broker_release.tar.gz

(adjust the filename to your needs)

Go to the unpacked folder and run setup.py with:

    sudo python3 setup.py install

This command will install all the python packages and places the start script to the python folder
"/user/local/bin"

Run the file sonos_broker with:

    ./sonos_broker


Normally, the script finds the interal ip address of your computer. If not, you have start the script with
the following parameter:

    ./sonos_broker --localip x.x.x.x

(x.x.x.x means your ip: run ifconfig - a to find it out)



2.CONFIGURATION (optional)

There is also a sh-script to daemonize the sonos_broker start named sonos_broker.sh.
If you want to start sonos_broker as background service, edit sonos_broker.sh:

Edit DIR variable to /path/location/of/sonos_broker (default: /usr/local/bin)

Make the file executable with:

    chmod +x /usr/local/bin/sonos_broker.sh

Start service with:

    sudo ./path/to/sonos_broker.sh start


To autostart the service on system boot, please follow the instruction for your linux distribution.


Attention!! Please notice that the script is running as with the 'background' flag. In order that, there is
no debug or error output. To get these hints in failure cases, remove this flag in sonos_broker.sh

from:

    start-stop-daemon -v --start --pidfile $PIDFILE --background --make-pidfile --startas $DAEMON --

to:

    start-stop-daemon -v --start --pidfile $PIDFILE --make-pidfile --startas $DAEMON --



3.RASPBERRY PI USER

For raspberry pi user, please follow these instruction prior to point 2:

    sudo apt-get update
    sudo apt-get upgrade
    sudo easy_install3 requests



Testing:
--------------------------------

Because of the server-client design, you're not bound to python to communicate
with the sonos broker instance. Open your browser and control your speaker. This project is focused on
house automation, therefore there is no web interface. (maybe this is your contribution :-) )

Most of the commands return a simple "200 - OK" or "400 Bad Request". Most of the return values
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


    seek
        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/seek/set/<value> #value format = HH:MM:ss

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


    track_duration

        get:
			http://<sonos_server:port>/speaker/<sonos_uid>/track_duration   #HH:MM:ss

		response (udp)
			speaker/<sonos_uid>/track_duration/<value>                      #HH:MM:ss


    track_position

        get:
			http://<sonos_server:port>/speaker/<sonos_uid>/track_position   #HH:MM:ss

		response (udp)
			speaker/<sonos_uid>/track_position/<value>                      #HH:MM:ss

			Attention, there is no automatic event for this value.
			If necessary poll this value (e.g. 1sec) to get the value by
			udp.


    streamtype

   		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/streamtype

		response (udp)
			speaker/<sonos_uid>/streamtype/<value>      (radio|music)

    play_uri

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play_uri/set/<value>

			    <value>. has to be urlsafe, qoute_plus
			    If you want to play a title from your network share use following format:

                x-file-cifs%3A%2F%2F192.168.178.100%2Fmusic%2Ftest.mp3
                (unqouted: x-file-cifs://192.168.0.3/music/test.mp3)

		response:
			no explicit response, but events will be triggered, if new track title


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
	* and many more
    * Sonos Group Management