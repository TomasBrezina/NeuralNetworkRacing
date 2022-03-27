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
from evolution import Evolution, Entity, F1Evolution

# simulation settings
settings = load_json("config.json")
entity = Entity()

SAVE_FILE = False
if ask_yes_no(title="Start",message="Load saved NN?"):
    SAVE_FILE = ask_load_nn("saves")

# if save file is  defined
if SAVE_FILE:
    entity.load_file(SAVE_FILE)
else:
    # create new neural network
    nn_stg = load_json("default_nn_config.json")
    entity.set_parameters_from_dict(nn_stg)
    entity.set_nn(entity.get_random_nn());

import f1_tracks

# window
app = App(settings)
app.start_simulation(
    entity=entity,
    track=app.tile_manager.generate_track_from_medium_path(f1_tracks.australia_track, shape=(8,4), spawn_index=-11)
    # track=app.tile_manager.generate_track(shape=(5,3), spawn_index=0)
)
