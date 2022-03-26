# -*- coding: utf-8 -*-

import pyglet
from pyglet.gl import *
import numpy as np


def index_loop(ind, len):
    return ind % len if ind >= len else ind
# colors
WHITE = (255,255,255,255)
GREEN = (0, 153, 51, 255)
RED = (204, 0, 0, 255)
GRAY = (128, 128, 128, 255)

# car images
cars_init = {
    "alfaromeo" : ["alfaromeo.png", (133, 25, 30, 255)],
    "alphatauri" : ["alphatauri.png", (48, 69, 96, 255)],
    "alpine" : ["alpine.png", (57, 145, 245, 255)],
    "astonmartin" : ["astonmartin.png", (25, 145, 109, 255)],
    "ferrari" : ["ferrari.png", (204, 42, 30, 255)],
    "haas": ["haas.png", (255, 255, 255, 255)],
    "mclaren": ["mclaren.png", (242, 156, 57, 255)],
    "mercedes": ["mercedes.png", (95, 207, 191, 255)],
    "redbull": ["redbull.png", (1, 31, 227, 255)],
    "williams": ["williams.png", (25, 95, 245, 255)]
}

"""
Rendering.

Coordinates [x,y]:
[0,0] = BOTTOM LEFT
"""
class Camera:

    def __init__(self, width, height):
        self.MOVEMENT_LIMIT = 0.5
        self.MOVEMENT_SPEED = 0.6
        self.ZOOM_SPEED = 0.1

        self.x = width / 2
        self.y = height / 2
        self.tar_x = self.x
        self.tar_y = self.y

        self.zoom = 1
        self.tar_zoom = 1

        self.zoom_width = width
        self.zoom_height = height

        self.width = width
        self.height = height

    def update_movement(self):
        # smooth camera movement
        diff_x = self.tar_x - self.x
        diff_y = self.tar_y - self.y
        shift_x = diff_x * min(abs(diff_x / self.width) * self.MOVEMENT_SPEED, self.MOVEMENT_LIMIT)
        shift_y = diff_y * min(abs(diff_y / self.height) * self.MOVEMENT_SPEED, self.MOVEMENT_LIMIT)
        self.set_pos(self.x + shift_x, self.y + shift_y)

    def update_zoom(self):
        diff_zoom = self.tar_zoom - self.zoom
        shift_zoom = diff_zoom * self.ZOOM_SPEED
        self.set_zoom_center(self.zoom + shift_zoom)

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

        self.zoom_width = self.width / self.zoom
        self.zoom_height = self.height / self.zoom

    def set_target_zoom_center(self, scale):
        self.set_target_zoom(self.width/2, self.height/2, scale)

    def set_zoom_center(self, scale):
        self.set_zoom(self.width/2, self.height/2, scale)

    def drag(self, dx, dy):
        self.x += dx
        self.y += dy
        self.tar_x = self.x
        self.tar_y = self.y

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def get_sides(self):
        x, y = round(self.x, 5), round(self.y, 5)
        sx, sy = round(self.zoom_width, 5) / 2, round(self.zoom_height / 2, 5)
        # left, right, bottom, top
        return x - sx, x + sx, y - sy, y + sy

    def on_resize(self, width, height):
        self.zoom_width *= width / self.width
        self.zoom_height *= height / self.height
        self.width = width
        self.height = height

    def translate_onscreen_point(self, x, y):
        left, right, bottom, top = self.get_sides()
        return x / self.zoom + left, y / self.zoom + bottom


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
            "name": ["","Comfortaa",True,30,(255,255,255,140),(10,78)],
            "gen": ["Generation: 0","Comfortaa",False,15,(255,255,255,140),(10,12)],
            "max": ["Best score: 0","Comfortaa",False,15,(255,255,255,140),(10,36)],
            "time": ["Time: 0 / 0","Comfortaa",False,15,(255,255,255,140),(10,62)],


            "save": ["[S] Save","Comfortaa",False,13,(255,255,255,140),(10,140)],
            "full": ["[F] Full","Comfortaa",False,13,(255,255,255,140),(10,160)],
            "pause": ["[P] Pause","Comfortaa",False,13,(255,255,255,140),(10,180)],
            "debug": ["[D] Debug","Comfortaa",False,13,(255,255,255,140),(10,200)],
            "labels": ["[L] Labels", "Comfortaa", False, 13, (255, 255, 255, 140), (10, 220)],
            "nodraw": ["[N] No draw", "Comfortaa", False, 13, (255, 255, 255, 140), (10, 240)],
            "track": ["[T] Gen track", "Comfortaa", False, 13, (255, 255, 255, 140), (10, 260)],

            "cam_move": ["[Mouse] Move&Zoom","Comfortaa",False,13,(255,255,255,140),(10,290)],
            "cam_change": ["[Left & Right] Change cars", "Comfortaa", False,13,(255,255,255,140),(10,310)],
            "cam_leader": ["[Up] Select leader", "Comfortaa", False, 13, (255, 255, 255, 140), (10, 330)],
            "cam_free": ["[C] Free Cam","Comfortaa",False,13,(255,255,255,140),(10,350)],

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
        self.car_labels_batch = pyglet.graphics.Batch()
        self.leaderboard_batch = pyglet.graphics.Batch()

        self.car_images = {}
        for name in cars_init:
            self.car_images[name] = self.load_car_image("graphics/cars/"+cars_init[name][0])

        self.width = width
        self.height = height

        # MODULES
        self.hud = HUD(width, height)
        self.camera = Camera(width, height)
        self.leaderboard = Leaderboard(self.leaderboard_batch)

    def draw_grid(self):
        step = 768
        size = 10
        for i in range(-size + 1, size):
            self.draw_line([[i * step, -size * step], [i * step, size * step]], (1, 1, 1, 0.3))
        for i in range(-size + 1, size):
            self.draw_line([[-size * step, i * step], [size * step, i * step]], (1, 1, 1, 0.3))

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

    def draw_leaderboard(self, sorted_cars):
        glLoadIdentity()
        glPushMatrix()
        glOrtho(0,self.width,0,self.height,1,-1)

        self.leaderboard.update(sorted_cars)

        self.leaderboard.draw_background()

        self.leaderboard_batch.draw()

        glPopMatrix()

    def draw_car_labels(self, cars):
        for car in cars:
            car.label.update_pos(car.xpos, car.ypos)
            car.label.draw_background()
        self.car_labels_batch.draw()

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
        del(self.car_labels_batch)
        self.car_labels_batch = pyglet.graphics.Batch()
        self.car_batch = pyglet.graphics.Batch()

