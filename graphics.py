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
    "alfaromeo" : ["alfaromeo.png", (0,0,0,255)],
    "alphatauri" : ["alphatauri.png",(0,0,170,255)],
    "alpine" : ["alpine.png",(52,205,243,255)],
    "astonmartin" : ["astonmartin.png",(10,183,45,255)],
    "ferrari" : ["ferrari.png",(150,150,150,255)],
    "haas": ["haas.png",(231,132,0,255)],
    "mclaren": ["mclaren.png",(203,0,0,255)],
    "mercedes": ["mercedes.png",(250,56,178,255)],
    "redbull": ["redbull.png",(228,229,0,255)],
    "williams": ["williams.png",(255,255,255,255)]
}

"""
Rendering.

Coordinates [x,y]:
[0,0] = BOTTOM LEFT
"""
class Camera:

    def __init__(self, width, height):
        self.MOVEMENT_SPEED = 0.4
        self.ZOOM_SPEED = 0.1

        self.x = width / 2
        self.y = height / 2
        self.tar_x = self.x
        self.tar_y = self.y

        self.zoom = 1
        self.tar_zoom = 1;

        self.zoom_width = width
        self.zoom_height = height

        self.width = width
        self.height = height

    def update(self):
        # smooth camera movement
        diff_x = self.tar_x - self.x
        diff_y = self.tar_y - self.y
        shift_x = diff_x * abs(diff_x / self.width) * self.MOVEMENT_SPEED
        shift_y = diff_y * abs(diff_y / self.height) * self.MOVEMENT_SPEED

        diff_zoom = self.tar_zoom - self.zoom
        shift_zoom = diff_zoom * self.ZOOM_SPEED

        self.set_zoom_center(self.zoom + shift_zoom)
        self.set_pos(self.x + shift_x, self.y + shift_y)

    def set_target(self, x, y):
        self.tar_x = x
        self.tar_y = y

    def set_target_zoom(self, x, y, scale):
        self.tar_zoom = self.zoom * scale

    def set_zoom(self, x, y, zoom):
        self.zoom = zoom

        """pos_x = x / self.width
        pos_y = y / self.height

        self.x = self.left + pos_x * self.zoom_width
        self.y = self.bottom + pos_y * self.zoom_height"""

        self.zoom_width = self.width / self.zoom;
        self.zoom_height = self.height / self.zoom;

    def set_target_zoom_center(self, scale):
        self.set_target_zoom(self.width/2, self.height/2, scale)

    def set_zoom_center(self, scale):
        self.set_zoom(self.width/2, self.height/2, scale)

    def drag(self, dx, dy):
        self.x += dx
        self.y += dy

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def get_sides(self):
        x, y = self.x, self.y
        sx, sy = self.zoom_width / 2, self.zoom_height / 2
        # left, right, bottom, top
        return x - sx, x + sx, y - sy, y + sy

    def on_resize(self, width, height):
        self.zoom_width *= width / self.width
        self.zoom_height *= height / self.height
        self.width = width
        self.height = height

    def translate_onscreen_point(self, x, y):
        left, right, bottom, top = self.get_sides()
        return x * self.zoom + left, y * self.zoom + bottom


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

    def draw_grid(self):
        step = 768
        for i in range(0, 15):
            self.draw_line([[i * step, -10 * step], [i * step, 14 * step]], (1, 1, 1, 0.3))
        for i in range(0, 15):
            self.draw_line([[-10 * step, i * step], [14 * step, i * step]], (1, 1, 1, 0.3))

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.camera.on_resize(width, height)
        self.hud.on_resize(width, height)

    def set_camera_view(self):
        glOrtho(*self.camera.get_sides(), 1, -1)

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

    def highligh_car(self, car):
        self.draw_circle(car.xpos, car.ypos, 20)

    def draw_circle(self, x, y, radius):
        circle = pyglet.shapes.Circle(x,y,radius)
        circle.draw()

    # draw track details
    def draw_cps(self, cps):
        for cp in cps:
            self.draw_point(cp)

    def draw_car_info(self, car):
        car.info.update_labels(car.xpos, car.ypos)
        car.info.draw()

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
                scale=0.24
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

class CarInfo:
    def __init__(self):
        self.x = 0
        self.y = 0

        try:
            pyglet.font.add_file("graphics/Comfortaa-Bold.ttf")
            pyglet.font.add_file("graphics/Comfortaa-Regular.ttf")
        except:
            print("Error >> loading font")

        # LABELS
        self.labels_init_dict = {
            # key:  [text, font_name, bold, size, color, (x,y)]
            "name": ["Car","Comfortaa",True,20,(255,255,255,140),(0,100)],
            "active": ["true","Comfortaa",False,15,(255,255,255,140),(0,80)],
            "score": ["0","Comfortaa",False,15,(255,255,255,140),(0,60)],
            "speed": ["0","Comfortaa",False,15,(255,255,255,140),(0,40)],
        }
        self.labels = self.init_labels(self.labels_init_dict)

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

    def update_labels(self, x, y):
        for key in self.labels:
            init_values = self.labels_init_dict[key]
            label = self.labels[key]
            label.x = x + init_values[5][0]
            label.y = y + init_values[5][1]

