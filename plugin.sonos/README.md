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
      broker_url = 192.168.178.31:12900               #this is the sonos server ip and port


  Go to /usr/smarthome/items
    
  Create a file named sonos.conf
  
  Edit file with this sample of mine:
  
  
    [sonos]
      sonos_uid = RINCON_000E68D3892A21401            # replace uid your speaker's uid

      [[mute]]
          type = bool
          sonos_recv = speaker/<sonos_uid>/mute
          sonos_send = speaker/<sonos_uid>/mute/set/{}
  
      [[led]]
          type = bool
          sonos_recv = speaker/<sonos_uid>/led
          sonos_send = speaker/<sonos_uid>/led/set/{}
  
      [[volume]]
          type = num
          sonos_recv = speaker/<sonos_uid>/volume
          sonos_send = speaker/<sonos_uid>/volume/set/{}

      [[stop]]
        type = bool
        sonos_recv = speaker/<sonos_uid>/stop
        sonos_send = speaker/<sonos_uid>/stop/set/{}

      [[play]]
        type = bool
        sonos_recv = speaker/<sonos_uid>/play
        sonos_send = speaker/<sonos_uid>/play/set/{}

      [[pause]]
        type = bool
        sonos_recv = speaker/<sonos_uid>/pause
        sonos_send = speaker/<sonos_uid>/pause/set/{}

      [[track]]
        type = str
        sonos_recv = speaker/<sonos_uid>/track
    
  
  To get your sonos speaker id, type this command in your browser (while sonos server running):
  
    http://<sonos_server_ip:port>/client/list
      
    
  
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
    
