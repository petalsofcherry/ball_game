import pygame
from pygame.locals import *

from game import config
from game.states import StartUp


class Game(object):
    def __init__(self):
        self.state = None
        self.nextState = StartUp()

    def run(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        # 让pygame完全控制鼠标
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        flag = 0

        if config.full_screen:
            flag = FULLSCREEN
        screen_size = config.SCREEN_SIZE
        screen = pygame.display.set_mode(screen_size, 0, 32)

        while True:
            if self.state != self.nextState:
                self.state = self.nextState
                self.state.firstDisplay(screen)

            for event in pygame.event.get():
                self.state.handle(event)
            self.state.update(self)

            self.state.display(screen)

if __name__ == '__main__':
    game = Game()
    game.run()
