#Release

v0.2.2.1-beta   2014-06-28

    -- bug: thread start as daemon didn't work properly
    -- minor bug in radio parser

v0.2.2-beta 2014-06-26
    
    -- logger functionality added (see sonos_broker.cfg and documentation)
    -- added radio station parser to get normalized artist and track titles
        -- you can add more regular expressions to lib_sonos/radio_parser.py to handle your stations
    -- some adjustments to thread-safe event handling
    -- system signal handling now implemented (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
    -- bug: now exceptions in event subscriptions handled as was intended 

v0.2.1      2014-06-15

    --  stop, play, pause, led, mute command now supports two value behaviours:
        -- toggle mode [if no parameter was passed]
        -- direct mode [if parameter was passed]
    --  Command: added bass command
    --  Command: added treble command
    --  Command: added loudness command (direct / toggle mode)
    --  Command: added playmode command ('normal', 'shuffle_norepeat', 'shuffle', 'repeat_all')
    --  changed pause command behaviour, if radio is played (wrapped to stop command). 
        This is the default sonos app behaviour.
    --  bugifx: additional_zone_member_property was not set correctly
    --  some minor soco framework updates
        

v0.2.0      2014-06-06

    --  Command: added join command (joins the speaker to another speaker)
    --  Command: added unjoin command (unjoins the speaker from the current group)
    --  Command: added partymode command (joins all speaker to one group)
    --  Command: added volume_up command (+2 volume, this is the default sonos speaker behaviour)
    --  Command: added volume_down command (-2 volume, this is the default sonos speaker behaviour)
    --  Event handling now based on soco core functionality
    --  added ZoneGroup event handling
    --  changed commands pause, play, stop, led, mute to toggle commands (no arguments necessary)
    --  fixed bug in play_snippet and play_uri command (case sensitive uri)
    --  speaker metadata will only be send, if something has changed
    --  many many code improvements

v0.1.9      2014-04-27

    --  removed startup parameters
    --  sonos broker is now configured by a config file
    --  Google-TTS: removed the requirement for a working smb share
    --  Google-TTS: removed auto config for smb shares (not necessary any more)
    --  Command: added favorite radiostation command
    --  Command: added maxvolume command

v0.1.8.1    2014-03-27

    --  bugfix: server does not start correctly if no local share for Google TTS was found

v0.1.8      2014-03-26

    --  add Google Text-To-Speech suppor (see documentation)
    --  minor bugfixes


#Overview

	
The shSonos project is primary a simple (python) sonos control server, mainly based on the brilliant SoCo project 
https://github.com/SoCo/SoCo). It implements a lightweight http server, which is controlled by simple url commands.
 
In addition , i decided to write a plugin for the fantastic "Smarthome.py Project" to control sonos speakers in a 
smart home environment (https://github.com/mknx/smarthome/).

 
#Requirements

Server:	python3 (with library 'requests')

Client-side: nothing special, just send your commands over http or use the Smarthome.py plugin to control the speakers
within smarthome.py


#Install


##Setup

Under the github folder "server.sonos/dist/" you'll find the actual release as a tar.gz file.
Unzip this file with:

    tar -xvf sonos_broker_release.tar.gz

(adjust the filename to your needs)

Go to the unpacked folder and run setup.py with:

    sudo python3 setup.py install

This command will install all the python packages and places the start script to the python folder
"/user/local/bin"

Make the file executable run the sonos_broker with:

    chmod +x sonos_broker
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

To get some debug output, please edit the sonos_broker.cf and uncomment this line in the logging section:

    loglevel = debug

You can set the debug level to debug, info, warning, error, critical.
Additionally, you can specify a file to pipe the debug log to this file.

    logfile = 'log.txt'


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
You can set a file quota in the config file. This limits the amount of disk space the broker can use to save tts files. 
If the quota exceeds, you will receive a message. By default the quota is set to 100 mb.

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


    current_state

        get:
            http://<sonos_server:port>/speaker/<sonos_uid>/current_state

            Dumps the current sonos player state with all values

        response (udp):
            JSON speaker structure


	volume

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/volume/<value:0-100>
		
		response (udp):
	        JSON speaker structure


    volume_up

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/volume_up

		response (udp):
	        JSON speaker structure

        The volume_up commands triggers a +2 volume. This is the default sonos speaker behaviour, if the volume-up
        button was pressed.


    volume_down

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/volume_down

		response (udp):
	        JSON speaker structure

        The volume_down commands triggers a -2 volume. This is the default sonos speaker behaviour, if the volume-down
        button was pressed.


    maxvolume

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/maxvolume/<value:-1-100>

		response (udp):
	        JSON speaker structure

        Sets the maximum volume for a sonos speaker. This setting also affects other sonos clients (iPad, Android etc).
        If a volume greater than maxvolume is set, the volume is set to maxvolume.
        The maximum volume will be ignored if play_snippet or play_tts are used.
        To unset maxvolume, set the value to -1.


    bass

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/bass/<value:-10-10>
			
			value: sonos default setting is 0
		
		response (udp):
	        JSON speaker structure
	        
	
	treble

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/treble/<value:-10-10>
		
		    value: sonos default setting is 0 
		    
		response (udp):
	        JSON speaker structure
	        
	        
	loudness

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/loudness/<optiona value: 0|1>
			
			loudness: by default, the command is a toggle command
            optional value: set the value directly [no toggle behaviour]  
			value: sonos default setting is 1
		
		response (udp):
	        JSON speaker structure


	mute

		set:
			http://<sonos_server:port>/speaker/<sonos_uid>/mute/<optional value: 0|1>

		    mute: by default, the command is a toggle command
            optional value: set the value directly [no toggle behaviour]  
    
		response (udp)
			JSON speaker structure


	led

		set:

			http://<sonos_server:port>/speaker/<sonos_uid>/led/<optional value: 0|1>

		    led: by default, the command is a toggle command
            optional value: set the value directly [no toggle behaviour]  

		response (udp)
		    JSON speaker structure


	play

	    set:
			http://<sonos_server:port>/speaker/<sonos_uid>/play

            play: command is a toggle command

		response (udp)
		    JSON speaker structure


    pause

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/pause

            pause: command is a toggle command

		response (udp)
			JSON speaker structure


    stop

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/stop/[optional value: 0|1]

            stop: by default, the command is a toggle command
            optional value: set the value directly [no toggle behaviour]  

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


    track_info

        get:
            http://<sonos_server:port>/speaker/<sonos_uid>/track_info

        response (udp)
            JSON speaker structure

            Gets the current track info. Only usefull to get the current track position. You need to poll this value,
            since there is no event for this property


    join

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/join/<sonos_uid_to_join>

			<sonos_uid_to_join> the uid of the sonos speaker to join

		response:
			no explicit response, but events will be triggered, if the zone group has been changed


    unjoin

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/unjoin

		response:
			no explicit response, but events will be triggered, if the zone group has been changed


    playmode

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/playmode/<value>

            value:  'normal', 'shuffle_norepeat', 'shuffle', 'repeat_all'
                    If no parameter was passed, the default value is 'normal'
            
		response:
			no explicit response, but events will be triggered, if the zone group has been changed


    partymode

        set:
			http://<sonos_server:port>/speaker/<sonos_uid>/partymode

		response:
			no explicit response, but events will be triggered, if the zone group has been changed


	list

		get:
			http://<sonos_server:port>/client/list

		response (http)
			<html code ....
				uid             : rincon_000f44c3892e01400
                ip              : 192.168.0.40
                model           : ZPS1
                current zone    : child room
			/>


###Response:

In almost any cases, you will get the appropriate response in the following JSON format (by udp):

    {
        "hardware_version": "1.8.3.7-2",
        "ip": "192.168.0.40",
        "led": true,
        "mac_address": "00:0F:12:D4:88:2F",
        "max_volume": -1,
        "model": "ZPS1",
        "mute": false,
        "pause": false,
        "play": true,
        "playlist_position": "10",
        "radio_show": "",
        "radio_station": "",
        "serial_number": "00-0F-12-D4-88-2F:1",
        "software_version": "26.1-76230",
        "status": true,
        "stop": false,
        "streamtype": "music",
        "track_album_art": "http://192.168.0.40:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a3ZJSDh87VrZXvJGwZ82zQu%3fsid%3d9%26flags%3d32",
        "track_artist": "Herbert Grönemeyer",
        "track_duration": "0:03:30",
        "track_position": "0:02:21",
        "track_title": "Halt Mich",
        "track_uri": "x-sonos-spotify:spotify%3atrack%3a3ZJSDh87VrZXvJGwZ82zQu?sid=9&flags=32",
        "uid": "rincon_000f44c3892e01400",
        "volume": "2",
        "zone_coordinator": "rincon_000f44c3892e01400",
        "zone_icon": "x-rincon-roomicon:bedroom",
        "zone_id": "RINCON_B9E94030D19801400:19",
        "additional zone_members": "rincon_000f44c3892e01400,rincon_b9e94030d19801400"
        "zone_name": "child room",
        "bass": "5",
        "treble": "2",
        "loudness": true,
        "playmode": "shuffle_norepeat"
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
