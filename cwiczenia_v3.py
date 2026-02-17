"""
==============================================
  SYMULATOR ĆWICZEŃ Z PIŁECZKĄ
  TRYB DEMO (5 powtórzeń) + TRYB GRY
==============================================
  STEROWANIE W GRZE:
    LEWA RĘKA  — W/A/S/D  (+Q/E: góra/dół)
    PRAWA RĘKA — ↑/←/↓/→  (+PgUp/Dn: góra/dół)
    SPACJA     — podaj piłkę
    1–5        — zmień ćwiczenie (wraca do demo)
    TAB        — pomiń demo
    R          — restart
    ESC        — wyjście
==============================================
"""

import pygame
import math
import sys

# ── Konfiguracja ──────────────────────────────────────────
W, H         = 1000, 720
FPS          = 60
HAND_SPEED   = 0.025
CATCH_RADIUS = 0.28
PASS_SPEED   = 0.045
DEMO_REPS    = 5       # ile auto-powtórzeń w demo
DEMO_SPEED   = 0.013   # prędkość animacji demo

# Kolory
BG         = (10, 14, 24)
MAT_DARK   = (26, 74, 58)
MAT_LIGHT  = (36, 104, 78)
MAT_LINE   = (42, 122, 92)
SKIN       = (228, 183, 138)
SKIN_SH    = (182, 138, 92)
SKIN_MID   = (210, 165, 118)
SKIN_LT    = (242, 205, 162)
CLOTH      = (52, 72, 145)
CLOTH_SH   = (35, 50, 102)
HAIR       = (42, 28, 14)
HAIR_LT    = (62, 44, 22)
BEARD      = (55, 36, 18)
EYE_COL    = (45, 30, 20)
BALL_COL   = (218, 55, 45)
BALL_SHIN  = (255, 120, 100)
BALL_SH    = (125, 22, 15)
UI_ACC     = (70, 202, 145)
UI_ACC2    = (255, 195, 60)
UI_TEXT    = (212, 230, 218)
UI_DIM     = (88, 112, 102)
UI_WARN    = (230, 80, 60)
UI_GOOD    = (80, 220, 120)
UI_DEMO    = (160, 120, 255)
WHITE      = (255, 255, 255)
HAND_L_COL = (100, 200, 255)
HAND_R_COL = (255, 180, 80)

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Symulator Ćwiczeń z Piłeczką")
clock  = pygame.time.Clock()

try:
    font_title = pygame.font.SysFont("DejaVu Sans", 24, bold=True)
    font_label = pygame.font.SysFont("DejaVu Sans", 16)
    font_small = pygame.font.SysFont("DejaVu Sans", 13)
    font_key   = pygame.font.SysFont("DejaVu Sans Mono", 13, bold=True)
    font_big   = pygame.font.SysFont("DejaVu Sans", 42, bold=True)
    font_med   = pygame.font.SysFont("DejaVu Sans", 26, bold=True)
    font_demo  = pygame.font.SysFont("DejaVu Sans", 32, bold=True)
except:
    font_title = pygame.font.SysFont(None, 26, bold=True)
    font_label = pygame.font.SysFont(None, 18)
    font_small = pygame.font.SysFont(None, 15)
    font_key   = pygame.font.SysFont(None, 15, bold=True)
    font_big   = pygame.font.SysFont(None, 46, bold=True)
    font_med   = pygame.font.SysFont(None, 28, bold=True)
    font_demo  = pygame.font.SysFont(None, 34, bold=True)

