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


####Available commands

----
####client_subscribe
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

####client_list
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
####get_play
 Gets the PLAY status for a Sonos speaker. If the speaker has additional zone members, the PLAY status for all
 members will be sent.

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
####set_play
 Sets the PLAY status for a Sonos speaker. If the speaker has additional zone members, the PLAY status for all
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
 Gets the PAUSE status for a Sonos speaker. If the speaker has additional zone members, the PAUSE status for all
 members will be sent.

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
 Sets the PAUSE status for a Sonos speaker. If the speaker has additional zone members, the PAUSE status for all
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
 Gets the STOP status for a Sonos speaker. If the speaker has additional zone members, the STOP status for all
 members will be sent.

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
 Sets the STOP status for a Sonos speaker. If the speaker has additional zone members, the STOP status for all
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
| volume | required | 0 - 100 | The volume to set. |
| group_command | optional | 0 or 1 | If 'True', the command is performed for all zone members of the speaker. |

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