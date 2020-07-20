# NeuralNetworkRacing
Simple 2D simulation using **pyglet** in which ANN learns to drive a car on a track.

You can download it and create and train a new ANN, you can also simply change simulation or car settings in their ***settings.json*** file.

I would be glad for any advice or contribution!
## Neural network and Evolution
Each artificial neural network has number of inputs and outputs. In this case there are several distance sensors and a car velocity which go (as a numbers) into the neural network. And it outputs steering and acceleration.
![Neural network](http://www.brez.cz/img/nnracing_example2.png)

The best cars are selected from each generation
and forms another slightly mutated generation.  Over time, cars improve.

## Enviroment
The track consists of several line segments. Between them there are checkpoints.
![enter image description here](http://www.brez.cz/img/nnracing_example1.png)
