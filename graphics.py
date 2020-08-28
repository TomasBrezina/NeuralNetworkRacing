# -*- coding: utf-8 -*-

import pyglet
from pyglet.gl import *

# colors
WHITE = (255,255,255,255)
GREEN = (0, 153, 51, 255)
RED = (204, 0, 0, 255)
GRAY = (128, 128, 128, 255)

# car images
racers_info = {
    "Black" : ["Black.png", (0,0,0,255)],
    "Blue" : ["Blue.png",(0,0,170,255)],
    "Cyan" : ["Cyan.png",(52,205,243,255)],
    "Green" : ["Green.png",(10,183,45,255)],
    "Gray" : ["Lightgray.png",(150,150,150,255)],
    "Orange": ["Orange.png",(231,132,0,255)],
    "Red": ["Red.png",(203,0,0,255)],
    "Pink": ["Pink.png",(250,56,178,255)],
    "Yellow": ["Yellow.png",(228,229,0,255)],
    "White": ["White.png",(255,255,255,255)]
}

"""
Rendering.
"""
class Graphics:
    def __init__(self, window):
        # INIT
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_PROGRAM_POINT_SIZE_EXT)
        self.window = window
        self.scale = 1

        self.car_batch = pyglet.graphics.Batch()
        self.car_images = []
        for name in racers_info:
            self.car_images.append((name, self.load_car_image("graphics/cars/"+racers_info[name][0])))

        # LABELS
        self.lb_stg = {
            "size": [20,700,325,520],
            "pos" : {
                "name" : [45,650],
                "gen" : [45,620],
                "max": [45, 590],
                "time": [45, 560],
                "save": [280, 650],
                "full": [280, 620],
                "pause": [280, 590],
                "show": [280, 560],
            }
        }
        try:
            pyglet.font.add_file("graphics/Comfortaa-Bold.ttf")
            pyglet.font.add_file("graphics/Comfortaa-Regular.ttf")
        except:
            print("Error >> loading font")

        ### LABELS ###
        self.labels = {}
        self.labels["name"] = pyglet.text.Label("", font_name="Comfortaa", bold=True, color=(225, 88, 88, 255), font_size=25, x=40, y=660)
        self.labels["gen"] = pyglet.text.Label("Generation: 0", font_name="Comfortaa", bold=True, font_size=15, x=500, y=630)
        self.labels["max"] = pyglet.text.Label("Best score: 0", font_name="Comfortaa", bold=True, font_size=15, x=500, y=600)
        self.labels["time"] = pyglet.text.Label("Time: 0 / 0", font_name="Comfortaa", bold=True, font_size=15, x=500,y=570)
        self.labels["save"] = pyglet.text.Label("Save  [S]",font_name="Comfortaa", font_size=15, x=200, y=630)
        self.labels["full"] = pyglet.text.Label("Full  [F]", font_name="Comfortaa",font_size=15, x=200, y=600)
        self.labels["pause"] = pyglet.text.Label("Pause [P]", font_name="Comfortaa",font_size=15, x=200, y=570)
        self.labels["show"] = pyglet.text.Label("Show  [O]", font_name="Comfortaa",font_size=15, x=200, y=540)

        # SCALE
        self.change_scale(self.scale)

    def set_track(self, vertex_list, bg=False):
        self.track_vertex_list = vertex_list
        self.track_bg = bg

    def clear(self):
        glClearColor(0.69, 0.76, 0.87, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

    def draw_bg(self, bg):
        bg.blit(0,0, width=self.window.width, height=bg.height/(bg.width/self.window.width))

    def draw_lines(self, vertex_list):
        for vl in vertex_list:
            vl.draw(pyglet.gl.GL_LINE_LOOP)

    # draw track details
    def draw_cps(self, cps):
        for key in cps:
            cp = cps[key]
            self.draw_point(cp)

    def draw_car_sensors(self,car):
        for sen in car.sensors:
            self.draw_line([(car.xpos,car.ypos), sen],(1,1,1,0.3))

    # update cars sprites before rendering
    def update_sprites(self,cars):
        for car in cars:
            car.sprite.update(x=car.xpos*self.scale,y=car.ypos*self.scale, rotation=-car.angle-90, scale=self.scale*0.09)

    # load car texture
    def load_car_image(self, dir):
        image = pyglet.image.load(dir)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        return image

    # draw every label
    def draw_labels(self):
        for key in self.labels:
            self.labels[key].draw()


    # draw a line
    def draw_line(self,line,color=(1,1,1,1)):
        sc = self.scale
        glColor4f(*color)
        glBegin(GL_LINES)
        glVertex2f(line[0][0]*sc, line[0][1]*sc)
        glVertex2f(line[1][0]*sc, line[1][1]*sc)
        glEnd()

    # draw a point
    def draw_point(self,point):
        sc = self.scale
        glBegin(GL_TRIANGLE_FAN)
        glColor3f(1,.5,.5)
        glVertex2f((point[0]+2)*sc, (point[1]-2)*sc)
        glVertex2f((point[0]+2)*sc, (point[1]+2)*sc)
        glVertex2f((point[0]-2)*sc, (point[1]+2)*sc)
        glVertex2f((point[0]-2)*sc, (point[1]-2)*sc)
        glEnd()

    def clear_batch(self):
        del(self.car_batch)
        self.car_batch = pyglet.graphics.Batch()

    def change_scale(self,scale):
        self.lb_stg["size"] = (20 * scale, self.window.height - (20 * scale), 325 * scale, self.window.height - (200 * scale))
        pos = self.lb_stg["pos"]
        for key in self.labels:
            label = self.labels[key]
            label.x = pos[key][0] * scale
            label.y = self.window.height - ((720 - pos[key][1])*scale)
            label.font_size = (label.font_size / self.scale) * scale
        self.scale = scale
