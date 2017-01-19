## Release

v1.0b3  (2017-01-19)

    -- much better event based  GoogleTTS handling

v1.0b2  (2017-01-17)

    -- bug: wrong path in systemd script
    -- bug: logging unicode error 

v1.0b1 (2017-01-08)
    
    -- integrated webservice to serve audio files for the Sonos speakers
    -- bug: the 'volume' of all zone members will now be restored correctly after playing the snippet
    -- command optional parameter 'play' added to command "unjoin"
        -- with 'play' set to true, the prevoiusly played track (before joining a group) will resumed
    -- changed executable name from "sonos_broker" to "sonos-broker"
    -- changed command line tool from "sonos_cmd" to "sonos-cmd"
    -- changed default installation path of sonos_broker.cfg to /etc/default/sonos-broker
    -- stopping a running Sonos Broker instance is handled a bit more gracefully
    -- updated setup script
    -- auto-start scripts for systemd and upstart automatically placed in the appropriate folder by the 
       installation script  
    -- 'daemonize' behaviour removed
    -- unnecessary parameter 'stop' removed
    -- updated documentation
    -- added "zone_member" command to Sonos Broker (to retrieve this value actively)
    -- added commands 'join' and 'unjoin' to Sonos Broker commandline tool
    -- bug: error when trying to decode non-ascii chars and the systems stdout was no set to utf8

v0.9   (2016-11-20)

    -- added missing 'track_album' property
    -- added missing 'track_album' to Sonos-Broker commandline
    -- added "get_playlist_position" command and "playlist_position" property to Sonos Broker and
       Sonos Broker commandline tool
    -- added "get_playlist_total_tracks" command and "playlist_total_tracks" property to Sonos Broker and 
       Sonos Broker commandline tool
    -- added missing 'track_album_art' property to Sonos Broker commandline tool
    -- bug: 'playlist_position' was not handled correctly
    -- changed maximum snippet length to 15 seconds
    -- bugfixed: Sonos Broker user-specific server port was ignored
    -- updated documentation
    

