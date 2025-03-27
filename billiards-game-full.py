import pygame
import sys
import math
import random
from pygame import gfxdraw
import numpy as np

# Stałe
WIDTH, HEIGHT = 1200, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
MAROON = (128, 0, 0)
DARK_GREEN = (0, 50, 0)
GRAY = (200, 200, 200)
LIGHT_BROWN = (210, 180, 140)

TABLE_WIDTH = 1000
TABLE_HEIGHT = 500
TABLE_X = (WIDTH - TABLE_WIDTH) // 2
TABLE_Y = (HEIGHT - TABLE_HEIGHT) // 2
POCKET_RADIUS = 25
CUSHION_WIDTH = 20

BALL_RADIUS = 15
MAX_VELOCITY = 15
FRICTION = 0.98

# Pozycje łuz
pockets = [
    (TABLE_X + CUSHION_WIDTH, TABLE_Y + CUSHION_WIDTH),
    (TABLE_X + TABLE_WIDTH // 2, TABLE_Y + CUSHION_WIDTH // 2),
    (TABLE_X - CUSHION_WIDTH + TABLE_WIDTH, TABLE_Y + CUSHION_WIDTH),
    (TABLE_X + CUSHION_WIDTH, TABLE_Y + TABLE_HEIGHT - CUSHION_WIDTH),
    (TABLE_X + TABLE_WIDTH // 2, TABLE_Y + TABLE_HEIGHT - CUSHION_WIDTH // 2),
    (TABLE_X - CUSHION_WIDTH + TABLE_WIDTH, TABLE_Y - CUSHION_WIDTH + TABLE_HEIGHT)
]

class Ball:
    def __init__(self, x, y, color, number=0):
        self.x = x
        self.y = y
        self.color = color
        self.number = number
        self.radius = BALL_RADIUS
        self.vx = 0
        self.vy = 0
        self.active = True
        self.mass = 1.0

    def update(self):
        if not self.active:
            return

        # Apply friction
        self.vx *= FRICTION
        self.vy *= FRICTION

        # Przyciąganie do dołka
        for pocket_x, pocket_y in pockets:
            distance = math.sqrt((self.x - pocket_x)**2 + (self.y - pocket_y)**2)
            if distance < POCKET_RADIUS * 1.5:
                pull_strength = (POCKET_RADIUS * 1.5 - distance) / (POCKET_RADIUS * 1.5) * 0.5
                self.vx += (pocket_x - self.x) * pull_strength
                self.vy += (pocket_y - self.y) * pull_strength

        # Stop if velocity is very small
        if abs(self.vx) < 0.1 and abs(self.vy) < 0.1:
            self.vx = 0
            self.vy = 0

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Check collisions with cushions
        self.check_cushion_collision()

    def check_cushion_collision(self):
        if self.x - self.radius < TABLE_X + CUSHION_WIDTH:
            self.x = TABLE_X + CUSHION_WIDTH + self.radius
            self.vx = -self.vx * 0.9
        elif self.x + self.radius > TABLE_X + TABLE_WIDTH - CUSHION_WIDTH:
            self.x = TABLE_X + TABLE_WIDTH - CUSHION_WIDTH - self.radius
            self.vx = -self.vx * 0.9
        if self.y - self.radius < TABLE_Y + CUSHION_WIDTH:
            self.y = TABLE_Y + CUSHION_WIDTH + self.radius
            self.vy = -self.vy * 0.9
        elif self.y + self.radius > TABLE_Y + TABLE_HEIGHT - CUSHION_WIDTH:
            self.y = TABLE_Y + TABLE_HEIGHT - CUSHION_WIDTH - self.radius
            self.vy = -self.vy * 0.9

    def check_pocket_collision(self):
        if not self.active:
            return False

        for pocket_x, pocket_y in pockets:
            distance = math.sqrt((self.x - pocket_x)**2 + (self.y - pocket_y)**2)
            if distance < POCKET_RADIUS + self.radius * 0.5:
                self.active = False
                POCKET_SOUND.play()
                return True
        return False

    def draw(self, screen):
        if not self.active:
            return

        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius, self.color)
        pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius, BLACK)

        if self.number > 0:
            font = pygame.font.SysFont('Arial', 12)
            text = font.render(str(self.number), True, WHITE if self.color != YELLOW else BLACK)
            text_rect = text.get_rect(center=(self.x, self.y))
            pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), 8, WHITE)
            screen.blit(text, text_rect)

    def is_moving(self):
        return abs(self.vx) > 0.1 or abs(self.vy) > 0.1

