$(document).on('pagecreate', function (bevent, bdata) {

  // ----- pfischi.music_control ---------------------------------------------------------
	$(bevent.target).find('span[data-widget="pfischi.music_control"]').on({
		'update': function (event, response) {
			event.stopPropagation();
			$(this).val(response);
      var action = $(this).attr('data-action')
      var val_on = $(this).attr('data-val-on')
      var val_off = $(this).attr('data-val-off')
      var active = 'false';
      if (response[0].toLowerCase().indexOf(action.toLowerCase()) >= 0){
        active = "true";
      }
			if(active == "true") {
        if(val_on == response[1]) {
  				$(this).find('#' + this.id + '-inactive').hide();
  				$(this).find('#' + this.id + '-active-on').show();
          $(this).find('#' + this.id + '-active-off').hide();
        }
        else {
  				$(this).find('#' + this.id + '-inactive').hide();
  				$(this).find('#' + this.id + '-active-on').hide();
          $(this).find('#' + this.id + '-active-off').show();
        }
			}
			else {
				$(this).find('#' + this.id + '-active-on').hide();
        $(this).find('#' + this.id + '-active-off').hide();
				$(this).find('#' + this.id + '-inactive').show();
		  }
      $(this).attr('data-active', active);
    },
		'click': function (event) {
      if ($(this).attr('data-active') == 'true') {
        io.write($(this).attr('data-send'), ($(this).val()[1] == $(this).attr('data-val-off') ? $(this).attr('data-val-on') : $(this).attr('data-val-off')) );
      }
		},
    'touchstart mousedown': function (event, response) {
      event.stopPropagation();
      if ($(this).attr('data-active') == 'true') {
        $(this).css({ transform: 'scale(.8)' });
      }
    },
    'touchend mouseup': function (event, response) {
      event.stopPropagation();
      $(this).css({ transform: 'scale(1)' });
    }
	});

  $(bevent.target).find('img[data-widget="pfischi_sonos.cover"]').on({
    'update': function (event, response) {
      event.stopPropagation();
			if (!response[0].trim()) {
					$(this).attr('src', $(this).attr('data-cover'));
			}
			else {
      	$(this).attr('src', response[0]);
			}
    }
  });

  $(bevent.target).find('div[data-widget="pfischi_sonos.artist"]').on({
    'update': function (event, response) {
      event.stopPropagation();
			if (response[2] == 'radio') {
				$(this).html(response[1]); // show radio track title
			}
			else {
				$(this).html(response[0]); // show track artist
			}
    }
  });

  $(bevent.target).find('div[data-widget="pfischi_sonos.title"]').on({
    'update': function (event, response) {
      event.stopPropagation();
			if (!response[2].trim()) {
				$(this).html('No music');
			}
			else {
				if (response[3] == 'radio') {
					$(this).html(response[1]); // show radio station
				}
				else {
					$(this).html(response[0]); // show track title
				}
			}
    }
  });

  $(bevent.target).find('div[data-widget="pfischi_sonos.album"]').on({
    'update': function (event, response) {
      event.stopPropagation();
      $(this).html(response[0]);
    }
  });

  $(bevent.target).find('div[class="play"]').on({
    'touchstart mousedown': function (event, response) {
      event.stopPropagation();
      $(this).css({ transform: 'scale(.8)' });
    },

    'touchend mouseup': function (event, response) {
      event.stopPropagation();
      $(this).css({ transform: 'scale(1)' });
    }
  });

  $(bevent.target).find('div[class="next"]').on({

    'touchstart mousedown': function (event, response) {
      event.stopPropagation();
      $(this).css({ transform: 'scale(.8)' });
    },

    'touchend mouseup': function (event, response) {
      event.stopPropagation();
      $(this).css({ transform: 'scale(1)' });
    }
  });
})
