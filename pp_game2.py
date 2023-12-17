import pygame
import sys
import math
import random

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna gry
width, height = 1200, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong Game")

# Kolory
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 191, 255)  # Lazurowy

# Paletki
paddle_width, paddle_height = 15, 80
paddle1_x, paddle1_y = 0, (height - paddle_height) // 2
paddle2_x, paddle2_y = width - paddle_width, (height - paddle_height) // 2
paddle_speed = 8

# Piłka
ball_size = 20
ball_speed = 40
ball_x, ball_y = width // 2, height // 2
ball_angle = random.uniform(-45, 45)  # Kąt początkowy dla piłki

# Stołowa geometria
table_color = blue
table_rect = pygame.Rect(0, 0, width, height)
table_border_width = 40
table_border_rect = pygame.Rect(table_border_width, table_border_width,
                                width - 2 * table_border_width, height - 2 * table_border_width)

net_color = white
net_width = 2
net_rects = [pygame.Rect(width // 2 - net_width // 2, i * height // 20, net_width, height // 20) for i in range(20)]

# Liczniki punktów
score_player1 = 0
score_player2 = 0

clock = pygame.time.Clock()

# Główna pętla gry
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    # Obsługa klawiszy dla gracza 1
    if keys[pygame.K_w] and paddle1_y > 0:
        paddle1_y -= paddle_speed
    if keys[pygame.K_s] and paddle1_y < height - paddle_height:
        paddle1_y += paddle_speed

    # Obsługa klawiszy dla gracza 2
    if keys[pygame.K_UP] and paddle2_y > 0:
        paddle2_y -= paddle_speed
    if keys[pygame.K_DOWN] and paddle2_y < height - paddle_height:
        paddle2_y += paddle_speed

    # Aktualizacja pozycji piłki
    ball_x += ball_speed * math.cos(math.radians(ball_angle))
    ball_y += ball_speed * math.sin(math.radians(ball_angle))

    # Odbicie od górnej i dolnej krawędzi
    if ball_y <= 0 or ball_y >= height - ball_size:
        ball_angle = 360 - ball_angle  # Odbicie od góry lub dołu

    # Sprawdzenie kolizji z paletkami
    if (
        paddle1_x <= ball_x <= paddle1_x + paddle_width and
        paddle1_y <= ball_y <= paddle1_y + paddle_height
    ):
        # Oblicz kąt odbicia w zależności od punktu na paletce
        relative_intersect_y = (paddle1_y + paddle_height / 2) - ball_y
        normalized_relative_intersect_y = (relative_intersect_y / (paddle_height / 2))
        ball_angle = normalized_relative_intersect_y * 60  # Maksymalny kąt odbicia 60 stopni

    elif (
        paddle2_x <= ball_x <= paddle2_x + paddle_width and
        paddle2_y <= ball_y <= paddle2_y + paddle_height
    ):
        # Oblicz kąt odbicia w zależności od punktu na paletce
        relative_intersect_y = (paddle2_y + paddle_height / 2) - ball_y
        normalized_relative_intersect_y = (relative_intersect_y / (paddle_height / 2))
        ball_angle = 180 - normalized_relative_intersect_y * 60  # Maksymalny kąt odbicia 60 stopni

    # Sprawdzenie, czy piłka opuściła planszę
    if ball_x <= 0:
        score_player2 += 1  # Zwiększ wynik gracza 2
        ball_x, ball_y = width // 2, height // 2  # Resetuj piłkę po środku
        ball_angle = random.uniform(45, 135)  # Kąt początkowy dla piłki
    elif ball_x >= width:
        score_player1 += 1  # Zwiększ wynik gracza 1
        ball_x, ball_y = width // 2, height // 2  # Resetuj piłkę po środku
        ball_angle = random.uniform(-135, -45)  # Kąt początkowy dla piłki

    # Rysowanie
    screen.fill(black)

    # Rysowanie białej ramki stołu
    pygame.draw.rect(screen, white, table_border_rect)

    # Rysowanie stołu
    pygame.draw.rect(screen, table_color, table_rect)

    # Rysowanie siatki
    for net_rect in net_rects:
        pygame.draw.rect(screen, net_color, net_rect)

    # Rysowanie paletki gracza 1
    pygame.draw.rect(screen, white, (paddle1_x, paddle1_y, paddle_width, paddle_height))

    # Rysowanie paletki gracza 2
    pygame.draw.rect(screen, white, (paddle2_x, paddle2_y, paddle_width, paddle_height))

    # Rysowanie piłki
    pygame.draw.ellipse(screen, white, (ball_x, ball_y, ball_size, ball_size))

    # Rysowanie wyników na ekranie
    font = pygame.font.Font(None, 72)
    score_text = font.render(f"{score_player1} : {score_player2}", True, white)
    screen.blit(score_text, (width // 2 - score_text.get_width() // 2, 10))

    # Aktualizacja okna
    pygame.display.flip()

    # Ustawienie liczby klatek na sekundę
    clock.tick(60)
