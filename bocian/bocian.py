import pygame
import random
import os

# Inicjalizacja Pygame
pygame.init()
pygame.mixer.init()  # Inicjalizacja modułu do odtwarzania dźwięku

# Ustawienia ekranu
WIDTH, HEIGHT = 1440, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Gra: Bocian")

# Kolory
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Zegar gry
clock = pygame.time.Clock()
FPS = 60
background_clock = pygame.time.Clock()
BACKGROUND_FPS = 100  # FPS dla tła

# Ścieżka do folderu z muzyką
OST_PATH = "assets/ost"

# Funkcja do odtwarzania muzyki w tle
def play_random_music():
    music_files = [file for file in os.listdir(OST_PATH) if file.endswith(".mp3")]
    if music_files:
        random_music = random.choice(music_files)
        pygame.mixer.music.load(os.path.join(OST_PATH, random_music))
        pygame.mixer.music.play()

# Szybowiec (bocian) z animacją
class Szybowiec:
    def __init__(self):
        self.frames = [
            pygame.image.load("assets/bocian/bocian1.png").convert_alpha(),
            pygame.image.load("assets/bocian/bocian2.png").convert_alpha(),
        ]
        self.current_frame = 0
        self.frame_rate = 10  # Szybkość animacji (ilość klatek na sekundę)
        self.rect = self.frames[0].get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT // 2
        self.speed_y = 0
        self.speed_x = 0.2  # Poziomy ruch w prawo
        self.gravity = 0.03  # Zmniejszona grawitacja
        self.target_height = self.rect.y  # Docelowa wysokość po wznoszeniu
        self.rise_speed = 3  # Prędkość wznoszenia
        self.animation_timer = 0

    def update(self):
        if self.rect.y > self.target_height:
            self.rect.y -= self.rise_speed
            if self.rect.y < self.target_height:
                self.rect.y = self.target_height

        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        self.animation_timer += 1
        if self.animation_timer >= FPS // self.frame_rate:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        self.rect.x += self.speed_x

        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface):
        surface.blit(self.frames[self.current_frame], self.rect)

    def lift(self, power):
        self.target_height = max(0, self.rect.y - power * 40)
        self.rise_speed = power
        self.speed_y = 0

# Klasa reprezentująca prąd powietrzny
class Prad:
    def __init__(self):
        self.value = random.randint(1, 5)
        self.rect = pygame.Rect(WIDTH + random.randint(0, 200), random.randint(100, HEIGHT - 100), 30, 30)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(str(self.value), True, WHITE)
        surface.blit(text, (self.rect.x + 5, self.rect.y + 5))

    def update(self):
        self.rect.x -= 2

# Klasa reprezentująca animowaną żabę
class Zaba:
    def __init__(self):
        self.frames = [
            pygame.image.load("assets/frog/00.png").convert_alpha(),
            pygame.image.load("assets/frog/01.png").convert_alpha(),
            pygame.image.load("assets/frog/02.png").convert_alpha(),
            pygame.image.load("assets/frog/03.png").convert_alpha(),
            pygame.image.load("assets/frog/04.png").convert_alpha(),
            pygame.image.load("assets/frog/05.png").convert_alpha(),
            pygame.image.load("assets/frog/06.png").convert_alpha(),
            pygame.image.load("assets/frog/07.png").convert_alpha(),
            pygame.image.load("assets/frog/08.png").convert_alpha(),
            pygame.image.load("assets/frog/09.png").convert_alpha(),
            pygame.image.load("assets/frog/10.png").convert_alpha(),
        ]
        # Skalowanie żaby 5x mniejsze
        self.frames = [pygame.transform.scale(frame, (frame.get_width() // 5, frame.get_height() // 5)) for frame in self.frames]
        self.current_frame = 0
        self.frame_rate = 8  # Szybkość animacji (ilość klatek na sekundę)
        self.animation_timer = 0
        self.rect = self.frames[0].get_rect()
        self.rect.x = WIDTH  # Żaba pojawi się na prawo od ekranu
        self.rect.y = HEIGHT - self.rect.height  # Na dole ekranu
        self.active = False  # Żaba jest aktywowana co pewien czas

    def update(self):
        if self.active:
            self.rect.x -= 2  # Żaba porusza się z tłem
            self.animation_timer += 1
            if self.animation_timer >= BACKGROUND_FPS // self.frame_rate:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, surface):
        if self.active:
            surface.blit(self.frames[self.current_frame], self.rect)

    def activate(self):
        self.active = True
        self.rect.x = WIDTH  # Żaba pojawia się po prawej stronie ekranu

    def deactivate(self):
        self.active = False

# Główna funkcja gry
def main():
    szybowiec = Szybowiec()
    prady = [Prad() for _ in range(3)]
    zaba = Zaba()
    frog_timer = 0
    metry = 0
    run = True

    # Ładowanie tła
    background_start = pygame.image.load("assets/background/background00.png").convert()
    background_game = pygame.image.load("assets/background/background01.png").convert()
    background_end = pygame.image.load("assets/background/background02.png").convert()

    background_x = 0
    start_bg_done = False  # Flaga do śledzenia, czy tło startowe zostało przewinięte
    background_mode = "start"  # Tryb tła: "start", "game", "end"

    play_random_music()

    while run:
        # Zegar dla gry
        clock.tick(FPS)

        # Zegar dla tła
        background_clock.tick(BACKGROUND_FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if not pygame.mixer.music.get_busy():
            play_random_music()

        # Tło - przewijanie wszystkich warstw
        background_x -= 2
        if background_x <= -WIDTH:
            if not start_bg_done:
                start_bg_done = True  # Tło startowe zostało przewinięte
                background_x = 0
                background_mode = "game"  # Zmiana na tryb gry
            else:
                background_x = 0  # Reset do tła gry po przewinięciu

        # Łączenie tła początkowego i głównego
        if background_mode == "start":
            screen.blit(background_start, (background_x, 0))
            screen.blit(background_game, (background_x + WIDTH, 0))
        elif background_mode == "game":
            screen.blit(background_game, (background_x, 0))
            screen.blit(background_game, (background_x + WIDTH, 0))
        elif background_mode == "end":
            screen.blit(background_game, (background_x, 0))
            screen.blit(background_end, (background_x + WIDTH, 0))

        # Aktualizacja prądów powietrznych po kliknięciu
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            for prad in prady:
                if prad.rect.collidepoint(mouse_pos):
                    szybowiec.lift(prad.value)
                    prady.remove(prad)
                    prady.append(Prad())

        # Aktualizacja pozycji szybowca i prądów
        szybowiec.update()
        for prad in prady:
            prad.update()

        # Kontrolowanie żaby - pojawia się co 3 cykle tła
        frog_timer += 1
        if frog_timer >= 720 and background_mode == "game":  # tylko w trybie gry
            zaba.activate()
            frog_timer = 0

        zaba.update()
        zaba.draw(screen)

        # Rysowanie szybowca i prądów
        szybowiec.draw(screen)
        for prad in prady:
            prad.draw(screen)

        # Sprawdzanie kolizji z żabą
        if zaba.active and szybowiec.rect.colliderect(zaba.rect):
            zaba.deactivate()

        # Sprawdzanie kolizji z prądami powietrznymi
        for prad in prady:
            if szybowiec.rect.colliderect(prad.rect):
                metry += prad.value
                prady.remove(prad)
                prady.append(Prad())

        # Rysowanie żaby
        zaba.draw(screen)

        # Odświeżanie ekranu
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

