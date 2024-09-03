import pygame
import random
from enum import Enum, auto

class PowerUpType(Enum):
    INCREASE_PADDLE = auto()
    DECREASE_PADDLE = auto()
    SPEED_BOOST = auto()
    SPLIT_BALL = auto()

# Load images for power-ups (assuming the images are located in a 'images' directory)
POWERUP_IMAGES = {
    PowerUpType.INCREASE_PADDLE: pygame.image.load('images/increase_paddle.png'),
    PowerUpType.DECREASE_PADDLE: pygame.image.load('images/decrease_paddle.png'),
    PowerUpType.SPEED_BOOST: pygame.image.load('images/speed_boost.png'),
    PowerUpType.SPLIT_BALL: pygame.image.load('images/split_ball.png')
}

class PowerUp:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.effect = random.choice(list(PowerUpType))
        self.image = POWERUP_IMAGES[self.effect]
        self.image = pygame.transform.scale(self.image, (width, height))
        self.active = True

    def render(self):
        if self.active:
            self.screen.blit(self.image, self.rect.topleft)

    def update(self, dt):
        pass  # Power-ups can move or have animations if needed
