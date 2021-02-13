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


class Hero(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = PHOTOS['hero']
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.speed = 5

    def update(self, keys, *args):#  ДВИЖЕНИЕ КОРАБЛЯ ИГРОКА В ЗАДАННОЙ ОБЛАСТИ
        if keys[K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.speed
        game.screen.blit(self.image, self.rect)


class Rocket(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = PHOTOS[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        if self.rect.y < 15 or self.rect.y > 600:
            self.kill()


class Vragi(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()


    def update(self, *args):
        game.screen.blit(self.image, self.rect) #ОБНОВЛНИЕ ПОЗИЦИЙ ПРОТИВНИКОВ

    def load_images(self):
        images = {0: '1',
                  1: '2',
                  2: '2',
                  3: '3',
                  4: '3'
                  }
        img1 = (PHOTOS['enemy{}'.format(images[self.row])])
        self.images.append(transform.scale(img1, (40, 35)))

