
# NeuralNetworkRacing

Neural network learns how to drive a car on a track.
Simple 2D simulation with **pyglet** & **numpy**.



https://user-images.githubusercontent.com/46631861/161601803-30c7b0d2-ae7f-4145-b3fa-95378e36cd19.mp4


> [!WARNING]
> This code is a product of my early programming days. I've refactored it, but it might not align with current best practices.

## ▶️️ HOW TO RUN?

### Install packages
    pip install -r requirements.txt

https://github.com/TomasBrezina/NeuralNetworkRacing/blob/e6ff65a77d38f0cdad01690a0a770a9eb9c2da2a/requirements.txt#L1-L3

### Run main file
Should work with ``Python 3.0`` and higher.

For example:

    py -3.10 .\__main__.py

Or use a virtual environment.

### Config (Optional)

**config.json**

    {
	    "width": 1280
	    "height": 720
	    "friction": 0.1
	    "render_timestep": 0.025 // time between frames in seconds - 0.025s = 40 FPS
	    "timeout_seconds": 30 // maximum time for each gen
	    "population": 40 // number of cars
	    "mutation_rate": 0.6 // mutation rate after gen
    }

**default_nn_config.json** - Default car config for new saves.  

    {
	    "name" : "test" 
	    "acceleration": 1
	    "friction": 0.95
	    "max_speed": 30 
	    "rotation_speed": 4
	    "shape": [6, 4, 3, 2] // neural network shape - do not change first and last layer
	    "max_score": 0
	    "gen_count": 0
    }

## 🕸️ NEURAL NETWORK
![nn-architecture](https://user-images.githubusercontent.com/46631861/161595500-a58ccd65-840a-4ced-b3b1-123bc6ee9926.png)

## 🧬 EVOLUTION
Best cars in each generation are chosen to be the parents of the next, slightly mutated generation.

## 🏎️ ENVIROMENT & TRACK GENERATION

| ![image](https://user-images.githubusercontent.com/46631861/161503165-7a99e1e1-d726-4797-8167-4bb582fa3457.png) | ![track-generation](https://user-images.githubusercontent.com/46631861/161503022-bf0ca0d1-f678-48ce-b570-5bcaaa47b6f3.gif) | 
|--|--|

