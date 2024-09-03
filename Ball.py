import pygame, random
from constant import *

class Ball:
    def __init__(self, name, screen, x, y, width, height):
        self.name = name
        self.screen = screen

        self.rect = pygame.Rect(x, y, width, height)

        self.dx = random.choice([-300, 300])
        self.dy = random.randint(-150, 150)

        self.color = (255, 255, 255)

        self.is_boosted = False  # Flag to indicate if the ball is blinking
        self.speed_boost_timer = 0   # Timer to handle blink duration

    def Collides(self, paddle):
        # first, check to see if the left edge of either is further to the right
        # than the right edge of the other
        if self.rect.x > paddle.rect.x + paddle.rect.width or paddle.rect.x > self.rect.x + self.rect.width:
            return False
        # then check to see if the bottom edge of either is higher than the top
        # edge of the other
        if self.rect.y > paddle.rect.y + paddle.rect.height or paddle.rect.y > self.rect.y + self.rect.height:
            return False
        return True

    def Reset(self):
        self.rect.x = WIDTH / 2 - 6
        self.rect.y = HEIGHT / 2 - 6
        self.dx = 0
        self.dy = 0
        self.color = (255, 255, 255)
        self.is_boosted = False  
        self.speed_boost_timer = 0
    
    def toggle_speed_boost(self, status):
        self.is_boosted = status
        self.speed_boost_timer = pygame.time.get_ticks() if status else 0

    def update(self, dt):
        self.rect.x += self.dx*dt
        self.rect.y += self.dy*dt

        if self.is_boosted:
            current_time = pygame.time.get_ticks()
            if current_time - self.speed_boost_timer > SPEED_BOOST_TIMER:  
                self.is_boosted = False  # Stop boosting
                self.color = (255, 255, 255)  # Default color
                self.dx = self.dx / SPEED_BOOST_VALUE
                self.dy = self.dy / SPEED_BOOST_VALUE
                self.ball_speed_boost_active = False
            else:
                self.color = (255, 255, 255) if (current_time // 250) % 2 == 0 else (255, 0, 0)
 

    def render(self):
        pygame.draw.rect(self.screen, self.color, self.rect, border_radius=5)
