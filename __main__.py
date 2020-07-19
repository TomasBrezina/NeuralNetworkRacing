# -*- coding: utf-8 -*-

"""

DEEP LEARNING CARS
Simple simulation written in Python in which a Neural Network learns to drive a racing car on a track.

Each neural netwok has a number inputs (distance sensors and other)
and it outputs acceleration and steering.

I used a simple Evolutionary algorithm to train the NN.

- Tomáš Březina 2020

Requirements:
pyglet
numpy
os
json
"""

from app import SimulationApp

"""
To change settings of a save visit saves directory and change .json file.
Do the same in case of general settings or track settings.
"""

# name of the current NN
savename = "TEST"

# directory of save folder
# if None then create new NN
savedir = "saves/TEST(3)"
#savedir = None

# directory of track folder
trackdir = "tracks/track2"


app = SimulationApp(trackdir, savename, savedir)
app.run()
