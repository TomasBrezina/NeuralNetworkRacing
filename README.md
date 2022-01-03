

# NeuralNetworkRacing
Simple 2D simulation using **pyglet** & **numpy** in which ANN learns to drive a car on a track.

## Youtube video:
[![AI learns to Race](https://i.ibb.co/gmmtYx1/ytthumbnail.png)](https://youtu.be/B0ptl-NChJQ "AI learns to Race")

## Neural network and Evolution
Each artificial neural network has a number of inputs and outputs. 

- **Inputs**
	 - distance sensors
	 - car velocity
- **Outputs**
	 - steering
	 - acceleration

![Neural network](http://www.brez.cz/projects/nn-racing/nnracing_example2.png)  

The most successful cars in a generation are parents of next (slightly mutated) generation.
Over time, the ANN improves.

![Architectures comparison](http://brez.cz/projects/nn-racing/arch_comp2.png)

## Environment
The track consists of several line segments. Between them are checkpoints.
![Track](http://www.brez.cz/projects/nn-racing/nnracing_example1.png)

