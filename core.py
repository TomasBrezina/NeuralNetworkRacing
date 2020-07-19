# -*- coding: utf-8 -*-

import pyglet

import numpy as np
from numpy import cos,sin,radians,sqrt,ones
from neural_network import NeuralNetwork

# finds intersection between two LINE SEGMENTS
def find_intersection( p0, p1, p2, p3 ) :
    s10_x = p1[0] - p0[0]
    s10_y = p1[1] - p0[1]
    s32_x = p3[0] - p2[0]
    s32_y = p3[1] - p2[1]
    denom = s10_x * s32_y - s32_x * s10_y
    if denom == 0 : return False # parallel
    denom_is_positive = denom > 0
    s02_x = p0[0] - p2[0]
    s02_y = p0[1] - p2[1]
    s_numer = s10_x * s02_y - s10_y * s02_x
    if (s_numer < 0) == denom_is_positive : return False # no collision
    t_numer = s32_x * s02_y - s32_y * s02_x
    if (t_numer < 0) == denom_is_positive : return False # no collision
    if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive : return None # no collision
    # collision detected
    t = t_numer / denom
    intersection_point = [ p0[0] + (t * s10_x), p0[1] + (t * s10_y) ]
    return intersection_point

# distance between two points
def dist_between(p0,p1):
    diffx = abs(p0[0] - p1[0])
    diffy = abs(p0[1] - p1[1])
    dist = sqrt(diffx**2+diffy**2)
    return dist

def index_loop(ind, len):
    while ind >= len:
        ind -= len
    return ind

"""
Core of simulation.
"""
class Simulation:
    def __init__(self, track, game_stg, save_stg):
        self.game_stg = game_stg
        self.save_stg = save_stg

        self.cars = set()
        self.track = track

        self.max_score = save_stg["best_result"]
        self.current_max_score = 0
        self.gen_count = save_stg["generations"]
        self.best_nn = None # best nn to save

    # first generation with random weights
    def first_generation(self, images, batch, shape=[5,3,3,2]):
        nn = NeuralNetwork(shape)
        nn.set_random_weights()
        self.new_generation([nn], images, batch)

    # generation with loaded NN
    def load_generation(self, nn, images, batch):
        self.new_generation([nn], images, batch)

    # new generation based on (best) neural networks
    def new_generation(self, best_nns, images, batch):
        self.gen_count += 1
        self.cars = set()
        for i in range(self.game_stg["population"]):
            # name, loaded image
            name,image = images[index_loop(i, len(images))]
            sprite = pyglet.sprite.Sprite(image, batch=batch)
            # starting point is on cp (this is important, dont change it)
            pos = (*self.track.cps_dict[self.track.stg["spawnindex"]], self.track.stg["spawna"])
            # get mutated version of one of best NNs
            best_nn = best_nns[index_loop(i, len(best_nns))].reproduce(self.get_mutation_rate())
            self.cars.add(Car(best_nn, pos, self.save_stg, sprite))
        return self.cars

    # return list of best nns (best = highest score (number of cps))
    def get_best_nns(self):
        max_score = 0
        for car in self.cars:
            if car.score > max_score:
                max_score = car.score
        best_nns = []
        for car in self.cars:
            if car.score == max_score:
                best_nns.append(car.nn)
        # for saving
        if max_score > self.max_score:
            self.max_score = max_score
        if max_score > self.current_max_score:
            self.current_max_score = max_score
            self.best_nn = best_nns[0]
        return best_nns

    # useless function
    def get_mutation_rate(self):
        return self.game_stg["mutation_rate"]

    # get car inputs (sensors and velocity)
    # because of track subdivision
    # only track segments near current cp are tested if sensors intersect with it
    def get_car_input(self, car):
        inp = ones(car.sensors.shape[0]+1)  # input array

        # index of cp on which car currently is
        cps_lenght = len(self.track.cps_dict)
        check_ind = index_loop(car.score + self.track.stg["spawnindex"], cps_lenght)

        # sensors index loop
        for sen_ind in range(car.sensors.shape[0]):
            sensor = car.sensors[sen_ind]  # current sensor
            sen_pos = [(car.xpos, car.ypos), car.translate_point(sensor)]  # sensor coordinates
            min_dist = 1  # smallest dist

            # goes through nearby cps
            # -1 previous cp
            # 0 = current cp
            # 1 = next cp
            for plus in [-2, -1, 0, 1]:
                # current cp
                cp_ind = index_loop(check_ind + plus, cps_lenght)
                if cp_ind < 0: cp_ind += cps_lenght
                # line segment which belongs to current cp
                lines = self.track.lines_dict[cp_ind]
                for line in lines:
                    # intersection point (if it exists)
                    intersection = find_intersection(
                        *sen_pos,
                        *line
                    )
                    if intersection:
                        dist = dist_between(intersection, (car.xpos, car.ypos))
                        # did the car crah?
                        if dist < 15:
                            car.speed = 0
                            car.active = False
                            car.sprite.opacity = 100
                        # normalized distance (0,1)
                        dist = dist / car.sensors_lengths[sen_ind]
                        if min_dist > dist: min_dist = dist
            inp[sen_ind] = min_dist
        # append normalized speed (0,1)
        inp[-1] = car.speed / self.save_stg["MAX_SPEED"]
        return inp

    # check if car is on next checkpoint
    # checkpoint are sorted in a loop so it is only looking for the next cp
    def car_checkpoint(self, car):
        cps_length = len(self.track.cps_dict)
        index = index_loop(car.score + self.track.stg["spawnindex"], cps_length)
        checkpoint = self.track.cps_dict[index]  # next checkpoint
        dist = dist_between((car.xpos, car.ypos), checkpoint)
        if (dist < 70):
            car.score += 1

    # behaviour of cars (acceleration, steering)
    # run nn
    def behave(self, dt):
        inactive = True
        for car in self.cars:
            if car.active == True:
                inactive = False
                # get nn input
                inp = self.get_car_input(car)
                self.car_checkpoint(car)
                # get nn output
                out = car.nn.forward(inp)
                # move the car!
                car.move(self.game_stg["friction"], out[1])
                car.turn((out[0]-.5)*2)
        # if no car is active :(
        if inactive: return False
        else: return True

    # tick
    def update(self, dt):
        for car in self.cars:
            car.update()

