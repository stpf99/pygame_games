import pygame
import random

# Inicjalizacja Pygame
pygame.init()

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

# Szybowiec (bocian) z animacją
class Szybowiec:
    def __init__(self):
        # Wczytanie klatek animacji bociana
        self.frames = [
            pygame.image.load("bocian1.png").convert_alpha(),
            pygame.image.load("bocian2.png").convert_alpha(),
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
        self.max_speed_y = 3  # Ograniczenie prędkości w pionie
        self.animation_timer = 0

    def update(self):
        # Płynne wznoszenie do docelowej wysokości
        if self.rect.y > self.target_height:
            self.rect.y -= self.rise_speed
            if self.rect.y < self.target_height:
                self.rect.y = self.target_height

        # Zastosowanie grawitacji, jeśli nie ma prądu
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        # Aktualizacja animacji (zmiana klatki co określoną liczbę FPS)
        self.animation_timer += 1
        if self.animation_timer >= FPS // self.frame_rate:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Poruszanie się w prawo
        self.rect.x += self.speed_x

        # Zabezpieczenie przed wyjściem poza ekran (tylko w pionie)
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT

    def draw(self, surface):
        surface.blit(self.frames[self.current_frame], self.rect)

    # Funkcja ustawiająca nową wysokość po kliknięciu na prąd
    def lift(self, power):
        self.target_height = max(0, self.rect.y - power * 40)  # Wyznacz docelową wysokość
        self.rise_speed = power  # Prędkość wznoszenia zależna od wartości prądu
        self.speed_y = 0  # Resetuj aktualną prędkość w pionie


# Prąd powietrzny
class Prad:
    def __init__(self):
        self.value = random.randint(1, 5)  # Losowa wartość od 1 do 5
        self.rect = pygame.Rect(WIDTH + random.randint(0, 200), random.randint(100, HEIGHT - 100), 30, 30)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        font = pygame.font.Font(None, 36)
        text = font.render(str(self.value), True, WHITE)
        surface.blit(text, (self.rect.x + 5, self.rect.y + 5))

    def update(self):
        self.rect.x -= 2  # Prąd przesuwa się w lewo razem z ekranem


# Główna funkcja gry
def main():
    szybowiec = Szybowiec()
    prady = [Prad() for _ in range(3)]  # Na początek generujemy 3 prądy powietrzne
    background = pygame.image.load("background.png").convert()  # Przewijające się tło
    background_x = 0
    metry = 0
    run = True

    while run:
        screen.fill(WHITE)

        # Wydarzenia
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Aktualizacja prądów powietrznych po kliknięciu
        if pygame.mouse.get_pressed()[0]:  # Jeśli lewy przycisk myszy jest wciśnięty
            mouse_pos = pygame.mouse.get_pos()
            for prad in prady:
                if prad.rect.collidepoint(mouse_pos):
                    szybowiec.lift(prad.value)  # Szybowiec płynnie wznosi się na podstawie prądu
                    prady.remove(prad)
                    prady.append(Prad())  # Nowy prąd pojawia się po usunięciu starego

        # Aktualizacja pozycji szybowca i prądów
        szybowiec.update()
        for prad in prady:
            prad.update()

        # Prerolling tła (przewijanie)
        background_x -= 2
        if background_x <= -WIDTH:
            background_x = 0

        # Rysowanie tła
        screen.blit(background, (background_x, 0))
        screen.blit(background, (background_x + WIDTH, 0))

        # Rysowanie szybowca i prądów
        szybowiec.draw(screen)
        for prad in prady:
            prad.draw(screen)

        # Aktualizacja świata (szybowiec podąża do mety)
        metry += szybowiec.speed_x  # Przemieszcza się w prawo, zwiększając przebyty dystans
        if metry >= 5000:  # Przykładowa wartość mety, można dostosować
            print("Wygrałeś!")
            run = False

        # Aktualizacja ekranu
        pygame.display.flip()

        # Ustawienie prędkości gry
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
