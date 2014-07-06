This is the subproject 'plugin.sonos' for the Smarthome.py framework (https://github.com/mknx/smarthome).
The plugin is designed to control the sonos speakers in connection with the sonos server.


##Release
  v0.1  2014-07-05
    
    --  first release


##Requirements:

  sonos_broker server min. v0.2.3 (https://github.com/pfischi/shSonos)
  
  sonos plugin for smarthome.py (https://github.com/pfischi/shSonos/tree/master/plugin.sonos)
  
  smarthome.py (https://github.com/mknx/smarthome)
  
  smartVISU (http://www.smartvisu.de/)
  
  
##Integration in smartVISU

Copy **sonos.html** to the smartVISU widget directory. If you are using the smarthome.py image on a Raspberry Pi, the
default path is:

```
/var/www/smartvisu/widgets
```

Add following line to the end of the files **widgets.js** and **widgets.min.js** (also located in teh widgets folder)

```JavaScript
$(document).delegate('[data-widget="sonos.music"]',{update:function(e,r){document.getElementById(this.id).src=r.toString()+'?_=' + new Date().getTime();}});
```

