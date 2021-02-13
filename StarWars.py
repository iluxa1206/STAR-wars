from pygame import *
import sys
from os.path import abspath, dirname
from random import choice

OSNOV_PAPKA = abspath(dirname(__file__))
SHRIFT = OSNOV_PAPKA + '/fonts/'
KARTINKI = OSNOV_PAPKA + '/images/'
MUSIC = OSNOV_PAPKA + '/sounds/'

# ЦВЕТА
WHITE = (255, 255, 255)
GREEN = (104, 238, 55)
YELLOW = (255, 249, 48)
BLUE = (104, 195, 255)
PURPLE = (203, 0, 235)
RED = (240, 24, 24)
GREY = (138, 138, 138)

SCREEN = display.set_mode((800, 600))
SHRIFT_1 = SHRIFT + 'star_wars.ttf'
NAME_PHOTO = ['hero', 'mystery',
             'enemy1',
             'enemy2',
             'enemy3',
             'boom',
             'laser', 'vraglaser']
PHOTOS = {name: image.load(KARTINKI + '{}.png'.format(name)).convert_alpha()
          for name in NAME_PHOTO}

POSSITION_OGRAD = 450
POSSITION_VRAGOV = 65
SDVIG_VRAGOV = 35
