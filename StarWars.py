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
  

class StarWars(object):
    def __init__(self):
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.clock = time.Clock()
        self.caption = display.set_caption('STAR WARS')
        self.screen = SCREEN
        self.background = image.load(KARTINKI + 'bg.jpg').convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        self.vragPos = POSSITION_VRAGOV
        self.titleText = Text(SHRIFT_1, 50, 'STAR WARS', WHITE, 260, 155)
        self.titleText2 = Text(SHRIFT_1, 25, 'Press any key', WHITE,
                               310, 225)
        self.gameOverText = Text(SHRIFT_1, 50, 'Game Over', WHITE, 250, 270)
        self.nextRoundText = Text(SHRIFT_1, 50, 'Next Round', WHITE, 240, 270)
        self.enemy1Text = Text(SHRIFT_1, 25, '   =   10 pts', GREEN, 368, 270)
        self.enemy2Text = Text(SHRIFT_1, 25, '   =  20 pts', BLUE, 368, 320)
        self.enemy3Text = Text(SHRIFT_1, 25, '   =  30 pts', PURPLE, 368, 370)
        self.enemy4Text = Text(SHRIFT_1, 25, '   =  ?????', RED, 368, 420)
        self.scoreText = Text(SHRIFT_1, 20, 'Score', WHITE, 5, 5)
        self.livesText = Text(SHRIFT_1, 20, 'Lives ', WHITE, 640, 5)

        self.life1 = Life(715, 3)
        self.life2 = Life(742, 3)
        self.life3 = Life(769, 3)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

    def reset(self, score):
        self.player = Hero()
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.rocket = sprite.Group()
        self.mysteryShip = Mystery()
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.vragRocket = sprite.Group()
        self.make_vragi()
        self.allSprites = sprite.Group(self.player, self.vragi,
                                       self.livesGroup, self.mysteryShip)
        self.keys = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewHero = False
        self.shipAlive = True

    def make_ograd(self, number):
        ogradGroup = sprite.Group()
        for row in range(4):
            for column in range(9):
                ograd = Blocker(10, GREY, row, column)
                ograd.rect.x = 50 + (200 * number) + (column * ograd.width)
                ograd.rect.y = POSSITION_OGRAD + (row * ograd.height)
                ogradGroup.add(ograd)
        return ogradGroup

    def create_audio(self):
        self.music = {}
        for music_name in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled',
                           'shipexplosion']:
            self.music[music_name] = mixer.Sound(
                MUSIC + '{}.wav'.format(music_name))
            self.music[music_name].set_volume(0.2)

        self.musicNotes = [mixer.Sound(MUSIC + '{}.wav'.format(i)) for i
                           in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.vragi.moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += self.vragi.moveTime


    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if should_exit(e):
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if len(self.rocket) == 0 and self.shipAlive:
                        if self.score < 1000:
                            rocket = Rocket(self.player.rect.x + 23,
                                            self.player.rect.y + 5, -1,
                                            15, 'laser', 'center')
                            self.rocket.add(rocket)
                            self.allSprites.add(self.rocket)
                            self.music['shoot'].play()
                        else:
                            leftrocket = Rocket(self.player.rect.x + 8,
                                                self.player.rect.y + 5, -1,
                                                15, 'laser', 'left')
                            rightrocket = Rocket(self.player.rect.x + 38,
                                                 self.player.rect.y + 5, -1,
                                                 15, 'laser', 'right')
                            self.rocket.add(leftrocket)
                            self.rocket.add(rightrocket)
                            self.allSprites.add(self.rocket)
                            self.music['shoot2'].play()

    def make_vragi(self):
        vragi = RaspolVrag(10, 5)
        for row in range(5):
            for column in range(10):
                vrag = Vragi(row, column)
                vrag.rect.x = 157 + (column * 50)
                vrag.rect.y = self.vragPos + (row * 45)
                vragi.add(vrag)

        self.vragi = vragi

    def make_vragi_shoot(self):
        if (time.get_ticks() - self.timer) > 700 and self.vragi:
            vrag = self.vragi.random_bottom()
            self.vragRocket.add(
                Rocket(vrag.rect.x + 14, vrag.rect.y + 20, 1, 5,
                       'vraglaser', 'center'))
            self.allSprites.add(self.vragRocket)
            self.timer = time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }

        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        self.vrag1= PHOTOS['enemy3']
        self.vrag1 = transform.scale(self.vrag1, (40, 40))
        self.vrag2 = PHOTOS['enemy2']
        self.vrag2 = transform.scale(self.vrag2, (40, 40))
        self.vrag3 = PHOTOS['enemy1']
        self.vrag3 = transform.scale(self.vrag3, (40, 40))
        self.vrag4 = PHOTOS['mystery']
        self.vrag4 = transform.scale(self.vrag4, (80, 40))
        self.screen.blit(self.vrag1, (318, 270))
        self.screen.blit(self.vrag2, (318, 320))
        self.screen.blit(self.vrag3, (318, 370))
        self.screen.blit(self.vrag4, (299, 420))

    def check_collisions(self):
        sprite.groupcollide(self.rocket, self.vragRocket, True, True)

        for vrag in sprite.groupcollide(self.vragi, self.rocket,
                                         True, True).keys():
            self.music['invaderkilled'].play()
            self.calculate_score(vrag.row)
            VragExplosion(vrag, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        for mystery in sprite.groupcollide(self.mysteryGroup, self.rocket,
                                           True, True).keys():
            mystery.mysteryEntered.stop()
            self.music['mysterykilled'].play()
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, self.explosionsGroup)
            newShip = Mystery()
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        for player in sprite.groupcollide(self.playerGroup, self.vragRocket,
                                          True, True).keys():
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
                self.gameOver = True
                self.startGame = False
            self.music['shipexplosion'].play()
            ShipExplosion(player, self.explosionsGroup)
            self.makeNewHero = True
            self.shipTimer = time.get_ticks()
            self.shipAlive = False

        if self.vragi.bottom >= 540:
            sprite.groupcollide(self.vragi, self.playerGroup, True, True)
            if not self.player.alive() or self.vragi.bottom >= 600:
                self.gameOver = True
                self.startGame = False

        sprite.groupcollide(self.rocket, self.allOgrad, True, True)
        sprite.groupcollide(self.vragRocket, self.allOgrad, True, True)
        if self.vragi.bottom >= POSSITION_OGRAD:
            sprite.groupcollide(self.vragi, self.allOgrad, False, True)
