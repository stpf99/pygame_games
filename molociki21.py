#!/usr/bin/env python3
"""
Molociki - PixelArt Plane Game (wersja z przewijanym terenem i animacjami)
- Rozdzielczość: 1280x720
- Sterowanie z akceleracją + tarcie
- 1p / 2p / 2p+AI (AI helper)
- Czarne przeszkody: kolizja -> KONIEC GRY
- Czarna beczka (fuel): +10 pkt, niebieska (bonus): +50 pkt
- Animowany teren (scrolling), animacje samolotów (bobbing + tilt)
- Zapis wyników do scores.txt
"""

import pygame
import random
import math
import os
import sys

# --- KONFIG ---
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
SCORES_FILE = "scores.txt"

# Pastelowa paleta (dla dzieci)
PASTEL_SKY = (200, 235, 255)
PASTEL_GREEN = (178, 255, 178)
PASTEL_PINK = (255, 178, 216)
PASTEL_PURPLE = (204, 153, 255)
PASTEL_YELLOW = (255, 249, 178)
PASTEL_ORANGE = (255, 204, 153)
BLACK = (10, 10, 10)
BONUS_BLUE = (51, 153, 255)
WHITE = (255, 255, 255)
TEXT_COLOR = (40, 40, 60)

# Kontrolki
CONTROLS_1 = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
CONTROLS_2 = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT}

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Molociki - Kolorowe Loty")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Consolas", 28)
SMALL = pygame.font.SysFont("Consolas", 18)

# Timer do spawnów
SPAWN_BARREL_MS = 1800
SPAWN_OBS_MS = 2200
pygame.time.set_timer(pygame.USEREVENT + 1, SPAWN_BARREL_MS)
pygame.time.set_timer(pygame.USEREVENT + 2, SPAWN_OBS_MS)

# --- SPRITE'y i obiekty ---

