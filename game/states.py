import sys
from random import randint

import pygame
from pygame.locals import *

from game import config
from game.objects import RedBall


class State(object):
    def handle(self, event):
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            # 刚刚出来的小球，给一个随机的速度
            random_speed = (randint(-400, 400), randint(-300, 0))
            new_ball = RedBall(event.pos,
                            random_speed,
                            ball_image,
                            bounce_sound)
            balls.append(new_ball)

    def firstDisplay(self, screen):
        screen.fill(config.background_color)
        pygame.display.update()

    def display(self, screen):
        pass


class Level(State):

    def __init__(self, number=1):
        self.number = number
        self.remaining = config.ball_level

        speed = config.red_ball_speed

        speed += (self.number - 1) * config.speed_increase

        self.weight = objects.Weight(speed)
        self.banana = objects.Banana()
        both = self.weight, self.banana
        self.sprites = pygame.sprite.RenderUpdates(both)

    def update(self, game):
        self.sprites.update()

        if self.white_ball.touches(self.red_ball):
            game.nextState = GameOver()

        elif self.weight.landed:
            self.weight.reset()
            self.remaining -= 1
            if self.remaining == 0:
                game.nextState = LevelCleared(self.number)

    def display(self, screen):
        screen.fill(config.background_color)
        updates = self.sprites.draw(screen)
        pygame.display.update(updates)


class Paused(State):
    finished = 0
    image = None
    text = ''

    def handle(self, event):
        State.handle(self, event)
        if event.type in [MOUSEBUTTONDOWN, KEYDOWN]:
            self.finished = 1

    def update(self, game):
        if self.finished:
            game.nextState = self.nextState()

    def firstDisplay(self, screen):
        screen.fill(config.background_color)

        font = pygame.font.Font(None, config.font_size)
        lines = self.text.strip().splitlines()

        height = len(lines) * font.get_linesize()

        center, top = screen.get_rect().center
        top -= height // 2

        if self.image:
            image = pygame.image.load(self.image).convert()

            r = image.get_rect()
            top += r.height // 2

            r.midbottom = center, top - 20

            screen.blit(image, r)

        antialias = 1
        black = 0, 0, 0


        for line in lines:
            text = font.render(line.strip(), antialias, black)
            r = text.get_rect()
            r.midtop = center, top
            screen.blit(text, r)
            top += font.get_linesize()

        pygame.display.update()


class Info(Paused):

    nextState = Level
    text = '''
    In this game you are a banana,
    trying to survive a course in
    self-defense against fruit,where the
    participants will 'defend' themselves
    against you with a 16 ton weight.'''


class StartUp(Paused):

    nextState = Info
    image = config.flowers_img
    text = '''
    Welcome to Squish.
    the game of Fruit Self-Defense'''


class LevelCleared(Paused):

    def __init__(self, number):
            self.number = number
            self.text = '''Level %i cleared
            Click to start next level''' % self.number

    def nextState(self):
            return Level(self.number + 1)


class GameOver(Paused):
    nextState = Level
    text = '''
    Game Over
    Click to Restart, Esc to Quit'''
