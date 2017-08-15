#!/bin/bash

# dependencies (as far as I know, both are native in Ubuntu 16.04):
# imagemagick => capture screenshots
# wmctrl => command line access to window manager

#### open a new chrome window in google.com and minimize all other windows ####

# update folder path, no quotes
image_resources_path=~/git/TF_screenshots_object_detector/image_resources/

# new chrome window title
browser_window_name="Google - Google Chrome"

# screen size
screen_width=1366
screen_height=768
#### size restrictions (due to desktop layout etc) ####
# chrome takes a minimal window size
# using wmctrl -lG returns a list with (x-offset, y-offset, width and height)
# on my machine, these were the minimal values
# [this was discovered after generating data once, when I drew boxes based on "ground truth" and saw some shifts]
min_window_width=363
min_window_height=332
## restrict minimal x,y (launch bar, status bar) ##
# also found these values by trying to move the window to (0,0) and seeing where it landed
min_x=75
min_y=34

# training-test image
number_of_images=200  # total number of images
number_of_images_training=160  # size of training set
training_set_path=training_set  # subdir
test_set_path=test_set  # subdir

#### run code ####

# check that a new browser window is open
if ! wmctrl -l | grep -q "$browser_window_name"; then
    echo "No new browser window was found! Please open a new browser window!"
    echo "Exiting!"
    exec $SHELL  # exit 1
fi

# change dir to image resources path
cd $image_resources_path

# move browser window and save screenshot
wmctrl -k on  # minimize all windows
wmctrl -a "$browser_window_name"  # pop up browser window

# write headers to file
echo 'observation_id,pos_x,pos_y,pos_window_width,pos_window_height,pos_x2,pos_y2' > windows_positions.csv

for ((i=1;i<=number_of_images;i++)); do
    # generate a random int between 1,10 (inclusive)
    # $(( ( RANDOM % 10 )  + 1 ))
    
    # generate 2 random numbers for x,y coordinates of the window
    pos_x=$(( (RANDOM % (( screen_width/2 )) ) + min_x ))
    pos_y=$(( (RANDOM % (( screen_height/2 )) ) + min_y ))
    # set window width and height accordingly (NOT COORDINATES)
    pos_window_width=$(( (RANDOM % (( screen_width - pos_x - min_window_width )) ) + min_window_width ))
    pos_window_height=$(( (RANDOM % (( screen_height - pos_y - min_window_height )) ) + min_window_height ))
    
    # append string to file
    echo $i,$pos_x,$pos_y,$pos_window_width,$pos_window_height,$(( pos_x + pos_window_width )),$(( pos_y + pos_window_height )) >> windows_positions.csv
    
    # change browser position, command args: gravity,X,Y,width,height / <G>,<X>,<Y>,<W>,<H>
    wmctrl -r "$browser_window_name" -e 0,$pos_x,$pos_y,$pos_window_width,$pos_window_height
    
    # set save directory
    if (("$i" <= "$number_of_images_training")); then
        scrn_sht_path=$training_set_path
    else
        scrn_sht_path=$test_set_path
    fi
    
    # save screenshots (after short sleep, there is a resize? animation)
    sleep 0.5s
    import -window root $scrn_sht_path/$i.png
    
done

echo "Done!"