class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y, bonus=False):
        super().__init__()
        self.bonus = bonus
        size = 22
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        # rysunek beczki: kontur czarny lub niebieski
        if self.bonus:
            pygame.draw.rect(surf, BONUS_BLUE, (0, 0, size, size), border_radius=5)
            pygame.draw.rect(surf, WHITE, (4, 4, size-8, size-8), border_radius=4)
        else:
            pygame.draw.rect(surf, BLACK, (0, 0, size, size), border_radius=5)
            pygame.draw.rect(surf, PASTEL_YELLOW, (4, 4, size-8, size-8), border_radius=4)
        self.image = surf
        self.rect = self.image.get_rect(center=(x, y))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, vx=0, vy=0, size=32):
        super().__init__()
        self.vx = vx
        self.vy = vy
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        s.fill((0,0,0,0))
        # prosty czarny "balon" / przeszkoda
        pygame.draw.ellipse(s, BLACK, (0, 0, size, int(size*0.75)))
        # mały jasny dekorek
        pygame.draw.circle(s, (40,40,40), (size//2, size//3), size//8)
        self.image = s
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # odbij od krawędzi (by były ruchome)
        if self.rect.left < 0 or self.rect.right > SCREEN_W:
            self.vx *= -1
        if self.rect.top < 0 or self.rect.bottom > SCREEN_H:
            self.vy *= -1


class Plane(pygame.sprite.Sprite):
    def __init__(self, x, y, color_body, color_wing, controls=None, is_ai=False):
        super().__init__()
        self.base_surf = pygame.Surface((60, 40), pygame.SRCALPHA)
        self.draw_on_base(color_body, color_wing)
        self.image = self.base_surf.copy()
        self.rect = self.image.get_rect(center=(x, y))
        # ruch
        self.controls = controls or {}
        self.is_ai = is_ai
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.acc = 0.35
        self.max_speed = 6.0
        self.friction = 0.14
        # stan
        self.fuel = 100.0
        self.score = 0
        # animacja
        self.bob_phase = random.random() * 2 * math.pi
        self.tilt = 0.0  # degrees

    def draw_on_base(self, body, wing):
        s = self.base_surf
        s.fill((0,0,0,0))
        # kadłub centrum
        pygame.draw.rect(s, body, (18, 10, 28, 18), border_radius=6)
        # dziób
        pygame.draw.polygon(s, wing, [(46, 10), (58, 20), (46, 30)])
        # skrzydła
        pygame.draw.rect(s, wing, (8, 6, 14, 8), border_radius=4)
        pygame.draw.rect(s, wing, (8, 26, 14, 8), border_radius=4)
        # okienko
        pygame.draw.rect(s, WHITE, (24, 14, 10, 8), border_radius=3)

    def handle_input(self, keys):
        # pobierz klawisze bezpiecznie
        up = self.controls.get("up", None)
        down = self.controls.get("down", None)
        left = self.controls.get("left", None)
        right = self.controls.get("right", None)

        # pion
        if up is not None and up >= 0 and keys[up]:
            self.speed_y = max(self.speed_y - self.acc, -self.max_speed)
        elif down is not None and down >= 0 and keys[down]:
            self.speed_y = min(self.speed_y + self.acc, self.max_speed)
        else:
            self.speed_y *= (1 - self.friction)

        # poziom
        if left is not None and left >= 0 and keys[left]:
            self.speed_x = max(self.speed_x - self.acc, -self.max_speed)
        elif right is not None and right >= 0 and keys[right]:
            self.speed_x = min(self.speed_x + self.acc, self.max_speed)
        else:
            self.speed_x *= (1 - self.friction)

        # zapobiegaj niezwykle małym wartościom
        if abs(self.speed_x) < 0.05: self.speed_x = 0.0
        if abs(self.speed_y) < 0.05: self.speed_y = 0.0

    def ai_move(self, barrels_group, obstacles_group, players_group):
        # Priorytet: niebieskie beczki (bonus), potem zwykłe
        barrels = list(barrels_group)
        if not barrels:
            # zwolnij, patroluj
            self.speed_x *= (1 - self.friction)
            self.speed_y *= (1 - self.friction)
            return

        bonus = [b for b in barrels if getattr(b, "bonus", False)]
        target = None
        if bonus:
            target = min(bonus, key=lambda b: (b.rect.centerx - self.rect.centerx)**2 + (b.rect.centery - self.rect.centery)**2)
        else:
            target = min(barrels, key=lambda b: (b.rect.centerx - self.rect.centerx)**2 + (b.rect.centery - self.rect.centery)**2)

        # kierunek do celu
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy) + 1e-6
        # przyciąganie
        ax = (dx / dist) * 0.9
        ay = (dy / dist) * 0.9

        # odpychanie od przeszkód (jeśli blisko)
        for ob in obstacles_group:
            dxo = self.rect.centerx - ob.rect.centerx
            dyo = self.rect.centery - ob.rect.centery
            do = math.hypot(dxo, dyo) + 1e-6
            if do < 90:
                # repulsja
                strength = (90 - do) / 90 * 2.2
                ax += (dxo / do) * strength
                ay += (dyo / do) * strength

        # delikatne zbliżanie do gracza (tankowanie) jeśli gracz ma niskie paliwo
        # znajdź pierwszy non-AI gracz
        human = None
        for p in players_group:
            if not p.is_ai:
                human = p
                break
        if human and human.fuel < 60 and self.fuel > 20:
            dxh = human.rect.centerx - self.rect.centerx
            dyh = human.rect.centery - self.rect.centery
            dh = math.hypot(dxh, dyh) + 1e-6
            ax += (dxh / dh) * 0.5
            ay += (dyh / dh) * 0.5

        # apply acceleration
        self.speed_x += ax * (self.acc / 0.8)
        self.speed_y += ay * (self.acc / 0.8)

        # clamp speed
        self.speed_x = max(-self.max_speed, min(self.max_speed, self.speed_x))
        self.speed_y = max(-self.max_speed, min(self.max_speed, self.speed_y))

    def update(self, keys=None, barrels_group=None, obstacles_group=None, players_group=None):
        if self.is_ai:
            self.ai_move(barrels_group or pygame.sprite.Group(), obstacles_group or pygame.sprite.Group(), players_group or pygame.sprite.Group())
        else:
            if keys is not None:
                self.handle_input(keys)

        # ruch
        self.rect.x += int(self.speed_x)
        self.rect.y += int(self.speed_y)
        # utrzymuj w ekranie
        self.rect.clamp_ip(pygame.Rect(0,0,SCREEN_W,SCREEN_H))

        # animacja bob (sinus) i tilt zależny od prędkości
        self.bob_phase += 0.08
        bob = math.sin(self.bob_phase) * 3
        tilt = -self.speed_x * 3.5  # obrót przeciwny do ruchu x
        self.tilt = tilt

        # stwórz animowaną wersję obrazu
        rotated = pygame.transform.rotozoom(self.base_surf, tilt, 1.0)
        # zastosuj bob przesunięcie poprzez przesunięcie rect do kreskowanego offsetu przy blitowaniu w draw()
        self.image = rotated
        # keep center
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery + bob))

    def refuel(self, amount=50.0):
        self.fuel = min(100.0, self.fuel + amount)


