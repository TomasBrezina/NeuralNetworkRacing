# -*- coding: utf-8 -*-

from pyglet.gl import *
from pyglet.window import key

from numpy import loadtxt, empty
from os import listdir
import json

from graphics import Graphics
from core import Simulation, index_loop
from neural_network import NeuralNetwork

from evolution import Evolution, Entity
from core import Track

from menu import SettingsMenu
from messages import *
from tiles import TileManager

# load .json file
def load_json(directory):
    try:
        with open(directory) as json_file:
            file = json.load(json_file)
        return file
    except:
        print("Failed to load: %s" % directory)
        return False

# save .json file
def save_json(directory,data):
    with open(directory, "w") as json_file:
        json.dump(data, json_file)

# save nn as a .json file
def save_neural_network(name, weights, settings, folder="saves"):
    # get name
    savefiles = listdir(folder)
    savename = name
    name_count = 0
    while savename + ".json" in savefiles:
        name_count += 1
        savename = "%s(%s)" % (name, name_count)
    savefile = {
        "settings": settings,
        "weights": [np_arr.tolist() for np_arr in weights]
    }
    with open(folder+"/"+savename+".json", "w") as json_file:
        json.dump(savefile, json_file)
    print("Saved ", savename)

"""
Window management.
"""

class App:
    def __init__(self, settings):
        ### NAME OF SAVE ###
        self.settings = settings

        ### INIT WINDOW ###
        self.window = pyglet.window.Window(fullscreen=False, resizable=True)
        self.window.set_caption("NEURAL NETWORK RACING by Tomas Brezina")
        if not self.window.fullscreen: self.window.set_size(settings["width"], settings["height"])
        self.window.set_minimum_size(400, 200)
        self.init_gl()

        ### LOAD ICON ###
        try:
            icon = pyglet.image.load("graphics/icon.ico")
            self.window.set_icon(icon)
        except:
            print("Error >>> Loading icon")

        ### MODULES ###
        self.entity = None

        self.simulation = Simulation()
        self.evolution = Evolution()
        self.evolution.mutation_rate = self.settings["mutation_rate"]
        self.graphics = Graphics(self.window.width, self.window.height)

        ### TRACK MANAGER ###
        self.tile_manager = TileManager()
        self.tile_manager.load_tiles(root_dir="tiles")

        ### LABELS ###
        self.graphics.hud.labels["name"].text = ""

        ### USER GUI ###
        self.camera_free = False
        self.camera_selected_car = None

        ### VARIABLES ###
        self.show = False  # show track, cps, etc.
        self.pause = False  # pause the simulation
        self.timer = 0  # number of ticks
        self.timer_limit = self.settings["timeout_seconds"] // self.settings["render_timestep"]  # max ticks

        ### BIND EVENTS ###
        self.window.event(self.on_key_press)
        self.window.event(self.on_close)
        self.window.event(self.on_resize)
        self.window.event(self.on_draw)
        self.window.event(self.on_mouse_drag)
        self.window.event(self.on_mouse_scroll)

    def init_gl(self):
        glViewport(0, 0, self.window.width, self.window.height)
        glEnable(pyglet.gl.GL_BLEND)
        glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        glLineWidth(5)
        glEnable(GL_PROGRAM_POINT_SIZE_EXT)

    # when key is released
    def on_key_press(self,symbol, modifiers):
        # save the nn
        if symbol == key.S:
            self.window.set_fullscreen(False)
            if self.evolution.best_result.nn:
                directory = "saves"
                filename = ask_save_nn_as()
                if filename:
                    filename = filename.split("/")[-1]  # filename and ext
                    self.evolution.save_file(save_name=filename, folder=directory)
                    show_message(f"Succesfully saved {filename} to /{directory}")
            else:
                show_error("No neural network to save yet.")
                print(f"Cannot save.")
        # TODO: load file
        if symbol == key.T:
            self.change_track(
                track=self.tile_manager.generate_track(shape=(5, 3))
            )

        elif symbol == key.DELETE:
            self.end_simulation()
        # fullscreen on/off
        elif symbol == key.F:
            #self.window.maximize()
            self.window.set_fullscreen(not self.window.fullscreen)
            if not self.window.fullscreen: self.window.set_size(self.settings["width"], self.settings["height"])
        # pause on/off
        elif symbol == key.P:
            self.pause = not self.pause
        # show on/off
        elif symbol == key.O:
            self.show = not self.show
        # control camera
        elif symbol == key.C:
            self.camera_free = not self.camera_free
        elif symbol == key.LEFT:
            self.camera_switch_cars(-1)
        elif symbol == key.RIGHT:
            self.camera_switch_cars(1)
        elif symbol == key.UP:
            self.camera_selected_car = self.simulation.get_leader()
        elif symbol == key.DOWN:
            self.camera_selected_car = self.simulation.get_leader()
        elif symbol == key.NUM_ADD:
            self.graphics.camera.set_zoom_center(1.2)
        elif symbol == key.NUM_SUBTRACT:
            self.graphics.camera.set_zoom_center(0.8)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modif):
        if self.camera_free:
            self.graphics.camera.drag(-dx, -dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            self.graphics.camera.set_zoom(x, y, 1.2)
        else:
            self.graphics.camera.set_zoom(x, y, 0.8)

    # switch cars
    def camera_switch_cars(self, step):
        if self.camera_selected_car:
            new_ind = self.simulation.cars.index(self.camera_selected_car)
            while True:
                new_ind -= step
                self.camera_selected_car = self.simulation.cars[index_loop(new_ind, len(self.simulation.cars))]
                if self.camera_selected_car.active: break

    # when closed (unnecessary)
    def on_close(self):
        pyglet.clock.unschedule(self.update)

    # when resized
    def on_resize(self, width, height):
        self.graphics.on_resize(width, height)

    # every frame
    def on_draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glPushMatrix()
        self.graphics.clear()
        self.graphics.set_camera_view()

        self.simulation.track.bg.blit(0, 0)

        #draw cars
        self.graphics.car_batch.draw()

        # draw hidden details
        if self.show:
            self.graphics.draw_grid()
            # draw edge of the track
            for vl in self.simulation.track.vertex_lists:
                self.graphics.draw_vertex_list(vl)
            for car in self.simulation.cars:
                self.graphics.draw_car_sensors(car)
            self.graphics.draw_cps(self.simulation.track.cps_arr)
        glPopMatrix()

        self.graphics.draw_hud()

    # create new generation from best nns
    def new_generation(self):
        self.graphics.clear_batch()

        results = self.simulation.get_nns_results()
        self.simulation.generate_cars_from_nns(
            nns=self.evolution.get_new_generation_from_results(
                results,
                self.settings["population"]
            ),
            parameters=self.entity.get_car_parameters(),
            images=self.graphics.car_images,
            batch=self.graphics.car_batch
        )
        self.entity.set_nn_from_result(self.evolution.find_best_result(results))

        self.update_labels(self.entity)
        self.camera_selected_car = self.simulation.cars[0]
        self.graphics.update_sprites(self.simulation.cars)

    # every frame
    def update(self,dt):
        if not self.pause:
            # car behaviour
            active = self.simulation.behave(dt)
            if not active:
                self.timer = 0
                self.new_generation()
            self.simulation.update(dt)

            # CAMERA
            if not self.camera_free:
                if self.camera_selected_car:
                    if not self.camera_selected_car.active:
                        self.camera_selected_car = self.simulation.get_leader()
                    self.graphics.camera.set_target(self.camera_selected_car.xpos, self.camera_selected_car.ypos)
                    self.graphics.camera.update()
                else:
                    pass
            # update sprites position and rotation
            self.graphics.update_sprites(self.simulation.cars)
            self.update_timelimit()

    # each tick
    def update_timelimit(self):
        self.timer += 1
        if self.timer >= self.timer_limit:
            self.timer = 0
            self.new_generation()
        seconds = int(self.timer * self.settings["render_timestep"])
        self.graphics.hud.labels["time"].text = "Time: " + str(seconds) + " / " + str(self.settings["timeout_seconds"])

    # update labels from self entity
    def update_labels(self, entity: Entity):
        self.graphics.hud.labels["name"].text = self.entity.name[:10]  # first 10 characters to fit screen
        self.graphics.hud.labels["gen"].text = "Generation: " + str(int(self.entity.gen_count))
        self.graphics.hud.labels["max"].text = "Best score: " + str(self.entity.max_score)

    def change_track(self, track):
        self.timer = 0
        self.simulation.track = track
        self.new_generation()

    # start of simulation
    def start_simulation(self, entity: Entity, track: Track=None):

        # entity
        self.entity = entity

        # set track or generate random
        self.simulation.track = track if track is not None else self.tile_manager.generate_track(shape=(5, 3))

        # set labels
        self.update_labels(self.entity)

        self.simulation.generate_cars_from_nns(
            nns=self.evolution.get_new_generation(
                [self.entity.get_nn()],
                self.settings["population"]
            ),
            parameters=self.entity.get_car_parameters(),
            images=self.graphics.car_images,
            batch=self.graphics.car_batch
        )

        self.camera_selected_car = self.simulation.get_leader()
        self.graphics.update_sprites(self.simulation.cars)

        self.on_resize(self.window.width, self.window.height)

        pyglet.clock.schedule_interval(self.update, self.settings["render_timestep"])
        pyglet.app.run()

    def end_simulation(self):
        pyglet.clock.unschedule(self.update)
        self.simulation = False

    # end
    def exit(self):
        pyglet.app.exit()
