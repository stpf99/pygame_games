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
        self.rotation = 0
        self.angular_velocity = 0
        self.is_striped = number > 8 and number != 8

    def update(self):
        if not self.active:
            return

        self.vx *= FRICTION
        self.vy *= FRICTION
        self.angular_velocity = math.sqrt(self.vx**2 + self.vy**2) * 0.1
        self.rotation += self.angular_velocity

        for pocket_x, pocket_y in pockets:
            distance = math.sqrt((self.x - pocket_x)**2 + (self.y - pocket_y)**2)
            if distance < POCKET_RADIUS * 1.5:
                pull_strength = (POCKET_RADIUS * 1.5 - distance) / (POCKET_RADIUS * 1.5) * 0.5
                self.vx += (pocket_x - self.x) * pull_strength
                self.vy += (pocket_y - self.y) * pull_strength

        if abs(self.vx) < 0.1 and abs(self.vy) < 0.1:
            self.vx = 0
            self.vy = 0
            self.angular_velocity = 0

        self.x += self.vx
        self.y += self.vy
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

        ball_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        if self.is_striped:
            pygame.gfxdraw.filled_circle(ball_surface, self.radius, self.radius, self.radius, WHITE)
            pygame.draw.rect(ball_surface, self.color,
                           (0, self.radius - 5, self.radius * 2, 10))
        else:
            pygame.gfxdraw.filled_circle(ball_surface, self.radius, self.radius, self.radius, self.color)

        pygame.gfxdraw.aacircle(ball_surface, self.radius, self.radius, self.radius, BLACK)

        if self.number > 0:
            font = pygame.font.SysFont('Arial', 16, bold=True)
            text = font.render(str(self.number), True, BLACK)  # Czarne cyfry
            text_rect = text.get_rect(center=(self.radius, self.radius))
            pygame.gfxdraw.filled_circle(ball_surface, self.radius, self.radius, 8, WHITE)
            ball_surface.blit(text, text_rect)

        rotated_surface = pygame.transform.rotate(ball_surface, math.degrees(self.rotation))
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rotated_rect)

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

    def ai_strike(self, target_x, target_y, power):
        dx = target_x - self.ball.x
        dy = target_y - self.ball.y
        self.angle = math.atan2(dy, dx)
        self.power = power
        self.ball.vx = -math.cos(self.angle) * self.power
        self.ball.vy = -math.sin(self.angle) * self.power

    def draw(self, screen):
        if not self.ball.active or self.ball.is_moving():
            return

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
            pygame.draw.rect(screen, BLACK, (self.ball.x - power_width // 2, self.ball.y + 50, power_width, 10), 1)
            pygame.draw.rect(screen, RED, (self.ball.x - power_width // 2, self.ball.y + 50,
                                         power_width * (self.power / self.max_power), 10))

    def draw_trajectory(self, screen, balls):
        if not self.charging or not self.ball.active or self.ball.is_moving():
            return

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

        for i in range(len(points) - 1):
            if i % 4 < 2:
                pygame.draw.line(screen, WHITE, points[i], points[i + 1], 2)

        if collision_point and collision_ball:
            sim_collision = Ball(collision_point[0], collision_point[1], collision_ball.color)
            angle = math.atan2(collision_ball.y - sim_ball.y, collision_ball.x - sim_ball.x)
            speed = math.sqrt(sim_ball.vx**2 + sim_ball.vy**2) * 0.8
            sim_collision.vx = math.cos(angle) * speed
            sim_collision.vy = math.sin(angle) * speed

            collision_points = []
            for _ in range(steps):
                sim_collision.update()
                collision_points.append((int(sim_collision.x), int(sim_collision.y)))

            for i in range(len(collision_points) - 1):
                if i % 4 < 2:
                    pygame.draw.line(screen, collision_ball.color, collision_points[i], collision_points[i + 1], 2)

class Game:
    def __init__(self):
        self.reset()
        self.blink_timer = 0
        self.blink_state = True
        self.ai_timer = 0

    def reset(self):
        self.balls = []
        self.player_turn = 1
        self.game_over = False
        self.winner = None
        self.player1_potted = 0
        self.player2_potted = 0
        self.player1_type = None
        self.player2_type = None
        self.setup_balls()
        self.cue = Cue(self.balls[0])

    def setup_balls(self):
        cue_ball = Ball(TABLE_X + TABLE_WIDTH // 4, TABLE_Y + TABLE_HEIGHT // 2, WHITE)
        self.balls.append(cue_ball)

        colors = [
            YELLOW, BLUE, RED, PURPLE, ORANGE, GREEN, MAROON, BLACK,
            YELLOW, BLUE, RED, PURPLE, ORANGE, GREEN, MAROON
        ]
        start_x = TABLE_X + TABLE_WIDTH * 3 // 4
        start_y = TABLE_Y + TABLE_HEIGHT // 2
        ball_positions = [
            (0, 0),
            (1, -1), (1, 1),
            (2, -2), (2, 0), (2, 2),
            (3, -3), (3, -1), (3, 1), (3, 3),
            (4, -4), (4, -2), (4, 0), (4, 2), (4, 4)
        ]

        for i, (row, col) in enumerate(ball_positions):
            x = start_x + row * BALL_RADIUS * 1.8
            y = start_y + col * BALL_RADIUS * 2
            self.balls.append(Ball(x, y, colors[i], i + 1))

    def update(self):
        all_stopped = True
        potted_balls = []
        first_hit = None

        for ball in self.balls:
            ball.update()
            if ball.is_moving():
                all_stopped = False

        if self.check_ball_collisions() and not first_hit:
            for ball in self.balls[1:]:
                if ball.active and math.sqrt((ball.x - self.balls[0].x)**2 + (ball.y - self.balls[0].y)**2) < BALL_RADIUS * 2:
                    first_hit = ball.number

        for ball in self.balls:
            if ball.check_pocket_collision():
                potted_balls.append(ball)

        if all_stopped:
            if potted_balls:
                valid_hit = True
                if self.player1_type is None and self.player2_type is None:
                    if any(b.number <= 7 for b in potted_balls if b.number != 0):
                        self.player1_type = "solid"
                        self.player2_type = "striped"
                    elif any(b.number > 8 for b in potted_balls if b.number != 0):
                        self.player1_type = "striped"
                        self.player2_type = "solid"

                current_type = self.player1_type if self.player_turn == 1 else self.player2_type
                if current_type == "solid" and any(b.number > 8 for b in potted_balls):
                    valid_hit = False
                elif current_type == "striped" and any(b.number <= 7 for b in potted_balls):
                    valid_hit = False

                for ball in potted_balls:
                    if ball.number != 0:
                        if self.player_turn == 1:
                            self.player1_potted += 1
                        else:
                            self.player2_potted += 1
                    if ball.number == 8:
                        remaining = sum(1 for b in self.balls if b.active and b.number != 0 and
                                      ((b.number <= 7 and current_type == "solid") or
                                       (b.number > 8 and current_type == "striped")))
                        if remaining > 0 or not valid_hit:
                            self.game_over = True
                            self.winner = 3 - self.player_turn
                        else:
                            self.game_over = True
                            self.winner = self.player_turn
                    elif ball.number == 0:
                        ball.active = True
                        ball.x = TABLE_X + TABLE_WIDTH // 4
                        ball.y = TABLE_Y + TABLE_HEIGHT // 2
                        ball.vx = 0
                        ball.vy = 0
                        valid_hit = False

                if not valid_hit or (first_hit and
                                  ((current_type == "solid" and first_hit > 8) or
                                   (current_type == "striped" and first_hit <= 7))):
                    self.player_turn = 3 - self.player_turn

            else:
                self.player_turn = 3 - self.player_turn

        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.blink_state = not self.blink_state
            self.blink_timer = 0

        if self.player_turn == 2 and all_stopped and not self.game_over:
            self.ai_timer += 1
            if self.ai_timer >= 60:
                self.ai_play()
                self.ai_timer = 0

    def ai_play(self):
        cue_ball = self.balls[0]
        best_target = None
        best_score = -float('inf')
        current_type = self.player2_type

        # Ocena wszystkich bil i kieszeni
        for ball in self.balls[1:]:
            if not ball.active or (ball.number == 8 and self.get_remaining_balls(2) > 0):
                continue
            if (current_type == "solid" and ball.number <= 7) or \
               (current_type == "striped" and ball.number > 8) or \
               (ball.number == 8 and self.get_remaining_balls(2) == 0):
                for pocket in pockets:
                    # Obliczanie trajektorii i punktacji
                    dx_ball = ball.x - cue_ball.x
                    dy_ball = ball.y - cue_ball.y
                    dist_to_ball = math.sqrt(dx_ball**2 + dy_ball**2)
                    angle_to_ball = math.atan2(dy_ball, dx_ball)

                    dx_pocket = pocket[0] - ball.x
                    dy_pocket = pocket[1] - ball.y
                    dist_to_pocket = math.sqrt(dx_pocket**2 + dy_pocket**2)
                    angle_to_pocket = math.atan2(dy_pocket, dx_pocket)

                    # Punktacja: bliskość kieszeni i wyrównanie kątów
                    alignment = abs(angle_to_ball - angle_to_pocket)
                    if alignment > math.pi:
                        alignment = 2 * math.pi - alignment
                    score = 1000 / (dist_to_ball + dist_to_pocket) - alignment * 10

                    # Sprawdzenie, czy pierwsza bila jest poprawna
                    first_hit = self.simulate_first_hit(cue_ball.x, cue_ball.y, angle_to_ball, 10)
                    if first_hit and ((current_type == "solid" and first_hit > 8) or
                                    (current_type == "striped" and first_hit <= 7)):
                        score -= 1000  # Kara za faul

                    if score > best_score:
                        best_score = score
                        best_target = (ball.x, ball.y, min(15, dist_to_ball / 50))  # Siła proporcjonalna do odległości

        if best_target:
            self.cue.ai_strike(best_target[0], best_target[1], best_target[2])

    def simulate_first_hit(self, x, y, angle, power):
        sim_ball = Ball(x, y, WHITE)
        sim_ball.vx = -math.cos(angle) * power
        sim_ball.vy = -math.sin(angle) * power
        for _ in range(50):
            sim_ball.update()
            for ball in self.balls[1:]:
                if ball.active:
                    dx = ball.x - sim_ball.x
                    dy = ball.y - sim_ball.y
                    if math.sqrt(dx**2 + dy**2) < BALL_RADIUS * 2:
                        return ball.number
        return None

    def get_remaining_balls(self, player):
        player_type = self.player1_type if player == 1 else self.player2_type
        if player_type == "solid":
            return sum(1 for b in self.balls if b.active and b.number <= 7 and b.number != 0)
        else:
            return sum(1 for b in self.balls if b.active and b.number > 8)

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
        if self.player_turn == 1:
            self.cue.draw_trajectory(screen, self.balls)

        font = pygame.font.SysFont('Arial', 30)
        remaining1 = self.get_remaining_balls(1)
        if self.player_turn == 1 and self.blink_state:
            p1_text = font.render(f"Gracz 1: {self.player1_potted}/{7-remaining1} Pozostało: {remaining1}", True, RED)
        else:
            p1_text = font.render(f"Gracz 1: {self.player1_potted}/{7-remaining1} Pozostało: {remaining1}", True, BLACK)
        screen.blit(p1_text, (20, 20))
        if self.player1_type:
            type_text = font.render("Pełne" if self.player1_type == "solid" else "Połówki", True, BLACK)
            screen.blit(type_text, (20, 60))

        remaining2 = self.get_remaining_balls(2)
        if self.player_turn == 2 and self.blink_state:
            p2_text = font.render(f"AI: {self.player2_potted}/{7-remaining2} Pozostało: {remaining2}", True, RED)
        else:
            p2_text = font.render(f"AI: {self.player2_potted}/{7-remaining2} Pozostało: {remaining2}", True, BLACK)
        p2_rect = p2_text.get_rect(topright=(WIDTH - 20, 20))
        screen.blit(p2_text, p2_rect)
        if self.player2_type:
            type_text = font.render("Pełne" if self.player2_type == "solid" else "Połówki", True, BLACK)
            type_rect = type_text.get_rect(topright=(WIDTH - 20, 60))
            screen.blit(type_text, type_rect)

        if self.game_over:
            font = pygame.font.SysFont('Arial', 50)
            game_over_text = f"{'Gracz 1' if self.winner == 1 else 'AI'} wygrywa!"
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
    pygame.display.set_caption("Bilard z AI")
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
            elif event.type == pygame.MOUSEBUTTONDOWN and game.player_turn == 1:
                if event.button == 1:
                    game.cue.start_charging()
            elif event.type == pygame.MOUSEBUTTONUP and game.player_turn == 1:
                if event.button == 1:
                    game.cue.strike()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game.reset()

        if pygame.mouse.get_pressed()[0] and game.player_turn == 1:
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
