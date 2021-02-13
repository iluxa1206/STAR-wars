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

        
        
class RaspolVrag(sprite.Group):
    def __init__(self, columns, rows):
        sprite.Group.__init__(self)
        self.vragi = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.direction = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.moveNumber = 15
        self.timer = time.get_ticks()
        self.bottom = game.vragPos + ((rows - 1) * 45) + 35
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for vrag in self:
                    vrag.rect.y += SDVIG_VRAGOV
                    if self.bottom < vrag.rect.y + 35:
                        self.bottom = vrag.rect.y + 35
            else:
                velocity = 10 if self.direction == 1 else -10 #СДВИГ ВЛЕВО И ВПРАВО
                for vrag in self:
                    vrag.rect.x += velocity
                self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(RaspolVrag, self).add_internal(*sprites) #ПЕРЕБОР ВСЕХ КАРТИНОК ВРАГОВ
        for s in sprites:
            self.vragi[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(RaspolVrag, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.vragi[row][column]
                       for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_vragi = (self.vragi[row - 1][col]
                       for row in range(self.rows, 0, -1))
        return next((en for en in col_vragi if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime = 150 #ИЗМЕНЕНИЕ СКОРОСТИ, ПРИ УМЕНЬШЕЕ КОЛИЧЕСТВА ПРОТИВНИКОВ
        elif len(self) > 1 and len(self) < 7:
            self.moveTime = 250
        elif len(self) <= 10:
            self.moveTime = 400

    def kill(self, vrag):
        self.vragi[vrag.row][vrag.column] = None
        is_column_dead = self.is_column_dead(vrag.column)
        if is_column_dead:
            self._aliveColumns.remove(vrag.column)

        if vrag.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif vrag.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)


class Blocker(sprite.Sprite):
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = size
        self.width = size
        self.color = color
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = PHOTOS['mystery']
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = time.get_ticks()
        self.mysteryEntered = mixer.Sound(MUSIC + 'mysteryentered.wav')
        self.mysteryEntered.set_volume(0.3)
        self.playSound = True

    def update(self, keys, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer
        if passed > self.moveTime:
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.mysteryEntered.play()
                self.playSound = False
            if self.rect.x < 840 and self.direction == 1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x += 2
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x -= 2
                game.screen.blit(self.image, self.rect)

        if self.rect.x > 830:
            self.playSound = True
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direction = 1
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = currentTime

 def get_image():
    return PHOTOS['boom']

class VragExplosion(sprite.Sprite):
    def __init__(self, vrag, *groups):
        super(VragExplosion, self).__init__(*groups)
        self.image = transform.scale(get_image(), (40, 35))
        self.image2 = transform.scale(get_image(), (50, 45))
        self.rect = self.image.get_rect(topleft=(vrag.rect.x, vrag.rect.y))
        self.timer = time.get_ticks()


    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect) #РАСШИРЕНИЕ ВЗРЫВА
        elif passed <= 200:
            game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < passed:
            self.kill()


class MysteryExplosion(sprite.Sprite):
    def __init__(self, mystery, score, *groups):
        super(MysteryExplosion, self).__init__(*groups)
        self.text = Text(SHRIFT_1, 20, str(score), WHITE,
                         mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(game.screen)
        elif 600 < passed:
            self.kill()


class ShipExplosion(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = PHOTOS['hero']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            game.screen.blit(self.image, self.rect)
        elif 900 < passed:
            self.kill()


class Life(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self) #ОТОБРАЖЕНИЕ КОЛИЧЕСТВА ЖИЗНЕЙ
        self.image = PHOTOS['hero']
        self.image = transform.scale(self.image, (23, 23))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


def should_exit(evt):
    return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)
