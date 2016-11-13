from __future__ import division
import pyprocessing as pyp

from pyprocessing import PVector, color
from math import sqrt, pow, sin, cos, acos, tan, atan, pi, e, log, exp
from random import random, uniform
import numpy as np

screen_size = (320, 200)
back_col = color(0, 0, 0)
default_fill_col = color(255,255,255)
background_particle_count = 100
frame_cycles = 360

class Transformation(object):
    @classmethod
    def transform(cls, transformation, vector):
        assert isinstance(transformation, np.ndarray)
        assert isinstance(vector, PVector)
        # if transformation is 3x3 then vector should be 3
        assert all([len(vector) == dimension for dimension in transformation.shape])

        response = np.matmul(transformation, vector)
        return PVector(*response)

    @classmethod
    def rotate_x(cls, theta, vector):
        assert isinstance(vector, PVector)
        transformation = np.array([[1,           0,            0         ],
                                   [0,           cos(theta), -sin(theta) ],
                                   [0,           sin(theta), cos(theta)  ]])
        return cls.transform(transformation, vector)

    @classmethod
    def rotate_y(cls, theta, vector):
        assert isinstance(vector, PVector)
        transformation = np.array([[cos(theta),  0,          sin(theta)  ],
                                   [0,           1,          0           ],
                                   [-sin(theta), 0,          cos(theta)  ]])
        return cls.transform(transformation, vector)

    @classmethod
    def rotate_z(cls, theta, vector):
        assert isinstance(vector, PVector)
        transformation = np.array([[cos(theta),  -sin(theta), 0           ],
                                   [sin(theta),  cos(theta),  0           ],
                                   [0,           0,           1           ]])
        return cls.transform(transformation, vector)

    @classmethod
    def transpose(cls, offset, vector):
        return PVector(*[sum(elems) for elems in zip(offset, vector)])

class Vector_Helpers(object):
    @classmethod
    def cartesian_to_spherical(cls, vector):
        length = vector.mag()
        azimuth = np.arctan2(vector.x, vector.y)
        polar = cls.angle_between(
            PVector(0,0,1),
            vector
        )
        return (length, polar, azimuth)

    @classmethod
    def angle_between(cls, vector_a, vector_b):
        if vector_a.mag() == 0 or vector_b.mag() == 0:
            return None
        normal_a, normal_b = vector_a.get(), vector_b.get()
        normal_a.normalize(), normal_b.normalize()

        return np.arccos(
            np.clip(
                normal_a.dot(normal_b),
                -1.0,
                1.0
            )
        )

class Positionable(object):
    """ Mixin for positionable objects """
    def __init__(self, **kwargs):
        self.position = kwargs.get('position', PVector(0,0,0))
        self.orientation = kwargs.get('orientation', PVector(1,0,0))

    @property
    def size(self):
        return self.orientation.mag()

    @property
    def position_spherical(self):
        return Vector_Helpers.cartesian_to_spherical(self.position)

    @property
    def orientation_spherical(self):
        return Vector_Helpers.cartesian_to_spherical(self.orientation)


class Drawable(Positionable):
    """ Mixin for drawable obkects """
    def __init__(self, **kwargs):
        Positionable.__init__(self, **kwargs)
        self.fill_color = kwargs.get('fill_color', default_fill_col)
        self.active = kwargs.get('active', False)

    def draw_poly(self):
        pass

    def draw(self):
        pyp.pushMatrix()
        pyp.noStroke()
        pyp.fill(self.fill_color)
        pyp.translate(*self.position)
        self.draw_poly()
        pyp.popMatrix()

class Particle(Drawable):
    def __init__(self, **kwargs):
        Drawable.__init__(self, **kwargs)
        self.iteration = 0

    def draw_poly(self):
        pyp.sphere(self.size)

    def draw(self):
        if self.active:
            Drawable.draw(self)

class Swarm(Drawable):
    """ Collection of particles that obey the same rules """
    pass


class Spawner(Drawable):
    def __init__(self, **kwargs):
        kwargs['active'] = True
        Drawable.__init__(self, **kwargs)
        self.angle = kwargs.get('angle', 0)
        self.center_particle = Particle(
            active=self.active,
            position=self.position,
            orientation=self.orientation
        )
        self.spawning_particle = Particle(
            active=self.active,
            position=self.spawn_position,
            orientation=self.orientation
        )

    def draw(self):
        self.spawning_particle.position = self.spawn_position
        self.center_particle.draw()
        self.spawning_particle.draw()

    @property
    def spawn_position(self):
        circle = PVector(self.size * sin(self.angle), self.size * cos(self.angle), 0)
        (r, theta, phi) = self.orientation_spherical
        if theta:
            circle = Transformation.rotate_y(-theta, circle)
        if phi:
            circle = Transformation.rotate_z(phi, circle)
        if self.position:
            circle = Transformation.transpose(self.position, circle)
        return circle



def setup():
    global screen_size
    global camera_pos
    global background_particles
    global spawner
    global frame_count

    frame_count = 0

    camera_pos = PVector(0,0,max(screen_size))

    spawner = Spawner(
        position=PVector(0,0,max(screen_size)/10),
        orientation=PVector(0,0,max(screen_size)/10)
    )

    #init background_particles
    # background_particles = []
    # for i in range(1, background_particle_count):
    #     background_particles.append(
    #         Particle(
    #             active=False
    #         )
    #     )


def draw():
    global screen_size
    global camera_pos
    global background_particles
    global spawner
    global frame_count


    pyp.camera(
        camera_pos.x, camera_pos.y, camera_pos.z,
        0, 0, 0,
        1, 0, 0
    )

    s = max(screen_size)

    pyp.pointLight(255,255,255,10*s,0,0)
    pyp.pointLight(255,255,255,0,10*s,0)
    pyp.pointLight(255,255,255,0,0,10*s)

    pyp.background(back_col)

    #calculate spawner angle
    spawner.angle = 2.0 * pi * (frame_count % frame_cycles) / frame_cycles
    print "angle: ", spawner.angle, "position:", spawner.spawn_position

    spawner.draw()

    frame_count += 1

    # for background_particle in background_particles:
        # background_particle.draw()

pyp.run()