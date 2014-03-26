#Release

v0.8        2014-03-26

    -- add Google Text-To-Speech suppor (see documentation)
    -- minor bugfixes


v0.1.7.1    2014-03-09

    -- fix: track_uri now shown
    -- socket now closed correctly

v0.1.7      2014-03-09

     -- audio snippet integration
     -- many many code improvements
     -- JSON format, less network traffic
     -- easier to configure sonos speaker in conf-file
     -- better radio integration
     -- new commands

v0.1.6      2014-02-18

    -- minor bugfix: changed EOL (end-of-line) from '\r\n' to '\n' in sonos_command method

v0.1.5      2014-02-12

    -- bugfix in play command



#Overview

	
The shSonos project is primary a simple (python) sonos control server, mainly based on the brilliant SoCo project https://github.com/SoCo/SoCo). 
It implements a lightweight http server, which is controlled by simple commands.
 
In addition , i decided to write a plugin for the fantastic "Smarthome.py Project" to control sonos speakers in a smart home. (https://github.com/mknx/smarthome/)

 
#Requirements:


server:	python3 (with library requests)

client-side: nothing special, just send your commands over http or use the plugin to control the speakers within
smarthome.py



#Install:


##1.SETUP


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

or

    ./sonos_broker -h

for help an additional arguments.


Normally, the script finds the interal ip address of your computer. If not, you have start the script with
the following parameter:

    ./sonos_broker --localip x.x.x.x

(x.x.x.x means your ip: run ifconfig - a to find it out)



##2.CONFIGURATION (optional)

There is also a sh-script to daemonize the sonos_broker start named sonos_broker.sh.
If you want to start sonos_broker as background service, edit sonos_broker.sh:

Edit DIR variable to /path/location/of/sonos_broker (default: /usr/local/bin)

Make the file executable with:

    chmod +x /usr/local/bin/sonos_broker.sh

Start service with:

    sudo ./path/to/sonos_broker.sh start


To autostart the service on system boot, please follow the instruction for your linux distribution and put this
script in the right place.


Attention!! Please notice that the script is running as with the 'background' flag. In order that, there is
no debug or error output. To get these hints in failure cases, remove this flag in sonos_broker.sh

from:

    start-stop-daemon -v --start --pidfile $PIDFILE --background --make-pidfile --startas $DAEMON --

to:

    start-stop-daemon -v --start --pidfile $PIDFILE --make-pidfile --startas $DAEMON --


If you want to start the broker with arguments (see below) keep in mind to edit the script.


##3.Google TTS Support

Sonos broker features the Google Text-To-Speech API. You can play any text limited to 100 chars.

###3.1 Prerequisite:

- running samaba server with at least one mountable share with read/write access
- readable fstab for auto-mode (linux only)

###3.1 Auto-Mode (only linux):

- create an entry 'in /etc/fstab' to automount the smb share
- add a comment prior to this entry with '#sonos'

here is mine:

```
#sonos
//192.168.0.10/music/snippets /mnt/google_tts cifs defaults,uid=1000,user=jonnycash,password=kNmx12,users,auto,user_xattr 0 0
```

That's it. The broker will now parse the line and fetches all necessary values.

###3.2 Manual Mode

You can set all values manually. To do this, start the broker with some additional arguments:

    ./sonos_broker --smb_url '//192.168.0.10/music/snippets' --local_share '/mnt/google_tts'


###3.3 Internals

If a text is given to the google tts function, sonos broker makes a http request to the Google API. The response is
stored as a mp3-file to local mounted samba share. Before the request is made, the broker checks whether a file exists
with the name. The file name of a tts-file is always:  BASE64(<tts_txt>_<tts_language>).mp3
You can set a file quota. This limits the amount of disk space the broker can use to save tts files. If the quota
exceeds, you will receive a message. By default the quota is set to 100 mb.

    ./sonos_broker --quota 1000

To disable the Google TTS support, start the broker with:

    ./sonos_broker --disable-tts


##4.RASPBERRY PI USER

For raspberry pi user, please follow these instruction prior to point 2:

    sudo apt-get update
    sudo apt-get upgrade
    sudo easy_install3 requests



#Testing:


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
		

#First implemented commands (more coming soon):



	volume

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/volume/<value:0-100>
		
		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/volume

		response (udp):
	        JSON speaker structure


	mute

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/mute/<value:0|1>
			
		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/mute
			
		response (udp)
			JSON speaker structure


	led

		set:

			http://<sonos_server:port>/speaker/<sonos_uid>/led/<value:0|1>
		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/led

		response (udp)
		    JSON speaker structure


	play

	    set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play/<value:0|1>

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/play

		response (udp)
		    JSON speaker structure


    pause

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/pause/<value:0|1>

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/pause

		response (udp)
			JSON speaker structure


    stop

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/stop/<value:0|1>

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/stop

		response (udp)
			JSON speaker structure


    next

        set:
            http://<sonos_server:port>/speaker/<sonos_uid>/next/<value:0|1>

        response:
			no explicit response, but events will be triggered, if new track title


    previous

        set:
            http://<sonos_server:port>/speaker/<sonos_uid>/previous/<value:0|1>

        response:
			no explicit response, but events will be triggered, if new track title


    seek

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/seek/<value> #value format = HH:MM:ss

        response:
			no explicit response, but events will be triggered, if the track position is changed


    artist

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/artist

		response (udp)
			response:
			no explicit response, but events will be triggered, if new track title


    track

        get:
		    http://<sonos_server:port>/speaker/<sonos_uid>/track

		response (udp)
			JSON speaker structure


    track_duration

        get:
			http://<sonos_server:port>/speaker/<sonos_uid>/track_duration   #HH:MM:ss

		response (udp)
			JSON speaker structure


    track_info

        get:
			http://<sonos_server:port>/speaker/<sonos_uid>/track_info

		response (udp)
            JSON speaker structure

            Gets the current track info. Only usefull to get the current track position. You need to poll this value,
            since there is no event for this property


    streamtype

        get:
			http://<sonos_server:port>/speaker/<sonos_uid>/streamtype

		response (udp)
			JSON speaker structure


    play_uri

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play_uri/<uri>

			    <uri> has to be urlsafe, qoute_plus
			    If you want to play a title from your network share use following format:

                x-file-cifs%3A%2F%2F192.168.178.100%2Fmusic%2Ftest.mp3
                (unqouted: x-file-cifs://192.168.0.3/music/test.mp3)

		response:
			no explicit response, but events will be triggered, if new track title


    play_snippet

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play_snippet/<uri>/<volume [-1-100]>

			<uri>. has to be urlsafe, qoute_plus
			If you want to play a title from your network share use following format:

            x-file-cifs%3A%2F%2F192.168.178.100%2Fmusic%2Ftest.mp3
            (unqouted: x-file-cifs://192.168.0.3/music/test.mp3)

            <volume> Plays the snippet with <volume>. The volume fades is set to its original value.
            If -1 i used, the snippet volume is set to the current volume of the sonos speaker

		response:
			no explicit response, but events will be triggered, if new track title


    play_tts

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play_tts/<text>/<google_tts_language><volume [-1-100]>

			<text>  has to be urlsafe, qoute_plus, max. 100 chars

            <google_tts_language> e.g: 'de', 'en, 'fr' ...

            <volume> Plays the tts_snippet with <volume>. The volume fades is set to its original value.
            If -1 i used, the snippet volume is set to the current volume of the sonos speaker


		response:
			no explicit response, but events will be triggered, if the tts_snippet is played


    current_state

        get:
            http://<sonos_server:port>/speaker/<sonos_uid>/current_state

            Dumps the current sonos player state.

        response (udp):
            JSON speaker structure


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


Response:
--------------------------------
In almost any cases, you will get the appropriate response in the following JSON format (by udp):

    {
        "hardware_version": "1.8.3.7-2",
        "ip": "192.168.0.10",
        "led": 1,
        "mac_address": "00:0E:59:D4:89:2F",
        "model": "ZPS1",
        "mute": 0,
        "pause": 0,
        "play": 1,
        "playlist_position": "1",
        "radio_show": "",
        "radio_station": "95.5 Charivari",
        "serial_number": "00-0E-59-D4-89-2F:7",
        "software_version": "24.0-71060",
        "stop": 0,
        "streamtype": "radio",
        "track_album_art": "http://192.168.0.10:1400/getaa?s=1&u=x-sonosapi-stream%3as17488%3fsid%3d254%26flags%3d32",
        "track_artist": "RADIO CHARIVARI 95.5",
        "track_duration": "0:00:00",
        "track_position": "0:02:16",
        "track_title": "LIVE",
        "track_uri": "",
        "uid": "rincon_000e58c3e01451",
        "volume": 11,
        "zone_icon": "x-rincon-roomicon:living",
        "zone_name": "Kitchen"
    }



TO DO:
--------------------------------

	* full SoCo command implementation
	* documentation
	* and many more
    * Sonos Group Management
