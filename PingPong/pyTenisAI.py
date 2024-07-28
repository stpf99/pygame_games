import pygame
import sys
import math
import random

# Inicjalizacja Pygame
pygame.init()

# Stałe gry
WIDTH, HEIGHT = 1280, 720
BALL_RADIUS = 15
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SPEED = 5
PADDLE_SPEED = 7
SPEED_INCREASE = 1.05
MAX_BALL_SPEED = 15
SPIN_FACTOR = 2
FPS = 60
SETS_TO_WIN = 3
GREETING_JUMPS = 3

# Kolory
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
BLUE_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 255, 0)

# Inicjalizacja ekranu
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tenis')

# Czcionki
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

# Dźwięki
bounce_sound = pygame.mixer.Sound("bounce.wav")
score_sound = pygame.mixer.Sound("score.wav")

# Mapowanie punktów
points_map = [0, 15, 30, 40, 'Ad']

# Funkcja do generowania tekstury tła
def generate_background():
    sand_color = (194, 178, 128)  # Złoty/piaskowy kolor
    background = pygame.Surface((WIDTH, HEIGHT))
    for x in range(WIDTH):
        for y in range(HEIGHT):
            color_variation = random.randint(-10, 10)
            pixel_color = (
                max(0, min(sand_color[0] + color_variation, 255)),
                max(0, min(sand_color[1] + color_variation, 255)),
                max(0, min(sand_color[2] + color_variation, 255)),
            )
            background.set_at((x, y), pixel_color)
    return background

# Generowanie tekstury tła
background_texture = generate_background()

# Funkcja do wyboru trybu gry i imion graczy
def choose_game_mode():
    input_box1 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 120, 140, 32)
    input_box2 = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 140, 32)
    ai_checkbox = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 20, 20)
    difficulty_slider = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 100, 10)
    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 140, 40)

    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active_box1 = False
    active_box2 = False
    player1_name = ''
    player2_name = ''
    ai_mode = False
    ai_difficulty = 0.5

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box1.collidepoint(event.pos):
                    active_box1 = not active_box1
                    active_box2 = False
                elif input_box2.collidepoint(event.pos):
                    active_box2 = not active_box2
                    active_box1 = False
                elif ai_checkbox.collidepoint(event.pos):
                    ai_mode = not ai_mode
                elif start_button.collidepoint(event.pos):
                    if player1_name and (player2_name or ai_mode):
                        done = True
                else:
                    active_box1 = active_box2 = False
                color = color_active if active_box1 or active_box2 else color_inactive
            if event.type == pygame.KEYDOWN:
                if active_box1:
                    if event.key == pygame.K_RETURN:
                        active_box1 = False
                    elif event.key == pygame.K_BACKSPACE:
                        player1_name = player1_name[:-1]
                    else:
                        player1_name += event.unicode
                elif active_box2:
                    if event.key == pygame.K_RETURN:
                        active_box2 = False
                    elif event.key == pygame.K_BACKSPACE:
                        player2_name = player2_name[:-1]
                    else:
                        player2_name += event.unicode

        # Rysowanie tła
        screen.blit(background_texture, (0, 0))

        # Rysowanie input boxów
        txt_surface1 = font.render(player1_name, True, color)
        screen.blit(txt_surface1, (input_box1.x + 5, input_box1.y + 5))
        pygame.draw.rect(screen, color, input_box1, 2)

        txt_surface2 = font.render(player2_name, True, color)
        screen.blit(txt_surface2, (input_box2.x + 5, input_box2.y + 5))
        pygame.draw.rect(screen, color, input_box2, 2)

        # AI Checkbox
        ai_text = font.render("AI opponent", True, WHITE_COLOR)
        screen.blit(ai_text, (ai_checkbox.x + 30, ai_checkbox.y - 5))
        pygame.draw.rect(screen, WHITE_COLOR, ai_checkbox, 2)
        if ai_mode:
            pygame.draw.rect(screen, WHITE_COLOR, ai_checkbox)

        # Poziom trudności AI
        difficulty_text = font.render("AI difficulty", True, WHITE_COLOR)
        screen.blit(difficulty_text, (difficulty_slider.x, difficulty_slider.y - 30))
        pygame.draw.rect(screen, WHITE_COLOR, difficulty_slider, 2)
        difficulty_indicator = pygame.Rect(difficulty_slider.x + ai_difficulty * 100, difficulty_slider.y - 5, 10, 20)
        pygame.draw.rect(screen, WHITE_COLOR, difficulty_indicator)

        if ai_mode:
            if pygame.mouse.get_pressed()[0]:
                mouse_x, _ = pygame.mouse.get_pos()
                if difficulty_slider.x <= mouse_x <= difficulty_slider.x + difficulty_slider.width:
                    ai_difficulty = (mouse_x - difficulty_slider.x) / difficulty_slider.width

        # Rysowanie przycisku start
        pygame.draw.rect(screen, WHITE_COLOR, start_button)
        start_text = font.render("Start Game", True, BLACK_COLOR)
        screen.blit(start_text, (start_button.x + 10, start_button.y + 5))

        # Aktualizacja ekranu
        pygame.display.flip()

    player2_name = "AI" if ai_mode else player2_name
    return player1_name, player2_name, ai_difficulty

