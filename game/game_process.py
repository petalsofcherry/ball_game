from math import sin, cos, pi

import pygame
from pygame.locals import *

from game import config
from game.states import StartUp
from game.vector2 import Vector2


class Game(object):
    def __init__(self):
        self.state = None
        self.nextState = StartUp()

    @classmethod
    def run(cls):
        pygame.mixer.pre_init(44100, 16, 2, 1024 * 4)
        pygame.init()
        pygame.mixer.set_num_channels(8)
        screen = pygame.display.set_mode(config.SCREEN_SIZE, 0, 32)
        screen.fill((0, 0, 0))

        sprite = pygame.image.load(config.ball_img).convert_alpha()

        clock = pygame.time.Clock()

        bounce_sound = pygame.mixer.Sound(config.collision_voice)

        # 让pygame完全控制鼠标
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        sprite_pos = Vector2(200, 150)

        balls = []

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
                    # 按Esc则退出游戏
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        exit()
                if event.type == MOUSEBUTTONDOWN:
                    # 刚刚出来的小球，给一个随机的速度
                    random_speed = (randint(-400, 400), randint(-300, 0))
                    new_ball = RedBall(event.pos,
                                       random_speed,
                                        ball_image,
                                        bounce_sound)
                    balls.append(new_ball)

            # 这里获取按键情况
            pressed_keys = pygame.key.get_pressed()

            rotation_direction = 0.
            movement_direction = 0.

            # 通过移动偏移量计算转动
            rotation_direction = pygame.mouse.get_rel()[0] / 5.0

            if pressed_keys[K_LEFT]:
                rotation_direction = +1.
            if pressed_keys[K_RIGHT]:
                rotation_direction = -1.
            if pressed_keys[K_UP]:
                movement_direction = +1.
            if pressed_keys[K_DOWN]:
                movement_direction = -1.

            rotated_sprite = pygame.transform.rotate(sprite, config.sprite_rotation)
            w, h = rotated_sprite.get_size()
            sprite_draw_pos = Vector2(sprite_pos.x - w / 2, sprite_pos.y - h / 2)
            screen.blit(rotated_sprite, sprite_draw_pos)

            time_passed = clock.tick()
            time_passed_seconds = time_passed / 1000.0
            dead_balls = []
            for ball in balls:
                ball.update(time_passed_seconds)
                ball.render(screen)
                # 每个红球的的寿命是10秒
                if ball.age > 10.0:
                    dead_balls.append(ball)
            for ball in dead_balls:
                balls.remove(ball)

            config.sprite_rotation += rotation_direction * config.sprite_rotation_speed * time_passed_seconds

            heading_x = sin(config.sprite_rotation * pi / 180.)
            heading_y = cos(config.sprite_rotation * pi / 180.)
            heading = Vector2(heading_x, heading_y)
            heading *= movement_direction

            sprite_pos += heading * config.sprite_speed * time_passed_seconds

            pygame.display.update()
