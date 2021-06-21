# -*- coding: utf-8 -*-

"""

DEEP LEARNING CARS
Simple simulation in Python in which a Neural Network learns to drive a racing car on a track.

Neural network has several inputs (distance sensors and car speed)
and it outputs acceleration and steering.

I used a simple Evolutionary algorithm to train the NN.

- Tomáš Březina 2020

Run command:
pip install -r requirements.txt

Requirements:
pyglet (graphics)
numpy (neural network, math, ..)
os (not necessary - only in save_neural_network function)
json (loading and saving settings and saves)
"""

from messages import ask_load_nn, ask_yes_no
from app import App, load_json
from core import Track
from evolution import Evolution
from tiles import TileManager

# simulation settings
settings = load_json("config.json")

SAVE_FILE = False
if ask_yes_no(title="Start",message="Load saved NN?"):
    SAVE_FILE = ask_load_nn("saves")

# if save file is  defined
if SAVE_FILE:
    nn_raw = load_json(SAVE_FILE)
    nn_stg = nn_raw["settings"]
    nn_weights = nn_raw["weights"]
else:
    # create new neural network
    nn_stg = load_json("default_nn_config.json")
    nn_weights = None



evolution = Evolution()
evolution.mutation_rate = settings["mutation_rate"]
evolution.set_parameters_from_dict(nn_stg)

# window
app = App(settings)
app.start_simulation(
    track=app.tile_manager.generate_track(shape=(5,3), spawn_index=0),
    evolution=evolution,
    nn_weights = nn_weights
)