# ════════════════════════════════════════════════════════
#  PSEUDO-3D
# ════════════════════════════════════════════════════════
ORIGIN = (W // 2, H // 2 + 35)
SCALE  = 130
PERSP  = 0.55

def proj(x, y, z):
    sx = ORIGIN[0] + x * SCALE
    sy = ORIGIN[1] - y * SCALE + z * SCALE * PERSP
    return (int(sx), int(sy))

def lerp(a, b, t):
    return a + (b - a) * t

def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def dist3(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ════════════════════════════════════════════════════════
#  STAŁE
# ════════════════════════════════════════════════════════
SHOULDER_L = (-0.44, 0.08, 0.90)
SHOULDER_R = ( 0.44, 0.08, 0.90)
HAND_LIMITS = {
    "L": {"x": (-1.25, 0.10), "y": (0.02, 0.55), "z": (-0.60, 2.20)},
    "R": {"x": (-0.10, 1.25), "y": (0.02, 0.55), "z": (-0.60, 2.20)},
}

# ════════════════════════════════════════════════════════
#  ĆWICZENIA
# ════════════════════════════════════════════════════════
EXERCISES = {
    1: {
        "name": "Boki – lewa ↔ prawa",
        "desc": "Podawaj poziomo nad głową, ręce na boki",
        "targets": [
            {"pos": (-1.05, 0.28, 1.88), "hold": "L"},
            {"pos": ( 1.05, 0.28, 1.88), "hold": "R"},
        ],
        "hint_l": "Lewa ręka wyciągnięta w bok, przyjmij piłkę",
        "hint_r": "Prawa ręka wyciągnięta w bok, przyjmij piłkę",
    },
    2: {
        "name": "Wzdłuż tułowia",
        "desc": "Podawaj wzdłuż ciała od stóp do głowy",
        "targets": [
            {"pos": (-0.12, 0.18, -0.45), "hold": "L"},
            {"pos": ( 0.12, 0.18,  1.90), "hold": "R"},
        ],
        "hint_l": "Lewa ręka przy stopach – przejmij piłkę",
        "hint_r": "Prawa ręka nad głową – przyjmij i podaj",
    },
    3: {
        "name": "Kąt prosty 90°",
        "desc": "W górę wzdłuż ciała, potem w bok – kąt 90°",
        "targets": [
            {"pos": (-0.12, 0.18, -0.45), "hold": "L"},
            {"pos": (-0.12, 0.28,  1.90), "hold": "L"},
            {"pos": ( 1.05, 0.28,  1.88), "hold": "R"},
            {"pos": ( 0.12, 0.18,  1.88), "hold": "R"},
            {"pos": (-1.05, 0.28,  1.88), "hold": "L"},
        ],
        "hint_l": "Lewa prowadzi piłkę w górę i odbiera z boku",
        "hint_r": "Prawa odbiera z boku i przekazuje z powrotem",
    },
    4: {
        "name": "Ósemka",
        "desc": "Piłka opisuje ósemkę między rękami",
        "targets": [
            {"pos": (-0.80, 0.22,  0.25), "hold": "L"},
            {"pos": ( 0.80, 0.22,  1.05), "hold": "R"},
            {"pos": (-0.80, 0.22,  1.05), "hold": "L"},
            {"pos": ( 0.80, 0.22,  0.25), "hold": "R"},
        ],
        "hint_l": "Lewa chwyta w dole i górze ósemki",
        "hint_r": "Prawa chwyta w górze i dole ósemki",
    },
    5: {
        "name": "Krążenie wokół głowy",
        "desc": "Piłka obiega głowę eliptycznie dookoła",
        "targets": [
            {"pos": (-0.68, 0.28, 1.62), "hold": "L"},
            {"pos": ( 0.00, 0.34, 2.15), "hold": "R"},
            {"pos": ( 0.68, 0.28, 1.62), "hold": "R"},
            {"pos": ( 0.00, 0.20, 1.18), "hold": "L"},
        ],
        "hint_l": "Lewa: lewa strona i dół obiegu",
        "hint_r": "Prawa: góra i prawa strona obiegu",
    },
}

# ════════════════════════════════════════════════════════
#  DEMO: pozycje automatyczne (jak w cwiczenia_final)
# ════════════════════════════════════════════════════════

def demo_get_positions(t, exercise):
    ping = t * 2 if t < 0.5 else (1 - t) * 2
    ep   = ease_in_out(ping)

    if exercise == 1:
        bx = lerp(-1.05, 1.05, ep)
        by = 0.20 + math.sin(ep * math.pi) * 0.28
        return (-1.05, 0.12, 1.88), (1.05, 0.12, 1.88), (bx, by, 1.90)

    elif exercise == 2:
        bz = lerp(-0.45, 1.90, ep)
        by = 0.15 + math.sin(ep * math.pi) * 0.28
        bx = lerp(-0.12, 0.12, ep)
        return (-0.15, 0.12, bz), (0.15, 0.12, bz), (bx, by, bz)

    elif exercise == 3:
        phase = (t * 4) % 4
        if phase < 1:
            p = ease_in_out(phase)
            bx, bz = 0.0, lerp(0.0, 1.90, p)
            by = 0.12 + p * 0.18
            lh = (-0.18, by - 0.05, bz); rh = (1.02, 0.12, 1.88)
        elif phase < 2:
            p = ease_in_out(phase - 1)
            bx = lerp(0.0, 1.10, p); bz = 1.90
            by = 0.30 + math.sin(p * math.pi) * 0.20
            lh = (-0.18, 0.12, 1.88); rh = (bx + 0.05, by - 0.05, bz)
        elif phase < 3:
            p = ease_in_out(phase - 2)
            bx, bz = 0.0, lerp(1.90, 0.0, p)
            by = 0.30 - p * 0.18
            rh = (0.18, by - 0.05, bz); lh = (-1.02, 0.12, 1.88)
        else:
            p = ease_in_out(phase - 3)
            bx = lerp(0.0, -1.10, p); bz = 1.90
            by = 0.30 + math.sin(p * math.pi) * 0.20
            rh = (0.18, 0.12, 1.88); lh = (bx - 0.05, by - 0.05, bz)
        return lh, rh, (bx, by, bz)

    elif exercise == 4:
        angle = t * math.pi * 2
        bx = math.sin(angle) * 0.75
        bz = math.cos(angle * 2) * 0.55 + 0.60
        by = 0.26 + math.sin(angle * 2) * 0.14
        return (bx - 0.12, by - 0.05, bz), (bx + 0.12, by - 0.05, bz), (bx, by, bz)

    elif exercise == 5:
        angle = t * math.pi * 2
        bx = math.cos(angle) * 0.65
        bz = 1.70 + math.sin(angle) * 0.46
        by = 0.22 + abs(math.sin(angle)) * 0.16
        if bx < 0:
            lh = (bx - 0.05, by - 0.04, bz); rh = (0.88, 0.10, 1.78)
        else:
            lh = (-0.88, 0.10, 1.78);         rh = (bx + 0.05, by - 0.04, bz)
        return lh, rh, (bx, by, bz)

    return (-0.5, 0.1, 1.5), (0.5, 0.1, 1.5), (0, 0.3, 1.5)


# ════════════════════════════════════════════════════════
#  RYSOWANIE MATTY
# ════════════════════════════════════════════════════════

def draw_mat():
    pts = [proj(-1.45, -0.02, -2.5), proj(1.45, -0.02, -2.5),
           proj(1.45,  -0.02,  2.8), proj(-1.45, -0.02,  2.8)]
    pygame.draw.polygon(screen, MAT_DARK, pts)
    for xi in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        pygame.draw.line(screen, MAT_LINE,
                         proj(xi, -0.02, -2.5), proj(xi, -0.02, 2.8), 1)
    for zi in [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
        pygame.draw.line(screen, MAT_LINE,
                         proj(-1.45, -0.02, zi), proj(1.45, -0.02, zi), 1)
    pygame.draw.polygon(screen, MAT_LIGHT, pts, 2)


# ════════════════════════════════════════════════════════
#  GŁOWA – REALISTYCZNY WIDOK Z GÓRY
#  Człowiek leży na plecach, patrzymy z góry-przodu.
#  Widoczna: czubek głowy z włosami, uszy, lekkie zarysowanie
#  brwi, nosa i ust przy dole elipsy (strona szyi).
# ════════════════════════════════════════════════════════

def draw_head():
    """
    Głowa w widoku pseudo-3D (leżąca, patrzymy z góry-ukos).
    Oś głowy: Z=1.45 (szyja) do Z=2.05 (czubek).
    X=0 = środek. Y=0 = płaszczyzna maty.
    """
    cx, cy = proj(0, 0.04, 1.75)   # centrum głowy (lekko uniesiona)

    # ── Główna elipsa czaszki ──────────────────────────────
    # Widok ukośny z góry: szersza w X, węższa w Z (spłaszczona perspektywą)
    ew, eh = 68, 50
    # Cień/głębokość pod głową
    pygame.draw.ellipse(screen, (15, 20, 15), (cx - ew//2 + 3, cy - eh//2 + 5, ew, eh))
    # Skóra głowy (potylica widoczna z góry)
    pygame.draw.ellipse(screen, SKIN_MID, (cx - ew//2, cy - eh//2, ew, eh))

    # ── Włosy – pokrywają większość czaszki (widok z góry) ──
    # Główna masa włosów: elipsa nieco mniejsza niż czaszka ale z wystawaniem
    hw, hh = 66, 48
    # Tło włosów (ciemna masa)
    pygame.draw.ellipse(screen, HAIR, (cx - hw//2, cy - hh//2 - 2, hw, hh))
    # Odrobina połysku na włosach
    pygame.draw.ellipse(screen, HAIR_LT,
                        (cx - hw//2 + 8, cy - hh//2 + 4, hw - 20, (hh - 14)//2))

    # ── Strefa twarzy – widoczna przy szyi (dół elipsy) ──
    # W widoku z góry-ukos widzimy część czoła i zarys nosa
    # "Twarz" to pas w dolnej 1/3 elipsy głowy
    face_rect = (cx - 28, cy + 2, 56, 28)
    pygame.draw.ellipse(screen, SKIN, face_rect)

    # ── Uszy (wystają po bokach) ──────────────────────────
    for ex_off, ew2 in [(-ew//2 - 4, 1), (ew//2 - 4, -1)]:
        ear_cx = cx + ex_off
        ear_cy = cy - 2
        pygame.draw.ellipse(screen, SKIN,    (ear_cx - 5, ear_cy - 8, 10, 16))
        pygame.draw.ellipse(screen, SKIN_SH, (ear_cx - 4, ear_cy - 5,  7, 11))
        # wewnętrzna małżowina
        pygame.draw.ellipse(screen, SKIN_MID,(ear_cx - 3, ear_cy - 4,  5,  9), 1)

    # ── Brwi (widoczne na granicy włosów/czoła) ───────────
    brow_y = cy + 6
    for bx_off in [-14, 14]:
        bx = cx + bx_off
        pygame.draw.line(screen, BEARD, (bx - 9, brow_y), (bx + 9, brow_y + 1), 2)

    # ── Nos – tylko zarys/cień widziany z góry ────────────
    nose_y = cy + 14
    # Grzbiet nosa – linia
    pygame.draw.line(screen, SKIN_SH, (cx, cy + 8), (cx, nose_y), 2)
    # Końcówka nosa – okrągły kształt
    pygame.draw.ellipse(screen, SKIN_SH, (cx - 5, nose_y - 3, 10, 8))
    # Nozdrza
    pygame.draw.circle(screen, SKIN_SH, (cx - 4, nose_y + 1), 2)
    pygame.draw.circle(screen, SKIN_SH, (cx + 4, nose_y + 1), 2)

    # ── Usta – wąska linia przy krawędzi twarzy ───────────
    mouth_y = cy + 22
    pygame.draw.line(screen, (165, 105, 85),
                     (cx - 9, mouth_y), (cx + 9, mouth_y), 2)
    # Kąciki ust
    pygame.draw.circle(screen, (155, 95, 75), (cx - 9, mouth_y), 2)
    pygame.draw.circle(screen, (155, 95, 75), (cx + 9, mouth_y), 2)

    # ── Kontur twarzy (krawędź żuchwy) ────────────────────
    pygame.draw.arc(screen, SKIN_SH,
                    (cx - 28, cy + 2, 56, 28), math.pi, 2 * math.pi, 1)

    # ── Obramowanie czaszki ───────────────────────────────
    pygame.draw.ellipse(screen, SKIN_SH, (cx - ew//2, cy - eh//2, ew, eh), 1)


def draw_body():
    """Tułów + nogi + głowa leżącej postaci."""
    # Nogi
    for sx in [-0.22, 0.22]:
        pygame.draw.polygon(screen, CLOTH, [
            proj(sx-0.10, 0, -0.5),  proj(sx+0.10, 0, -0.5),
            proj(sx+0.10, 0, -1.90), proj(sx-0.10, 0, -1.90)])
        pygame.draw.polygon(screen, CLOTH_SH, [
            proj(sx-0.10, 0, -0.5),  proj(sx+0.10, 0, -0.5),
            proj(sx+0.10, 0, -1.90), proj(sx-0.10, 0, -1.90)], 2)
        pygame.draw.polygon(screen, CLOTH, [
            proj(sx-0.08, 0, -1.90), proj(sx+0.08, 0, -1.90),
            proj(sx+0.07, 0, -2.72), proj(sx-0.07, 0, -2.72)])
        pygame.draw.polygon(screen, SKIN, [
            proj(sx-0.09, 0, -2.67), proj(sx+0.09, 0, -2.67),
            proj(sx+0.12, 0.03, -3.02), proj(sx-0.06, 0.03, -3.02)])
    # Tułów
    pygame.draw.polygon(screen, CLOTH, [
        proj(-0.35, 0, -0.5), proj(0.35, 0, -0.5),
        proj(0.30,  0,  1.05), proj(-0.30, 0,  1.05)])
    pygame.draw.polygon(screen, CLOTH_SH, [
        proj(-0.35, 0, -0.5), proj(0.35, 0, -0.5),
        proj(0.30,  0,  1.05), proj(-0.30, 0,  1.05)], 2)
    # Barki
    for sx in [-0.42, 0.42]:
        pygame.draw.polygon(screen, CLOTH, [
            proj(sx-0.10, 0, 0.75), proj(sx+0.10, 0, 0.75),
            proj(sx+0.10, 0, 1.12), proj(sx-0.10, 0, 1.12)])
        pygame.draw.polygon(screen, CLOTH_SH, [
            proj(sx-0.10, 0, 0.75), proj(sx+0.10, 0, 0.75),
            proj(sx+0.10, 0, 1.12), proj(sx-0.10, 0, 1.12)], 1)
    # Szyja
    pygame.draw.polygon(screen, SKIN, [
        proj(-0.10, 0, 1.02), proj(0.10, 0, 1.02),
        proj(0.10,  0, 1.24), proj(-0.10, 0, 1.24)])
    # Głowa
    draw_head()


def draw_arm_3d(shoulder_3d, hand_3d, is_left, highlight_col=None):
    s_2d = proj(*shoulder_3d)
    h_2d = proj(*hand_3d)
    elbow_off = 0.18 if is_left else -0.18
    ex_ = (shoulder_3d[0] + hand_3d[0]) / 2 + elbow_off
    ey_ = (shoulder_3d[1] + hand_3d[1]) / 2 + 0.10
    ez_ = (shoulder_3d[2] + hand_3d[2]) / 2
    e_2d = proj(ex_, ey_, ez_)
    pygame.draw.line(screen, SKIN_SH, s_2d, e_2d, 12)
    pygame.draw.line(screen, SKIN,    s_2d, e_2d,  9)
    pygame.draw.line(screen, SKIN_SH, e_2d, h_2d, 10)
    pygame.draw.line(screen, SKIN,    e_2d, h_2d,  7)
    col = highlight_col if highlight_col else SKIN
    pygame.draw.circle(screen, col,     h_2d, 11)
    pygame.draw.circle(screen, SKIN_SH, h_2d, 11, 2)


def draw_ball_at(pos3d):
    sp = proj(pos3d[0], -0.01, pos3d[2])
    h  = max(0, pos3d[1])
    sh_a = max(15, int(90 - h * 120))
    sh = pygame.Surface((36, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, sh_a), (0, 0, 36, 14))
    screen.blit(sh, (sp[0]-18, sp[1]-7))
    bp = proj(*pos3d)
    r  = 16
    pygame.draw.circle(screen, BALL_SH,  (bp[0]+2, bp[1]+3), r)
    pygame.draw.circle(screen, BALL_COL,  bp, r)
    pygame.draw.circle(screen, BALL_SHIN, (bp[0]-5, bp[1]-5), r//3+1)


# ════════════════════════════════════════════════════════
#  TRAIL
# ════════════════════════════════════════════════════════

class Trail:
    def __init__(self, maxlen=42):
        self.pts = []
        self.maxlen = maxlen

    def add(self, pos):
        self.pts.append(tuple(pos))
        if len(self.pts) > self.maxlen:
            self.pts.pop(0)

    def clear(self):
        self.pts.clear()

    def draw(self):
        n = len(self.pts)
        if n < 2:
            return
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        for i in range(1, n):
            ratio = i / n
            a = int(145 * ratio)
            w = max(1, int(4 * ratio))
            pygame.draw.line(surf, (*BALL_COL, a),
                             proj(*self.pts[i-1]), proj(*self.pts[i]), w)
        screen.blit(surf, (0, 0))


# ════════════════════════════════════════════════════════
#  TRYB DEMO
# ════════════════════════════════════════════════════════

class DemoMode:
    def __init__(self, exercise):
        self.exercise  = exercise
        self.t         = 0.0
        self.rep_count = 0         # ile pełnych cykli
        self.done      = False
        self._last_half = 0        # wykrywamy przejście przez 0.5 → nowe powtórzenie

    def update(self, dt):
        if self.done:
            return
        prev_t = self.t
        self.t += DEMO_SPEED
        # liczymy powtórzenia przez przejście granicy 0.0 (pełny cykl)
        cur_loop = int(self.t)
        prev_loop = int(prev_t)
        if cur_loop > prev_loop:
            self.rep_count = cur_loop
        if self.rep_count >= DEMO_REPS:
            self.done = True

    def get_positions(self):
        return demo_get_positions(self.t % 1.0, self.exercise)

    def reps_done(self):
        return min(self.rep_count, DEMO_REPS)


def draw_demo_overlay(demo):
    """Wyświetla planszę DEMO z licznikiem powtórzeń i opisem."""
    ex     = demo.exercise
    ex_inf = EXERCISES[ex]
    reps   = demo.reps_done()

    # ── Górny baner ──────────────────────────────────────
    ph = 80
    p  = pygame.Surface((W, ph), pygame.SRCALPHA)
    p.fill((8, 12, 22, 225))
    screen.blit(p, (0, 0))
    pygame.draw.rect(screen, UI_DEMO, (0, 0, 5, ph))

    demo_lbl = font_demo.render("▶  DEMO  –  OBSERWUJ RUCH PIŁKI", True, UI_DEMO)
    screen.blit(demo_lbl, (18, 8))
    ex_s = font_label.render(
        f"Ćwiczenie {ex}: {ex_inf['name']}  —  {ex_inf['desc']}", True, UI_TEXT)
    screen.blit(ex_s, (18, 48))

    # Pomiń
    skip_s = font_key.render("[TAB] Pomiń demo  /  [ESC] Wyjście", True, UI_DIM)
    screen.blit(skip_s, (W - skip_s.get_width() - 16, 56))

    # ── Dolny baner ──────────────────────────────────────
    bh = 88
    bot = pygame.Surface((W, bh), pygame.SRCALPHA)
    bot.fill((8, 12, 22, 225))
    screen.blit(bot, (0, H - bh))
    pygame.draw.rect(screen, UI_DEMO, (0, H - bh, 5, bh))

    # Opis kroków
    desc_lines = [
        ex_inf["hint_l"],
        ex_inf["hint_r"],
    ]
    for i, line in enumerate(desc_lines):
        col = HAND_L_COL if i == 0 else HAND_R_COL
        s = font_small.render(("🫲 " if i == 0 else "🫱 ") + line, True, col)
        screen.blit(s, (18, H - bh + 8 + i * 18))

    # Licznik powtórzeń (kółka)
    cx0  = W // 2 - (DEMO_REPS * 28) // 2
    cy0  = H - bh + 54
    rep_lbl = font_label.render("Powtórzenia: ", True, UI_DIM)
    screen.blit(rep_lbl, (cx0 - rep_lbl.get_width() - 6, cy0 - 8))
    for i in range(DEMO_REPS):
        filled = i < reps
        col    = UI_DEMO if filled else (40, 55, 50)
        brd    = UI_DEMO if filled else UI_DIM
        pygame.draw.circle(screen, col, (cx0 + i * 28, cy0), 10)
        pygame.draw.circle(screen, brd, (cx0 + i * 28, cy0), 10, 2)
        if filled:
            pygame.draw.circle(screen, WHITE, (cx0 + i * 28 - 3, cy0 - 3), 3)

    # Komunikat po zakończeniu
    if demo.done:
        ready_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        ready_surf.fill((0, 0, 0, 90))
        screen.blit(ready_surf, (0, 0))
        t_s = font_big.render("GOTOWY? NACIŚNIJ  ENTER  aby grać!", True, UI_GOOD)
        screen.blit(t_s, (W//2 - t_s.get_width()//2, H//2 - t_s.get_height()//2))


# ════════════════════════════════════════════════════════
#  TRYB GRY – STAN
# ════════════════════════════════════════════════════════

class GameState:
    def __init__(self, exercise=1):
        self.exercise = exercise
        self.reset_round()

    def reset_round(self):
        self.lhand       = [-0.75, 0.20, 0.88]
        self.rhand       = [ 0.75, 0.20, 0.88]
        self.ball        = [-0.75, 0.26, 0.88]
        self.ball_holder = "L"
        self.ball_from   = None
        self._fly_dest   = "R"
        self.ball_t      = 0.0
        self.target_idx  = 0
        self.reps        = 0
        self.score       = 0
        self.combo       = 0
        self.best_combo  = 0
        self.flash_msg   = ""
        self.flash_timer = 0.0
        self.flash_color = UI_GOOD
        self.target_pulse = 0.0

    def current_target(self):
        targets = EXERCISES[self.exercise]["targets"]
        return targets[self.target_idx % len(targets)]

    def pass_ball(self):
        if self.ball_holder in ("L", "R"):
            dest             = "R" if self.ball_holder == "L" else "L"
            self.ball_from   = tuple(self.ball)
            self.ball_holder = "fly"
            self.ball_t      = 0.0
            self._fly_dest   = dest

    def update_ball_flight(self, dt):
        if self.ball_holder != "fly":
            return
        self.ball_t += dt * (PASS_SPEED * 60)
        dest_pos = self.rhand if self._fly_dest == "R" else self.lhand
        if self.ball_t >= 1.0:
            self.ball_t      = 1.0
            self.ball_holder = self._fly_dest
            self.ball        = list(dest_pos)
            self._check_target()
        else:
            te    = ease_in_out(self.ball_t)
            arc_h = 0.22 * math.sin(self.ball_t * math.pi)
            self.ball[0] = lerp(self.ball_from[0], dest_pos[0], te)
            self.ball[1] = lerp(self.ball_from[1], dest_pos[1], te) + arc_h
            self.ball[2] = lerp(self.ball_from[2], dest_pos[2], te)

    def _check_target(self):
        tgt      = self.current_target()
        d        = dist3(tuple(self.ball), tgt["pos"])
        holder_ok = (self.ball_holder == tgt["hold"])
        if d < 0.58 and holder_ok:
            self.target_idx  += 1
            self.combo        += 1
            self.best_combo   = max(self.best_combo, self.combo)
            pts               = 10 * self.combo
            self.score        += pts
            n_tgts = len(EXERCISES[self.exercise]["targets"])
            if self.target_idx % n_tgts == 0:
                self.reps       += 1
                self.flash_msg   = f"+{pts}   Powtórzenie {self.reps}!"
                self.flash_color = UI_GOOD
            else:
                self.flash_msg   = f"+{pts}   Combo ×{self.combo}!"
                self.flash_color = UI_ACC2
            self.flash_timer = 0.95
        else:
            self.combo        = 0
            self.flash_msg    = "Cel chybiony!"
            self.flash_color  = UI_WARN
            self.flash_timer  = 0.80

    def update(self, dt, keys):
        lim = HAND_LIMITS["L"]
        if keys[pygame.K_a]:  self.lhand[0] = clamp(self.lhand[0] - HAND_SPEED, *lim["x"])
        if keys[pygame.K_d]:  self.lhand[0] = clamp(self.lhand[0] + HAND_SPEED, *lim["x"])
        if keys[pygame.K_w]:  self.lhand[2] = clamp(self.lhand[2] + HAND_SPEED, *lim["z"])
        if keys[pygame.K_s]:  self.lhand[2] = clamp(self.lhand[2] - HAND_SPEED, *lim["z"])
        if keys[pygame.K_q]:  self.lhand[1] = clamp(self.lhand[1] + HAND_SPEED, *lim["y"])
        if keys[pygame.K_e]:  self.lhand[1] = clamp(self.lhand[1] - HAND_SPEED * 0.5, *lim["y"])

        lim = HAND_LIMITS["R"]
        if keys[pygame.K_LEFT]:     self.rhand[0] = clamp(self.rhand[0] - HAND_SPEED, *lim["x"])
        if keys[pygame.K_RIGHT]:    self.rhand[0] = clamp(self.rhand[0] + HAND_SPEED, *lim["x"])
        if keys[pygame.K_UP]:       self.rhand[2] = clamp(self.rhand[2] + HAND_SPEED, *lim["z"])
        if keys[pygame.K_DOWN]:     self.rhand[2] = clamp(self.rhand[2] - HAND_SPEED, *lim["z"])
        if keys[pygame.K_PAGEUP]:   self.rhand[1] = clamp(self.rhand[1] + HAND_SPEED, *lim["y"])
        if keys[pygame.K_PAGEDOWN]: self.rhand[1] = clamp(self.rhand[1] - HAND_SPEED * 0.5, *lim["y"])

        if self.ball_holder == "L":
            self.ball = [self.lhand[0], self.lhand[1] + 0.07, self.lhand[2]]
        elif self.ball_holder == "R":
            self.ball = [self.rhand[0], self.rhand[1] + 0.07, self.rhand[2]]

        self.update_ball_flight(dt)
        if self.flash_timer > 0:
            self.flash_timer -= dt
        self.target_pulse = (self.target_pulse + dt * 3.2) % (2 * math.pi)


# ════════════════════════════════════════════════════════
#  HUD TRYBU GRY
# ════════════════════════════════════════════════════════

def draw_target_marker(gs):
    tgt   = gs.current_target()
    tp    = tgt["pos"]
    pulse = (math.sin(gs.target_pulse) + 1) / 2
    r     = int(12 + pulse * 7)
    alpha = int(95 + pulse * 110)

    sp   = proj(tp[0], -0.01, tp[2])
    s_el = pygame.Surface((52, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(s_el, (70, 205, 148, alpha // 2), (0, 0, 52, 20))
    screen.blit(s_el, (sp[0]-26, sp[1]-10))

    bp   = proj(*tp)
    s2   = pygame.Surface((r*2+10, r*2+10), pygame.SRCALPHA)
    pygame.draw.circle(s2, (70, 205, 148, alpha),   (r+5, r+5), r,   2)
    pygame.draw.circle(s2, (70, 205, 148, alpha//3), (r+5, r+5), r+5)
    screen.blit(s2, (bp[0]-r-5, bp[1]-r-5))

    col = HAND_L_COL if tgt["hold"] == "L" else HAND_R_COL
    lbl = font_small.render(tgt["hold"], True, col)
    screen.blit(lbl, (bp[0] - lbl.get_width()//2, bp[1] - r - 20))


def draw_game_hud(gs):
    ex_info = EXERCISES[gs.exercise]

    # ── Górny panel ──────────────────────────────────────
    ph = 78
    p  = pygame.Surface((W, ph), pygame.SRCALPHA)
    p.fill((8, 12, 22, 222))
    screen.blit(p, (0, 0))
    pygame.draw.rect(screen, UI_ACC, (0, 0, 5, ph))

    title_s = font_title.render("ĆWICZENIA Z PIŁECZKĄ  –  TRYB GRY", True, UI_ACC)
    screen.blit(title_s, (18, 8))
    ex_s = font_label.render(
        f"[{gs.exercise}]  {ex_info['name']}  —  {ex_info['desc']}", True, UI_TEXT)
    screen.blit(ex_s, (18, 46))

    # Wynik + combo
    sc_s = font_med.render(str(gs.score), True, UI_ACC2)
    screen.blit(sc_s, (W - sc_s.get_width() - 18, 5))
    lbl_s = font_small.render("WYNIK", True, UI_DIM)
    screen.blit(lbl_s, (W - lbl_s.get_width() - 18, 48))

    mid_x = W // 2
    rep_s = font_label.render(f"Powtórzenia: {gs.reps}", True, UI_TEXT)
    screen.blit(rep_s, (mid_x - rep_s.get_width() - 55, 10))
    cmb_col = UI_ACC2 if gs.combo >= 3 else UI_TEXT
    cmb_s = font_label.render(f"Combo: ×{gs.combo}", True, cmb_col)
    screen.blit(cmb_s, (mid_x - cmb_s.get_width() - 55, 32))
    bc_s = font_small.render(f"Rekord: ×{gs.best_combo}", True, UI_DIM)
    screen.blit(bc_s, (mid_x - bc_s.get_width() - 55, 54))

    # Flash
    if gs.flash_timer > 0:
        al = min(255, int(gs.flash_timer * 285))
        fs = font_big.render(gs.flash_msg, True, gs.flash_color)
        fx, fy = W//2 - fs.get_width()//2, H//2 - 85
        gl = pygame.Surface((fs.get_width()+34, fs.get_height()+22), pygame.SRCALPHA)
        gl.fill((0, 0, 0, min(185, al)))
        screen.blit(gl, (fx-17, fy-11))
        sf = pygame.Surface(fs.get_size(), pygame.SRCALPHA)
        sf.blit(fs, (0, 0))
        sf.set_alpha(al)
        screen.blit(sf, (fx, fy))

    # ── Dolny panel ──────────────────────────────────────
    bh  = 120
    bot = pygame.Surface((W, bh), pygame.SRCALPHA)
    bot.fill((8, 12, 22, 222))
    screen.blit(bot, (0, H - bh))
    pygame.draw.rect(screen, UI_ACC, (0, H - bh, 5, bh))

    y0 = H - bh + 5
    tgt = gs.current_target()
    hint = ex_info["hint_l"] if tgt["hold"] == "L" else ex_info["hint_r"]
    hcol = HAND_L_COL if tgt["hold"] == "L" else HAND_R_COL
    hs = font_small.render(f"►  {hint}", True, hcol)
    screen.blit(hs, (18, y0))

    ky = H - bh + 26
    _draw_ctrl_group(16,  ky, "LEWA  [WASD + Q/E]",
                     [("W","↑"),("A","←"),("S","↓"),("D","→"),("Q","↑Y"),("E","↓Y")],
                     HAND_L_COL, gs.ball_holder == "L")
    _draw_ctrl_group(245, ky, "PRAWA  [↑←↓→ + PgUp/Dn]",
                     [("↑","↑"),("←","←"),("↓","↓"),("→","→"),("Pg↑","↑Y"),("Pg↓","↓Y")],
                     HAND_R_COL, gs.ball_holder == "R")

    sp_col = UI_ACC if gs.ball_holder != "fly" else UI_DIM
    sp_s = font_key.render("[SPACJA] Podaj piłkę", True, sp_col)
    screen.blit(sp_s, (470, ky))

    ex_x = 470
    ex_y = ky + 22
    for i in range(1, 6):
        active = (i == gs.exercise)
        col    = UI_ACC if active else UI_DIM
        k_s    = font_key.render(f"[{i}]", True, col)
        n_s    = font_small.render(f" {EXERCISES[i]['name']}  ", True, col)
        screen.blit(k_s, (ex_x, ex_y))
        ex_x += k_s.get_width() + 2
        screen.blit(n_s, (ex_x, ex_y + 1))
        ex_x += n_s.get_width()

    for row, (k, d) in enumerate([("R", "Restart"), ("ESC", "Wyjście")]):
        ks = font_key.render(f"[{k}]", True, (85, 220, 165))
        ds = font_small.render(f" {d}", True, UI_DIM)
        screen.blit(ks, (W - 170, ky + row * 20))
        screen.blit(ds, (W - 170 + ks.get_width(), ky + row * 20 + 1))

    # Pasek celności
    holder   = tgt["hold"]
    hand_pos = gs.lhand if holder == "L" else gs.rhand
    d        = dist3(hand_pos, tgt["pos"])
    fill     = max(0.0, 1.0 - d / 2.0)
    bx, by2, bw, bhh = W - 200, H - bh + 68, 184, 11
    acc_lbl = font_small.render("Celność dłoni:", True, UI_DIM)
    screen.blit(acc_lbl, (bx, by2 - 16))
    pygame.draw.rect(screen, (28, 44, 38), (bx, by2, bw, bhh), border_radius=5)
    fc = UI_GOOD if fill > 0.65 else (UI_ACC2 if fill > 0.35 else UI_WARN)
    if fill > 0:
        pygame.draw.rect(screen, fc, (bx, by2, int(bw * fill), bhh), border_radius=5)
    pygame.draw.rect(screen, UI_DIM, (bx, by2, bw, bhh), 1, border_radius=5)

    # Catch-zone ring
    if gs.ball_holder == "fly":
        dest_h = gs.rhand if gs._fly_dest == "R" else gs.lhand
        hp     = proj(*dest_h)
        zr     = int(CATCH_RADIUS * SCALE * 0.68)
        zs     = pygame.Surface((zr*2+6, zr*2+6), pygame.SRCALPHA)
        za     = int(65 + 55 * math.sin(gs.target_pulse * 2))
        rc     = HAND_R_COL if gs._fly_dest == "R" else HAND_L_COL
        pygame.draw.circle(zs, (*rc, za), (zr+3, zr+3), zr, 2)
        screen.blit(zs, (hp[0]-zr-3, hp[1]-zr-3))


def _draw_ctrl_group(x, y, title, keys, col, active):
    ts = font_small.render(title, True, col if active else UI_DIM)
    screen.blit(ts, (x, y - 2))
    kx = x
    for k, desc in keys:
        ks = font_key.render(f"[{k}]", True, col if active else UI_DIM)
        ds = font_small.render(desc + " ", True, UI_DIM)
        screen.blit(ks, (kx, y + 16))
        screen.blit(ds, (kx, y + 34))
        kx += max(ks.get_width(), ds.get_width()) + 3


# ════════════════════════════════════════════════════════
#  PĘTLA GŁÓWNA
# ════════════════════════════════════════════════════════

def main():
    # Stan globalny
    mode      = "demo"   # "demo" | "game"
    exercise  = 1
    demo      = DemoMode(exercise)
    gs        = GameState(exercise)
    trail     = Trail()

    while True:
        dt   = min(clock.tick(FPS) / 1000.0, 0.05)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                # Zmiana ćwiczenia → zawsze wraca do demo
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                   pygame.K_4, pygame.K_5):
                    new_ex = int(event.unicode)
                    if new_ex != exercise or mode == "game":
                        exercise = new_ex
                        demo     = DemoMode(exercise)
                        gs       = GameState(exercise)
                        trail.clear()
                        mode = "demo"

                # Pomiń demo / przejdź do gry
                elif event.key in (pygame.K_TAB, pygame.K_RETURN):
                    if mode == "demo":
                        mode = "game"
                        gs   = GameState(exercise)
                        trail.clear()

                # Restart
                elif event.key == pygame.K_r:
                    demo  = DemoMode(exercise)
                    gs    = GameState(exercise)
                    trail.clear()
                    mode  = "demo"

                # Podanie (tylko w trybie gry)
                elif event.key == pygame.K_SPACE and mode == "game":
                    if gs.ball_holder != "fly":
                        gs.pass_ball()

        # ── UPDATE ────────────────────────────────────────
        if mode == "demo":
            demo.update(dt)
            if demo.done and keys[pygame.K_RETURN]:
                mode = "game"
                gs   = GameState(exercise)
                trail.clear()
        else:
            gs.update(dt, keys)
            trail.add(gs.ball)

        # ── RYSOWANIE ─────────────────────────────────────
        screen.fill(BG)
        draw_mat()
        draw_body()

        if mode == "demo":
            lh3, rh3, bpos = demo.get_positions()
            trail.add(bpos)
            trail.draw()
            draw_arm_3d(SHOULDER_L, lh3, is_left=True)
            draw_arm_3d(SHOULDER_R, rh3, is_left=False)
            draw_ball_at(bpos)
            draw_demo_overlay(demo)

        else:  # game
            draw_target_marker(gs)
            trail.draw()
            lh_col = HAND_L_COL if gs.ball_holder == "L" else None
            rh_col = HAND_R_COL if gs.ball_holder == "R" else None
            draw_arm_3d(SHOULDER_L, tuple(gs.lhand), is_left=True,  highlight_col=lh_col)
            draw_arm_3d(SHOULDER_R, tuple(gs.rhand), is_left=False, highlight_col=rh_col)
            draw_ball_at(gs.ball)
            draw_game_hud(gs)

        pygame.display.flip()


if __name__ == "__main__":
    main()