# --- GRA: teren przewijany w poziomie (endless) ---

class ScrollingTerrain:
    def __init__(self, w, h, tile=48):
        self.w = w
        self.h = h
        self.tile = tile
        # tworzymy surface dwukrotnej szerokości by scrollować w pętli
        self.surface = pygame.Surface((w*2, h))
        self.offset = 0  # 0..w-1
        self.create_tiles()

    def create_tiles(self):
        # losowy, przyjazny dzieciom wzór
        colors = [PASTEL_GREEN, PASTEL_PINK, PASTEL_PURPLE, PASTEL_YELLOW, PASTEL_ORANGE]
        for y in range(0, self.h, self.tile):
            for x in range(0, self.w*2, self.tile):
                c = random.choice(colors)
                rect = pygame.Rect(x,y,self.tile,self.tile)
                pygame.draw.rect(self.surface, c, rect)
                # prosty wzorek pikselowy
                for px in range(x, x+self.tile, 12):
                    for py in range(y, y+self.tile, 12):
                        if (px+py) % 24 == 0:
                            self.surface.set_at((px, py), (255,255,255))

    def update(self, speed=2.5):
        # przesuwamy offset w lewo (im większy speed, tym szybszy lot)
        self.offset = (self.offset + speed) % self.w

    def draw(self, target_surface):
        # rysuj część surface zaczynając od offset
        x = int(self.offset)
        # blitujemy dwa fragmenty by pokryć ekran
        target_surface.blit(self.surface, (-x, 0), area=pygame.Rect(0,0,self.w,self.h))
        target_surface.blit(self.surface, (self.w - x, 0), area=pygame.Rect(self.w,0,self.w,self.h))


# --- Scores: bezpieczne wczytywanie/zapisywanie i UI wpisywania imienia ---

def load_scores():
    scores = []
    if not os.path.exists(SCORES_FILE):
        return scores
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) != 2:
                    continue
                name = parts[0].strip()
                try:
                    score = int(parts[1].strip())
                except:
                    continue
                scores.append((name, score))
        scores.sort(key=lambda t: t[1], reverse=True)
    except Exception as e:
        print("load_scores error:", e)
    return scores

def save_score(name, score):
    try:
        with open(SCORES_FILE, "a", encoding="utf-8") as f:
            f.write(f"{name},{score}\n")
    except Exception as e:
        print("save_scores error:", e)


# --- MENU i główna logika gry ---

