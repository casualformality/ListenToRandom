#!/usr/local/bin/python

# 
# This version uses pyglet to play the sounds. Pygame doesn't work on OS X
#  systems since they deprecated CoreAudio, so this works around it
# 

import sys, pyglet, _thread, time, random, os, threading, scipy

from os import listdir
from os.path import isfile, join

def block_and_play(sounds, sem):
    while 1:
        sem.acquire()
        sound = random.choice(sounds)
        sound.play()

def play_sounds(dirname, freq):
    my_volume = volume
    scipy.random.seed()

    files = listdir(dirname)
    # Get full path for files
    files = [f for f in files if isfile(join(dirname, f))]
    # Filter out everything that isn't an OGG
    files = [f for f in files if f.endswith(".ogg")]

    # Preload sound list.  Otherwise, this becomes a total
    #  resource hog.  If this takes up too much RAM, consider
    #  reducing the number of sounds before changing this
    #  behavior.  It *really* takes a lot of resources to
    #  constantly load and unload the sound files.
    sounds = []
    for f in files:
        sound = pyglet.media.load(join(dirname, f), streaming=False)
        # Set volume for each sound to sane level
        # sound.set_volume(volume) Not supported in pyglet :(
        sounds.append(sound)

    # This function signals to any of the listening threads to
    #  start playing a random sound whenever this semaphore is
    #  released (incremented).  The first thread to catch it
    #  acquires (decrements) the semaphore, so no other thread
    #  sees it.
    sem = threading.Semaphore()

    # Since the sounds aren't particularly long, creating freq/5
    #  listener threads seems like a sane value. If you find the
    #  threads are blocking needlessly long to play the sound, or
    #  if this number hogs too many resources, change as needed.
    processes = []
    for i in range(int(freq/5)):
        _thread.start_new_thread(block_and_play, (sounds, sem, ))

    # Wait a random amount of time between 1 and 100 seconds before
    #  telling the listeners to play a random sound from its list
    while 1:
        sleep_time = scipy.random.random_integers(1, 100)
        time.sleep(sleep_time / freq)
        sem.release()

if(len(sys.argv) > 1):
    try:
        volume = float(sys.argv[1]);
    except ValueError:
        print("Usage: ./sounds.py [volume]")
        sys.exit()
else:
    volume = 0.2;

try:
    # Start a randomizer thread for each sound type
    _thread.start_new_thread(play_sounds, ('clav/', 100.0, ) )
    _thread.start_new_thread(play_sounds, ('celesta/', 100.0, ) )
    # Skip playing the swells, since pyglet makes them sound choppy
    #_thread.start_new_thread(play_sounds, ('swells/', 5.0, ) )
except:
    print("Error: unable to start thread")

# Wait for user input to quit nicely
while True:
    input("Press [Enter] to quit.")
    sys.exit()
