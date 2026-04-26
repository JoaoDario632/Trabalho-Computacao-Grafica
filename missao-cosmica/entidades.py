import pygame
import math
import random

LARGURA, ALTURA = 900, 650

PRETO        = (0,   0,   0)
BRANCO       = (255, 255, 255)
AZUL_ESC     = (10,  10,  40)
AMARELO      = (255, 220,  50)
CIANO        = (0,   220, 255)
VERDE        = (50,  230,  80)
VERMELHO     = (255,  60,  60)
LARANJA      = (255, 150,  30)
ROXO         = (180,  60, 255)
CINZA        = (120, 120, 120)
CINZA_CLARO  = (200, 200, 210)
AZUL_INFO    = (80, 150, 255)


def criar_nave_surface(tamanho=40):
    s = tamanho
    surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
    cx, cy = s, s

    pontos_corpo = [
        (cx,          cy - s + 4),
        (cx - s + 8,  cy + s - 6),
        (cx + s - 8,  cy + s - 6),
    ]
    pygame.draw.polygon(surf, CIANO, pontos_corpo)
    pygame.draw.polygon(surf, BRANCO, pontos_corpo, 2)

    asa_esq = [
        (cx - 4,      cy + 4),
        (cx - s + 2,  cy + s - 4),
        (cx - s + 14, cy + s - 14),
    ]
    asa_dir = [
        (cx + 4,      cy + 4),
        (cx + s - 2,  cy + s - 4),
        (cx + s - 14, cy + s - 14),
    ]
    pygame.draw.polygon(surf, AZUL_INFO, asa_esq)
    pygame.draw.polygon(surf, AZUL_INFO, asa_dir)

    pygame.draw.circle(surf, LARANJA, (cx, cy + s - 8), 6)
    pygame.draw.circle(surf, AMARELO, (cx, cy + s - 8), 3)

    return surf


