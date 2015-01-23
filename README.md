## Release

v0.5.1     (2015-01-23)

    --  Hotfix: error while handling a DIDL item (in SoCo framework)

v0.5       (2015-01-18)

    --  interactive command shell added to interact with the speakers directly (see docu)
    --  commands added: get_playlist, set_playlist (see documentation). Its now possible to
        save and set the playlist for a speaker / zone.
    --  commands added: 'is_coordinator'[readonly], 'tts_local_mode'[readonly]: please 
        read the documentation
    --  changed some strings to clarify, that a non-existing or broken GoogleTTS 
        configuration disables only the 'local mode'; the 'streaming mode' is always 
        available
    --  changed the 'client_list'command: only the uids will be shown
    --  bugfix: error during processing a Spotify track
    --  bugfix: an error occurred, if the Broker was started with the '-l' parameter and a 
        previous online speaker went offline
    --  changed logging handler in daemon.py to global logging handler specified in the 
        config file
    --  new SoCo version     
    --  new start option "-l"
        --  this options lists all available Sonos speaker in the network. 
            This is helpful to get the speakers UIDs.
         
v0.4       (2014-11-09)

    --  added new SoCo version
    --  changed event parser logic ( thanks to the great SoCo framework)
    --  play_tts can now executed like a radio stream without saving the tts file locally
        --  this has some disadvantages (no exact timestamp to resume the previous paused track,
            some time delay due to the radio stream buffering); the "local mode" should be the 
            preferred one
    --  added 'fade_in' parameter to play_snippet and play_tts command
        -- the volume for the resumed track fades in
    --  better Google TTS handling (especially resuming previous tracks) by implementing the SoCo snapshot
        functionality --> this needs some testing ;)
    --  bug: changed base64 encode and decode algorithm for saving google tts files to urlsafe variant
    --  sonos broker should no stop reliable
    --  minor bug fixes in documentation
    

