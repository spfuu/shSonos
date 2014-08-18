#Release
v0.3

    --  !! ATTENTION !!: commands are changed to JSON commands. These are more flexible 
        than the old HTTP GET commands.
        Please adapt your clients to this new feature. Older clients won't work. 
        Please read the manual to set it up and get some example implementations.
        If you're running the Broker together with the Smarthome.py framework, 
        make sure you use the newest Sonos plugin. 

    --  !! ATTENTION !! Read previous point !!
    --  !! ATTENTION !! Read previous point !!
     
    --  commands 'volume', 'mute', 'led', 'treble', 'bass', 'loudness' can now be group 
        commands by adding 'group_command: 1' to the json command structure 
    --  the Broker now sends only the current changed speaker values instead of the whole 
        sonos data structure. This results in much less network traffic / overhead.
    --  Bug: fixed permission problem when saving a google tts sound file
    --  Bug: sometimes the search for the group coordinator doesn't found a valid object
    --  added some debug outputs, especially the commands are now logged more detailed
    


##This is just the working developer branch. I'm using it as backup. Don't use this code for your code base. It won't work. Use the Developer or Master Branch instead. 