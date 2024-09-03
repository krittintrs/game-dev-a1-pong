from enum import Enum
import pygame, sys, random, math

from constant import *
from Ball import Ball
from Paddle import Paddle, WeakAIPaddle, StrongAIPaddle, StrongAIPaddleLeft, PaddleSize
from PowerUp import PowerUp, PowerUpType

PLAYER_1_BLINK_EVENT = pygame.USEREVENT + 1
PLAYER_2_BLINK_EVENT = pygame.USEREVENT + 2

class GameState(Enum):
    START = 'start'
    SERVE = 'serve'
    PLAY = 'play'
    DONE = 'done'

class Player(Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2
    
class AIType(Enum):
    WEAK = 'weak'
    STRONG = 'strong'

class GameMain:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.music_channel = pygame.mixer.Channel(0)
        self.music_channel.set_volume(0.2)
        
        self.sounds_list = {
            'paddle_hit': pygame.mixer.Sound('sounds/paddle_hit.wav'),
            'score': pygame.mixer.Sound('sounds/score.wav'),
            'wall_hit': pygame.mixer.Sound('sounds/wall_hit.wav'),
            'increase_paddle': pygame.mixer.Sound('sounds/increase_paddle.wav'),
            'decrease_paddle': pygame.mixer.Sound('sounds/decrease_paddle.wav'),
            'speed_boost': pygame.mixer.Sound('sounds/speed_boost.wav'),
            'split_ball': pygame.mixer.Sound('sounds/split_ball.wav'),
        }

        self.small_font = pygame.font.Font('./font.ttf', 24)
        self.large_font = pygame.font.Font('./font.ttf', 48)
        self.score_font = pygame.font.Font('./font.ttf', 96)

        self.player1_score = 0
        self.player2_score = 0

        self.serving_player = Player.PLAYER_1
        self.winning_player = 0
        self.last_hit_player = Player.PLAYER_1

        self.player1_color = (0, 255, 255)   # neon blue
        self.player2_color = (255, 20, 147)  # neon pink
        self.player1 = Paddle(self.screen, 30, 90, PADDLE_WIDTH, PaddleSize.MEDIUM, self.player1_color)
        # self.player1 = StrongAIPaddleLeft(self.screen, 30, 90, PADDLE_WIDTH, PaddleSize.MEDIUM, self.player1_color)

        self.weak_ai = WeakAIPaddle(self.screen, WIDTH - 30, HEIGHT - 90, PADDLE_WIDTH, PaddleSize.MEDIUM, self.player2_color)
        self.strong_ai = StrongAIPaddle(self.screen, WIDTH - 30, HEIGHT - 90, PADDLE_WIDTH, PaddleSize.MEDIUM, self.player2_color)
        
        self.current_ai_type = AIType.WEAK
        self.player2 = self.get_current_ai()

        ball = Ball('ball_1', self.screen, WIDTH/2 - 6, HEIGHT/2 - 6, BALL_SIZE, BALL_SIZE)
        self.balls = [ball]

        self.powerups = []
        self.game_state = GameState.START
    
        # Timer for generating power-ups/power-downs
        self.powerup_timer = 0

    def get_current_ai(self):
        if self.current_ai_type == AIType.WEAK:
            return self.weak_ai
        elif self.current_ai_type == AIType.STRONG:
            return self.strong_ai
        
    def update(self, dt, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.game_state == GameState.START:
                        self.game_state = GameState.SERVE
                    elif self.game_state == GameState.SERVE:
                        self.game_state = GameState.PLAY
                    elif self.game_state == GameState.DONE:
                        self.game_state = GameState.SERVE
                        self.reset_field()
                        self.reset_players_score()
                        if self.winning_player == Player.PLAYER_1:
                            self.serving_player = Player.PLAYER_2
                        else:
                            self.serving_player = Player.PLAYER_1
            
            if event.type == PLAYER_1_BLINK_EVENT:
                if self.blink_count < 4:
                    if self.blink_count % 2 == 0:
                        glow_color = (255, 255, 255)
                        inner_color = (255, 255, 255)
                    else:
                        glow_color = self.player1_color
                        inner_color = (0, 0, 0)

                    self.player1.glow_color = glow_color
                    self.player1.inner_color = inner_color

                    self.blink_count += 1
                else:
                    self.player1.glow_color = self.player1_color
                    self.player1.inner_color = (0, 0, 0)
                    pygame.time.set_timer(PLAYER_1_BLINK_EVENT, 0)  # Stop the timer

            if event.type == PLAYER_2_BLINK_EVENT:
                if self.blink_count < 4:
                    if self.blink_count % 2 == 0:
                        glow_color = (255, 255, 255)
                        inner_color = (255, 255, 255)
                    else:
                        glow_color = self.player2_color
                        inner_color = (0, 0, 0)

                    self.player2.glow_color = glow_color
                    self.player2.inner_color = inner_color

                    self.blink_count += 1
                else:
                    self.player2.glow_color = self.player2_color
                    self.player2.inner_color = (0, 0, 0)
                    pygame.time.set_timer(PLAYER_2_BLINK_EVENT, 0)  # Stop the timer

        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            self.player1.dy = -PADDLE_SPEED
        elif key[pygame.K_s]:
            self.player1.dy = PADDLE_SPEED
        else:
            self.player1.dy = 0       
        
        if self.game_state == GameState.SERVE:
            self.balls[0].dy = random.uniform(-150, 150)
            if self.serving_player == Player.PLAYER_1:
                self.balls[0].dx = random.uniform(420, 600)
            else:
                self.balls[0].dx = -random.uniform(420, 600)

        elif self.game_state == GameState.PLAY:
            self.check_collisions()
            self.update_powerups(dt)
            for ball in self.balls:
                ball.update(dt)

        self.player1.update(dt)
        # self.player1.update(dt, self.balls)
        self.player2.update(dt, self.balls)

    def render(self):
        self.screen.fill((40, 45, 52))

        if self.game_state == GameState.START:
            t_welcome = self.small_font.render("Welcome to Pong!", False, (255, 255, 255))
            text_rect = t_welcome.get_rect(center=(WIDTH / 2, 30))
            self.screen.blit(t_welcome, text_rect)

            t_press_enter_begin = self.small_font.render('Press Enter to begin!', False, (255, 255, 255))
            text_rect = t_press_enter_begin.get_rect(center=(WIDTH / 2, 60))
            self.screen.blit(t_press_enter_begin, text_rect)

        elif self.game_state == GameState.SERVE:
            t_ai_mode = self.small_font.render(f'{str(self.current_ai_type.value).upper()} AI Mode ({WINNING_SCORE} to Win)', False, (255, 255, 255))
            text_rect = t_ai_mode.get_rect(center=(WIDTH / 2, 30))
            self.screen.blit(t_ai_mode, text_rect)

            if self.serving_player == Player.PLAYER_1:
                serve = 'Player'
            elif self.serving_player == Player.PLAYER_2:
                serve = 'AI'
            t_serve = self.small_font.render(f'{serve}\'s serve!', False, (255, 255, 255))
            text_rect = t_serve.get_rect(center=(WIDTH / 2, 60))
            self.screen.blit(t_serve, text_rect)

            t_enter_serve = self.small_font.render("Press Enter to serve!", False, (255, 255, 255))
            text_rect = t_enter_serve.get_rect(center=(WIDTH / 2, 90))
            self.screen.blit(t_enter_serve, text_rect)

        elif self.game_state == GameState.DONE:
            if self.winning_player == Player.PLAYER_1:
                winner = 'Player'
            elif self.winning_player == Player.PLAYER_2:
                winner = 'AI'
            t_win = self.large_font.render(f'{winner} wins!', False, (255, 255, 255))
            text_rect = t_win.get_rect(center=(WIDTH / 2, 30))
            self.screen.blit(t_win, text_rect)

            t_restart = self.small_font.render("Press Enter to restart", False, (255, 255, 255))
            text_rect = t_restart.get_rect(center=(WIDTH / 2, 70))
            self.screen.blit(t_restart, text_rect)

        # render paddle
        self.player1.render()
        self.player2.render()

        # render ball
        for ball in self.balls:
            ball.render()

        # render power-ups
        for powerup in self.powerups:
            powerup.render()

        # render score    
        self.DisplayScore()

    def reset_field(self):
        self.reset_balls_list()
        self.reset_players()
        self.powerups = []

    def reset_balls_list(self):
        ball = Ball('ball_1', self.screen, WIDTH/2 - 6, HEIGHT/2 - 6, BALL_SIZE, BALL_SIZE)
        self.balls = [ball]
        self.balls[0].Reset()
    
    def reset_players(self):
        self.player1.Reset() 
        self.player2.Reset() 
        
    def reset_players_score(self):
        self.player1_score = 0
        self.player2_score = 0

    def check_collisions(self):
        for ball in self.balls:
            # ball hit player 1 paddle
            if ball.Collides(self.player1):
                ball.dx = -ball.dx * 1.03
                ball.rect.x = self.player1.rect.x + 15

                if ball.dy < 0:
                    ball.dy = -random.uniform(30, 450)
                else:
                    ball.dy = random.uniform(30, 450)

                self.music_channel.play(self.sounds_list['paddle_hit'])
                self.last_hit_player = Player.PLAYER_1

            # ball hit player 2 paddle
            if ball.Collides(self.player2):
                ball.dx = -ball.dx * 1.03
                ball.rect.x = self.player2.rect.x - BALL_SIZE
                if ball.dy < 0:
                    ball.dy = -random.uniform(30, 450)
                else:
                    ball.dy = random.uniform(30, 450)

                self.music_channel.play(self.sounds_list['paddle_hit'])
                self.last_hit_player = Player.PLAYER_2

            # ball hit top wall
            if ball.rect.y <= 0:
                ball.rect.y = 0
                ball.dy = -ball.dy
                self.music_channel.play(self.sounds_list['wall_hit'])

            # ball hit bottom wall
            if ball.rect.y >= HEIGHT - BALL_SIZE:
                ball.rect.y = HEIGHT - BALL_SIZE
                ball.dy = -ball.dy
                self.music_channel.play(self.sounds_list['wall_hit'])

            # ball hit player 1 goal
            if ball.rect.x < 0:
                self.serving_player = Player.PLAYER_1
                self.player2_score += 1
                self.music_channel.play(self.sounds_list['score'])
                if self.player2_score == WINNING_SCORE:
                    # player lose to AI
                    self.winning_player = Player.PLAYER_2
                    self.game_state = GameState.DONE
                    # change to weak AI
                    self.current_ai_type = AIType.WEAK
                    self.player2 = self.get_current_ai()
                elif len(self.balls) > 1:
                    self.balls.remove(ball)
                    continue
                else:
                    self.reset_field()
                    self.game_state = GameState.SERVE
            
            # ball hit player 2 goal
            if ball.rect.x > WIDTH:
                self.serving_player = Player.PLAYER_2
                self.player1_score += 1
                self.music_channel.play(self.sounds_list['score'])
                if self.player1_score == WINNING_SCORE:
                    # player win against AI
                    self.winning_player = Player.PLAYER_1
                    self.game_state = GameState.DONE
                    # if win against weak AI, change to strong AI
                    if self.current_ai_type == AIType.WEAK:
                        self.current_ai_type = AIType.STRONG
                    else:
                        self.current_ai_type = AIType.WEAK
                    self.player2 = self.get_current_ai()
                elif len(self.balls) > 1:
                    self.balls.remove(ball)
                    continue
                else:
                    self.reset_field()  
                    self.game_state = GameState.SERVE  

            # ball hit powerups
            for powerup in self.powerups:
                if powerup.active and ball.rect.colliderect(powerup.rect):
                    # self.apply_powerup(powerup)
                    if self.last_hit_player == Player.PLAYER_1:
                        self.apply_powerup(powerup, self.player1, ball)
                    elif self.last_hit_player == Player.PLAYER_2:
                        self.apply_powerup(powerup, self.player2, ball)
                    powerup.active = False

    def update_powerups(self, dt):
        self.powerup_timer += dt
        if self.powerup_timer > random.uniform(5, 15):  
            self.spawn_powerup()
            self.powerup_timer = 0

        # for powerup in self.powerups:
        #     powerup.update(dt)

    def spawn_powerup(self):
        max_attempts = 100  # Set a limit to avoid infinite loops
        attempt = 0
        
        while attempt < max_attempts:
            x = random.randint(POWERUPS_SIZE, WIDTH - POWERUPS_SIZE)
            y = random.randint(POWERUPS_SIZE, HEIGHT - POWERUPS_SIZE)
            
            new_rect = pygame.Rect(x, y, POWERUPS_SIZE, POWERUPS_SIZE)
            
            # Check for collision with existing power-ups
            collision = any(new_rect.colliderect(powerup.rect) for powerup in self.powerups)
            
            if not collision:
                self.powerups.append(PowerUp(self.screen, x, y, POWERUPS_SIZE, POWERUPS_SIZE))
                break  # Exit the loop once a valid position is found
            
            attempt += 1
        
        if attempt == max_attempts:
            print("Warning: Could not find a non-colliding position for the power-up.")

    def apply_powerup(self, powerup: PowerUp, player, ball: Ball):
        # Paddle Size
        current_size = PaddleSize(player.rect.height)
        if powerup.effect == PowerUpType.INCREASE_PADDLE:
            self.music_channel.play(self.sounds_list['increase_paddle'])
            if current_size != PaddleSize.LARGE:
                new_size = PaddleSize(min(current_size.value + 40, PaddleSize.LARGE.value))
                player.rect.height = new_size.value
            self.blink_count = 0
            if player == self.player1:
                pygame.time.set_timer(PLAYER_1_BLINK_EVENT, POWERUPS_TIMER) 
            elif player == self.player2:
                pygame.time.set_timer(PLAYER_2_BLINK_EVENT, POWERUPS_TIMER) 

        elif powerup.effect == PowerUpType.DECREASE_PADDLE:
            self.music_channel.play(self.sounds_list['decrease_paddle'])
            if current_size != PaddleSize.SMALL:
                new_size = PaddleSize(max(current_size.value - 40, PaddleSize.SMALL.value))
                player.rect.height = new_size.value
            self.blink_count = 0
            if player == self.player1:
                pygame.time.set_timer(PLAYER_1_BLINK_EVENT, POWERUPS_TIMER) 
            elif player == self.player2:
                pygame.time.set_timer(PLAYER_2_BLINK_EVENT, POWERUPS_TIMER)

        # Ball Speed
        elif powerup.effect == PowerUpType.SPEED_BOOST:
            self.music_channel.play(self.sounds_list['speed_boost'])
            ball.dx *= SPEED_BOOST_VALUE
            ball.dy *= SPEED_BOOST_VALUE
            ball.color = (255, 0, 0)  # red
            ball.toggle_speed_boost(True)

        # Split Ball
        elif powerup.effect == PowerUpType.SPLIT_BALL:
            self.music_channel.play(self.sounds_list['split_ball'])
            # Spawn a new ball moving in the opposite direction
            original_ball = ball  # The original ball
            new_ball_dx = -original_ball.dx  # Opposite direction
            new_ball_dy = -original_ball.dy  # Opposite direction
            
            # Create and add the new ball
            ball_num = len(self.balls) + 1
            new_ball = Ball('ball_' + str(ball_num), self.screen, original_ball.rect.x, original_ball.rect.y, BALL_SIZE, BALL_SIZE)
            new_ball.dx = new_ball_dx
            new_ball.dy = new_ball_dy
            new_ball.color = (255, 255, 255)

            self.balls.append(new_ball)

    def DisplayScore(self):
        self.t_p1_score = self.score_font.render(str(self.player1_score), False, (255, 255, 255))
        self.t_p2_score = self.score_font.render(str(self.player2_score), False, (255, 255, 255))
        self.screen.blit(self.t_p1_score, (WIDTH/2 - 150, HEIGHT/3))
        self.screen.blit(self.t_p2_score, (WIDTH / 2 + 120, HEIGHT / 3))

if __name__ == '__main__':
    clock = pygame.time.Clock()
    game = GameMain()

    while True:
        dt = clock.tick(60) / 1000
        events = pygame.event.get()
        game.update(dt, events)
        game.render()
        pygame.display.update()
