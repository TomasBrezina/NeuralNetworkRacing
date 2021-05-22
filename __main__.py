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

from app import App, load_json
from core import Track

# simulation settings
settings = load_json("config.json")

from tiles import TileManager
mng = TileManager()
mng.load_tiles(root_dir="tiles")

track = Track(
    nodes=mng.generate(shape=(4, 3)),
    spawn_index=10,
)

# SETTINGS
NEW_NEURAL_NETWORK = False
SAVE_FILE = "saves/test.json"

if NEW_NEURAL_NETWORK:
    # create new neural network
    nn_stg = load_json("default_nn_config.json")
    nn_weights = False
else:
    # you can change savefile settings in saves folder
    nn_raw = load_json(SAVE_FILE)
    nn_stg = nn_raw["settings"]
    nn_weights = nn_raw["weights"]


# window
app = App(settings)
app.start_simulation(
    track=track,
    nn_stg=nn_stg,
    nn_weights=nn_weights,
)
