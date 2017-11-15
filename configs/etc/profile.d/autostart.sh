# launch our autostart apps (if we are on the correct tty)
if [ "`tty`" = "/dev/tty1" ]; then
    # Turn off LED
    /home/pi/turn_off.sh

    # Google Home Automation & Fauxmo
    python /home/pi/google_smarthome/MY_MY_smarthome.py &

    # Launch KODI and Retro Pie
    while :
    do
        kodi-standalone #auto
        emulationstation #auto
    done
fi
