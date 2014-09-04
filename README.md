#Release
v0.3

    --  !! ATTENTION !!: commands are changed to JSON commands. They are more flexible 
        than the old HTTP GET commands.
        Please adapt your clients to this new feature. Older clients won't work. 
        Please read the manual to set it up and get some example implementations.
        If you're running the Broker together with the Smarthome.py framework, 
        make sure you use the newest Sonos plugin. 

    --  !! ATTENTION !! Read previous point !!
    --  !! ATTENTION !! Read previous point !!
     
    --  commands 'Volume', 'Mute', 'Led', 'Treble', 'Bass', 'Loudness' can now be group 
        commands by adding 'group_command: 1' to the json command structure 
    --  !! seek command is now named SetTrackPosition (see documentation)
    --  !! to get the current track position, poll GetTrackInfo with 'force_refresh' option
        (see documentation)
    --  removed command track_info() (this was only useful to get the current track 
        position; use GetTrackInfo instead
    --  the Broker now sends only the current changed speaker values instead of the whole 
        sonos data structure. This results in much less network traffic / overhead.
    --  Bug: fixed a problem with join command: join could fail, if the group to join have
        had more than ne speaker
    --  Bug: fixed permission problem when saving a google tts sound file
    --  Bug: sometimes the search for the group coordinator doesn't found a valid object
    --  Bug: Loglevel for the SoCo framework differed from the Broker settings
    --  added some debug outputs, especially the commands are now logged more detailed
    --  much cleaner code and improvements 


###This is just the working developer branch. I'm using it as a backup. 
###Don't use this code for your code base. It won't work. 
###Use the Developer or Master Branch instead. 


###Available commands

####Overview

[client_subscribe](@client_subscribe)
[client_list](@client_list)
[get_play](@get_play)
[set_play](@set_play)


----
#### <a name="client_subscribe"></a>client_subscribe
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

####client_unsubscribe
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

#### <a name="client_list">client_list
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
                <p>uid: rincon_000e58c3892e01410</p>
                <p>ip: 192.168.0.4</p>
                <p>model: Sonos PLAY:1</p>
                <p>current zone: Kitchen</p>
                <p>----------------------</p>
                <p>uid: rincon_b8e93730d19801410</p>
                <p>ip: 192.168.0.10</p>
                <p>model: Sonos PLAY:3</p>
                <p>current zone: Kueche</p>
                <p>----------------------</p>
            </body>
        </html>
    
    Response Code: 200 OK or Exception with Code 400 and the specific error message.        
    
----
#### <a name="get_play">get_play
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
#### <a name="set_play">set_play
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
####get_pause
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
####set_pause
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
####get_stop
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
####set_stop
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
####get_volume
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
####set_volume
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
####get_max_volume
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
####set_max_volume
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
####get_mute
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
####set_mute
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
####volume_up
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
####volume_down
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
####next
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
####previous
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
####get_bass
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
####set_bass
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
####get_treble
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
####set_treble
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
####get_loudness
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
####set_loudness
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
####get_led
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
####set_led
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
####current_state
 Sends all available information from a Sonos speaker to the subscribed clients.
  
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| uid | required | | The UID of the Sonos speaker. |
| group_command | optional | 0 or 1 | If 'True', the command is performed for all zone members of the speaker. |

######Example
    JSON format:
    {
        'command': 'current_state',
        'parameter': {
            'uid': 'rincon_b8e93730d19801401',
            'group_command': 1
        }
    }
######HTTP Response
    HTTP 200 OK or Exception with HTTP status 400 and the specific error message.
    
######UDP Response sent to subscribed clients:
    {
        test
    }