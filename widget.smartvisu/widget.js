/*
-----------------------------------------------
ADD this line to widget.js
-----------------------------------------------
 */

$(document).delegate('[data-widget="sonos.music"]',{update:function(e,r){document.getElementById(this.id).src=r.toString()+'?_=' + new Date().getTime();}});