def draw_text_center(surf, text, y, size=28, color=TEXT_COLOR):
    font = pygame.font.SysFont("Consolas", size)
    r = font.render(text, True, color)
    rect = r.get_rect(center=(SCREEN_W//2, y))
    surf.blit(r, rect)

def start_menu_loop():
    selected = 0
    options = ["1 Player", "2 Players", "2 Players + AI", "Exit"]
    while True:
        screen.fill(PASTEL_PURPLE)
        draw_text_center(screen, "Molociki - Kolorowe Loty", 120, 44, TEXT_COLOR)
        # draw options
        for i, opt in enumerate(options):
            color = TEXT_COLOR if i != selected else (255,100,100)
            draw_text_center(screen, opt, 260 + i*64, 32, color)
        # top scores
        scores = load_scores()
        draw_text_center(screen, "Top Scores", 480, 26, TEXT_COLOR)
        for i, (n,s) in enumerate(scores[:6]):
            txt = f"{i+1}. {n} - {s}"
            draw_text_center(screen, txt, 520 + i*24, 20, TEXT_COLOR)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return selected  # 0..3
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()
                bx = SCREEN_W//2
                by0 = 260
                for i in range(len(options)):
                    rect = pygame.Rect(0,0,420,44)
                    rect.center = (bx, by0 + i*64)
                    if rect.collidepoint(mx,my):
                        return i

def enter_name_and_save(total_scores):
    # total_scores: list of tuples e.g. [("Player1", 120), ...] we save all
    # We'll allow user to enter a single name to tag top human score(s)
    name = ""
    active = True
    while active:
        screen.fill(PASTEL_PINK)
        draw_text_center(screen, "Koniec Gry! Zapisz wynik", 120, 40, TEXT_COLOR)
        draw_text_center(screen, "Wpisz imię (Enter aby zapisać) :", 220, 24, TEXT_COLOR)
        # show what will be saved
        y = 280
        for n,s in total_scores:
            draw_text_center(screen, f"{n}: {s}", y, 22, TEXT_COLOR)
            y += 34
        # input box
        box = pygame.Rect(SCREEN_W//2 - 200, SCREEN_H - 220, 400, 48)
        pygame.draw.rect(screen, WHITE, box, border_radius=8)
        txts = FONT.render(name or "_", True, TEXT_COLOR)
        screen.blit(txts, (box.x + 12, box.y + 6))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    if name.strip():
                        # save each human score under this name (append suffix if multiple)
                        for idx, (label, val) in enumerate(total_scores):
                            save_score(f"{name}" if len(total_scores)==1 else f"{name}_{idx+1}", val)
                        active = False
                        return
                elif ev.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12 and ev.unicode.isprintable():
                        name += ev.unicode

def game_loop(mode_index):
    # mode_index: 0=1p,1=2p,2=2p+AI
    terrain = ScrollingTerrain(SCREEN_W, SCREEN_H, tile=48)
    all_sprites = pygame.sprite.Group()
    barrels = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    planes = pygame.sprite.Group()

    # spawn initial barrels + obstacles
    for _ in range(8):
        b = Barrel(random.randint(80, SCREEN_W-80), random.randint(80, SCREEN_H-80), bonus=(random.random()<0.18))
        barrels.add(b); all_sprites.add(b)
    for _ in range(6):
        ob = Obstacle(random.randint(80, SCREEN_W-80), random.randint(80, SCREEN_H-80),
                      vx=random.choice([-1,1])*random.uniform(0.6,1.4),
                      vy=random.choice([-1,1])*random.uniform(0.3,1.0),
                      size=random.choice([28,34,40]))
        obstacles.add(ob); all_sprites.add(ob)

    # players
    p1 = Plane(180, SCREEN_H//2, (255,100,100), (255,180,180), controls=CONTROLS_1, is_ai=False)
    planes.add(p1); all_sprites.add(p1)
    p2 = None; ai = None
    if mode_index >= 1:
        p2 = Plane(300, SCREEN_H//2 + 60, (100,150,255), (180,220,255), controls=CONTROLS_2, is_ai=False)
        planes.add(p2); all_sprites.add(p2)
    if mode_index == 2:
        ai = Plane(420, SCREEN_H//2 - 60, (255,250,140), (255,230,140), controls=None, is_ai=True)
        planes.add(ai); all_sprites.add(ai)

    running = True
    game_over = False

    spawn_barrel_cooldown = 0
    spawn_obs_cooldown = 0

    while running:
        dt = clock.tick(FPS) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.USEREVENT + 1:
                # spawn new barrel periodically
                b = Barrel(random.randint(80, SCREEN_W-80), random.randint(80, SCREEN_H-80), bonus=(random.random()<0.18))
                barrels.add(b); all_sprites.add(b)
            if ev.type == pygame.USEREVENT + 2:
                ob = Obstacle(random.randint(80, SCREEN_W-80), random.randint(80, SCREEN_H-80),
                              vx=random.choice([-1,1])*random.uniform(0.6,1.4),
                              vy=random.choice([-1,1])*random.uniform(0.3,1.0),
                              size=random.choice([28,34,40]))
                obstacles.add(ob); all_sprites.add(ob)

        keys = pygame.key.get_pressed()
        # update terrain
        terrain.update(speed=3.0)

        # update sprites: obstacles independent, planes require groups ref
        obstacles.update()
        for pl in list(planes):
            if pl.is_ai:
                pl.update(keys=None, barrels_group=barrels, obstacles_group=obstacles, players_group=planes)
            else:
                pl.update(keys=keys, barrels_group=barrels, obstacles_group=obstacles, players_group=planes)

        # collision plane <-> barrel
        for pl in list(planes):
            hits = pygame.sprite.spritecollide(pl, barrels, dokill=True)
            for b in hits:
                if getattr(b, "bonus", False):
                    pl.score += 50
                    pl.refuel(60.0)
                else:
                    pl.score += 10
                    pl.refuel(40.0)
                # optional: spawn small sparkle (not implemented for simplicity)

        # plane <-> obstacle => IMMEDIATE KONIEC dla wszystkich graczy (spec req)
        someone_hit = None
        for pl in list(planes):
            if pygame.sprite.spritecollideany(pl, obstacles):
                someone_hit = pl
                break
        if someone_hit:
            # koniec gry natychmiast
            game_over = True
            running = False
            # prepare scores: collect only human players
            total_scores = []
            for idx, pl in enumerate(planes):
                if not pl.is_ai:
                    label = f"Player{idx+1}"
                    total_scores.append((label, int(pl.score)))
            # call input name and save
            enter_name_and_save(total_scores)
            break

        # fuel decreases over time for humans and AI
        for pl in planes:
            pl.fuel = max(0.0, pl.fuel - 0.03)
        # check if all human players out of fuel => game over
        humans = [p for p in planes if not p.is_ai]
        if humans and all(h.fuel <= 0 for h in humans):
            total_scores = [(f"Player{idx+1}", int(p.score)) for idx,p in enumerate(planes) if not p.is_ai]
            enter_name_and_save(total_scores)
            break

        # Draw everything
        terrain.draw(screen)
        # draw barrels and obstacles and planes (planes updated already)
        for spr in all_sprites:
            # some sprites like obstacles move, so draw from their current image/rect
            screen.blit(spr.image, spr.rect)
        # draw planes (their image includes rotation & bob)
        for pl in planes:
            screen.blit(pl.image, pl.rect)

        # HUD
        # display fuel & score for humans
        hud_x = 12
        hud_y = 12
        i = 0
        for pl in planes:
            label = "AI" if pl.is_ai else f"P{i+1}"
            # frame
            pygame.draw.rect(screen, WHITE, (hud_x + i*260, hud_y, 240, 44), border_radius=8)
            # fill fuel bar
            pygame.draw.rect(screen, (220,220,220), (hud_x + 10 + i*260, hud_y + 8, 160, 24), border_radius=6)
            fuel_w = int((pl.fuel/100.0) * 160)
            pygame.draw.rect(screen, (80,200,120), (hud_x + 10 + i*260, hud_y + 8, fuel_w, 24), border_radius=6)
            # score text
            s1 = SMALL.render(f"{label}", True, TEXT_COLOR)
            s2 = SMALL.render(f"Score: {int(pl.score)}", True, TEXT_COLOR)
            screen.blit(s1, (hud_x + 176 + i*260, hud_y + 6))
            screen.blit(s2, (hud_x + 176 + i*260, hud_y + 22))
            i += 1

        pygame.display.flip()

    # after loop -> return to menu
    return

def main():
    while True:
        sel = start_menu_loop()
        if sel == 3:
            pygame.quit(); sys.exit()
        game_loop(sel)

if __name__ == "__main__":
    main()
