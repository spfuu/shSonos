This is the subproject 'plugin.sonos' for the Smarthome.py framework (https://github.com/mknx/smarthome).
The plugin is designed to control the sonos speakers in connection with the sonos server.

1. Installation
-----------------------------

  Login to your Raspberry Pi
  
  Go to /usr/smarthome/plugins
  
  Create directory sonos (or whatver you want, plugins will be scanned automatically in this subfolder)
  
  Copy __init__.py to your newly created path.
  
  Done


2. Integration in Smarthome.py
------------------------------

  Go to /usr/smarthome/items
  
  Create a file named sonos.conf
  
  Edit file with this sample of mine:
  
    [sonos]
        sonos_uid = RINCON_000E58D5892E11230 #your sonos speaker id here

        [[mute]]
                type = bool
                sonos_recv = <sonos_uid> mute
                sonos_send = <sonos_uid> mute {}

  To get your sonos speaker id, use (while sonos server running)
    
    a. the python script in the server.sonos project:
      
      sonos_client.py refresh all
      sonos_client.py list all complete
      
      
        
