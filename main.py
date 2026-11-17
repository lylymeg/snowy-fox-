import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snowy Fox & Footprints Simulator")
clock = pygame.time.Clock()

# Couleurs (Thème Nuit Polaire & Douceur Hivernale)
BG_COLOR = (16, 22, 36)
SNOW_GROUND = (222, 232, 245)
SNOW_SHADOW = (182, 198, 222)
FOX_ORANGE = (238, 128, 52)
FOX_DARK = (175, 78, 28)
FOX_WHITE = (250, 248, 255)
BERRY_RED = (240, 65, 95)
TEXT_COLOR = (242, 246, 255)
GRAY = (130, 145, 170)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

class Snowflake:
    def __init__(self, x=None, y=None, big=False):
        self.x = float(x if x is not None else random.uniform(0, WIDTH))
        self.y = float(y if y is not None else random.uniform(75, HEIGHT))
        self.radius = random.uniform(3.5, 5.5) if big else random.uniform(1.5, 3.2)
        self.speed_y = random.uniform(1.2, 2.6) if big else random.uniform(0.8, 1.8)
        self.sway_phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.sway_phase += 0.04
        self.x += math.sin(self.sway_phase) * 0.6
        self.y += self.speed_y
        self.x %= WIDTH

class Footprint:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.alpha = 190

    def update(self):
        self.alpha = max(0, self.alpha - 0.35)

    def draw(self, surface):
        if self.alpha <= 4:
            return
        a = int(self.alpha)
        fp_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(fp_surf, (130, 150, 185, a), (3, 5, 10, 7))
        surface.blit(fp_surf, (int(self.x) - 8, int(self.y) - 8))

class Berry:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.bob = random.uniform(0, math.pi * 2)

    def update(self):
        self.bob += 0.07

    def draw(self, surface):
        by = int(self.y + math.sin(self.bob) * 2)
        pygame.draw.circle(surface, (75, 165, 95), (int(self.x) - 3, by - 5), 4)
        pygame.draw.circle(surface, BERRY_RED, (int(self.x), by), 5)
        pygame.draw.circle(surface, (255, 180, 195), (int(self.x) - 1, by - 2), 2)

class Fox:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
        self.facing_right = True
        self.step_timer = 0
        self.walk_phase = 0.0
        self.wait_timer = random.randint(40, 110)

    def pick_new_target(self):
        self.target_x = random.uniform(110, WIDTH - 110)
        self.target_y = random.uniform(HEIGHT - 195, HEIGHT - 55)

    def update(self, berries, footprints):
        # Si une baie est disponible, le renard s'en approche doucement
        target_berry = None
        if berries:
            target_berry = min(berries, key=lambda b: math.hypot(b.x - self.x, b.y - self.y))
            self.target_x, self.target_y = target_berry.x, target_berry.y
        else:
            self.wait_timer -= 1
            if self.wait_timer <= 0:
                self.wait_timer = random.randint(70, 150)
                self.pick_new_target()

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 6:
            self.facing_right = dx >= 0
            speed = 1.7
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
            self.walk_phase += 0.22

            self.step_timer += 1
            if self.step_timer >= 14:
                self.step_timer = 0
                footprints.append(Footprint(self.x, self.y + 10, math.atan2(dy, dx)))

        # Manger la baie si elle est atteinte
        if target_berry and dist < 16:
            berries.remove(target_berry)
            self.pick_new_target()

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        bob = int(math.sin(self.walk_phase) * 2.5)
        dir_sign = 1 if self.facing_right else -1

        # Queue touffue avec bout blanc
        tail_x = cx - dir_sign * 20
        tail_y = cy - 4 + bob
        pygame.draw.ellipse(surface, FOX_ORANGE, (tail_x - 14, tail_y - 7, 28, 14))
        tip_x = tail_x - dir_sign * 10
        pygame.draw.circle(surface, FOX_WHITE, (tip_x, tail_y), 5)

        # Corps du renard
        pygame.draw.ellipse(surface, FOX_ORANGE, (cx - 16, cy - 10 + bob, 32, 18))

        # Petites pattes
        leg_offset = int(math.sin(self.walk_phase) * 4)
        pygame.draw.line(surface, FOX_DARK, (cx - 8 + leg_offset, cy + 6), (cx - 8 + leg_offset, cy + 14), 3)
        pygame.draw.line(surface, FOX_DARK, (cx + 8 - leg_offset, cy + 6), (cx + 8 - leg_offset, cy + 14), 3)

        # Tête et oreilles pointues
        head_x = cx + dir_sign * 13
        head_y = cy - 11 + bob
        pygame.draw.circle(surface, FOX_ORANGE, (head_x, head_y), 10)
        pygame.draw.polygon(surface, FOX_ORANGE, [
            (head_x - dir_sign * 6, head_y - 6),
            (head_x - dir_sign * 9, head_y - 18),
            (head_x - dir_sign * 1, head_y - 9)
        ])
        pygame.draw.polygon(surface, FOX_ORANGE, [
            (head_x + dir_sign * 2, head_y - 7),
            (head_x + dir_sign * 1, head_y - 18),
            (head_x + dir_sign * 7, head_y - 8)
        ])

        # Museau blanc et petit nez
        snout_x = head_x + dir_sign * 7
        pygame.draw.circle(surface, FOX_WHITE, (snout_x, head_y + 2), 5)
        pygame.draw.circle(surface, (35, 30, 40), (head_x + dir_sign * 11, head_y + 1), 2)

        # Œil
        pygame.draw.circle(surface, (25, 25, 35), (head_x + dir_sign * 3, head_y - 2), 2)

