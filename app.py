# -*- coding: utf-8 -*-

from pyglet.gl import *
from pyglet.window import key

from numpy import savetxt, loadtxt, empty
from os import mkdir, listdir
import json

from graphics import Graphics
from core import Simulation, Track
from neural_network import NeuralNetwork

# load .json file
def load_settings(directory):
    try:
        with open(directory) as json_file:
            stg = json.load(json_file)
        return stg
    except:
        return False

# save .json file
def save_settings(directory,data):
    with open(directory, "w") as json_file:
        json.dump(data, json_file)

# save nn as a folder
def save_neural_network(nn, save_stg, name, folder="saves"):
    valid_name = False
    count = 0
    new_name = name
    while not valid_name:
        save_dir = folder + "/" + new_name
        try:
            mkdir(save_dir)
            valid_name = True
            print("Save folder", new_name, " created ")
        except FileExistsError:
            count += 1
            new_name = name + "(" + str(count) + ")"
    for ind in range(len(nn.weights)):
        savetxt(save_dir+"/"+str(ind+1)+".csv", nn.weights[ind], delimiter=",")
    with open(save_dir+"/save_settings.json", "w") as json_file:
        json.dump(save_stg, json_file)

# load nn from a folder
def load_neural_network(directory):
    listd = listdir(directory)
    listd = sorted(listd)

    shape = []
    weights = []
    for ind in range(len(listd)):
        filename = listd[ind]
        if filename.endswith(".csv"):
            layer = loadtxt(directory + "/" + filename, delimiter=",")
            weights.append(layer)
            shape.append(len(layer))
    shape.append(2) # because of 2 outputs

    nn = NeuralNetwork(shape)
    nn.set_weights(weights)
    return nn

# load track from a folder
def load_track(directory):
    raw = loadtxt(directory, delimiter=",")
    raw = raw.reshape((raw.shape[0], 2, 2))
    shaped = empty((2, raw.shape[0], 2))
    shaped[0,:] = raw[:,0]
    shaped[1,:] = raw[:,1]
    return shaped

"""
Window management.
"""

class SimulationApp:
    def __init__(self, trackdir, savename="New NN", savedir=None):
        ### NAME OF SAVE ###
        self.savename = savename

        ### LOAD ###
        self.game_stg = False
        self.save_stg = False
        self.nn = False
        self.game_stg = load_settings("settings.json")
        if savedir:
            self.save_stg = load_settings(savedir+"/save_settings.json")
            self.nn = load_neural_network(savedir)
        else:
            self.save_stg = load_settings("saves/default_save_settings.json")
            self.nn = False
        track = Track(trackdir, load_track(trackdir+"/track.csv"), load_settings(trackdir+"/track_settings.json"))

        ### INIT WINDOW ###
        self.window = pyglet.window.Window(fullscreen=False, resizable=False)
        self.window.set_caption("NEURAL NETWORK RACING by Tomas Brezina")
        self.window.set_size(track.stg["WIDTH"], track.stg["HEIGHT"])

        ### LOAD ICON ###
        try:
            icon = pyglet.image.load("graphics/icon.ico")
            self.window.set_icon(icon)
        except:
            print("Error >>> Loading icon")

        ### MODULES ###
        self.simulation = Simulation(track, self.game_stg, self.save_stg)
        self.graphics = Graphics(self.window, track)

        ### LABELS ###
        self.graphics.labels["name"].text = self.savename

        ### VARIABLES ###
        self.show = False  # show track, cps, etc.
        self.pause = True  # pause the simulation
        self.timer = 0  # number of ticks
        self.timer_limit = self.game_stg["timeout_seconds"] // self.game_stg["render_timestep"]  # max ticks

        ### RESIZE ###
        self.graphics.change_scale(self.window.width / self.game_stg["WIDTH"])

        ### BIND EVENTS ###
        self.window.event(self.on_key_release)
        self.window.event(self.on_close)
        self.window.event(self.on_resize)
        self.window.event(self.on_draw)

    # when key is released
    def on_key_release(self,symbol, modifiers):
        # save the nn
        if symbol == key.S:
            self.pause = True
            self.window.minimize()
            self.window.set_fullscreen(False)
            if self.savename and self.simulation.best_nn:
                _save_stg = self.save_stg
                _save_stg["generations"] = self.simulation.gen_count
                _save_stg["best_result"] = self.simulation.max_score
                save_neural_network(self.simulation.best_nn, _save_stg, self.savename)
        # fullscreen on/off
        if symbol == key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
        # pause on/off
        if symbol == key.P:
            self.pause = not self.pause
        # show on/off
        if symbol == key.O:
            self.show = not self.show

    # when closed (unnecessary)
    def on_close(self):
        pyglet.clock.unschedule(self.update)

    # when resized
    def on_resize(self, width, height):
        self.graphics.change_scale(width / self.game_stg["WIDTH"])

    # every frame
    def on_draw(self):
        # update sprites position and angle
        self.graphics.update_sprites(self.simulation.cars)
        # draw it
        self.graphics.on_draw()
        # draw track details
        if self.show:
            self.graphics.on_draw_show(self.simulation.track.cps_dict)

    # behaviour 
    def behave(self,dt):
        active = self.simulation.behave(dt)
        if not active:
            self.timer = 0
            self.new_generation()
        self.timelimit()

    # create new generation based on the best NNs
    def new_generation(self):
        self.graphics.labels["gen"].text = "Generation: " + str(int(self.simulation.gen_count))
        self.graphics.clear_batch()
        self.simulation.new_generation(self.simulation.get_best_nns(), self.graphics.car_images, self.graphics.car_batch)
        self.graphics.labels["max"].text = "Best score: " + str(self.simulation.max_score)


    # tick
    def update(self,dt):
        if not self.pause:
            # car behaviour
            self.behave(dt)
            self.simulation.update(dt)

    # each tick
    def timelimit(self):
        self.timer += 1
        if self.timer >= self.timer_limit:
            self.timer = 0
            self.new_generation()
        seconds = int(self.timer * self.game_stg["render_timestep"])
        self.graphics.labels["time"].text = "Time: " + str(seconds) + " / " + str(self.game_stg["timeout_seconds"])

    # start of simulation
    def run(self):
        self.graphics.labels["gen"].text = "Generation: " + str(int(self.simulation.gen_count))
        self.graphics.labels["max"].text = "Best score: " + str(self.simulation.max_score)
        # new save or loaded one
        if self.nn == False:
            self.simulation.first_generation(self.graphics.car_images, self.graphics.car_batch, shape=self.save_stg["SHAPE"])
        else:
            self.simulation.load_generation(self.nn,self.graphics.car_images,self.graphics.car_batch)
        pyglet.clock.schedule_interval(self.update, self.game_stg["render_timestep"])
        pyglet.app.run()

    # end
    def exit(self):
        pyglet.app.exit()