class Cue:
    def __init__(self, ball):
        self.ball = ball
        self.angle = 0
        self.power = 0
        self.max_power = 20
        self.charging = False
        self.length = 200

    def update(self, mouse_pos):
        if self.charging or (self.ball.active and not self.ball.is_moving()):
            dx = mouse_pos[0] - self.ball.x
            dy = mouse_pos[1] - self.ball.y
            self.angle = math.atan2(dy, dx)

    def start_charging(self):
        if self.ball.active and not self.ball.is_moving():
            self.charging = True
            self.power = 0

    def continue_charging(self):
        if self.charging:
            self.power = min(self.power + 0.5, self.max_power)

    def strike(self):
        if self.charging and self.ball.active:
            self.ball.vx = -math.cos(self.angle) * self.power
            self.ball.vy = -math.sin(self.angle) * self.power
            self.charging = False
            self.power = 0

    def draw(self, screen):
        if not self.ball.active or self.ball.is_moving():
            return

        # Draw cue stick
        end_x = self.ball.x + math.cos(self.angle) * 50
        end_y = self.ball.y + math.sin(self.angle) * 50
        pygame.draw.line(screen, BLACK, (self.ball.x, self.ball.y), (end_x, end_y), 1)

        if self.charging:
            cue_end_x = self.ball.x - math.cos(self.angle) * (self.length + self.power * 5)
            cue_end_y = self.ball.y - math.sin(self.angle) * (self.length + self.power * 5)
            pygame.draw.line(screen, LIGHT_BROWN,
                            (self.ball.x - math.cos(self.angle) * 20,
                             self.ball.y - math.sin(self.angle) * 20),
                            (cue_end_x, cue_end_y), 6)
            pygame.draw.line(screen, BLACK,
                            (self.ball.x - math.cos(self.angle) * 20,
                             self.ball.y - math.sin(self.angle) * 20),
                            (cue_end_x, cue_end_y), 2)

            power_width = 100
            pygame.draw.rect(screen, BLACK, (WIDTH // 2 - power_width // 2, HEIGHT - 30, power_width, 10), 1)
            pygame.draw.rect(screen, RED, (WIDTH // 2 - power_width // 2, HEIGHT - 30,
                                         power_width * (self.power / self.max_power), 10))

    def draw_trajectory(self, screen, balls):
        if not self.charging or not self.ball.active or self.ball.is_moving():
            return

        # Simulate cue ball trajectory
        sim_ball = Ball(self.ball.x, self.ball.y, WHITE)
        sim_ball.vx = -math.cos(self.angle) * self.power
        sim_ball.vy = -math.sin(self.angle) * self.power

        points = []
        steps = 50
        collision_point = None
        collision_ball = None

        for _ in range(steps):
            sim_ball.update()
            points.append((int(sim_ball.x), int(sim_ball.y)))

            # Check for collisions
            for ball in balls:
                if ball != self.ball and ball.active:
                    dx = ball.x - sim_ball.x
                    dy = ball.y - sim_ball.y
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance < sim_ball.radius + ball.radius:
                        collision_point = (int(sim_ball.x), int(sim_ball.y))
                        collision_ball = ball
                        break
            if collision_point:
                break

        # Draw dashed line for cue ball
        for i in range(len(points) - 1):
            if i % 4 < 2:  # Creates dashed effect
                pygame.draw.line(screen, WHITE, points[i], points[i + 1], 2)

        # If there's a collision, simulate the next ball's trajectory
        if collision_point and collision_ball:
            sim_collision = Ball(collision_point[0], collision_point[1], collision_ball.color)
            # Simplified collision physics for visualization
            angle = math.atan2(collision_ball.y - sim_ball.y, collision_ball.x - sim_ball.x)
            speed = math.sqrt(sim_ball.vx**2 + sim_ball.vy**2) * 0.8
            sim_collision.vx = math.cos(angle) * speed
            sim_collision.vy = math.sin(angle) * speed

            collision_points = []
            for _ in range(steps):
                sim_collision.update()
                collision_points.append((int(sim_collision.x), int(sim_collision.y)))

            # Draw colored trajectory for collided ball
            for i in range(len(collision_points) - 1):
                if i % 4 < 2:
                    pygame.draw.line(screen, collision_ball.color, collision_points[i], collision_points[i + 1], 2)

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.balls = []
        self.player_turn = 1
        self.game_over = False
        self.winner = None
        self.player1_potted = 0
        self.player2_potted = 0
        self.setup_balls()
        self.cue = Cue(self.balls[0])

    def setup_balls(self):
        cue_ball = Ball(TABLE_X + TABLE_WIDTH // 4, TABLE_Y + TABLE_HEIGHT // 2, WHITE)
        self.balls.append(cue_ball)

        colors = [RED, YELLOW, BLUE, PURPLE, ORANGE, GREEN, MAROON, BLACK,
                 YELLOW, BLUE, PURPLE, ORANGE, GREEN, MAROON, RED]

        start_x = TABLE_X + TABLE_WIDTH * 3 // 4
        start_y = TABLE_Y + TABLE_HEIGHT // 2
        rows = 5
        ball_index = 0

        for row in range(rows):
            for col in range(row + 1):
                if ball_index < len(colors):
                    x = start_x + row * BALL_RADIUS * 1.8
                    y = start_y - (row * BALL_RADIUS) + col * BALL_RADIUS * 2
                    self.balls.append(Ball(x, y, colors[ball_index], ball_index + 1))
                    ball_index += 1

    def update(self):
        all_stopped = True
        collision_occurred = False
        for ball in self.balls:
            ball.update()
            if ball.is_moving():
                all_stopped = False

        if self.check_ball_collisions():
            collision_occurred = True

        balls_potted = False
        for ball in self.balls:
            if ball.check_pocket_collision():
                balls_potted = True
                if ball.number != 0:
                    if self.player_turn == 1:
                        self.player1_potted += 1
                    else:
                        self.player2_potted += 1
                if ball.number == 0:  # Reset cue ball if potted
                    ball.active = True
                    ball.x = TABLE_X + TABLE_WIDTH // 4
                    ball.y = TABLE_Y + TABLE_HEIGHT // 2
                    ball.vx = 0
                    ball.vy = 0

        if all_stopped and not balls_potted and not collision_occurred:
            self.player_turn = 3 - self.player_turn

        balls_left = sum(1 for ball in self.balls if ball.active and ball.number != 0)
        if balls_left == 0:
            self.game_over = True
            self.winner = self.player_turn

    def check_ball_collisions(self):
        collision_happened = False
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]
                if not ball1.active or not ball2.active:
                    continue
                dx = ball2.x - ball1.x
                dy = ball2.y - ball1.y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < ball1.radius + ball2.radius:
                    collision_happened = True
                    HIT_SOUND.play()
                    angle = math.atan2(dy, dx)
                    v1 = ball1.vx * math.cos(angle) + ball1.vy * math.sin(angle)
                    v2 = ball2.vx * math.cos(angle) + ball2.vy * math.sin(angle)
                    new_v1 = (v1 * (ball1.mass - ball2.mass) + 2 * ball2.mass * v2) / (ball1.mass + ball2.mass)
                    new_v2 = (v2 * (ball2.mass - ball1.mass) + 2 * ball1.mass * v1) / (ball1.mass + ball2.mass)
                    ball1.vx += (new_v1 - v1) * math.cos(angle)
                    ball1.vy += (new_v1 - v1) * math.sin(angle)
                    ball2.vx += (new_v2 - v2) * math.cos(angle)
                    ball2.vy += (new_v2 - v2) * math.sin(angle)
                    overlap = (ball1.radius + ball2.radius - distance) / 2
                    ball1.x -= overlap * math.cos(angle)
                    ball1.y -= overlap * math.sin(angle)
                    ball2.x += overlap * math.cos(angle)
                    ball2.y += overlap * math.sin(angle)
        return collision_happened

    def draw(self, screen):
        pygame.draw.rect(screen, BROWN, (TABLE_X - 50, TABLE_Y - 50, TABLE_WIDTH + 100, TABLE_HEIGHT + 100))
        pygame.draw.rect(screen, DARK_GREEN, (TABLE_X, TABLE_Y, TABLE_WIDTH, TABLE_HEIGHT))
        pygame.draw.rect(screen, GREEN, (TABLE_X, TABLE_Y, TABLE_WIDTH, CUSHION_WIDTH))
        pygame.draw.rect(screen, GREEN, (TABLE_X, TABLE_Y + TABLE_HEIGHT - CUSHION_WIDTH, TABLE_WIDTH, CUSHION_WIDTH))
        pygame.draw.rect(screen, GREEN, (TABLE_X, TABLE_Y, CUSHION_WIDTH, TABLE_HEIGHT))
        pygame.draw.rect(screen, GREEN, (TABLE_X + TABLE_WIDTH - CUSHION_WIDTH, TABLE_Y, CUSHION_WIDTH, TABLE_HEIGHT))
        for pocket_x, pocket_y in pockets:
            self.draw_pocket(screen, pocket_x, pocket_y)
        for ball in self.balls:
            ball.draw(screen)
        self.cue.draw(screen)
        self.cue.draw_trajectory(screen, self.balls)
        font = pygame.font.SysFont('Arial', 30)
        turn_text = f"Gracz {self.player_turn}"
        screen.blit(font.render(turn_text, True, BLACK), (20, 20))
        score1_text = f"Gracz 1: {self.player1_potted}"
        score2_text = f"Gracz 2: {self.player2_potted}"
        screen.blit(font.render(score1_text, True, BLACK), (20, 60))
        screen.blit(font.render(score2_text, True, BLACK), (20, 90))
        if self.game_over:
            font = pygame.font.SysFont('Arial', 50)
            game_over_text = f"Gracz {self.winner} wygrywa!"
            text_surface = font.render(game_over_text, True, RED)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, WHITE, (text_rect.x - 20, text_rect.y - 20,
                                           text_rect.width + 40, text_rect.height + 40))
            screen.blit(text_surface, text_rect)
            restart_text = "Naciśnij R aby zrestartować"
            restart_surface = font.render(restart_text, True, BLACK)
            restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            screen.blit(restart_surface, restart_rect)

    def draw_pocket(self, screen, pocket_x, pocket_y):
        DARK_POCKET_COLOR = (30, 30, 30)
        POCKET_EDGE_COLOR = (50, 50, 50)
        pygame.gfxdraw.filled_circle(screen, pocket_x, pocket_y, POCKET_RADIUS, DARK_POCKET_COLOR)
        pygame.gfxdraw.filled_circle(screen, pocket_x, pocket_y, POCKET_RADIUS - 10, BLACK)
        net_color = (60, 60, 60)
        for i in range(8):
            angle = i * (math.pi / 4)
            net_length = POCKET_RADIUS * 0.6
            net_start_x = pocket_x + math.cos(angle) * (POCKET_RADIUS * 0.4)
            net_start_y = pocket_y + math.sin(angle) * (POCKET_RADIUS * 0.4)
            net_end_x = pocket_x + math.cos(angle) * net_length
            net_end_y = pocket_y + math.sin(angle) * net_length
            pygame.draw.line(screen, net_color, (net_start_x, net_start_y), (net_end_x, net_end_y), 1)

def generate_hit_sound():
    sample_rate = 44100
    duration = 0.1
    frequency = 500
    amplitude = 32767
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sound_data_mono = (amplitude * np.sin(2 * np.pi * frequency * t) * np.exp(-t * 10)).astype(np.int16)
    sound_data_stereo = np.column_stack((sound_data_mono, sound_data_mono))
    sound = pygame.sndarray.make_sound(sound_data_stereo)
    return sound

def main():
    pygame.init()
    pygame.mixer.init()
    global screen, clock
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bilard")
    clock = pygame.time.Clock()

    global HIT_SOUND, POCKET_SOUND
    HIT_SOUND = generate_hit_sound()
    POCKET_SOUND = pygame.mixer.Sound(buffer=b'\x00\x80' * 1000)

    game = Game()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.cue.start_charging()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.cue.strike()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game.reset()

        if pygame.mouse.get_pressed()[0]:
            game.cue.continue_charging()

        game.cue.update(mouse_pos)
        game.update()

        screen.fill(GRAY)
        game.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
