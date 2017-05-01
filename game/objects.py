from game import config
from game.vector2 import Vector2
import pygame.sprite.Sprite


class Voice(object):
    @classmethod
    def get_voice(cls, x_coord, screen_width):
        """这个函数根据位置决定要播放声音左右声道的音量"""
        right_volume = float(x_coord) / screen_width
        left_volume = 1.0 - right_volume
        return (left_volume, right_volume)


class Ball(pygame.sprite.Sprite):
    def __init__(self, position, speed, image, bounce_sound):
        super(Ball, self).__init__()
        self.position = Vector2(position)
        self.speed = Vector2(speed)
        self.image = image
        self.bounce_sound = bounce_sound
        self.age = 0.0

    def update(self, time_passed):
        w, h = self.image.get_size()
        screen_width, screen_height = config.SCREEN_SIZE

        x, y = self.position.x, self.position.y
        x -= w / 2
        y -= h / 2
        # 是不是要反弹了
        bounce = False

        # 小球碰壁了么？
        if y + h >= screen_height:
            self.speed.y = -self.speed.y * config.BOUNCINESS
            self.position.y = screen_height - h / 2.0 - 1.0
            bounce = True
        if x <= 0:
            self.speed.x = -self.speed.x * config.BOUNCINESS
            self.position.x = w / 2.0 + 1
            bounce = True
        elif x + w >= screen_width:
            self.speed.x = -self.speed.x * config.BOUNCINESS
            self.position.x = screen_width - w / 2.0 - 1
            bounce = True

        # 根据时间计算现在的位置，物理好的立刻发现这其实不标准，
        # 正规的应该是“s = 1/2*g*t*t”，不过这样省事省时一点，咱只是模拟~
        self.position += self.speed * time_passed
        # 根据重力计算速度
        self.speed.y += time_passed * config.GRAVITY

        if bounce:
            self.play_bounce_sound()

        self.age += time_passed

    def play_bounce_sound(self):
        """这个就是播放声音的函数"""
        channel = self.bounce_sound.play()

        if channel is not None:
            # 设置左右声道的音量
            left, right = Voice.get_voice(self.position.x, config.SCREEN_SIZE[0])
            channel.set_volume(left, right)

    def render(self, surface):
        w, h = self.image.get_size()
        x, y = self.position
        x -= w / 2
        y -= h / 2
        surface.blit(self.image, (x, y))


class WhiteBall(Ball):
    pass


class RedBall(Ball):
    pass
