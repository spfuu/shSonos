##Release

v.04    (2017-03-07)

    -- moved the js and css content to visu.js and visu.css
    -- bug: transport_actions should now work correctly in any cases

v0.3    (2017-02-18)

    -- complete rewrite of widget for Sonos Broker >= 1.0
    -- compatible for SmartVISU 2.8 and 2.9 (untested)

v0.2    (2014-12-05)

    --  fixed issue, that a cover was not shown correctly

v0.1.1  (2014-07-09)

    --  if no album cover is given, a transparent png is shown

v0.1    (2014-07-08)

    --  first release

---
### Requirements

Sonos Broker server min. v1.0b7 (https://github.com/pfischi/shSonos)
Sonos Plugin for smarthome.py (https://github.com/pfischi/shSonos/tree/master/plugin.sonos)
SmarthomeNG >=v1.2 (https://github.com/smarthomeNG)
smartVISU >=v2.8 (http://www.smartvisu.de/)

##### IMPORTANT
It is highly recommended that you use the same Sonos item structure as shown in the 
[Sonos plugin example](https://github.com/pfischi/shSonos/blob/develop/plugin.sonos/examples/sonos.conf). This item
structure always matches the requirements for the Sonos widget. You can edit ```sonos.html``` if you have your own 
structure. 

---
### Integration in smartVISU

Copy **sonos.html** to your smartVISU pages directory, e.g.

```
/var/www/smartvisu/pages/YOUR_PATH_HERE 
```

Change to this directory and append the content of **sonos.js** to ```visu.js``` and **sonos.css** to ```visu.css```.
Create both file if they do not not exist.


Copy **sonos_empty.jpg** to the base pic's folder, e.g.
```
/var/www/smartvisu/pages/base/pics/sonos_empty.jpg
```

Edit your page where you want to display the widget and add the following code snippet:

```
{% import "sonos.html" as sonos %}

{% block content %}

<div class="block">
  <div class="set-2" data-role="collapsible-set" data-theme="c" data-content-theme="a" data-mini="true">
    <div data-role="collapsible" data-collapsed="false" >
      {{ sonos.player('sonos_kueche', 'Sonos.Kueche') }}
    </div>
  </div>
</div>

{% endblock %}

```
Rename ```Sonos.Kueche``` to your Sonos item name in SmarthomeNG.
If your're using another root directory than ```/``` for your SmartVISU installation, you have to adapt the file
`sonos.html` and change the following entry to your needs:
```
{% set cover_default      = '[YOUR_WBE_ROOT_HERE]/pages/base/pics/sonos_empty.jpg' %}
```