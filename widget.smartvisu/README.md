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

Add following line to the end of the files **widgets.js** and **widgets.min.js** (also located in the widgets folder)

```JavaScript
$(document).delegate('[data-widget="sonos.music"]',{update:function(e,r){document.getElementById(this.id).src=r.toString()+'?_=' + new Date().getTime();}});
```

##Integration in smarthome.py

To make use of the auto-generation feature of smarthome.py and smartVISU, init the widget in your item.conf with the 
following syntax:

```
sv_widget = {% import "sonos.html" as sonos %} {{ sonos.music(id, gad_play, gad_stop, gad_vol_up, gad_vol_down, gad_volume, gad_album_art) }}
```

Change the gad items to your needs. Here is an example integration:

```
[floor1]
    [[room1]]
        name = Lautsprecher
        type = foo
        sv_page = room
        sv_widget = {% import "sonos.html" as sonos %} {{ sonos.music('radio1', 'Kueche.play', 'Kueche.stop', 'Kueche.volume_up', 'Kueche.volume_down', 'Kueche.volume', 'Kueche.track_album_art') }}
```

You can find an example configuration for the item 'Kueche' here:

https://github.com/pfischi/shSonos/blob/develop/plugin.sonos/examples/sonos.conf

 