class Leaderboard:
    def __init__(self, batch):
        self.batch = pyglet.graphics.Batch()

        self.car_labels = []

        self.start_x = 50
        self.start_y = 650

        self.limit = 20

        self.height = 22
        self.width = 43

        self.font_size = 10

        self.init_labels(batch)

    def init_labels(self, batch):
        for i in range(1, self.limit + 1):
            label = CarLabel(order=i, name="", height=self.height, width=self.width, batch=batch, font_size=self.font_size)
            label.update_pos(self.start_x, self.start_y - (self.height * i))
            self.car_labels.append(label)

    def update(self, sorted_cars):
        for i, car in enumerate(sorted_cars):
            self.car_labels[index_loop(i, len(self.car_labels))].labels["name"].text = car.label.labels["name"].text
            self.car_labels[index_loop(i, len(self.car_labels))].bg_init_dict["white_bg"][0] = car.label.bg_init_dict["white_bg"][0]

            if i >= len(self.car_labels):
                break

    def draw_background(self):
        for label in self.car_labels:
            label.draw_background()

class CarLabel:
    def __init__(self, order=1, name="", color=(255, 255, 255, 128), height=24, width=43, margin=25, batch=None, font_size=12):
        self.x = 0
        self.y = 0

        # black sizes
        self.height = height
        self.width = width
        self.margin = margin

        self.font_size = font_size

        h, m = self.height, self.margin
        w_w, b_w = 28, self.width

        self.bg_init_dict = {
            # key: [color, [(0,0),(0,0),(0,0),(0,0)]
            "black_bg": [(0, 0, 0, 128), [(0, m), (0, m + h), (b_w, m + h), (b_w, m)]],
            "white_bg": [color, [(0, m), (0, m + h), (-w_w, m + h), (-w_w, m)]]
        }

        self.labels = {}
        self.labels_init_dict = {
            # key:  [text, font_name, bold, size, color, (x,y), anchor_x]
            "order": [str(order),"Comfortaa", True, self.font_size, (0,0,0,255), (-5, m), "right"],
            "name": [name, "Comfortaa", True, self.font_size, (255, 255, 255, 255), (5, m), "left"],
        }

        self.init_labels(batch=batch)

    def init_labels(self, batch):
        for key in self.labels_init_dict:
            val = self.labels_init_dict[key]
            self.labels[key] = pyglet.text.Label(
                val[0],
                anchor_x=val[6],
                font_name=val[1],
                bold=val[2],
                font_size=val[3],
                color=val[4],
                x=val[5][0],
                y=val[5][1],
                batch=batch
            )

    def draw_labels(self):
        self.labels["order"].draw()
        self.labels["name"].draw()

    def draw_background(self):
        for key in self.bg_init_dict:
            val = self.bg_init_dict[key]

            glBegin(GL_TRIANGLE_FAN)
            glColor4ub(*val[0])
            for j in val[1]:
                glVertex2f(self.x + j[0], self.y + j[1])
            glEnd()

    def draw(self):
        self.draw_background()
        self.draw_labels()

    def update_pos(self, x, y):
        self.x = x
        self.y = y
        for key in self.labels:
            init_values = self.labels_init_dict[key]
            label = self.labels[key]
            label.x = x + init_values[5][0]
            label.y = y + init_values[5][1]


class CarInfo:
    def __init__(self):
        self.x = 0
        self.y = 0

        # corners of black background
        self.bg_width = 100
        self.bg_height = 100
        self.bg_margin = -160

        # LABELS
        self.labels_init_dict = {
            # key:  [text, font_name, bold, size, color, (x,y)]
            "name": ["Car","Comfortaa",True,20,(255,255,255,200),(0,-100)],
            "active": ["true","Comfortaa",False,15,(255,255,255,200),(0,-120)],
            "score": ["0","Comfortaa",False,15,(255,255,255,200),(0,-140)],
            "speed": ["0","Comfortaa",False,15,(255,255,255,200),(0,-160)],
        }
        self.labels = self.init_labels(self.labels_init_dict)

    def init_labels(self, label_init):
        labels = {}
        for key in label_init:
            val = label_init[key]
            labels[key] = pyglet.text.Label(
                val[0],
                anchor_x="center",
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
        self.draw_background()
        for key in self.labels:
            self.labels[key].draw()

    def draw_background(self):
        w = self.bg_width / 2
        h = self.bg_height
        m = self.bg_margin
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(0,0,0,.5)
        glVertex2f(self.x - w, self.y + m)
        glVertex2f(self.x + w, self.y + m)
        glVertex2f(self.x + w, self.y + m + h)
        glVertex2f(self.x - w, self.y + m + h)
        glEnd()

    def update_labels(self, x, y):
        self.x = x
        self.y = y
        for key in self.labels:
            init_values = self.labels_init_dict[key]
            label = self.labels[key]
            label.x = x + init_values[5][0]
            label.y = y + init_values[5][1]