def criar_asteroide_surface(raio, cor_base):
    surf = pygame.Surface((raio * 2 + 4, raio * 2 + 4), pygame.SRCALPHA)
    cx, cy = raio + 2, raio + 2
    n_lados = random.randint(7, 11)
    pontos = []
    for i in range(n_lados):
        angulo = math.radians(360 / n_lados * i + random.uniform(-15, 15))
        r = raio * random.uniform(0.72, 1.0)
        px = cx + r * math.cos(angulo)
        py = cy + r * math.sin(angulo)
        pontos.append((px, py))
    pygame.draw.polygon(surf, cor_base, pontos)
    pygame.draw.polygon(surf, BRANCO, pontos, 2)
    for _ in range(3):
        ox = random.randint(cx - raio // 2, cx + raio // 2)
        oy = random.randint(cy - raio // 2, cy + raio // 2)
        pygame.draw.circle(
            surf,
            (cor_base[0] // 2, cor_base[1] // 2, cor_base[2] // 2),
            (ox, oy),
            random.randint(3, 6),
        )
    return surf


def criar_projetil_surface(poder, ang):
    l = 4 * 2 ** poder
    h = 10 * 2 ** poder

    surf = pygame.Surface((l, h), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, AMARELO, (0, 0, l, h))
    pygame.draw.ellipse(surf, BRANCO, (l // 4, h // 10, l // 2, h // 1.25))
    surf = pygame.transform.rotate(surf, ang)
    return surf


def criar_estrelas(n=120):
    estrelas = []
    for _ in range(n):
        x = random.randint(0, LARGURA)
        y = random.randint(0, ALTURA)
        brilho = random.randint(80, 255)
        raio = random.choice([1, 1, 1, 2])
        vel = random.uniform(0.2, 1.0)
        estrelas.append([x, y, brilho, raio, vel])
    return estrelas


class Nave:
    ESCALA_MIN = 0.5
    ESCALA_MAX = 2.0
    VEL_BASE = 5
    DURACAO_BONUS_TIRO = 10 * 60
    DURACAO_BONUS_VIDA = 60 * 60

    def __init__(self):
        self.x = LARGURA // 2
        self.y = ALTURA // 2
        self.angulo = 0
        self.escala = 1.0
        self.escala_key = 1
        self.escala_dict = {
            0: 0.5,
            1: 1.0,
            2: 2.0
        }
        self.flip_h = False
        self.flip_v = False
        self.tamanho_base = 40
        self.surf_original = criar_nave_surface(self.tamanho_base)
        self.surf_atual = self.surf_original
        self.rect = self.surf_atual.get_rect(center=(self.x, self.y))
        self.vidas = 3
        self.pontos = 0
        self.invencivel = 0
        self.efeito_motor = 0
        self.bonus_tiro_timer = 0
        self.bonus_vida_timer = 0

    @property
    def tamanho_atual(self):
        return int(self.tamanho_base * self.escala)

    @property
    def angulo_visual(self):
        ang = self.angulo

        if self.flip_h:
            ang = -ang

        if self.flip_v:
            ang = 180 - ang

        return ang % 360

    def _recalcular_surface(self):
        s = max(10, self.tamanho_atual)
        surf = pygame.transform.scale(self.surf_original, (s * 2, s * 2))
        surf = pygame.transform.rotate(surf, self.angulo_visual)

        self.surf_atual = surf
        self.rect = surf.get_rect(center=(self.x, self.y))

    def update(self, teclas):
        vel = self.VEL_BASE
        dx, dy = 0, 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx -= vel
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx += vel
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy -= vel
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy += vel

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.x = max(30, min(LARGURA - 30, self.x + dx))
        self.y = max(30, min(ALTURA - 30, self.y + dy))

        if self.invencivel > 0:
            self.invencivel -= 1

        if self.bonus_tiro_timer > 0:
            self.bonus_tiro_timer -= 1

        if self.bonus_vida_timer > 0:
            self.bonus_vida_timer -= 1

        self.efeito_motor = (self.efeito_motor + 1) % 10
        self._recalcular_surface()

    def rotacionar(self, delta):
        if self.flip_h and not self.flip_v or self.flip_v and not self.flip_h:
            delta *= -1
        self.angulo = (self.angulo + delta) % 360

    def escalar(self, alvo):
        escala_alvo = self.escala_key + alvo
        if 0 <= escala_alvo <= 2:
            self.escala_key = escala_alvo

    def escala_atual(self):
        return self.escala_dict[self.escala_key]

    def alternar_flip_h(self):
        self.flip_h = not self.flip_h

    def alternar_flip_v(self):
        self.flip_v = not self.flip_v

    def ativar_bonus_tiro(self):
        self.bonus_tiro_timer = self.DURACAO_BONUS_TIRO

    def ativar_bonus_vida(self):
        if self.vidas < 3:
            self.vidas += 1
            self.bonus_vida_timer = self.DURACAO_BONUS_VIDA

    def atirar(self):
        ang = self.angulo_visual
        vx = -math.sin(math.radians(ang)) * 12
        vy = -math.cos(math.radians(ang)) * 12
        return Projetil(self.x, self.y, vx, vy, self.escala_key, ang)

    def receber_dano(self):
        if self.invencivel == 0:
            self.vidas -= 1
            self.invencivel = 90
            return True
        return False

    def draw(self, surface):
        if self.invencivel > 0 and (self.invencivel // 6) % 2 == 0:
            return

        if self.efeito_motor < 5:
            t = self.tamanho_atual
            for i in range(3):
                r = random.randint(3, 8 + i * 3)
                ox = self.x + random.randint(-4, 4)
                oy = self.y + random.randint(t // 2 - 2, t // 2 + 6)
                cor = [LARANJA, AMARELO, VERMELHO][i]
                pygame.draw.circle(surface, cor, (ox, oy), r)

        surface.blit(self.surf_atual, self.rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.surf_atual)


class Asteroide:
    CORES = [
        (160, 120, 80),
        (130, 90, 60),
        (90, 90, 110),
        (100, 110, 80),
    ]

    def __init__(self, nivel=1):
        lado = random.choice(["top", "bottom", "left", "right"])
        if lado == "top":
            self.x, self.y = random.randint(0, LARGURA), -40
        elif lado == "bottom":
            self.x, self.y = random.randint(0, LARGURA), ALTURA + 40
        elif lado == "left":
            self.x, self.y = -40, random.randint(0, ALTURA)
        else:
            self.x, self.y = LARGURA + 40, random.randint(0, ALTURA)

        self.raio = random.randint(20, 45) + nivel * 2
        cor = random.choice(self.CORES)
        self.surf_original = criar_asteroide_surface(self.raio, cor)
        self.surf_atual = self.surf_original
        self.angulo = 0
        self.vel_rotacao = random.uniform(-2, 2)
        self.pontos_valor = max(10, 60 - self.raio)

        if self.raio < 37:
            self.vida = 4
        elif self.raio < 54:
            self.vida = 6
        else:
            self.vida = 8

        self.bonus_tiro = random.random() < 0.2
        self.bonus_vida = random.random() < 0.05

        ang = math.atan2(ALTURA // 2 - self.y, LARGURA // 2 - self.x)
        vel = random.uniform(1.5, 2.5 + nivel * 0.3)
        self.vx = math.cos(ang) * vel + random.uniform(-0.5, 0.5)
        self.vy = math.sin(ang) * vel + random.uniform(-0.5, 0.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angulo = (self.angulo + self.vel_rotacao) % 360
        self.surf_atual = pygame.transform.rotate(self.surf_original, self.angulo)

    @property
    def rect(self):
        return self.surf_atual.get_rect(center=(int(self.x), int(self.y)))

    def fora_da_tela(self):
        margem = self.raio + 60
        return (
            self.x < -margem
            or self.x > LARGURA + margem
            or self.y < -margem
            or self.y > ALTURA + margem
        )

    def colidir_com(self, outro_rect, outra_mask):
        r = self.rect
        offset = (outro_rect.x - r.x, outro_rect.y - r.y)
        minha_mask = pygame.mask.from_surface(self.surf_atual)
        return minha_mask.overlap(outra_mask, offset) is not None

    def draw(self, surface):
        surface.blit(self.surf_atual, self.rect.topleft)

        if self.bonus_tiro:
            pygame.draw.circle(surface, AMARELO, self.rect.center, max(8, self.raio // 2), 2)

        if self.bonus_vida:
            pygame.draw.circle(surface, VERDE, self.rect.center, max(10, self.raio // 2 + 4), 3)


class Projetil:
    def __init__(self, x, y, vx, vy, poder, ang):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.poder = 2 ** poder
        self.surf = criar_projetil_surface(poder, ang)
        self.vida = 80

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1

    @property
    def rect(self):
        return self.surf.get_rect(center=(int(self.x), int(self.y)))

    def fora_da_tela(self):
        return (
            self.x < -20
            or self.x > LARGURA + 20
            or self.y < -20
            or self.y > ALTURA + 20
        )

    def draw(self, surface):
        surface.blit(self.surf, self.rect.topleft)


class ParticulaExplosao:
    def __init__(self, x, y, cor):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-8, 8)
        ang = random.uniform(0, math.pi * 2)
        vel = random.uniform(1.5, 6)
        self.vx = math.cos(ang) * vel
        self.vy = math.sin(ang) * vel
        self.cor = cor
        self.vida = random.randint(20, 50)
        self.vida_max = self.vida
        self.raio = random.randint(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.vida -= 1

    def draw(self, surface):
        alpha = int(255 * self.vida / self.vida_max)
        r = max(1, int(self.raio * self.vida / self.vida_max))
        cor = (*self.cor, alpha)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, cor, (r + 1, r + 1), r)
        surface.blit(s, (self.x - r, self.y - r))