"""
Track object.

The way it works is the best I have come up with so far. 
I tried grid subdivision or some lines algorithms, but this is simple, and I will be able to generate tracks randomly.

Track consists of several 2-point "gates" in a loop. These points connect to form the edge of a track.
    
Checkpoints are in the middle of every "gate". So to each checkpoint belongs only 2 line segments connected to the next "gate".

When car is at the CP it checks for intersection only with nearby lines belonging to nearby CPs.
And dont have to find intersection on every line.
"""
class Track:
    def __init__(self, trackdir, nodes, stg):
        self.trackdir = trackdir
        self.nodes = nodes
        self.lines_dict = {}
        self.cps_dict = {}
        lenght = nodes.shape[1]
        for i in range(lenght):
            self.lines_dict[i] = np.array([
                [nodes[0,i],nodes[0,index_loop(i+1, lenght)]],
                [nodes[1,i],nodes[1,index_loop(i+1, lenght)]]
            ])
            # CP is midpoint between "gate"
            gate = nodes[:,i]
            cp = [(gate[0,0] + gate[1,0]) // 2, (gate[0,1] + gate[1,1]) // 2]
            self.cps_dict[i] = cp
        self.stg = stg

"""
Car object. 
"""
class Car:
    def __init__(self, nn, pos, save_stg, sprite):
        self.nn = nn

        self.save_stg = save_stg
        self.xpos = pos[0]
        self.ypos = pos[1]
        self.angle = pos[2]

        self.active = True
        self.speed = 0
        # number of cps
        self.score = 0

        # sprite
        self.sprite = sprite

        # sensors - from point [0, 0]
        #    \    /
        #     \  /
        # -----[]-----
        self.sensors = np.array([
            [25, -120],
            [170, -70],
            [170, 70],
            [25, 120],
        ])

        # sensors lengths
        self.sensors_lengths = np.zeros((self.sensors.shape[0],))
        for i in range(self.sensors.shape[0]):
            self.sensors_lengths[i] = dist_between((0,0),self.sensors[i])

    # returns translated point (coordinates from perspective of car -> coordinates on screen)
    def translate_point(self, p):
        x, y = p
        new_x = x * np.cos(radians(self.angle)) + y * np.sin(radians(self.angle)) + self.xpos
        new_y = -(-x * np.sin(radians(self.angle)) + y * np.cos(radians(self.angle))) + self.ypos
        return (new_x,new_y)

    # tick
    def update(self):
        if self.active == True:
            self.xpos += cos(radians(self.angle)) * self.speed
            self.ypos += sin(radians(self.angle)) * self.speed

    # tick
    def move(self, friction, direction=1):
        self.speed += self.save_stg["ACCELERATION"] * direction
        if self.speed > self.save_stg["MAX_SPEED"]:
            self.speed = self.save_stg["MAX_SPEED"]
        self.speed *= friction

    # tick
    def turn(self, direction=1):
        #direction = 1 or -1
        self.angle += self.save_stg["ROTATION_SPEED"] * direction
        if self.angle > 360: self.angle -= 360
        if self.angle < 0: self.angle += 360
