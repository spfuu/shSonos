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

  Go to /usr/smarthome/etc and edit plugins.conf and add ths entry:
  
  
    [sonos]
  
      class_name = Sonos
      class_path = plugins.sono
  


  Go to /usr/smarthome/items
    
  Create a file named sonos.conf
  
  Edit file with this sample of mine:
  
  
    [sonos]
        sonos_uid = RINCON_000E58D5892E11230 #your sonos speaker id here

        [[mute]]
                type = bool
                sonos_recv = <sonos_uid> mute
                sonos_send = <sonos_uid> mute {}
  
  
  To get your sonos speaker id, use (while sonos server running) the python script in the server.sonos project:
      
  !!! The server can only handle one connection, so make sure, no other client is connected (e.g. Smarthome.py).
  !!! It will result in a client loop and no server response 
      
  
    sonos_client.py refresh all
    sonos_client.py list all complete
      
  
  
  response:
      
      <result status="True" type="data">
        <data>
          <speaker>
            <hardware_version>1.8.3.7-2</hardware_version>
            <id>1</id>
            <ip>192.168.178.40</ip>
            <mac_address>00:0E:58:C4:80:2E</mac_address>
            <model>ZPS1</model>
            <serial_number>00-0E-58-C4-80-2E:7</serial_number>
            <software_version>24.0-71060</software_version>
            <status>1</status>
            <uid></uid>RINCON_000E58D5892E11230
            <zone_icon>x-rincon-roomicon:living</zone_icon>
            <zone_name>Wohnzimmer</zone_name>
          </speaker>
        </data>
        <info></info>
      </result>      
        
    
  To run this plugin with a logic, here is my example:
    
  Go to /usr/smarthome/logics and create a self-named file (e.g. sonos.py)
  Edit this file and place your logic here:
    
    
    #!/usr/bin/env python
    #

    if sh.ow.ibutton():
        sh.sonos.mute(1)
    else:
        sh.sonos.mute(0)

    
  Last step: go to /usr/smarthome/etc and edit logics.conf
  Add a section for your logic:
    
    # logic
    [sonos_logic]
        filename = sonos.py
        watch_item = ow.ibutton
    
    
    
  In this small example, the sonos speaker with uid RINCON_000E58D5892E11230 is muted when the iButton is connected       to an iButton Probe.
    
