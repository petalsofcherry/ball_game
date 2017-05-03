import sys

import pygame
from pygame.locals import *

from game import config
from game.objects import RedBall, WhiteBall

class State(object):
    red_balls = []
    def handle(self, event):
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            red_ball_image = pygame.image.load(config.red_ball_img).convert_alpha()
            new_ball = RedBall(red_ball_image)
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

        white_ball_image = pygame.image.load(config.white_ball_img).convert_alpha()
        self.white_ball = WhiteBall(white_ball_image)
        self.sprites = pygame.sprite.RenderUpdates(self.red_balls + [self.white_ball])

    def update(self, game):
        time_passed_seconds = game.clock.tick() / 1000.
        self.sprites.update(time_passed_seconds)

        for red_ball in self.red_balls:
            if self.white_ball.touches(red_ball):
                game.nextState = GameOver()


        dead_red_balls = []
        for red_ball in self.red_balls:
            # 每个小球的的寿命是5秒
            if red_ball.age > 5:
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
    you are a ball,
    away from red ball'''


class StartUp(Paused):

    nextState = Info
    image = config.flowers_img
    text = '''
    Welcome to hell'''


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
