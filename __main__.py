# -*- coding: utf-8 -*-

"""

DEEP LEARNING CARS
Simple simulation in Python in which a Neural Network learns to drive a racing car on a track.

Neural network has several inputs (distance sensors and car speed)
and it outputs acceleration and steering.

I used a simple Evolutionary algorithm to train the NN.

- Tomáš Březina 2020

Requirements:
pyglet (graphics)
numpy (neural network, math, ..)
os (not necessary - only in save_neural_network function)
json (loading and saving settings and saves)
"""

from app import App, load_json, load_track
from core import Track
import pyglet.image

# simulation settings
settings = {
    "WIDTH": 1280,
    "HEIGHT": 720,
    "friction": 0.8,
    "render_timestep": 0.03,
    "timeout_seconds": 60,
    "population": 40,
    "mutation_rate": 0.15
}

# load track
trackdir = "tracks/track2"
try: trackbg = pyglet.image.load(trackdir+"/bg.png")
except: trackbg = False
track = Track(load_track(trackdir + "/track.csv"), load_json(trackdir + "/track_settings.json"), trackbg)

NAME = "test" # name of the current NN
NEW_NEURAL_NETWORK = False
SAVEFILE = "saves/test5322.json"

if NEW_NEURAL_NETWORK:
    # create new neural network
    nn_stg = {
        "ACCELERATION": 3,
        "MAX_SPEED": 20,
        "ROTATION_SPEED": 3.5,
        "SHAPE": [5, 4, 3, 2],
        "best_result": 0,
        "generations": 0
    }
    nn_weights = False
else:
    # you can change savefile settings in saves folder
    nn_raw = load_json(SAVEFILE)
    nn_stg = nn_raw["settings"]
    nn_weights = nn_raw["weights"]


# window
app = App(settings)

app.start_simulation(
    track=track,
    nn_stg=nn_stg,
    nn_weights=nn_weights,
    name=NAME
)
