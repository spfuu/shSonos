logger.debug(logic.sonos_speaker)
logger.debug('Sonos VolumeUpDown triggered by logic ' + logic.name)

if not hasattr(logic, 'sonos_speaker'):
    logger.error("no 'sonos_speaker' attribute found in logic '{logic}".format(logic=logic.name))
    exit()

logger.debug('######################################')

# list value
# [0,0], [0,1] -> Volume down (1 start, 0 stop)
# [1,0], [1,1] -> Volume up (1 start, 0 stop)

value = trigger['value']
logger.debug(value)

stepping = 3

max_volume = sh.Sonos_Kueche.max_volume()

if value[0] == 1:
    if value[1] == 1:
        logger.debug('vol up')
        sh.Sonos_Kueche.volume.fade(max_volume, stepping, 1)
else:
    if value[1] == 1:
        logger.debug('vol down')
        sh.Sonos_Kueche.volume.fade(0, stepping, 1)
    else:
        prev_val = sh.Sonos_Kueche.volume.prev_value()

        # stop fading in any cases (up and down) by setting a new absolute value
        if sh.Sonos_Kueche.volume() > prev_val:
            prev_val += stepping + 1
            if prev_val >= 100:
                prev_val = 100
        else:
            prev_val -= stepping - 1
            if prev_val <= 1:
                prev_val = 0
        logger.debug(prev_val)
        sh.Sonos_Kueche.volume(int(prev_val))
