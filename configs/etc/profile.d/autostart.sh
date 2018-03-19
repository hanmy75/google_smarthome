# launch our autostart apps (if we are on the correct tty)
RUN_FOLDER=/home/pi/google_smarthome/src

if [ "`tty`" = "/dev/tty1" ]; then
    # Turn off LED
    /home/pi/turn_off.sh

    # Google Home Automation & Fauxmo
    python $RUN_FOLDER/MY_smarthome.py &

    # Launch flic daemon
    sudo $RUN_FOLDER/flicd -d -f /home/pi/flic.sqlite3
    sleep 4
    python3 $RUN_FOLDER/switch_flic_button.py &

    # Launch KODI and Retro Pie
    while :
    do
        kodi-standalone #auto
        emulationstation #auto
    done
fi
