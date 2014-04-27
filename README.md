#Release

v0.1.9      2014-04-27

    -- removed startup parameters
    -- sonos broker is now configured by a config file
    -- Google-TTS: removed the requirement for a working smb share
    -- Google-TTS: removed auto config for smb shares (not necessary any more)
    -- Command: added favorite radiostation command
    -- Command: added maxvolume command

v0.1.8.1    2014-03-27

    -- bugfix: server does not start correctly if no local share for Google TTS was found

v0.1.8      2014-03-26

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


#Overview

	
The shSonos project is primary a simple (python) sonos control server, mainly based on the brilliant SoCo project https://github.com/SoCo/SoCo). 
It implements a lightweight http server, which is controlled by simple commands.
 
In addition , i decided to write a plugin for the fantastic "Smarthome.py Project" to control sonos speakers in a smart home. (https://github.com/mknx/smarthome/)

 
#Requirements

Server:	python3 (with library 'requests')

Client-side: nothing special, just send your commands over http or use the Smarthome.py plugin to control the speakers
within smarthome.py


#Install


##Setup

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

Normally, the script finds the interal ip address of your computer. If not, you have to edit your sonos_broker.cfg.

    [sonos_broker]
    server_ip = x.x.x.x

(x.x.x.x means your ip: run ifconfig - a to find it out)


##Configuration (optional)

You can edit the settings of Sonos Broker. Open 'sonos_broker.cfg' with your favorite editor and edit the file.
All values within the config file should be self-explaining. For Google-TTS options, see the appropriate section in this
Readme.

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



##Google TTS Support

Sonos broker features the Google Text-To-Speech API. You can play any text limited to 100 chars.

###Prerequisite:

- local / remote mounted folder or share with read/write access
- http access to this local folder (e.g. /var/www)
- settings configured in sonos_broker.conf

###Internals

If a text is given to the google tts function, sonos broker makes a http request to the Google API. The response is
stored as a mp3-file to local mounted samba share. Before the request is made, the broker checks whether a file exists
with the name. The file name of a tts-file is always:  BASE64(<tts_txt>_<tts_language>).mp3
You can set a file quota in the config file. This limits the amount of disk space the broker can use to save tts files. If the quota
exceeds, you will receive a message. By default the quota is set to 100 mb.

    sonos_broker.cfg:

        [google_tts]
        quota = 200

By default, Google TTS support is disabled. To enable the service, add following line to sonos_broker.cfg:

    sonos_broker.cfg:

        [google_tts]
        enable = true

You have to set the local save path (where the mp3 is stored) and the accessible local url:

     sonos_broker.cfg

        [google_tts]
        save_path =/your/path/here
        server_url = http://192.168.0.2/tts

This is an example of a google_tts section in the sonos_broker.cfg file:

    [google_tts]
    enable=true
    quota=200
    save_path =/your/path/here
    server_url = http://192.168.0.2/tts


##Raspberry Pi User


For raspberry pi user, please follow these instruction prior to point 2:

    sudo apt-get update
    sudo apt-get upgrade
    sudo easy_install3 requests

To get samba shares working on your Pi (to get Google TTS support), here is a good how-to:

http://raspberrypihelp.net/tutorials/12-mount-a-samba-share-on-raspberry-pi


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

##Speaker commands

	volume

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/volume/<value:0-100>
		
		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/volume

		response (udp):
	        JSON speaker structure


    maxvolume

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/maxvolume/<value:-1-100>

		get:
			http://<sonos_server:port>/speaker/<sonos_uid>/maxvolume

		response (udp):
	        JSON speaker structure

        Sets the maximum volume for the sonos speaker. This setting also affects other sonos clients (iPad, Android etc).
        If a volume greater than maxvolume is set, the volume is set to maxvolume.
        The maximum volume will be ignored if play_snippet or play_tts are used.
        To unset maxvolume, set the value to -1.


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

            <volume> Plays the snippet with <volume>. The volume is set back  to its original value.
            If -1 i used, the snippet volume is set to the current volume of the sonos speaker

		response:
			no explicit response, but events will be triggered, if new track title


    play_tts

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play_tts/<text>/<google_tts_language><volume [-1-100]>

			<text>  has to be urlsafe, qoute_plus, max. 100 chars

            <google_tts_language> e.g: 'de', 'en, 'fr' ...

            <volume> Plays the tts_snippet with <volume>. The volume is set back to its original value.
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


###Response:

In almost any cases, you will get the appropriate response in the following JSON format (by udp):

    {
        "hardware_version": "1.8.3.7-2",
        "ip": "192.168.0.10",
        "led": 1,
        "mac_address": "00:0E:59:D4:89:2F",
        "model": "ZPS1",
        "mute": 0,
        "max_volume" : 0
        "pause": 0,
        "play": 1,
        "playlist_position": "1",
        "radio_show": "",
        "radio_station": "95.5 Charivari",
        "serial_number": "00-0E-59-D4-89-2F:7",
        "software_version": "24.0-71060",
        "stop": 0,
        "status" : 1                    #speaker online / offline?
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


##Library commands

    favorite radio stations

        get:
            http://<sonos_server:port>/library/favradio/<start_item>/<max_items>

            Get all favorite radio stations from sonos library

            start_item [optional]: item to start, starting with 0 (default: 0)
            max_items [optional]: maximum items to fetch. (default: 50)

            Parameter max_items can only be used, if start_item is set (positional argument)

            It's a good idea to check to see if the total number of favorites is greater than the amount you
            requested (`max_items`), if it is, use `start` to page through and  get the entire list of favorites.

        response (http):
            JSON object, utf-8 encoded

            Example:

            {
                "favorites":
                    [
                        { "title": "Radio TEDDY", "uri": "x-sonosapi-stream:s80044?sid=254&flags=32" },
                        { "title": "radioeins vom rbb 95.8 (Pop)", "uri": "x-sonosapi-stream:s25111?sid=254&flags=32" }
                    ],
                "returned": 2,
                "total": "10"
            }


##TO DO:


	* full SoCo command implementation
	* documentation
	* and many more
    	* Sonos Group Management