## Overview

	
The shSonos project is Sonos control server, mainly based on the brilliant SoCo project (https://github.com/SoCo/SoCo). 
It implements a lightweight http server, which is controlled by simple HTTP json commands.
It sends all available Sonos speaker data to all subscribed clients and notifies them of all changes.

The Sonos Broker implements some nice additional features like GoogleTTS, saving/restoring the playlist, maximum
volume settings for each Sonos speaker and much more.

In addition , i decided to write a plugin for the fantastic "Smarthome.py Project" to control Sonos speakers in a 
smart home environment (https://github.com/mknx/smarthome/).


## Requirements

#### Deleting old files

If're updating the Broker it may be a good idea to delete old files. Please adapt the paths to your system.

```
sudo rm -rf /usr/local/bin/sonos*
sudo rm -rf /usr/local/lib/python3.5/site-packages/*sonos*
sudo rm -rf /usr/local/lib/python3.5/site-packages/soco
```

#### Server-side

python3.4
python3 libraries 'requests' and 'xmltodict' 


#### Client-side 

Nothing special, just send your commands over http (JSON format) or use the Smarthome.py plugin to control
the speakers within Smarthome.py.
You can use the included built-in implementation, the [Sonos Broker commandline tool](#cmd_tool) 


## Installation

#### Setup

Under the github folder "server.sonos/dist/" you'll find the actual release as a tar.gz file. Here are two ways to 
install the Sonos Broker:

##### 1. pip

If python3-pip is installed, you can simply call

    python3 -m pip -v install sonos-broker-{release-version}.tar.gz

Every dependency should be installed automatically. 
    
##### 2. manually 

Untar the file with and install it manually. 

    tar -xvf sonos-broker-{release}.tar.gz
    cd sonos-broker-{release}
    sudo python3 setup.py install --force

If an error occurred, you should try to (re)-install all necessary dependencies:
  
    pip3 install requests
    pip3 install xmltodict

Both methods will install ```sonos-broker``` and ```sonos-cmd``` under ```/usr/local/bin``` to make both commands 
system-wide executable. 
The default config file is installed under ```/etc/default/sonos-broker``.

The internal ip address should be set up automatically. If not, you have to edit ```/etc/default/sonos-broker```

    [sonos_broker]
    server_ip = x.x.x.x #your ip here


#### Configuration / Start options

You can edit the settings of Sonos Broker. Open '/etc/default/sonos-broker' (by default) with your favorite editor and 
edit the file. All values within the config file should be self-explaining. For Google-TTS options, see the appropriate 
section in this Readme.

You can start the sonos broker with
```
sonos_broker start
```

You can add the -d (--debug) parameter to get more output
```
sonos_broker start -d
```

An user-specified config file can be passed with the '-c' flag. Default: /etc/default/sonos-broker
```
sonos_broker start -c /your/config/file/path/here
```

To get a short overview of your speakers in the network start the server with
```
sonos_broker list
```

To get an overview of all parameters type
```
sonos_broker -h
```
and / or
```
sonos_broker {command} -h
```

After the successful installation with ```sudo python3 setup.py install --force``` an autostart script should be placed 
automatically in your systems autostart directory. The autostart implementations are integrated for systems based on 
'SYSTEMD' and 'UPSTART'. 'SYSVINIT' is NOT supported because of there are too many different sysvinit implementations. 
To control the Broker via the system service control, see the commands below:
 
<b>SYSTEMD:</b>
```sudo systemctl [start|stop|restart] sonos-broker```

For autostart:
```sudo systemctl enable sonos-broker```


<b>UPSTART:</b>
```sudo service sonos-broker [start|stop|restart]```

For autostart uncomment following line in ```/etc/init/sonos-broker.conf```:
```#start on runlevel [2345]```


To get some more debug output when running the Broker as a service, please edit the Sonos Broker config file 
(default: /etc/default/sonos-broker) and uncomment this line in the logging section:

    loglevel = debug

You can set the debug level to debug, info, warning, error, critical.
Additionally, you can specify a file to pipe the debug log to this file.

    logfile = /path/to/your/log.txt


## Interactive Command Line

You can control the Broker and your speakers without implementing your own client. To start the interactive
command line (the Broker must be running) type
```
sonos-cmd
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
 

## Integrated webservice for audio files

Sonos Broker integrates an internal webservice to serve audio files for Sonos speakers. You can enable this feature in
the \[webservice\] section of the Sonos Broker configuration. If enabled, you can store audio files in the configurable
web root path (valid extensions: aac, mp4, mp3, ogg, wav, web) and they can be played with the 
[play_snippet](#p_snippet) command. The URL is available via http://SONOS_BROKER_IP:SONOS_BROKER_PORT/. 
This service is also helpful for the Google TTS functionality.


## Google TTS Support

Sonos broker features the Google Text-To-Speech API. You can play any text limited to 100 chars.


#### Prerequisite:

- local / remote mounted folder or share with read/write access
- http access to this local folder (e.g. /var/www)
- settings configured in sonos-broker configuration file (default: /etc/default/sonos-broker)
- running a webservice

#### Internals

If a text is given to the google tts function, the Sonos Broker makes a http request to the Google API. The response is 
stored as a mp3-file to a local / remote folder. 
    
Before the request is made, the broker checks whether a file exists with the same name. The file name of a tts-file 
is always:  BASE64(<tts_txt>_<tts_language>).mp3. You can set a file quota in the config file. This limits the amount 
of disk space the broker can use to save tts files. If the quota exceeds, you will receive a message. By default the 
quota is set to 100 mb.

    [google_tts]
    quota = 200

By default, Google TTS support is disabled. To enable the service, add following line to your sonos-broker 
configuration:

    [google_tts]
    enable = true

You have to set the local save path (where the mp3 is stored) and an accessible url. If're using the integrated
webservice, 'save_path' and 'root_path' in the \[webservice\] section should be the same value.     
The server url must point to a webservice that handles the Sonos speaker requests, e.g. a nginx or apache server. By 
enabling the integrated webservice, this is done by the Sonos Broker.
 
    [google_tts]
    save_path = /var/www/tts
    server_url = http://192.168.0.2/tts

This is an example of a google_tts section in Sonos Broker configuration file:

    [google_tts]
    enable=true
    quota=200
    save_path = /var/www/tts
    server_url = http://192.168.0.2:12900/tts


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
        "playlist_position": "1",
        "playlist_total_tracks": "10",
        "playmode": "normal",
        "radio_show": "",
        "radio_station": "",
        "serial_number": "00-0E-58-C3-89-2E:7",
        "software_version": "27.2-80271",
        "sonos_playlists": "DepecheMode,my_fav-list2,my-fav-list2",
        "status": true,
        "stop": 1,
        "streamtype": "music",
        "track_album": "Feuerwehrmann Sam 02",
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
###### [get_balance](#g_balance)
###### [set_balance](#s_balance)
###### [get_loudness](#g_loudness)
###### [set_loudness](#s_loudness)
###### [get_led](#g_led)
###### [set_led](#s_led)
###### [get_playmode](#g_playmode)
###### [set_playmode](#s_playmode)
###### [get_track_position](#g_track_position)
###### [set_track_position](#s_track_position)
###### [get_track_album](#g_track_album)
###### [get_track_title](#g_track_title)
###### [get_track_artist](#g_track_artist)
###### [get_track_album_art](#g_track_album_art)
###### [get_track_uri](#g_track_uri)
###### [get_playlist_position](#g_playlist_position)
###### [get_playlist_total_tracks](#g_playlist_total_tracks)
###### [get_radio_station](#g_radio_station)
###### [get_radio_show](#g_radio_show)
###### [join](#s_join)
###### [unjoin](#s_unjoin)
###### [partymode](#s_partymode)
###### [play_tunein](#p_tunein)
###### [play_uri](#p_uri)
###### [clear_queue](#clear_queue)
###### [play_snipptet](#p_snippet)
###### [play_tts](#p_tts)
###### [get_alarms](#g_alarms)
###### [current_state](#cur_state)
###### [get_favorite_radio_stations](#g_fav_radio)
###### [is_coordinator](#is_coor)
###### [tts_local_mode](#tts_local)
###### [get_sonos_playlists](#get_sonos_playlists)
###### [load_sonos_playlist](#load_sonos_playlist)
###### [refresh_media_library](#ref_lib)
###### [zone_members](#zone_members)
###### [get_wifi_state](#get_wifi)
###### [set_wifi_state](#set_wifi)
###### [discover](#discover)
###### [sonos_broker_version](#sonos_broker_version)

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
        'command': 'set_treble',
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
#### <a name="g_balance">get_balance
 Gets the current balance settings from a Sonos speaker.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'balance'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_balance',
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
        "balance": [-100 - 100], 
        "uid": "rincon_b8e93730d19801410",
        ...
    }

----
#### <a name="s_balance">set_balance
 Sets the treble for a Sonos speaker.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| balance | required | -100 - 100 | The balance to be set. Default: 0|
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'set_balance',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'treble': ,
            'group_command': 0
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    { 
        ...
        "balance": [-100 - 100], 
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

#### <a name="g_track_album">get_track_album
 Returns the album title of the currently played track.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'track_album'-status changes.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_track_album',
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
        "track_album": "Delta Machine",
        "uid": "rincon_b8e93730d19801410",
        ...
    }

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

----
#### <a name="g_playlist_position">get_playlist_position
 Returns the position of the currently played track in the playlist.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'playlist_position'-status changes.

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | string | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_playlist_position',
        'parameter': {
            'uid': 'rincon_b8e91111d11111400'
        }
    }

######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    JSON format:
    {
        ...
        "uid": "rincon_b8e91111d11111400",
        "playlist_position": "3"
        ...
    }

----
#### <a name="g_playlist_total_tracks">get_playlist_total_tracks
 Returns the total number of tracks in the current playlist.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'playlist_total_tracks'-status changes.

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | string | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_playlist_total_tracks',
        'parameter': {
            'uid': 'rincon_b8e91111d11111400'
        }
    }

######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    JSON format:
    {
        ...
        "uid": "rincon_b8e91111d11111400",
        "playlist_total_tracks": "13"
        ...
    }
    
----
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
| play | optional | True/False, 0/1 | Should the speaker automatically start playing after unjoin. |

######Example
    JSON format:
    {
        'command': 'unjoin',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'play': False
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
#### <a name="clear_queue">clear_queue
 Clears the queue.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |


######Example
    JSON format:
    {
        'command': 'clear_queue',
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
        "track_title": "",
        "uid": "rincon_000e58c3892e01410",
        ...
    }
    

----
#### <a name="p_tunein">play_tunein
 Plays a radio station by a give name.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| station_name | required | | A radio station. The first found station is played. The more accurate the name, the better is the result. |


######Example
    JSON format:
    {
        'command': 'play_tunein',
        'parameter': {
            'uid': 'rincon_b8e93730d19801410',
            'station_name': '98.8 KISS FM'
        }   
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "radio_show": "Die BJ Barry Show",
        "radio_station": "98.8 KISS FM",
        "track_album_art": "http://192.168.178.21:1400/getaa?s=1&u=x-sonosapi-stream%3as16523%3fsid%3d254%26sn%3d0",
        "track_artist": "Sia Feat. Kendrick Lamar",
        "track_title": "Sia Feat. Kendrick Lamar - The Greatest",
        "uid": "rincon_000e58c3892e01410"
        ...
    }
    
    All values for a radio station will be sent, but only new and/or different values.

----
#### <a name="p_snippet">play_snippet
 Plays a audio snippet. After the snippet was played (maximum 60 seconds, longer snippets will be truncated)
 the previous played song will be resumed.
 
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
 Plays a text-to-speech snippet using the Google TTS API. To setup the Broker for TTS support, please take a deeper 
 look at the dedicated Google TTS section in this document.

| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| tts | required | | The text to be auditioned, max. 100 chars. |
| language | optional | en, de, es, fr, it| The tts language. Default: 'de'. |
| fade_in | optional | 0 or 1 | If True, the volume for the resumed track / radio fades in |
| volume | optional | -1 - 100 | The snippet volume. If -1 (default) the current volume is used.  After the snippet was played, the prevoius volume value is set. |
| group_command | optional | 0 or 1 | If 'True', the command is executed for all zone members of the speaker. This affects only the parameter 'volume'.|

######Example
    JSON format:
    {
        'command': 'play_tts',
        'parameter': {
            'uid': 'rincon_000e58c3892e01410',
            'tts': 'Die Temperatur im Wohnzimmer beträgt 2 Grad Celsius.'
            'language': 'de',
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
        "additional_zone_members": "",
        "alarms": "",
        "balance": 0,
        "bass": 0,
        "display_version": "6.0",
        "hardware_version": "1.8.1.2-2",
        "household_id": "Sonos_Ef8RhcyY1ijYDDFp1I3GitguTP",
        "ip": "192.168.0.11",
        "is_coordinator": true,
        "led": 1,
        "loudness": 1,
        "mac_address": "B8-E9-37-38-E1-72",
        "max_volume": -1,
        "model": "Sonos PLAY:3",
        "model_number": "S3",
        "mute": 0,
        "pause": 1,
        "play": 0,
        "playlist_position": "1",
        "playlist_total_tracks": "10",
        "playmode": "normal",
        "radio_show": "",
        "radio_station": "",
        "serial_number": "B8-E9-37-38-E1-72:5",
        "software_version": "31.3-22220",
        "sonos_playlists": "Morning,Evening,U2",
        "status": true,
        "stop": 0,
        "streamtype": "music",
        "track_album_art": "http://192.168.0.11:1400/getaa?s=1&u=x-sonos-http%3atr%253a119434742.mp3%3fsid%3d2%26flags%3d8224%26sn%3d1",
        "track_artist": "Was ist Was",
        "track_duration": "0:02:22",
        "track_position": "00:00:00",
        "track_title": "Europa - Teil 10",
        "track_uri": "x-sonos-http:tr%3a119434742.mp3?sid=2&flags=8224&sn=1",
        "treble": 0,
        "tts_local_mode": false,
        "uid": "rincon_b8e91111d11111400",
        "volume": 17,
        "wifi_state": 1,
        "zone_icon": "/img/icon-S3.png",
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
            'uid': 'rincon_b8e91111d11111400',
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:

    JSON format: 
    {
        "is_coordinator": true,
        "uid": "rincon_b8e91111d11111400"
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
            'uid': 'rincon_b8e91111d11111400',
        }
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:

    JSON format: 
    {
        "is_coordinator": true,
        "uid": "rincon_b8e91111d11111400"
    }


----
#### <a name="get_sonos_playlists">get_sonos_playlists
 Gets all Sonos playlists separated by ','.

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | string | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'get_sonos_playlists',
        'parameter': {
            'uid': 'rincon_b8e91111d11111400'
        }
    }

######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    JSON format:
    {
        ...
        "uid": "rincon_b8e91111d11111400",
        "sonos_playlists": "mylist,another_list,Abba'
        ...
    }


----
#### <a name="load_sonos_playlist">load_sonos_playlist
 Loads a Sonos playlist by a given name.
 
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| sonos_playlist | required | string | A Sonos playlist name. (see get_sonos_playlists) |
| play_after_insert | optional | 0 or 1 | Start playing after loading the Sonos playlist. Default: 0 |
| clear_queue | optional | 0 or 1 | Clears the queue before loading list. Default: 0 |

######Example
    JSON format:
    {
        'command': 'load_sonos_playlist',
        'parameter': {
            'uid': "rincon_b8e91111d11111400",
            'sonos_playlist': "DepecheMode",
            'play_after_insert': 1,
            'clear_queue': 1
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    No specific response


----
#### <a name="ref_lib">refresh_media_library
 Updates the local media library. This is useful when adding a new music file to your local media library.
 
| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| display_option | optional | NONE, ITUNES, WMP| Default 'NONE'. For further information see <a href="http://www.sonos.com/support/help/3.4/en/sonos_user_guide/Chap07_new/Compilation_albums.htm">Sonos Help Page</<a>|

######Example
    JSON format:
    {
        'command': 'refresh_media_library',
        'parameter': {
            'display_option': "ITUNES"
        }
    }

######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    No UDP response
    

----
#### <a name="zone_members">zone_members
 Gets all additional zone members of the group the current speaker is part of. If the speaker is the only member of the
 group, the response is empty.
 In most cases, you don't have to execute this command, because all subscribed clients will be notified automatically
 about 'zone_members'-status changes.

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |

######Example
    JSON format:
    {
        'command': 'zone_members',
        'parameter': {
            'uid': rincon_b8e91111d11111400
    }
   
######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "zone_members": ["rincon_c4441111d11111400", "rincon_d5ee1111d11111400"]
        "uid": "rincon_b8e91111d11111400"
        ...
    }

----
#### <a name="get_wifi">get_wifi_state
 Gets the current wifi status. Since there is no sonos event for the wifi state, you have to trigger
 this command manually to retrieve the value. 

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| force_refresh | optional | 0 or 1| If True|1, the Broker queries the speaker for its wifi state, otherwise the cached value for state is used. Default: 0|

######Example
    JSON format:
    {
        'command': 'get_wifi_state',
        'parameter': {
            'uid': rincon_b8e91111d11111400,
            'force_refresh': 0
    }
   
######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    JSON format: 
    {
        ...
        "wifi_state": 1,
        "uid": "rincon_b8e91111d11111400"
        ...
    }
    

----
#### <a name="set_wifi">set_wifi_state
 Sets the current wifi status. The parameter "persistent" only affects the wifi state "off". 
 Normally, after a reboot the wifi interface is enabled again. With a combination of "wifi_state = 0"
 and "persistent = 1" the wifi interface will remain deactivated.

| parameter | required / optional | valid values | description |
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| wifi_state | required | 0 or 1 | If False, the wifi interface will be deactivated, otherwise it will be enabled. |
| persistent | optional | 0 or 1 | If True, the wifi interface will remain deactivated after a reboot of the speaker. Default: 0 |

######Example
    JSON format:
    {
        'command': 'set_wifi_state',
        'parameter': {
            'uid': rincon_000e58c3892e01410,
             'wifi_state': 0,
             'persistent': 0
         }
    }
   
######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    No UDP response


----
#### <a name="sonos_broker_version">sonos_broker_version
 Gets the Sonos Broker version.
 
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| no parameters  |

######Example
    JSON format:
    {
        'command': 'sonos_broker_version'
    }

######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######HTTP Response
    Sonos Broker version string.

----
#### <a name="discover>discover
 Performs a manual scan for Sonos speaker in the network. This command requires no parameters.
 
######Example
    JSON format:
    {
        'command': 'discover'
    }
   
######HTTP Response
    HTTP 200 OK
        or
    Exception with HTTP status 400 and the specific error message.

###### UDP Response sent to subscribed clients:
    No UDP response