## Overview

	
The shSonos project is Sonos control server, mainly based on the brilliant SoCo project (https://github.com/SoCo/SoCo). 
It implements a lightweight http server, which is controlled by simple HTTP json commands.
It sends all available Sonos speaker data to all subscribed clients and notifies them of all changes.

The Sonos Broker implements some nice additional features like GoogleTTS, saving/restoring the playlist, maximum
volume settings for each Sonos speaker and much more.

In addition , i decided to write a plugin for the fantastic "Smarthome.py Project" to control Sonos speakers in a 
smart home environment (https://github.com/mknx/smarthome/).


## Requirements

Server:	python3 (with library 'requests')

Client-side: nothing special, just send your commands over http (JSON format) or use the Smarthome.py plugin to control 
the speakers within Smarthome.py.


## Installation

#### Setup

Under the github folder "server.sonos/dist/" you'll find the actual release as a tar.gz file.
Unzip this file with:

    tar -xvf sonos_broker_release.tar.gz

(adjust the filename to your needs)

Go to the unpacked folder and run setup.py with:

    sudo python3 setup.py install

This command will install all the python packages and places the start script to the python folder
"/user/local/bin"

Make the file executable and run the sonos_broker with:

    chmod +x sonos_broker
    ./sonos_broker

Normally, the script finds the internal ip address of your computer. If not, you have to edit your sonos_broker.cfg.

    [sonos_broker]
    server_ip = x.x.x.x

(x.x.x.x means your ip: run ifconfig - a to find it out)


#### Configuration / Start options

You can edit the settings of Sonos Broker. Open 'sonos_broker.cfg' with your favorite editor and edit the file.
All values within the config file should be self-explaining. For Google-TTS options, see the appropriate section in this
Readme.

If you start the sonos broker with
```
sonos_broker
```
the server will be automatically daemonized.

You can add the -d (--debug) parameter to hold the process in the foreground.
```
sonos_broker -d
```

You can stop the server with
```
sonos_broker -s
```

To get a short overview of your speakers in the network start the server with
```
sonos_broker -l
```

To get an overview of all parameters type
```
sonos_broker -h
```

To autostart the service on system boot, please follow the instruction for your linux distribution and put this
script in the right place.

To get some debug output, please edit the sonos_broker.cfg and uncomment this line in the logging section (or use the 
-d start parameter):

    loglevel = debug

You can set the debug level to debug, info, warning, error, critical.
Additionally, you can specify a file to pipe the debug log to this file.

    logfile = log.txt


## Interactive Command Line

You can control the Broker and your speakers without implementing your own client. To start the interactive
command line (the Broker must be running) type
```
./sonos_cmd
```
in the root folder of the Sonos Broker.

With the
```
help
```
command you can show up all options.

Within the shell type  
```
update
```
to get all the speakers in the network.

Type
```
list
```
or
```
speaker
```
to show all available speakers.

To interact with one of these speakers type
```
speaker [number of the speaker]
```

Now you should see the uid of the speaker as the command line prompt. Type
```
help
```
for all available commands. All of them are interactive and self-explaining.

An
```
exit
```
redirects you to the first command line level.
 

## Google TTS Support

Sonos broker features the Google Text-To-Speech API. You can play any text limited to 100 chars.


#### Prerequisite:

- local / remote mounted folder or share with read/write access
- http access to this local folder (e.g. /var/www)
- settings configured in sonos_broker.conf

#### Internals

If a text is given to the google tts function, sonos broker makes a http request to the Google API. The response can be 
    1. stored as a mp3-file to the local / remote folder. 
    2. or handled like a radio stream without saving the file locally.
    
The first option should always be the preferred one. The "radio stream" option has some big disadvantages (time delay,
no snippet length and therefor inaccurate track resuming). If Google TTS is disabled (either by disabling Google TTS in
the sonos_broker.cfg or other failures), the stream mode is assumed. You can force this behaviour by setting the 
command parameter 'force_stream_mode' to 1 (see [play_tts command](#p_tts)).

Before the request is made ('local mode'), the broker checks whether a file exists
with the same name. The file name of a tts-file is always:  BASE64(<tts_txt>_<tts_language>).mp3
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


## Raspberry Pi User

For raspberry pi user, please follow these instruction prior the Broker installation:

    sudo apt-get update
    sudo apt-get upgrade
    sudo easy_install3 requests

## Implementation:

Because of the server-client design, you're not bound to Python to communicate
with the Sonos broker instance. You just have to implement a client which is listening on an open UDP port to receive 
Sonos speaker status changes. To control the server your client has to send [JSON commands](#available-commands). 
At this moment there is no dedicated web interface. (maybe this is your contribution :-) ). You can find a sonos widget 
for smartVISU / Smarthome.py here:

https://github.com/pfischi/shSonos/tree/develop/widget.smartvisu


#### Client subscription

To subscribe your client to the Broker, simply send the appropriate [JSON command](#client_subscribe)(this step is not 
necessary for smarthome.py-plugin user, it's done automatically).
Use this [command](#client_unsubscribe) to unsubscribe.
	
After subscription, your client will receive all status updates of all sonos speakers in the network,
whether	they were triggered by you or other clients (iPad, Android). The received data comes in a JSON format and looks
like this:

#### Sonos speaker data:

In almost any cases, you'll get the appropriate response in the following JSON format (by udp):

    {
        "additional_zone_members": "rincon_112ef9e4892e00001",
        "alarms": {
            "32": {
                "Duration": "02:00:00",
                "Enabled": false,
                "IncludedLinkZones": false,
                "PlayMode": "SHUFFLE_NOREPEAT",
                "Recurrence": "DAILY",
                "StartTime": "07:00:00",
                "Volume": 25
            }
        },
        "bass": 0,
        "hardware_version": "1.8.3.7-2",
        "ip": "192.168.0.4",
        "led": 1,
        "loudness": 1,
        "mac_address": "10:1F:21:C3:77:1A",
        "max_volume": -1,
        "model": "Sonos PLAY:1",
        "mute": "0",
        "pause": 0,
        "play": 0,
        "playlist_position": 0,
        "playmode": "normal",
        "radio_show": "",
        "radio_station": "",
        "serial_number": "00-0E-58-C3-89-2E:7",
        "software_version": "27.2-80271",
        "status": true,
        "stop": 1,
        "streamtype": "music",
        "track_album_art": "http://192.168.0.4:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a3xCk8npVehdV55KuPdjrmZ%3fsid%3d9%26flags%3d32",
        "track_artist": "Feuerwehrmann Sam & Clemens Gerhard",
        "track_duration": "0:10:15",
        "track_position": "00:00:00",
        "track_title": "Das Baby im Schafspelz",
        "track_uri": "x-sonos-spotify:spotify%3atrack%3a3xCk8npVehdV55KuPdjrmZ?sid=9&flags=32",
        "treble": 0,
        "uid": "rincon_000e58c3892e01410",
        "volume": 8,
        "zone_icon": "x-rincon-roomicon:bedroom",
        "zone_name": "Kinderzimmer"
    }
    
 Please notice: the Broker sends only **new** or changed data to the clients. In most case you'll ge only a subset of
 the data shown above. To force the Broker to send all data, your client have to trigger the 
 [current_state](#current-state) command. 
    
 To put it in a nutshell: code your own client (Python, Perl, C#...) with an open and listening UDP port and subscribe
 your client to the Sonos Broker. Send JSON commands to control your Sonos speaker(s).

#### Get the UID

 Most of the commands need a speaker uid. Start the Sonos Broker with the argument '-l to get a short overview of your 
 sonos speakers in the network and to retrieve the uid. You can also perform a sonos [client_list](#client_list) 
 command. 

#### Client Implementation Example

 [Here you can find](plugin.sonos/README.md) a client implementation for the Broker. It is a sonos plugin for the 
 [Smarthome.py](https://github.com/mknx/smarthome) home automation framework.

## Available commands

#### Overview

Click on the links below to get a detailed command descriptions and their usage.

###### [client_subscribe](#cl_subs)
###### [client_unsubscribe](#cl_unsubs)
###### [client_list](#cl_li)
###### [get_play](#g_pl)
###### [set_play](#s_pl)
###### [get_pause](#g_pause)
###### [set_pause](#s_pause)
###### [get_stop](#g_stop)
###### [set_stop](#s_stop)
###### [get_volume](#g_volume)
###### [set_volume](#s_volume)
###### [get_max_volume](#g_m_volume)
###### [set_max_volume](#s_m_volume)
###### [get_mute](#g_mute)
###### [set_mute](#s_mute)
###### [volume_up](#v_up)
###### [volume_down](#v_down)
###### [next](#nex)
###### [previous](#prev)
###### [get_bass](#g_bass)
###### [set_bass](#s_bass)
###### [get_treble](#g_treble)
###### [set_treble](#s_treble)
###### [get_loudness](#g_loudness)
###### [set_loudness](#s_loudness)
###### [get_led](#g_led)
###### [set_led](#s_led)
###### [get_playmode](#g_playmode)
###### [set_playmode](#s_playmode)
###### [get_track_position](#g_track_position)
###### [set_track_position](#s_track_position)
###### [get_track_title](#g_track_title)
###### [get_track_artist](#g_track_artist)
###### [get_track_album_art](#g_track_album_art)
###### [get_track_uri](#g_track_uri)
###### [get_radio_station](#g_radio_station)
###### [get_radio_show](#g_radio_show)
###### [join](#s_join)
###### [unjoin](#s_unjoin)
###### [partymode](#s_partymode)
###### [play_uri](#p_uri)
###### [play_snipptet](#p_snippet)
###### [play_tts](#p_tts)
###### [get_alarms](#g_alarms)
###### [current_state](#cur_state)
###### [get_favorite_radio_stations](#g_fav_radio)
###### [is_coordinator](#is_coor)
###### [tts_local_mode](#tts_local)
###### [get_playlist](#get_playlist)
###### [set_playlist](#set_playlist)

----
#### <a name="cl_subs"></a>client_subscribe
 Subscribes a client to the Sonos Broker. After the subscription, the client will receive all
 status changes from the Sonos speakers in the network.
 
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| ip | required | | The IP of the client which wants to subscribe to the broker. |
| port | required | 1-65535 | A client-side open UDP port which receives the data. |

######Example
    JSON format:
    {
        'command':
        'client_subscribe',
        'parameter':
        {
            'ip': '192.168.0.2',
            'port': 2333
        }
    }
    
######HTTP Response
    HTTP Response: no additional data
    Response Code: 200 OK or Exception with Code 400 and the specific error message.
    
----

#### <a name="cl_unsubs"></a>client_unsubscribe
 Unsubscribes a client from the Broker. After unssubscription the client will not longer receive
 status changes from the Sonos speakers. If your're running more than one client with the same
 IP but with different ports, only the client with the specific port will be unsubscribed.
 
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| ip | required | | The IP of the client which wants to unsubscribe from the broker. |
| port | required | 1-65535 | A (client-side) open UDP port. |

######Example
    JSON format:
    {
        'command': 'client_unsubscribe',
        'parameter': {
            'ip': '192.168.0.2',
            'port': 2333
        }
    }
    
######HTTP Response
    HTTP Response: no additional data
    Response Code: 200 OK or Exception with Code 400 and the specific error message.    

----

#### <a name="cl_li">client_list
 Shows all available Sonos speaker in the network.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |

No special parameter needed.

######Example
    JSON format:
    {
        'command': 'client_list'
    }

######HTTP Response
    HTTP Response:
        <html><head><title>Sonos Broker</title></head>
            <body>
                rincon_000e58c3892e01410\nrincon_b8e93730d19801410\n ... [uids]
            </body>
        </html>
    
    Response Code: 200 OK or Exception with Code 400 and the specific error message.        
    
----
#### <a name="g_pl">get_play
 Gets the 'play' status for a Sonos speaker. If the speaker has additional zone members, the 'play' status for all
 members will be sent.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'play'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_play',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "play": 0|1, 
        "uid": "rincon_b8e93730d19801410",
         ...
    }

----
#### <a name="s_pl">set_play
 Sets the PLAY status for a Sonos speaker. If the speaker has additional zone members, the 'play' status for all
 members will be set (this is the Sonos standard behavior).

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| play | required | 0 or 1 | If the value is set to 'False', the Sonos speaker is paused. |

######Example
    JSON format:
    {
        'command': 'set_play',
        'parameter': {
            'play': 1,
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "play": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

    The response is only sent if the new value is different from the old value.
    
----
#### <a name="g_pause"></a>get_pause
 Gets the 'pause' status for a Sonos speaker. If the speaker has additional zone members, the 'pause' status for all
 members will be sent.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'pause'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_pause',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "pause": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_pause"></a>set_pause
 Sets the 'pause' status for a Sonos speaker. If the speaker has additional zone members, the 'pause' status for all
 members will be set (this is the Sonos standard behavior).

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| pause | required | 0 or 1 | If the value is set to 'False', the Sonos speaker starts playing. |

######Example
    JSON format:
    {
        'command': 'set_pause',
        'parameter': {
            'pause': 1,
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "pause": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

    The response is only sent if the new value is different from the old value.
    
----
#### <a name="g_stop">get_stop
 Gets the 'stop' status for a Sonos speaker. If the speaker has additional zone members, the 'stop' status for all
 members will be sent.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'stop'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_stop',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "stop": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_stop">set_stop
 Sets the 'stop' status for a Sonos speaker. If the speaker has additional zone members, the 'stop' status for all
 members will be set (this is the Sonos standard behavior).

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| stop | required | 0 or 1 | If the value is set to 'False', the Sonos speaker starts playing. |

######Example
    JSON format:
    {
        'command': 'set_stop',
        'parameter': {
            'stop': 1,
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "stop": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

    The response is only sent if the new value is different from the old value.
    
----
#### <a name="g_volume">get_volume
 Gets the current volume from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'volume'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_volume',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "volume": [0-100], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_volume">set_volume
 Sets the volume for a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| volume | required | 0 - 100 | The volume to be set. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_volume',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'volume': 25,
            'group_command': 0
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "volume": [0-100], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="g_m_volume">get_max_volume
 Gets the maximum volume value from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'max_volume'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_max_volume',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "max_volume": [-1 - 100], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_m_volume">set_max_volume
 Sets the maximum volume for a Sonos speaker. This also affects any volume changes performed on other devices (Android, 
 iPad). If the volume is greater than the maximum volume, the volume is changed to this maximum volume value.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| max_volume | required | -1-100 | If the value is -1 (default), maximum volume will be ignored / unset. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_max_volume',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'max_volume': -1,
            'group_command': 1
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "max_volume": [-1 - 100], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="g_mute">get_mute
 Gets the mute status from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'mute'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_mute',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "mute": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_mute">set_mute
 Mutes or unmutes a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| mute | required | 0 or 1 | To mute the speaker set the value to 1, to unmute 0. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_mute',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'mute': 1,
            'group_command': 0
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "mute": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="v_up">volume_up
 Increases the volume of a Sonos speaker by +2.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'volume_up',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'group_command': 0
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "volume": [0 - 100], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="v_down">volume_down
 Decreases the volume of a Sonos speaker by -2.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'volume_down',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'group_command': 0
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "volume": [0 - 100], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="nex">next
 Go to the next track in the current playlist.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'next',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "track_album_art": "http://192.168.0.4:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a1AGslpGIhRzXSOYtE52VcB%3fsid%3d9%26flags%3d32",
        "track_artist": "Willi Röbke",
        "track_duration": "0:10:16",
        "track_position": "0:00:10",
        "track_title": "Steuermann Norman",
        "track_uri": "x-sonos-spotify:spotify%3atrack%3a1AGslpGIhRzXSOYtE52VcB?sid=9&flags=32",
        "uid": "rincon_000e58c3892e01410",
        ...
    }
    
    All values for a new track will be sent, but only new and/or different values.

----
#### <a name="prev">previous
 Go back to the previous track in the current playlist.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'previous',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "track_album_art": "http://192.168.0.4:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a1AGslpGIhRzXSOYtE52VcB%3fsid%3d9%26flags%3d32",
        "track_artist": "Willi Röbke",
        "track_duration": "0:10:16",
        "track_position": "0:00:10",
        "track_title": "Steuermann Norman",
        "track_uri": "x-sonos-spotify:spotify%3atrack%3a1AGslpGIhRzXSOYtE52VcB?sid=9&flags=32",
        "uid": "rincon_000e58c3892e01410",
        ...
    }
    
    All values for a new track will be sent, but only new and/or different values.

----
#### <a name="g_bass">get_bass
 Gets the current bass settings from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'bass'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_bass',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "bass": [-10 - 10], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_bass">set_bass
 Sets the bass for a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| bass | required | -10 - 10 | The bass to be set. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_volume',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'bass': 5,
            'group_command': 0
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "bass": [-10 -10], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="g_treble">get_treble
 Gets the current treble settings from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'treble'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_treble',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "treble": [-10 - 10], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_treble">set_treble
 Sets the treble for a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| treble | required | -10 - 10 | The treble to be set. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_volume',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'treble': 1,
            'group_command': 1
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "treble": [-10 - 10], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="g_loudness">get_loudness
 Gets the current loudness settings from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'loudness'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_loudness',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "loudness": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_loudness">set_loudness
 Sets the loudness for a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| loudness | required | 0 or 1 | The loudness to be set. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_loudness',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'loudness': 1,
            'group_command': 1
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "loudness": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="g_led">get_led
 Gets the current led status from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'led'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_led',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "led": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_led">set_led
 Sets the led for a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| led | required | 0 or 1 | The led status to be set. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_led',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'led': 1,
            'group_command': 1
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "led": 0|1, 
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="g_playmode">get_playmode
 Gets the current playmode from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'playmode'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_playmode',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "playmode": 'normal' | 'shuffle_norepeat' | 'shuffle' | 'repeat_all' 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_playmode">set_playmode
 Sets the playmode for a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| playmode | required | 'normal', 'shuffle_norepeat', 'shuffle', 'repeat_all' | The playmode to be set. |

######Example
    JSON format:
    {
        'command': 'set_playmode',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'playmode': 'shuffle'
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "playmode": 'normal' | 'shuffle_norepeat' | 'shuffle' | 'repeat_all'
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

----
#### <a name="g_track_position">get_track_position
 Gets the current track position. To get a real-time track position ( e.g. for a GUI) you have to poll this
 function manually and frequently with the 'force_refresh = 1' option since there is no automatism from the
 Sonos API side.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| force_refresh | optional | 0 or 1 | If true, the Broker polls the Sonos speaker to get the current track position. |

######Example
    JSON format:
    {
        'command': 'get_track_position',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
            'force_refresh': 1
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "track_position": "00:02:14",
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_track_position">set_track_position
 Moves the currently playing track a given elapsed time. 

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| timestamp | required | format: HH:MM:ss | The track position to be set. |

######Example
    JSON format:
    {
        'command': 'set_playmode',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'timestamp': '00:01:12'
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "track_position": "00:02:14",
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    The response is only sent if the new value is different from the old value.

#### <a name="g_track_title">get_track_title
 Returns the title of the currently played track.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'track_title'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_track_title',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "track_title": "Ordinary Love",
        "uid": "rincon_b8e93730d19801410",
        ...
    }

#### <a name="g_track_artist">get_track_artist
 Returns the artist of the currently played track.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'track_artist'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_track_artist',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "track_artist": "U2",
        "uid": "rincon_b8e93730d19801410",
        ...
    }

#### <a name="g_track_album_art">get_track_album_art
 Returns the album-cover url of the currently played track.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'track_album_art'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_track_album_art',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "track_album_art": "http://192.168.0.23:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a7kCrYUDtWsPldoh\OKPTKPL%3fsid%3d9%26flags%3d32",
        "uid": "rincon_b8e93730d19801410",
        ...
    }

#### <a name="g_track_uri">get_track_uri
 Returns the track url of the currently played track.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'track_uri'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_track_uri',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "track_uri": "x-sonos-spotify:spotify%3atrack%3a7kCrYUDtWsPldohOKPTKPL?sid=9&flags=32",
        "uid": "rincon_b8e93730d19801410",
        ...
    }
    
    All URIs can be passed to the play_uri and play_snippet functions.

#### <a name="g_radio_station">get_radio_station
 Returns the title of the currently played radio station. 
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'radio_station'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_radio_station',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "radio_station": "radioeins vom rbb",
        "uid": "rincon_b8e93730d19801410",
        ...
    }

#### <a name="g_radio_show">get_radio_show
 Returns the title of the currently played radio show. 
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'radio_show'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_radio_show',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        "radio_show": "Die Profis",
        "uid": "rincon_b8e93730d19801410",
        ...
    }

#### <a name="s_join">join
 Joins a Sonos speaker to another speaker(s). 

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| join_uid | required | | A UID of a Sonos speaker to join. This can also be a uid of any speaker within an existing group. |

######Example
    JSON format:
    {
        'command': 'join',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
            'join_uid': 'rincon_00e33110q27811000'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        [many value here, see current_state command]
        ...
    }
    
    After a successfully join, the complete metadata for all speakers in the group
    wil be sent to all subscribed clients. This is exactly the same behavior for
    a single speaker if a current_state command is triggered. 

#### <a name="s_unjoin">unjoin
 Unjoins a Sonos speaker from a group. 

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'unjoin',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        [many value here, see current_state command]
        ...
    }
    
    After a successfully unjoin, the complete metadata for the speaker wil be sent to 
    all subscribed clients. This is exactly the same behavior if a current_state 
    command is triggered. 

#### <a name="s_partymode">partymode
 Joins all Sonos speaker in the network to one group.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of any Sonos speaker in the network. |

######Example
    JSON format:
    {
        'command': 'partymode',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {   
        ...
        [many value here, see current_state command]
        ...
    }
    
    After a successfully 'partymode' command, the complete metadata for all speakers 
    in the group wil be sent to all subscribed clients. This is exactly the same behavior 
    for a single speaker if a current_state command is triggered.

----
#### <a name="p_uri">play_uri
 Plays a track or a music stream by URI.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| uri | required | | A valid url. This can be an internal sonos url (see get_track_uri or) an external url. |


######Example
    JSON format:
    {
        'command': 'play_uri',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'uri': 'x-sonos-spotify:spotify%3atrack%3a1AGslpGIhRzXSOYtE52VcB?sid=9&flags=32'
            
            # external url: http://www.tonycuffe.com/mp3/tail%20toddle.mp3
            # internal sonos url: x-sonos-spotify:spotify%3atrack%3a3xCk8npVehdV55KuPdjrmZ?sid=9&flags=32
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "track_album_art": "http://192.168.0.4:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a1AGslpGIhRzXSOYtE52VcB%3fsid%3d9%26flags%3d32",
        "track_artist": "Willi Röbke",
        "track_duration": "0:10:16",
        "track_position": "0:00:10",
        "track_title": "Steuermann Norman",
        "track_uri": "x-sonos-spotify:spotify%3atrack%3a1AGslpGIhRzXSOYtE52VcB?sid=9&flags=32",
        "uid": "rincon_000e58c3892e01410",
        ...
    }
    
    All values for a new track will be sent, but only new and/or different values.

----
#### <a name="p_snippet">play_snippet
 Plays a audio snippet. After the snippet was played (maximum 60 seconds, longer snippets will be truncated)
 the previous played song will be resumed. You can queue up to 10 snippets. They're played in the order they 
 are called.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| uri | required | | A valid url. This can be an internal sonos url (see get_track_uri or) an external url. |
| volume | optional | -1 - 100 | The snippet volume. If -1 (default) the current volume is used.  After the snippet was played, the prevoius volume value is set. |
| fade_in | optional | 0 or 1 | If True, the volume for the resumed track / radio fades in |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. This affects only the parameter 'volume'.|

######Example
    JSON format:
    {
        'command': 'play_snippet',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
            'uri': 'x-sonos-spotify:spotify%3atrack%3a1AGslpGIhRzXSOYtE52VcB?sid=9&flags=32'
            'volume': 8,
            'group_command': 0
            
            # external url: http://www.tonycuffe.com/mp3/tail%20toddle.mp3
            # internal sonos url: x-sonos-spotify:spotify%3atrack%3a3xCk8npVehdV55KuPdjrmZ?sid=9&flags=32
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        [snippet metadata will be sent. After the snippet was played, the metadata for] 
        [the resumed track will be sent (e.g. see play_uri UDP response)]
    }
    
    All values for a new track will be sent, but only new and/or different values.

----
#### <a name="p_tts">play_tts
 Plays a text-to-speech snippet using the Google TTS API. After the snippet was played (maximum 10 seconds in streaming 
 mode, longer snippets will be truncated) the previous played song will be resumed. You can queue up to 10 snippets. 
 They're played in the order they are called. To setup the Broker for TTS support, please take a deeper look at the 
 dedicated Google TTS section in this document.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| tts | required | | The text to be auditioned, max. 100 chars. |
| language | optional | en, de, es, fr, it| The tts language. Default: 'de'. |
| force_stream_mode | optional | 0 or 1| If True, the tts snippet will not be saved locally. This has some disadvantages like time delay and inaccurate track resuming.|
| fade_in | optional | 0 or 1 | If True, the volume for the resumed track / radio fades in |
| volume | optional | -1 - 100 | The snippet volume. If -1 (default) the current volume is used.  After the snippet was played, the prevoius volume value is set. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. This affects only the parameter 'volume'.|

######Example
    JSON format:
    {
        'command': 'play_tts',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
            'tts': 'Die Temperatur im Wohnzimmer ist 2 Grad Celsius.'
            'language': 'de',
            'force_stream_mode': '0'
            'volume': 30,
            'group_command': 1
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        [snippet metadata will be sent. After the tts snippet was played, the metadata for] 
        [the resumed track will be sent (e.g. see play_uri UDP response)]
    }
    
    All values for a new track will be sent, but only new and/or different values.

----
#### <a name="g_alarms"></a>get_alarms
 [readonly]
 Gets all registered alarms for a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'alarms'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_pause',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410'
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "alarms": {
        "32": {
            "Duration": "02:00:00",
            "Enabled": false,
            "IncludedLinkZones": false,
            "PlayMode": "SHUFFLE_NOREPEAT",
            "Recurrence": "DAILY",
            "StartTime": "07:00:00",
            "Volume": 25
            }
        },
        "uid": "rincon_000e58c3892e01410",
        ...
    }

----
#### <a name="cur_state">current_state
 Sends all available information from a Sonos speaker to the subscribed clients. You should use this command right after
 your client has been subscribed to the Broker to get the actual Sonos speaker state.
  
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| group_command | optional | 0 or 1 | If 'True', the command is performed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'current_state',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
            'group_command': 1
        }
    }
######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format:
    {
        "additional_zone_members": "rincon_112ef9e4892e00001",
        "alarms": {
            "32": {
                "Duration": "02:00:00",
                "Enabled": false,
                "IncludedLinkZones": false,
                "PlayMode": "SHUFFLE_NOREPEAT",
                "Recurrence": "DAILY",
                "StartTime": "07:00:00",
                "Volume": 25
            }
        },
        "bass": 0,
        "hardware_version": "1.8.3.7-2",
        "ip": "192.168.0.4",
        "led": 1,
        "loudness": 1,
        "mac_address": "10:1F:21:C3:77:1A",
        "max_volume": -1,
        "model": "Sonos PLAY:1",
        "mute": "0",
        "pause": 0,
        "play": 0,
        "playlist_position": 0,
        "playmode": "normal",
        "radio_show": "",
        "radio_station": "",
        "serial_number": "00-0E-58-C3-89-2E:7",
        "software_version": "27.2-80271",
        "status": true,
        "stop": 1,
        "streamtype": "music",
        "track_album_art": "http://192.168.0.4:1400/getaa?s=1&u=x-sonos-spotify%3aspotify%253atrack%253a3xCk8npVehdV55KuPdjrmZ%3fsid%3d9%26flags%3d32",
        "track_artist": "Feuerwehrmann Sam & Clemens Gerhard",
        "track_duration": "0:10:15",
        "track_position": "00:00:00",
        "track_title": "Das Baby im Schafspelz",
        "track_uri": "x-sonos-spotify:spotify%3atrack%3a3xCk8npVehdV55KuPdjrmZ?sid=9&flags=32",
        "treble": 0,
        "uid": "rincon_000e58c3892e01410",
        "volume": 8,
        "zone_icon": "x-rincon-roomicon:bedroom",
        "zone_name": "Kinderzimmer"
    }
    
    This is a complete status response for a Sonos speaker.

----
#### <a name="g_fav_radio"></a>get_favorite_radio_stations
 [readonly]
 Returns the favorite radio stations.
 
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| start_item | optional | | Start position within the Sonos radio favorite list starting with 0. Default: 0 |
| max_items | optional | | Maximum returned items. Default: 50 |

######Example
    JSON format:
    {
        'command': 'get_favorite_radio_stations',
        'parameter': {
            'start_item': 0, # optional, default: 0
            'max_items': 10, # optional, default: 50
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
    JSON format:
    {
        "total": "2",
        "favorites": [
            {
                "title": "Radio TEDDY",
                "uri": "x-sonosapi-stream:s80044?sid=254&flags=32"
            },
            {
                "title": "radioeins vom rbb 95.8 (Pop)",
                "uri": "x-sonosapi-stream:s25111?sid=254&flags=32"
            }
        ],
        "returned": 2
    }
    
    Returns a list containing the total number of favorites, the number of favorites returned, 
    and the actual list of favorite radio stations, represented as a dictionary with 'title' 
    and 'uri' keys.
    Depending on what you're building, you'll want to check to see if the total number of 
    favorites is greater than the amount you requested (`max_items`), if it is, use `start` 
    to page through and get the entire list of favorites.

    
###### UDP Response sent to subscribed clients:
    No UDP response

----
#### <a name="is_coor">is_coordinator
 [readonly]
 Returns the status whether the specified speaker is a zone coordinator or not.
  
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'is_coordinator',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:

    JSON format: 
    {
        "is_coordinator": true,
        "uid": "rincon_b8e93730d19801400"
    }

----
#### <a name="tts_local">tts_local_mode
[readonly]
Returns the status whether Google TTS 'local mode' is available or not. To get the 'local mode' running, 
you have to configure the Google TTS options correctly. If False, only the 'streaming mode' is available. 
This has some disadvantages. Please read the Google TTS section in this documentation. 
  
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. | This can be any uid, the return value is the same for all speakers.

######Example
    JSON format:
    {
        'command': 'tts_local_mode',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:

    JSON format: 
    {
        "is_coordinator": true,
        "uid": "rincon_b8e93730d19801400"
    }

----
#### <a name="get_playlist">get_playlist
 [readonly]
 Returns the the current playlist as a base64 string. You can save this string to use it with the set_playlist command.

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_playlist',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
        }
    }

######HTTP Response
    HTTP 200 OK and a base64 string representing the playlist
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    No UDP response


----
#### <a name="set_playlist">set_playlist
 Sets the playlist for a speaker ( and for the entire zone). You should read a file containing
 the base64-coded playlist (gathered by the get_playlist command) and assign the json variable
  'playlist' with this value.

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| playlist | required | base64 encoded string| The playlist as a base64 encoded string. |
| play_after_insert | optional | 0 or 1 | Starts playing the after inserting the playlist. Default: 0  |

######Example
    JSON format:
    {
        'command': 'set_playlist',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
            'playlist': '#so_pl#gASVwhsAAAAAAABdlIwUc29jby5kYXRhX3N0cnVjdHVyZX.... ,
            'play_after_insert': 1
        }
    }

######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    No UDP response