# Initialisation
fox = Fox(WIDTH // 2, HEIGHT - 125)
snowflakes = [Snowflake() for _ in range(75)]
footprints = []
berries = [Berry(WIDTH // 2 + 120, HEIGHT - 110)]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mouse_pos[1] > 80:
                if mouse_pos[1] > HEIGHT - 210:
                    fox.target_x, fox.target_y = mouse_pos
                for _ in range(10):
                    snowflakes.append(Snowflake(mouse_pos[0] + random.randint(-30, 30), mouse_pos[1], big=True))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                bx = random.randint(100, WIDTH - 100)
                by = random.randint(HEIGHT - 190, HEIGHT - 55)
                berries.append(Berry(bx, by))
            elif event.key == pygame.K_r:
                footprints = []
                berries = []
                fox = Fox(WIDTH // 2, HEIGHT - 125)

    # Maintenir un flux doux de flocons
    if len(snowflakes) < 90 and random.random() < 0.35:
        snowflakes.append(Snowflake(y=75))

    for flake in snowflakes[:]:
        flake.update()
        if flake.y > HEIGHT:
            snowflakes.remove(flake)

    for fp in footprints[:]:
        fp.update()
        if fp.alpha <= 4:
            footprints.remove(fp)

    for berry in berries:
        berry.update()

    fox.update(berries, footprints)

    # --- RENDU GRAPHIQUE ---
    screen.fill(BG_COLOR)

    # Collines enneigées en arrière-plan
    pygame.draw.ellipse(screen, SNOW_SHADOW, (-80, HEIGHT - 250, 560, 150))
    pygame.draw.ellipse(screen, SNOW_SHADOW, (430, HEIGHT - 245, 620, 150))

    # Plaine enneigée au premier plan
    pygame.draw.rect(screen, SNOW_GROUND, (0, HEIGHT - 205, WIDTH, 205))
    pygame.draw.line(screen, (245, 250, 255), (0, HEIGHT - 205), (WIDTH, HEIGHT - 205), 3)

    # Traces de pattes dans la neige
    for fp in footprints:
        fp.draw(screen)

    # Baies rouges
    for berry in berries:
        berry.draw(screen)

    # Petit renard
    fox.draw(screen)

    # Flocons de neige
    for flake in snowflakes:
        pygame.draw.circle(screen, (245, 250, 255), (int(flake.x), int(flake.y)), int(flake.radius))

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("SNOWY FOX — PROMENADE HIVERNALE & TRACES", True, TEXT_COLOR)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Traces : {len(footprints)} | Baies : {len(berries)}", True, (255, 175, 110))
    screen.blit(stats_txt, (40, 42))

    inst_txt = font_small.render("CLIC GAUCHE : Guider / Neiger | B : Ajouter une baie | R : Reset", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 40, 42))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()