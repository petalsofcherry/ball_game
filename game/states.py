import os
import sys
import time

import pygame
from pygame.locals import *

from game import config
from game.objects import RedBall, WhiteBall


class State(object):
    def handle(self, event):
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()

    def firstDisplay(self, screen):
        screen.fill(config.background_color)
        pygame.display.flip()

    def display(self, screen):
        pass


class Level(State):
    def __init__(self, number=1):
        self.number = number
        self.remaining = config.ball_level
        self.red_ball_image = pygame.image.load(config.red_ball_img).convert_alpha()

        speed = config.red_ball_speed

        speed += (self.number - 1) * config.speed_increase

        white_ball_image = pygame.image.load(config.white_ball_img).convert_alpha()
        self.white_ball = WhiteBall(white_ball_image)
        self.red_sprites = pygame.sprite.RenderUpdates()
        self.white_sprites = pygame.sprite.RenderUpdates(self.white_ball)
        self.gap = 0
        self.count = 0

    def update(self, game):
        if self.count == 10:
            game.nextState = LevelCleared(self.number)

        for a_red_ball in self.red_sprites:
            for another_red_ball in self.red_sprites:
                if a_red_ball is not another_red_ball and a_red_ball.touches(another_red_ball) and \
                        not (a_red_ball.be_bounce and another_red_ball.be_bounce):
                    a_red_ball.speed = a_red_ball.speed * (-1)
                    another_red_ball.speed = another_red_ball.speed * (-1)
                    a_red_ball.be_bounce = True
                    another_red_ball.be_bounce = True
                    a_red_ball.play_bounce_sound()

        for red_ball in self.red_sprites:
            red_ball.be_bounce = False

        time_passed_seconds = game.clock.tick() / 1000.
        self.gap += time_passed_seconds
        if int(self.gap) == 2:
            new_ball = RedBall(self.red_ball_image)
            now_sprite = pygame.sprite.RenderUpdates(new_ball)
            self.red_sprites.add(now_sprite)
            self.gap = 0
            self.count += 1

        self.red_sprites.update(time_passed_seconds)
        self.white_sprites.update()

        for red_ball in self.red_sprites:
            if self.white_ball.touches(red_ball):
                game.nextState = GameOver()

        dead_red_balls = []
        for red_ball in self.red_sprites:
            if red_ball.age > 5:
                dead_red_balls.append(red_ball)
        for red_ball in dead_red_balls:
            self.red_sprites.remove(red_ball)

    def display(self, screen):
        screen.fill(config.background_color)
        updates = self.red_sprites.draw(screen) + self.white_sprites.draw(screen)
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