# Inicjalizacja pozycji graczy i piłki
paddle1_pos = [PADDLE_WIDTH // 2, HEIGHT // 2]
paddle2_pos = [WIDTH - PADDLE_WIDTH // 2, HEIGHT // 2]
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [BALL_SPEED, BALL_SPEED]  # Zmieniono na listę
ball_angle = 0

# Punkty i statystyki
gem_score1 = 0
gem_score2 = 0
games1 = 0
games2 = 0
sets1 = 0
sets2 = 0
match_results = []

# Kształt graczy
player_shape = 0

# Funkcja do rysowania graczy
def draw_player(position, color, shape):
    if shape == 0:  # Okrąg
        pygame.draw.circle(screen, color, position, PADDLE_HEIGHT // 2)
    elif shape == 1:  # Elipsa
        pygame.draw.ellipse(screen, color, pygame.Rect(position[0] - PADDLE_WIDTH // 2, position[1] - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT))
    elif shape == 2:  # Prostokąt
        pygame.draw.rect(screen, color, pygame.Rect(position[0] - PADDLE_WIDTH // 2, position[1] - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT))
    elif shape == 3:  # Kwadrat
        side = min(PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, color, pygame.Rect(position[0] - side // 2, position[1] - side // 2, side, side))
    elif shape == 4:  # Gwiazda
        draw_star(position, color, size=PADDLE_HEIGHT // 2)

# Funkcja do rysowania gwiazdy
def draw_star(position, color, size=30):
    x, y = position
    num_points = 5
    angle_between_points = math.radians(360 / num_points)
    points = []
    for i in range(num_points * 2):
        angle = i * angle_between_points + math.radians(ball_angle)
        radius = size if i % 2 == 0 else size // 2
        point_x = x + math.cos(angle) * radius
        point_y = y + math.sin(angle) * radius
        points.append((point_x, point_y))
    pygame.draw.polygon(screen, color, points)

# Funkcja do rysowania siatki
def draw_net():
    net_color = WHITE_COLOR
    net_width = 2
    for i in range(0, HEIGHT, 20):
        pygame.draw.line(screen, net_color, (WIDTH // 2, i), (WIDTH // 2, i + 10), net_width)

# Funkcja do regulacji kąta odbicia piłki
def adjust_angle(velocity, ball_position, paddle_position):
    # Obliczenie różnicy w pozycji
    diff = ball_position[1] - paddle_position[1]
    angle = (diff / (PADDLE_HEIGHT // 2)) * (math.pi / 4)  # Maksymalnie 45 stopni
    speed = math.hypot(*velocity)
    new_velocity = (speed * math.cos(angle), speed * math.sin(angle))
    # Ustawienie nowego kierunku piłki
    if velocity[0] < 0:
        return [-abs(new_velocity[0]), new_velocity[1]]
    else:
        return [abs(new_velocity[0]), new_velocity[1]]

# Funkcja do zastosowania podkręcenia
def apply_spin(velocity, ball_position, paddle_position):
    paddle_center = paddle_position[1]
    distance_from_center = ball_position[1] - paddle_center
    spin = (distance_from_center / (PADDLE_HEIGHT // 2)) * SPIN_FACTOR
    return [velocity[0], velocity[1] + spin]

# Funkcja do zapisywania wyników
def save_scores():
    with open("tenis.txt", "a") as file:
        for result in match_results:
            file.write(f'{result[0]} vs {result[1]}: {result[1]}-{result[2]}\n')

# Funkcja do aktualizacji rankingu
def update_ranking():
    ranking = {}
    try:
        with open("tenis.txt", "r") as file:
            for line in file:
                players, score = line.split(':')
                player1, player2 = players.split(' vs ')
                score1, score2 = map(int, score.split('-'))
                if player1 not in ranking:
                    ranking[player1] = {'wins': 0, 'losses': 0}
                if player2 not in ranking:
                    ranking[player2] = {'wins': 0, 'losses': 0}
                if score1 > score2:
                    ranking[player1]['wins'] += 1
                    ranking[player2]['losses'] += 1
                else:
                    ranking[player1]['losses'] += 1
                    ranking[player2]['wins'] += 1
    except FileNotFoundError:
        pass
    return ranking

# Funkcja do wyświetlania rankingu
def display_ranking(ranking):
    screen.fill(BLACK_COLOR)
    y_offset = 100
    sorted_ranking = sorted(ranking.items(), key=lambda item: item[1]['wins'], reverse=True)
    for player, stats in sorted_ranking:
        text = f'{player}: {stats["wins"]} Wins, {stats["losses"]} Losses'
        rendered_text = large_font.render(text, True, WHITE_COLOR)
        screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y_offset))
        y_offset += 50
    pygame.display.flip()
    pygame.time.wait(5000)

# Funkcja do witania się graczy
def player_greeting():
    for _ in range(GREETING_JUMPS):
        screen.blit(background_texture, (0, 0))
        draw_net()
        paddle1_pos[1] -= 10
        paddle2_pos[1] -= 10
        draw_player(paddle1_pos, BLUE_COLOR, player_shape)
        draw_player(paddle2_pos, GREEN_COLOR, player_shape)
        pygame.display.flip()
        pygame.time.wait(200)
        screen.blit(background_texture, (0, 0))
        draw_net()
        paddle1_pos[1] += 10
        paddle2_pos[1] += 10
        draw_player(paddle1_pos, BLUE_COLOR, player_shape)
        draw_player(paddle2_pos, GREEN_COLOR, player_shape)
        pygame.display.flip()
        pygame.time.wait(200)

def get_display_score(score):
    if score >= len(points_map):
        return 'Ad'
    return points_map[score]

def main():
    global ball_vel, ball_pos, ball_angle, paddle1_pos, paddle2_pos, gem_score1, gem_score2, games1, games2, sets1, sets2, player_shape

    # Wybór imion graczy i trybu gry
    player1_name, player2_name, ai_difficulty = choose_game_mode()

    # Powitanie graczy
    player_greeting()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Ruch gracza 1
        if keys[pygame.K_w] and paddle1_pos[1] - PADDLE_HEIGHT // 2 > 0:
            paddle1_pos[1] -= PADDLE_SPEED
        if keys[pygame.K_s] and paddle1_pos[1] + PADDLE_HEIGHT // 2 < HEIGHT:
            paddle1_pos[1] += PADDLE_SPEED

        # Ruch gracza 2
        if player2_name == "AI":
            # Ruch AI bazujący na trudności
            if ball_vel[0] > 0:
                if paddle2_pos[1] < ball_pos[1]:
                    paddle2_pos[1] += PADDLE_SPEED * ai_difficulty
                else:
                    paddle2_pos[1] -= PADDLE_SPEED * ai_difficulty
        else:
            if keys[pygame.K_UP] and paddle2_pos[1] - PADDLE_HEIGHT // 2 > 0:
                paddle2_pos[1] -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and paddle2_pos[1] + PADDLE_HEIGHT // 2 < HEIGHT:
                paddle2_pos[1] += PADDLE_SPEED

        # Ruch piłki
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]
        ball_angle += 5

        # Odbicie piłki od ścian
        if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
            ball_vel[1] = -ball_vel[1]
            bounce_sound.play()

        # Odbicie piłki od padli
        if ball_pos[0] <= PADDLE_WIDTH + BALL_RADIUS:
            if paddle1_pos[1] - PADDLE_HEIGHT // 2 <= ball_pos[1] <= paddle1_pos[1] + PADDLE_HEIGHT // 2:
                ball_vel = adjust_angle(ball_vel, ball_pos, paddle1_pos)
                ball_vel = apply_spin(ball_vel, ball_pos, paddle1_pos)
                ball_vel[0] = -ball_vel[0]
                ball_vel[0] = min(ball_vel[0] * SPEED_INCREASE, MAX_BALL_SPEED)
                ball_vel[1] = min(ball_vel[1] * SPEED_INCREASE, MAX_BALL_SPEED)
                bounce_sound.play()
                player_shape = (player_shape + 1) % 5
            else:
                gem_score2 += 1
                score_sound.play()
                ball_pos = [WIDTH // 2, HEIGHT // 2]
                ball_vel = [BALL_SPEED, BALL_SPEED]

        elif ball_pos[0] >= WIDTH - PADDLE_WIDTH - BALL_RADIUS:
            if paddle2_pos[1] - PADDLE_HEIGHT // 2 <= ball_pos[1] <= paddle2_pos[1] + PADDLE_HEIGHT // 2:
                ball_vel = adjust_angle(ball_vel, ball_pos, paddle2_pos)
                ball_vel = apply_spin(ball_vel, ball_pos, paddle2_pos)
                ball_vel[0] = -ball_vel[0]
                ball_vel[0] = max(ball_vel[0] * SPEED_INCREASE, -MAX_BALL_SPEED)
                ball_vel[1] = max(ball_vel[1] * SPEED_INCREASE, -MAX_BALL_SPEED)
                bounce_sound.play()
                player_shape = (player_shape + 1) % 5
            else:
                gem_score1 += 1
                score_sound.play()
                ball_pos = [WIDTH // 2, HEIGHT // 2]
                ball_vel = [-BALL_SPEED, -BALL_SPEED]


        # Sprawdzenie wygranej w gemie
        if gem_score1 >= 3 and gem_score1 - gem_score2 >= 2:
            games1 += 1
            gem_score1 = 0
            gem_score2 = 0
        elif gem_score2 >= 3 and gem_score2 - gem_score1 >= 2:
            games2 += 1
            gem_score1 = 0
            gem_score2 = 0
        elif gem_score1 == 4 and gem_score2 == 4:
            gem_score1 = 3
            gem_score2 = 3

        # Sprawdzenie wygranej w secie
        if games1 >= 6 and games1 - games2 >= 2:
            sets1 += 1
            games1 = 0
            games2 = 0
        elif games2 >= 6 and games2 - games1 >= 2:
            sets2 += 1
            games1 = 0
            games2 = 0

        # Sprawdzenie wygranej w meczu
        if sets1 == SETS_TO_WIN:
            match_results.append((player1_name, player2_name, sets1, sets2))
            save_scores()
            break
        elif sets2 == SETS_TO_WIN:
            match_results.append((player2_name, player1_name, sets2, sets1))
            save_scores()
            break

        # Rysowanie tła
        screen.blit(background_texture, (0, 0))

        # Rysowanie siatki
        draw_net()

        # Rysowanie graczy
        draw_player(paddle1_pos, BLUE_COLOR, player_shape)
        draw_player(paddle2_pos, GREEN_COLOR, player_shape)

        # Rysowanie piłki z gwiazdą
        draw_star(ball_pos, WHITE_COLOR, size=BALL_RADIUS)

        # Wyświetlanie wyniku
        score_text = font.render(f'{player1_name}: {get_display_score(gem_score1)} - {player2_name}: {get_display_score(gem_score2)}', True, WHITE_COLOR)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        # Wyświetlanie wyników gemów i setów
        game_set_text = font.render(f'Games: {games1} - {games2}, Sets: {sets1} - {sets2}', True, WHITE_COLOR)
        screen.blit(game_set_text, (WIDTH // 2 - game_set_text.get_width() // 2, 60))

        # Aktualizacja ekranu
        pygame.display.flip()
        clock.tick(FPS)

    # Wyświetlanie rankingu po zakończeniu gry
    ranking = update_ranking()
    display_ranking(ranking)

    pygame.quit()

if __name__ == '__main__':
    main()
