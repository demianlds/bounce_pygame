import pygame
import random
import sys

'''
Deadly Bounce is a two‑player arcade game
where each player controls a paddle on their side of the screen. 
Your goal is to keep the green balls bouncing back to your opponent while avoiding 
the red balls—each red hit costs you 1 HP.
The first player to lose all 3 HP loses the match.

'''

# Initialization
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deadly Bounce")
clock = pygame.time.Clock()
FPS = 60

# Colors
BACKGROUND = (115,23,23)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fonts
font = pygame.font.SysFont("Arial", 32)
big_font = pygame.font.SysFont("Arial", 48)

# Game Settings
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SIZE = 20
BALL_SPEED = 3
COLOR_CHANGE_INTERVAL = 300


class Paddle:
    def __init__(self, x, keys):
        self.rect = pygame.Rect(x, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.up_key, self.down_key = keys
        self.hp = 3
        self.immunity_timer = 0  # Tiempo restante de inmunidad (en frames)

    def move(self, keys_pressed):
        if keys_pressed[self.up_key] and self.rect.top > 0:
            self.rect.y -= 6
        if keys_pressed[self.down_key] and self.rect.bottom < HEIGHT:
            self.rect.y += 6

        # Reducir el timer de inmunidad si está activo
        if self.immunity_timer > 0:
            self.immunity_timer -= 1

    def take_damage(self):
        if self.immunity_timer <= 0:
            # Reducir tamaño un tercio
            new_height = max(self.rect.height - PADDLE_HEIGHT // 3, 10)  # Evitar tamaño 0 o negativo, mínimo 10 px
            # Ajustar posición para que la barra no se "caiga"
            self.rect.y += (self.rect.height - new_height) // 2
            self.rect.height = new_height

            # Reducir hp
            self.hp -= 1

            # Activar inmunidad (1 segundo -> FPS = 60, entonces 60 frames)
            self.immunity_timer = FPS

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)



class Ball:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(200, 600), random.randint(100, 500), BALL_SIZE, BALL_SIZE)
        self.vel_x = random.choice([-BALL_SPEED, BALL_SPEED])
        self.vel_y = random.choice([-BALL_SPEED, BALL_SPEED])
        self.color = RED
        self.color_timer = 0
        self.has_hit_left = False
        self.has_hit_right = False

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vel_y *= -1

        self.color_timer += 1
        if self.color_timer >= COLOR_CHANGE_INTERVAL:
            self.color = GREEN if self.color == RED else RED
            self.color_timer = 0

    def draw(self):
        pygame.draw.ellipse(screen, self.color, self.rect)

    def time_until_color_change(self):
        return (COLOR_CHANGE_INTERVAL - self.color_timer) // FPS


def draw_text(text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y)) if center else text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)
    return text_rect


def main_menu():
    while True:
        screen.fill(BACKGROUND)
        draw_text("Deadly Bounce", big_font, WHITE, WIDTH // 2, HEIGHT // 3)

        play_button = draw_text("Play", font, GREEN, WIDTH // 2, HEIGHT // 2)
        quit_button = draw_text("Quit", font, RED, WIDTH // 2, HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(winner):
    while True:
        screen.fill(BACKGROUND)
        draw_text(f"{winner} wins!", big_font, WHITE, WIDTH // 2, HEIGHT // 3)

        play_again_btn = draw_text("Play Again", font, GREEN, WIDTH // 2, HEIGHT // 2)
        quit_btn = draw_text("Quit", font, RED, WIDTH // 2, HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_btn.collidepoint(event.pos):
                    return
                if quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)


def game_loop():
    left_paddle = Paddle(30, (pygame.K_w, pygame.K_s))
    right_paddle = Paddle(WIDTH - 50, (pygame.K_UP, pygame.K_DOWN))

    balls = [Ball(), Ball()]
    run = True

    while run:
        screen.fill(BACKGROUND)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Move and update paddles
        left_paddle.move(keys)
        right_paddle.move(keys)
        left_paddle.move(keys)
        right_paddle.move(keys)

        for ball in balls:
            ball.update()

        # Left paddle collision
        if ball.rect.colliderect(left_paddle.rect):
            if not ball.has_hit_left:
                if ball.color == RED:
                    left_paddle.take_damage()
                else:
                    ball.vel_x *= -1
                ball.has_hit_left = True
        else:
            ball.has_hit_left = False

        # Right paddle collision
        if ball.rect.colliderect(right_paddle.rect):
            if not ball.has_hit_right:
                if ball.color == RED:
                    right_paddle.take_damage()
                else:
                    ball.vel_x *= -1
                ball.has_hit_right = True
        else:
            ball.has_hit_right = False

            # Bounce off sides
            if ball.rect.left <= 0 or ball.rect.right >= WIDTH:
                ball.vel_x *= -1

            ball.draw()

        # Draw paddles and HP
        left_paddle.draw()
        right_paddle.draw()
        draw_text(f"P1: {left_paddle.hp}", font, WHITE, 80, 20, center=False)
        draw_text(f"P2: {right_paddle.hp}", font, WHITE, WIDTH - 160, 20, center=False)

        # Timer
        timer_text = f"Color change in: {min([ball.time_until_color_change() for ball in balls])}s"
        draw_text(timer_text, font, WHITE, WIDTH // 2, 30)

        # Game over condition
        if left_paddle.hp <= 0:
            return game_over_screen("Player 2")
        if right_paddle.hp <= 0:
            return game_over_screen("Player 1")

        pygame.display.flip()
        clock.tick(FPS)


# Start
while True:
    main_menu()
    game_loop()
