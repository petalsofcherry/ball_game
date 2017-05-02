import sys
from random import randint
from math import sin, cos, pi

import pygame
from pygame.locals import *

from game import config
from game.objects import RedBall, WhiteBall
from game.vector2 import Vector2


class State(object):
    def handle(self, event):
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            red_ball_image = pygame.image.load(config.red_ball_img).convert_alpha()
            new_ball = RedBall(event.pos,
                            red_ball_image)
            self.red_balls.append(new_ball)

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

        self.white_ball = WhiteBall()
        all_balls = self.red_balls + [self.white_ball]
        self.sprites = pygame.sprite.RenderUpdates(all_balls)

    def update(self, game):
        self.sprites.update()

        if self.white_ball.touches(self.red_ball):
            game.nextState = GameOver()

        elif self.weight.landed:
            self.weight.reset()
            self.remaining -= 1
            if self.remaining == 0:
                game.nextState = LevelCleared(self.number)

        time_passed_seconds = game.clock.tick() / 1000.
        dead_red_balls = []
        for red_ball in self.red_balls:
            red_ball.update(time_passed_seconds)
            # 每个小球的的寿命是10秒
            if red_ball.age > 10.0:
                dead_red_balls.append(red_ball)
        for red_ball in dead_red_balls:
            self.red_balls.remove(red_ball)

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
