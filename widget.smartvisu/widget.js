/*
-----------------------------------------------
ADD this line to widget.js
-----------------------------------------------
 */

$(document).delegate('[data-widget="sonos.music"]',{update:function(e,r){if (r.toString()){document.getElementById(this.id).src=r.toString()+'?_='+new Date().getTime();}else{document.getElementById(this.id).src="pages/base/pics/trans.png";}}});