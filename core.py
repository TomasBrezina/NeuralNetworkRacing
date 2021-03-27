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
    return ind % len if ind >= len else ind

"""
Core of simulation.
"""
class Simulation:
    def __init__(self, track, save_stg):
        self.save_stg = save_stg
        self.friction = 0.9

        self.cars = []
        self.track = track

        # STATISTICS
        self.max_score = save_stg["best_result"]
        self.current_max_score = 0
        self.gen_count = save_stg["generations"]

        # BEST ONES
        self.best_nn = None  # best nn to save

    # first generation with random weights
    def first_generation(self, shape, population, mutation_rate, images, batch):
        nn = NeuralNetwork(shape)
        nn.set_random_weights()
        self.new_generation([nn], population, mutation_rate, images, batch)

    # generation with loaded NN
    def load_generation(self, nn, population, mutation_rate, images, batch):
        self.new_generation([nn], population, mutation_rate, images, batch)

    # new generation based on (best) neural networks
    def new_generation(self, best_nns, population, mutation_rate, images, batch):
        self.gen_count += 1
        self.cars = []
        for i in range(population):
            # name, loaded image
            name,image = images[index_loop(i, len(images))]
            sprite = pyglet.sprite.Sprite(image, batch=batch)
            # starting point is on cp (this is important, dont change it)
            pos = (*self.track.cps_arr[self.track.spawn_index], self.track.spawn_angle)
            # get mutated version of one of best NNs
            best_nn = best_nns[index_loop(i, len(best_nns))].reproduce(mutation_rate)
            self.cars.append(Car(best_nn, pos, self.save_stg, sprite))

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

    # returns current leader
    def get_leader(self):
        if self.cars: return max(self.cars, key=lambda car:car.score)
        else: return None

    # get car inputs (sensors and velocity)
    # because of track subdivision
    # only track segments near current cp are tested if sensors intersect with it
    def get_car_input(self, car):
        inp = ones(car.sensors.shape[0]+1)  # input array

        # index of cp on which car currently is
        cps_length = len(self.track.cps_arr)
        check_ind = index_loop(car.score + self.track.spawn_index, cps_length)

        # sensors index loop
        for sen_ind in range(car.sensors.shape[0]):
            new_pos = car.translate_point(car.sensors_shape[sen_ind])
            # update position of sensor
            car.sensors[sen_ind] = new_pos
            sen_pos = [(car.xpos, car.ypos), new_pos]  # sensor coordinates
            min_dist = 1  # smallest dist

            # goes through nearby cps
            # -1 previous cp
            # 0 = current cp
            # 1 = next cp
            for plus in [-2, -1, 0, 1]:
                # current cp
                cp_ind = index_loop(check_ind + plus, cps_length)
                if cp_ind < 0: cp_ind += cps_length
                # line segment which belongs to current cp
                lines = self.track.lines_arr[cp_ind]
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
        cps_length = len(self.track.cps_arr)
        index = index_loop(car.score + self.track.spawn_index, cps_length)
        checkpoint = self.track.cps_arr[index]  # next checkpoint
        dist = dist_between((car.xpos, car.ypos), checkpoint)
        if (dist < 120):
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
                car.move(self.friction, out[1])  # number between 0 and 1
                car.turn((out[0]-.5)*2)  # number between -1 and 1
        # if no car is active :(
        if inactive: return False
        else: return True

    # tick
    def update(self, dt):
        for car in self.cars:
            car.update()

"""
Track object.

The way this works is the best I have come up with so far. 
I tried grid subdivision or some line intersect. algorithms, but this is simple, and I will be able to generate tracks randomly.

Track consists of several 2-point "gates" in a loop. These points connect to form the edge of a track.
    
Checkpoints are in the middle of every "gate". So to each checkpoint belongs only 2 line segments connected to the next "gate".

When car is at the CP it checks for intersection only with nearby lines belonging to nearby CPs.
And dont have to find intersection on every line.
"""
class Track:
    def __init__(self, nodes, spawn_index=0, spawn_angle=0, bg=False):
        self.nodes = nodes
        self.vertex_lists = (
            pyglet.graphics.vertex_list(len(self.nodes[0]), ('v2i', (self.nodes[0].flatten()).astype(int))),
            pyglet.graphics.vertex_list(len(self.nodes[1]), ('v2i', (self.nodes[1].flatten()).astype(int)))
        )
        self.bg = bg

        # (n, left/right, prev/next, x/y)
        self.lines_arr = self.nodes_to_lines(self.nodes)
        self.cps_arr = self.nodes_to_cps(self.nodes)
        self.spawn_index = spawn_index
        self.spawn_angle = spawn_angle

    def nodes_to_lines(self, nodes):
        """
        :param nodes: shape (left/right, n, x/y)
        :return: lines: shape (n, left/right, prev/next, x/y)
        """
        lines = np.swapaxes(np.stack((nodes, np.roll(nodes, -1, 1)), axis=2), 0, 1)
        return lines

    def nodes_to_cps(self, nodes):
        """
        :param nodes: shape (left/right, n, x/y)
        :return: cps: point in the center with shape (n, xy)
        """
        center_point = lambda gate: [(gate[0,0] + gate[1,0]) // 2, (gate[0,1] + gate[1,1]) // 2]
        return np.array([center_point(nodes[:,i,:]) for i in range(nodes.shape[1])])

    def change_scale(self, scale):
        pass
        """for i in range(len(self.vertex_lists)):
            self.vertex_lists[i].vertices = (self.nodes[i].flatten() * scale).astype(int)
        if self.bg: self.bg.scale = scale"""

"""
Car object. 
Each one has its own neural network and sprite.
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
        self.sensors_shape = np.array([
            [25, -140],
            [190, -100],
            [190, 100],
            [25, 140],
        ])
        self.sensors = np.copy(self.sensors_shape)
        self.sensors_lengths = [dist_between((0,0), pos) for pos in self.sensors]

    # returns translated point (coordinates from perspective of car -> coordinates on screen)
    def translate_point(self, p):
        x, y = p
        _cos = np.cos(radians(self.angle))
        _sin = np.sin(radians(self.angle))
        new_x = x * _cos + y * _sin + self.xpos
        new_y = -(-x * _sin + y * _cos) + self.ypos
        return (new_x, new_y)

    # apply translation to every sensor
    def update_sensors(self):
        self.translate_point(self.sensors)

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
        # direction = 1 or -1
        self.angle += self.save_stg["ROTATION_SPEED"] * direction
        if self.angle > 360: self.angle -= 360
        if self.angle < 0: self.angle += 360
