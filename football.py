import sys
import math
import time
import pygame

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Football Game")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)

# Klasa reprezentująca boisko
class Field(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        # Rysowanie obszaru poza boiskiem
        pygame.draw.rect(self.image, WHITE, pygame.Rect(0, 0, WIDTH, HEIGHT), 4)

        # Rysowanie linii środkowej
        pygame.draw.line(self.image, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 4)

        # Rysowanie okręgu środkowego
        pygame.draw.circle(self.image, WHITE, (WIDTH // 2, HEIGHT // 2), 73, 4)

        # Rysowanie pola karnego (prawa strona)
        pygame.draw.rect(self.image, WHITE, pygame.Rect(WIDTH - 120, (HEIGHT - 330) // 2, 120, 330), 4)

        # Rysowanie pola karnego (lewa strona)
        pygame.draw.rect(self.image, WHITE, pygame.Rect(0, (HEIGHT - 330) // 2, 120, 330), 4)

        # Rysowanie bramki (prawa strona)
        pygame.draw.rect(self.image, WHITE, pygame.Rect(WIDTH - 20, (HEIGHT - 150) // 2, 10, 150), 4)

        # Rysowanie bramki (lewa strona)
        pygame.draw.rect(self.image, WHITE, pygame.Rect(10, (HEIGHT - 150) // 2, 10, 150), 4)
   

        # Dodanie trybun
        pygame.draw.rect(self.image, WHITE, pygame.Rect(0, 0, WIDTH, 40), 4)
        pygame.draw.rect(self.image, WHITE, pygame.Rect(0, HEIGHT - 40, WIDTH, 40), 4)

        # Dodanie pól autowych
        pygame.draw.rect(self.image, WHITE, pygame.Rect(0, 0, WIDTH, 20), 4)
        pygame.draw.rect(self.image, WHITE, pygame.Rect(0, HEIGHT - 20, WIDTH, 20), 4)

        # Dodanie ławek sędziowskich
        pygame.draw.rect(self.image, WHITE, pygame.Rect(WIDTH // 4, HEIGHT - 40, WIDTH // 2, 20), 4)

# Klasy reprezentująca piłkarzy
class Player2(pygame.sprite.Sprite):
    def __init__(self, x, y, color_top=WHITE, color_bottom=RED):
        super().__init__()
        self.image = pygame.Surface((20, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color_top, pygame.Rect(0, 0, 20, 20))
        pygame.draw.rect(self.image, color_bottom, pygame.Rect(0, 20, 20, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 0
        self.acceleration = 0.2
        self.max_speed = 8
        self.shoot_label = ""
        self.last_shoot_time = 0
        self.goals_scored = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.x += self.speed

        # Ograniczenie do obszaru boiska
        self.rect.x = max(0, min(self.rect.x, WIDTH - 20))  # Ograniczenie szerokości
        self.rect.y = max(0, min(self.rect.y, HEIGHT - 40))  # Ograniczenie wysokości

class Player1(pygame.sprite.Sprite):
    def __init__(self, x, y, color_top=WHITE, color_bottom=BLACK):
        super().__init__()
        self.image = pygame.Surface((20, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color_top, pygame.Rect(0, 0, 20, 20))
        pygame.draw.rect(self.image, color_bottom, pygame.Rect(0, 20, 20, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 0
        self.acceleration = 0.2
        self.max_speed = 8
        self.shoot_label = ""  # Dodane atrybuty
        self.last_shoot_time = 0  # Dodane atrybuty
        self.goals_scored = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
            self.rect.x += self.speed

        # Ograniczenie do obszaru boiska
        self.rect.x = max(0, min(self.rect.x, WIDTH - 20))  # Ograniczenie szerokości
        self.rect.y = max(0, min(self.rect.y, HEIGHT - 40))  # Ograniczenie wysokośc

# Klasa reprezentująca piłkę
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        pygame.draw.circle(self.image, WHITE, (7, 7), 7)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.angle = math.radians(45)

    def update(self):
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        # Ograniczenie do obszaru pomiędzy liniami autowymi
        self.rect.x = max(goal_width, min(self.rect.x, WIDTH - goal_width - self.rect.width))
        self.rect.y = max(20, min(self.rect.y, HEIGHT - 20 - self.rect.height))

        if self.rect.left <= goal_width or self.rect.right >= WIDTH - goal_width:
            self.angle = math.pi - self.angle
        if self.rect.top <= 10 or self.rect.bottom >= HEIGHT - 10:
            self.angle = -self.angle

class GoalLine(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, player):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.player = player

    def check_goal(self, ball):
        if pygame.sprite.collide_rect(ball, self):
            print(f"Gol dla Gracza {self.player}!")
            self.player.goals_scored += 1  # Zwiększenie liczby punktów gracza
            ball.rect.center = (WIDTH // 2, HEIGHT // 2)  # Przywrócenie piłki do środka po golu
            ball.speed = 5
            ball.angle = math.radians(45)


class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, player):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.player = player


# Utworzenie obiektów boiska, piłkarzy, piłki, linii bramki i bramek
field = Field()
player1 = Player1(WIDTH // 2, HEIGHT // 2, color_top=WHITE, color_bottom=RED)
player2 = Player2(WIDTH // 2 - 50, HEIGHT // 2, color_top=WHITE, color_bottom=BLACK)
ball = Ball(WIDTH // 2, HEIGHT // 2)
goal_width = 4
goal_height = 150
# Utworzenie obiektów bramek i linii bramki
goal1 = Goal(10, (HEIGHT - 150) // 2, 10, 150, player1)
goal2 = Goal(WIDTH - 20, (HEIGHT - 150) // 2, 10, 150, player2)
goal_line1 = GoalLine(0, (HEIGHT - 150) // 2, 20, 150, player1)
goal_line2 = GoalLine(WIDTH - 20, (HEIGHT - 150) // 2, 20, 150, player2)
# Grupa sprite'ów
all_sprites = pygame.sprite.Group(field, player1, player2, ball, goal_line1, goal_line2, goal1, goal2)

# Główna pętla gry
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    all_sprites.update()

    # Sprawdzenie kolizji piłki z graczem 1
    if pygame.sprite.collide_rect(player1, ball):
        print("Kolizja z piłką (Gracz 1)!")
        player_center = player1.rect.center
        ball_vector = pygame.Vector2(ball.rect.center) - player_center
        ball_angle = math.atan2(ball_vector.y, ball_vector.x)
        ball.angle = -ball_angle

        # Zmiana kierunku piłki po strzale z lewej nogi
        if player1.shoot_label == "L":
            ball.angle = math.radians(180)  # Piłka zawsze zmienia kierunek na lewo po strzale z lewej nogi
        # Zmiana kierunku piłki po strzale z prawej nogi
        elif player1.shoot_label == "R":
            ball.angle = math.radians(0)  # Piłka zawsze zmienia kierunek na prawo po strzale z prawej nogi

    if pygame.sprite.collide_rect(player2, ball):
        print("Kolizja z piłką (Gracz 2)!")
        player_center = player2.rect.center  # Poprawione na player2
        ball_vector = pygame.Vector2(ball.rect.center) - player_center
        ball_angle = math.atan2(ball_vector.y, ball_vector.x)
        ball.angle = -ball_angle

        # Zmiana kierunku piłki po strzale z lewej nogi
        if player2.shoot_label == "L":  # Poprawione na player2
            ball.angle = math.radians(180)  # Piłka zawsze zmienia kierunek na lewo po strzale z lewej nogi
        # Zmiana kierunku piłki po strzale z prawej nogi
        elif player2.shoot_label == "R":  # Poprawione na player2
            ball.angle = math.radians(0)  # Piłka zawsze zmienia kierunek na prawo po strzale z prawej nogi



    # Sprawdzenie kolizji piłki z liniami bramki
    goal_line1.check_goal(ball)
    goal_line2.check_goal(ball)

    all_sprites.draw(screen)

    font = pygame.font.Font(None, 48)
    label1 = font.render(f"PLAYER_1: {player1.goals_scored}", True, RED)
    label2 = font.render(f"PLAYER_2: {player2.goals_scored}", True, BLACK)

    screen.blit(label2, (30, 10))
    screen.blit(label1, (WIDTH - label2.get_width() - 30, 10))

    pygame.display.flip()
    clock.tick(30)