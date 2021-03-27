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
settings = {
    "WIDTH": 1280,
    "HEIGHT": 720,
    "friction": 0.8,
    "render_timestep": 1/40,
    "timeout_seconds": 30,
    "population": 30,
    "mutation_rate": 0.15
}

from tiles import TileManager
mng = TileManager()
mng.load_tiles(root_dir="tiles")
track = Track(
    nodes=mng.generate(shape=(4, 3)),
    spawn_angle=90,
    spawn_index=0,
)

# SETTINGS
NAME = "test"  # name of the current NN
NEW_NEURAL_NETWORK = True
SAVE_FILE = "saves/test.json"

if NEW_NEURAL_NETWORK:
    # create new neural network
    nn_stg = {
        "ACCELERATION": 3.5,
        "MAX_SPEED": 35,
        "ROTATION_SPEED": 3.5,
        "SHAPE": [5, 4, 3, 2],
        "best_result": 0,
        "generations": 0
    }
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
    name=NAME
)
