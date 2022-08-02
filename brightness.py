from xmlrpc.client import Boolean
from pynput.keyboard import Listener
from pynput import keyboard
import subprocess
import time
import os
import math

#from subprocess import call

# ---------------------------------------
# BRIGHTNESS ADJUST
# -----------------
# WTF IS THIS?!
# IT'S A TEMPORARY SHITASS SOLUTION TO CHANGING THE BRIGHTNESS SMOOTHLY
# IT SUCKS
# IT'S WRITTEN IN GOT DAMN PYTHON
# IT DOESN'T WORK PROPERLY
# IT ONLY WORKS ON MY TABLOP
# PLEASE DON'T USE THIS PIECE OF SH*T
# PLEASE

BACKLIGHT_LOCATION = "/sys/class/backlight/intel_backlight/"
MAX_BRIGHTNESS = 7500   # automatic this number means nothing

newBrightness = 0.0
currentBrightness = 0.0

# i was gonna use threads but it doesnt work and it sucks
changeThreadIsRunning = False

tick = 0

# this literally does nothing
TEST_MODE = False

def command(c):
    x = subprocess.check_output([c], shell=True)
    s = ""
    for i in x:
        s += chr(i)
    return s


def setup():
    MAX_BRIGHTNESS    = float(command("cat "+BACKLIGHT_LOCATION+"max_brightness"))
    currentBrightness = math.sqrt(float(command("cat "+BACKLIGHT_LOCATION+"actual_brightness")) / MAX_BRIGHTNESS)
    newBrightness     = currentBrightness
    return MAX_BRIGHTNESS, currentBrightness
    
    


# this changes the brightness smoothly
# i tried to make it multithreaded so that you can hold down the brightness change button without
# the event listener waiting for this to complete
# but i failed
# rest in piece the many hours i lost trying to figure shiz out
def gradBrightnessChange():

    # on my tablop anyways, I can't be arsed learning how to read the max brightness from system lmao

    # ignore this this is useless
    global tick

    global newBrightness
    global currentBrightness

    global changeThreadIsRunning
    changeThreadIsRunning = True

    

    # calculate brightness difference
    diff = newBrightness-currentBrightness

    # floating point maths  s u c k s    so we need tolerance instead of exact ==
    TOLERANCE = 0.01
    while (not (diff < TOLERANCE and diff > -TOLERANCE)):

        # I was gonna make it transition in a really cool way
        # shame it never happened thanks to threading not heckin working
        diff = newBrightness-currentBrightness
        if (diff > 0.):
            currentBrightness += 0.01
        elif (diff < 0.):
            currentBrightness -= 0.01

        # note to self; don't use python
        
        # When we change the brightness, changing it at a low brightness causes massive changes in the 
        # actual brightness, but changing it at a high brightness barely looks like anything changes
        # To normalize it, perform a square so that the brightness value changes a little at low brightness,
        # and then a LOT when we're going very bright
        # prepare to consume a lot of power. 
        # Congrats, you are wasting expensive energy on having your screen bright.
        v = int( (currentBrightness*currentBrightness) * MAX_BRIGHTNESS)

        # why is this still here
        tick += 1

        # bleh
        # print(str(v), str(currentBrightness))

        # run the command thing that changes the system light. You better not require a password
        # when running sudo or everything breaks huehue.
        os.system("echo "+str(v)+" | sudo tee "+BACKLIGHT_LOCATION+"brightness")

        # "why don't you just run the script as sudo root?"
        # I CANT BECAUSE OF THIS GOD DAMN THING AJSKLDFHASD
        # -------------------------------------------------
        # ImportError: this platform is not supported: ('failed to acquire X connection: Can\'t connect to display ":0": b\'Authorization required, but no authorization protocol specified\\n\'', DisplayConnectionError(':0', b'Authorization required, but no authorization protocol specified\n'))

        # Try one of the following resolutions:

        # * Please make sure that you have an X server running, and that the DISPLAY environment variable is set correctly

        # "THIS PLATFORM NOT SUPPORTED" MY ASS!

        # "Why don't you just use the normal keyboard library?"
        # BECAUSE F1 AND F2, THE KEYS USED TO CONTROL BRIGHTNESS, IS JUST READ AS "UNKNOWN"
        # PIECE OF POOP LIBRARY

        # Why.
        time.sleep(0.02)

    # theres no threads
    changeThreadIsRunning = False
    #print("End thread")


# amongus

releasedKey = True

def on_press(key):
    global newBrightness
    global releasedKey

    if (releasedKey):
        # read key. F1 and F2 are encoded in this weird string thing.
        # If you wanna set your own custom keys do it yourself huehue
        if (str(key) == "<269025026>"):
            #print("brightness up")
            newBrightness += 0.05
            if (newBrightness > 1.0):
                newBrightness = 1.0
            gradBrightnessChange()
            
        # Why are you still looking at this.

        if (str(key) == "<269025027>"):
            #print("Brightness down")
            newBrightness -= 0.05
            if (newBrightness < 0.0):
                newBrightness = 0.0
            gradBrightnessChange()
        #print(str(key) + " key pressed")
        releasedKey = False

# Literally does nothing
def on_release(key):
    global releasedKey
    releasedKey = True


MAX_BRIGHTNESS, currentBrightness = setup()
newBrightness = currentBrightness

print("max_brightness:      "+str(MAX_BRIGHTNESS))
print("current_brightness:  "+str(currentBrightness))

# Listener event thing to listen to keys when they're pressed.
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()



# oh thank f*ck it's over.

# if u really run this shit
# $ python3 brightness.py

