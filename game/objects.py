from game import config
from game.vector2 import Vector2
from random import uniform, choice, randrange
import pygame


class Voice(object):
    @classmethod
    def get_voice(cls, x_coord):
        """这个函数根据位置决定要播放声音左右声道的音量"""
        right_volume = float(x_coord) / config.SCREEN_SIZE[0]
        left_volume = 1.0 - right_volume
        return (left_volume, right_volume)


class Ball(pygame.sprite.Sprite):
    def __init__(self, image):
        super(Ball, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        shrink = -config.margin * 2
        self.area = screen.get_rect().inflate(shrink, shrink)
        self.age = 0.0


class RedBall(Ball):
    def __init__(self, image):
        super(RedBall, self).__init__(image)
        pygame.mixer.pre_init(44100, 16, 2, 1024 * 4)
        pygame.mixer.set_num_channels(8)
        self.bounce_sound = pygame.mixer.Sound(config.collision_voice)

        self.reset()

    def reset(self):
        self.position = choice([Vector2(randrange(0, config.SCREEN_SIZE[0]), 0),
                               Vector2(0, randrange(0, config.SCREEN_SIZE[1])),
                               Vector2(800, randrange(0, config.SCREEN_SIZE[1])),
                               Vector2(randrange(0, config.SCREEN_SIZE[0]), 600)])
        if self.position.y == 0:
            self.speed = Vector2(uniform(-250, 250), uniform(0, 250))
        elif self.position.y == 600:
            self.speed = Vector2(uniform(-250, 250), uniform(-250, 0))
        elif self.position.x == 0:
            self.speed = Vector2(uniform(0, 250), uniform(-250, 250))
        elif self.position.x == 800:
            self.speed = Vector2(uniform(-250, 0), uniform(-250, 250))

        self.rect.centerx, self.rect.centery = self.position.x, self.position.y

    def update(self, time_passed):
        self.position += self.speed * time_passed

        self.rect.centerx, self.rect.centery = self.position.x, self.position.y

        w, h = self.image.get_size()
        screen_width, screen_height = config.SCREEN_SIZE

        x, y = self.position.x, self.position.y
        # 是不是要反弹了
        bounce = False

        # 小球碰壁了么？
        if y + h/2 >= screen_height:
            self.speed.y = -self.speed.y * config.BOUNCINESS
            self.position.y = screen_height - h / 2.0 - 1.0
            bounce = True
        elif y - h/2 <= 0:
            self.speed.y = -self.speed.y * config.BOUNCINESS
            self.position.y = h / 2.0 + 1
            bounce = True
        elif x - w/2 <= 0:
            self.speed.x = -self.speed.x * config.BOUNCINESS
            self.position.x = w / 2.0 + 1
            bounce = True
        elif x + w/2 >= screen_width:
            self.speed.x = -self.speed.x * config.BOUNCINESS
            self.position.x = screen_width - w / 2.0 - 1
            bounce = True

        if bounce:
            self.play_bounce_sound()

        self.age += time_passed

    def play_bounce_sound(self):
        """这个就是播放声音的函数"""
        channel = self.bounce_sound.play()

        if channel is not None:
            # 设置左右声道的音量
            left, right = Voice.get_voice(self.position.x)
            channel.set_volume(left, right)


class WhiteBall(Ball):
    def __init__(self, image):
        super(WhiteBall, self).__init__(image)
        self.rect.bottom = self.area.bottom

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect.centery = pygame.mouse.get_pos()[1]
        self.rect = self.rect.clamp(self.area)

    def touches(self, other):
        return self.rect.colliderect(other.rect)
