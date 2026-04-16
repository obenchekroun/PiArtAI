#! /usr/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}
source .venv/bin/activate
python3 generate_picture.py --width 600 --height 448 images/
python3 display_picture.py -r images/output.png

# echo "Going to sleep in 60 seconds, until next time ..."
# echo "0" | sudo tee /sys/class/rtc/rtc0/wakealarm  #reset
# date '+%s' -d '+ 3 hours' | sudo tee /sys/class/rtc/rtc0/wakealarm # With an interval
# date '+%s' -d 'tomorrow 06:00:00' | sudo tee /sys/class/rtc/rtc0/wakealarm OR at fixed time
# sudo shutdown -h +1 "PiArtAI going to sleep in 60 seconds. Send sudo shutdown -c to cancel"
