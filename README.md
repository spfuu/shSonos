#Release
v0.3

    --  !! ATTENTION !!: commands are changed to JSON commands. They are more flexible 
        than the old HTTP GET commands.
        Please adapt your clients to this new feature. Older clients won't work. 
        Please read the manual to set it up and get some example implementations.
        If you're running the Broker together with the Smarthome.py framework, 
        make sure you use the newest Sonos plugin. 

    --  !! ATTENTION !! Read previous point !!
    --  !! ATTENTION !! Read previous point !!
     
    --  commands 'Volume', 'Mute', 'Led', 'Treble', 'Bass', 'Loudness' can now be group 
        commands by adding 'group_command: 1' to the json command structure 
    --  !! seek command is now named SetTrackPosition (see documentation)
    --  !! to get the current track position, poll GetTrackInfo with 'force_refresh' option
        (see documentation)
    --  removed command track_info() (this was only useful to get the current track 
        position; use GetTrackInfo instead
    --  the Broker now sends only the current changed speaker values instead of the whole 
        sonos data structure. This results in much less network traffic / overhead.
    --  Bug: fixed a problem with join command: join could fail, if the group to join have
        had more than ne speaker
    --  Bug: fixed permission problem when saving a google tts sound file
    --  Bug: sometimes the search for the group coordinator doesn't found a valid object
    --  Bug: Loglevel for the SoCo framework differed from the Broker settings
    --  added some debug outputs, especially the commands are now logged more detailed
    --  much cleaner code and improvements 


###This is just the working developer branch. I'm using it as a backup. 
###Don't use this code for your code base. It won't work. 
###Use the Developer or Master Branch instead. 


###Available commands


> ######client_subscribe
>  
> | parameter | required / optional | valid values | description |     
> | :-------- | :------------------ | :----------- | :---------- |
> | ip | required |  |  The IP of the client which wants to subscribe to the broker.
> | port | required | 1-65535 | The PORT of the client which wants to subscribe to the broker.

> ######example
>
> {
>   'command': 
>       'client_subscribe',
>       'parameter': 
>       {
>           'ip': '192.168.0.2',
>           'port': 2333,
>       }
> }

####client_unsubscribe
    
| parameter | required / optional | valid values | description |     
| :-------- | :------------------ | :----------- | :---------- |
| ip | required |  |  The IP of the client which wants to unsubscribe from the broker.
| port | required | 1-65535 | The PORT of the client which wants to unsubscribe from the broker.

######example
    {
        'command': 'client_unsubscribe',
        'parameter': {
            'ip': '192.168.0.2',
            'port': 2333,
        }
    }
