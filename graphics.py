# -*- coding: utf-8 -*-

import pyglet
from pyglet.gl import *
import numpy as np

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

Coordinates [x,y]:
[0,0] = BOTTOM LEFT
"""
class Camera:
    def __init__(self, width, height):
        self.left = 0
        self.right = width
        self.bottom = 0
        self.top = height

        self.zoom = 1
        self.zoom_width = width
        self.zoom_height = height

        self.width = width
        self.height = height

    def set_zoom(self, x, y, scale):
        self.zoom /= scale
        pos_x = x / self.width
        pos_y = y / self.height
        real_x = self.left + pos_x * self.zoom_width
        real_y = self.bottom + pos_y * self.zoom_height
        self.zoom_width /= scale
        self.zoom_height /= scale

        self.left = real_x - pos_x * self.zoom_width
        self.right = real_x + (1 - pos_x) * self.zoom_width
        self.bottom = real_y - pos_y * self.zoom_height
        self.top = real_y + (1 - pos_y) * self.zoom_height

    def set_zoom_center(self, scale):
        self.set_zoom(self.width/2, self.height/2, scale)

    def drag(self, dx, dy):
        self.left += dx
        self.right += dx
        self.bottom += dy
        self.top += dy

    def set_pos_center(self, x, y):
        shift_x = self.zoom_width / 2
        shift_y = self.zoom_height / 2
        self.left = x - shift_x
        self.right = x + shift_x
        self.bottom = y - shift_y
        self.top = y + shift_y

    def on_resize(self, width, height):
        self.zoom_width *= width / self.width
        self.zoom_height *= height / self.height
        self.width = width
        self.height = height

class HUD:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        try:
            pyglet.font.add_file("graphics/Comfortaa-Bold.ttf")
            pyglet.font.add_file("graphics/Comfortaa-Regular.ttf")
        except:
            print("Error >> loading font")
        # LABELS
        labels_init_dict = {
            # key:  [text, font_name, bold, size, color, (x,y)]
            "name": ["","Comfortaa",True,30,(255,255,255,140),(10,75)],
            "gen": ["Generation: 0","Comfortaa",False,15,(255,255,255,140),(10,12)],
            "max": ["Best score: 0","Comfortaa",False,15,(255,255,255,140),(10,36)],
            "time": ["Time: 0 / 0","Comfortaa",False,15,(255,255,255,140),(10,60)],
            "save": ["[S] Save","Comfortaa",False,15,(255,255,255,140),(200,12)],
            "full": ["[F] Full","Comfortaa",False,15,(255,255,255,140),(200,36)],
            "pause": ["[P] Pause","Comfortaa",False,15,(255,255,255,140),(200,60)],
            "show": ["[O] Show","Comfortaa",False,15,(255,255,255,140),(200,84)],
            "cam_move": ["[Mouse] Move&Zoom","Comfortaa",False,15,(255,255,255,140),(320,12)],
            "cam_change": ["[Arrws] Change cars", "Comfortaa", False,15,(255,255,255,140),(320,36)],
            "cam_free": ["[C] Free Cam","Comfortaa",False,15,(255,255,255,140),(320,60)],

        }
        self.labels = self.init_labels(labels_init_dict)

    def init_labels(self, label_init):
        labels = {}
        for key in label_init:
            val = label_init[key]
            labels[key] = pyglet.text.Label(
                val[0],
                font_name=val[1],
                bold=val[2],
                font_size=val[3],
                color=val[4],
                x=val[5][0],
                y=val[5][1]
            )
        return labels

    # draw every label
    def draw(self):
        for key in self.labels:
            self.labels[key].draw()

    def on_resize(self, width, height):
        pass

class Graphics:
    def __init__(self, width, height):
        self.car_batch = pyglet.graphics.Batch()
        self.car_images = []
        for name in racers_info:
            self.car_images.append((name, self.load_car_image("graphics/cars/"+racers_info[name][0])))

        self.width = width
        self.height = height

        # MODULES
        self.hud = HUD(width, height)
        self.camera = Camera(width, height)

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.camera.on_resize(width, height)
        self.hud.on_resize(width, height)

    def set_camera_view(self):
        glOrtho(self.camera.left, self.camera.right, self.camera.bottom, self.camera.top, 1, -1)

    def set_default_view(self):
        glOrtho(0,self.width,0,self.height,1,-1)

    def clear(self):
        glClearColor(0.69, 0.76, 0.87, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

    def draw_hud(self):
        glLoadIdentity()
        glPushMatrix()
        glOrtho(0,self.width,0,self.height,1,-1)
        self.hud.draw()
        glPopMatrix()

    def draw_vertex_list(self, vl):
        vl.draw(GL_LINE_LOOP)

    # draw track details
    def draw_cps(self, cps):
        for cp in cps:
            self.draw_point(cp)

    def draw_car_sensors(self,car):
        for sen in car.sensors:
            line = np.array([(car.xpos, car.ypos), sen])
            self.draw_line(line, (1, 1, 1, 0.3))

    # update cars sprites before rendering
    def update_sprites(self, cars):
        for car in cars:
            car.sprite.update(
                x=car.xpos,
                y=car.ypos,
                rotation=-car.angle - 90,
                scale=0.11
            )

    # load car texture
    def load_car_image(self, dir):
        image = pyglet.image.load(dir)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        return image

    # draw a line
    def draw_line(self, line, color=(1, 1, 1, 1)):
        glColor4f(*color)
        glBegin(GL_LINES)
        glVertex2f(line[0][0], line[0][1])
        glVertex2f(line[1][0], line[1][1])
        glEnd()

    # draw a point
    def draw_point(self, point, size=5):
        glBegin(GL_TRIANGLE_FAN)
        glColor3f(1,.5,.5)
        glVertex2f((point[0]+size), (point[1]-size))
        glVertex2f((point[0]+size), (point[1]+size))
        glVertex2f((point[0]-size), (point[1]+size))
        glVertex2f((point[0]-size), (point[1]-size))
        glEnd()

    def clear_batch(self):
        del(self.car_batch)
        self.car_batch = pyglet.graphics.Batch()

