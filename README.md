# NeuralNetworkRacing
Simple 2D simulation using **pyglet** in which ANN learns to drive a car on a track.

You can download it and create and train a new ANN.

I would be glad for any advice or contribution!

[![AI learns to Race](https://yt-embed.herokuapp.com/embed?v=B0ptl-NChJQ)](https://youtu.be/B0ptl-NChJQ "AI learns to Race")

## Neural network and Evolution
Each artificial neural network has number of inputs and outputs. 
The inputs are distance sensors and car speed, these number enter the neural network and it outputs steering and acceleration.
![Neural network](http://www.brez.cz/projects/nn-racing/nnracing_example2.png)

The most successful cars in a generation are parents of next (slightly mutated) generation.
Over time, the results improve.

## Enviroment
The track consists of several line segments. Between them there are checkpoints.
![Track](http://www.brez.cz/projects/nn-racing/nnracing_example1.png)
