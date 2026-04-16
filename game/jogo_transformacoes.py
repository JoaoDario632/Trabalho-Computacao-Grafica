"""
=============================================================
  MISSÃO CÓSMICA — Jogo de Computação Gráfica
  Disciplina: Computação Gráfica
  Demonstra: Translação, Rotação, Escala e Reflexão
=============================================================

CONTROLES:
  Setas / WASD  → Translação (mover a nave)
  Q / E         → Rotação (girar a nave)
  + / -         → Escala (aumentar/diminuir a nave)
  F             → Reflexão horizontal (flip)
  V             → Reflexão vertical
  ESPAÇO        → Atirar
  R             → Reiniciar após Game Over
  ESC           → Sair
"""

import pygame
import math
import random
import sys

# ─────────────────────────────────────────────
#  INICIALIZAÇÃO
# ─────────────────────────────────────────────
pygame.init()

LARGURA, ALTURA = 900, 650
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Missão Cósmica — Transformações Geométricas")
relogio = pygame.time.Clock()

# ─────────────────────────────────────────────
#  CORES
# ─────────────────────────────────────────────
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
AZUL_INFO    = ( 80, 150, 255)

# ─────────────────────────────────────────────
#  FONTES
# ─────────────────────────────────────────────
fonte_hud    = pygame.font.SysFont("consolas", 16, bold=True)
fonte_titulo = pygame.font.SysFont("consolas", 28, bold=True)
fonte_info   = pygame.font.SysFont("consolas", 13)
fonte_grande = pygame.font.SysFont("consolas", 46, bold=True)

# ─────────────────────────────────────────────
#  FUNÇÕES DE DESENHO DE SUPERFÍCIES
# ─────────────────────────────────────────────

def criar_nave_surface(tamanho=40):
    """
    Desenha a nave em uma Surface com canal alpha.
    A nave é um triângulo estilizado com detalhes.
    Sempre desenhamos 'apontando para cima' (ângulo 0).
    A rotação é aplicada externamente via pygame.transform.rotate().
    """
    s = tamanho
    surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
    cx, cy = s, s

    # Corpo principal (triângulo)
    pontos_corpo = [
        (cx,          cy - s + 4),   # Ponta (frente)
        (cx - s + 8,  cy + s - 6),   # Base esquerda
        (cx + s - 8,  cy + s - 6),   # Base direita
    ]
    pygame.draw.polygon(surf, CIANO, pontos_corpo)
    pygame.draw.polygon(surf, BRANCO, pontos_corpo, 2)

    # Asas
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

    # Motor (círculo na base)
    pygame.draw.circle(surf, LARANJA, (cx, cy + s - 8), 6)
    pygame.draw.circle(surf, AMARELO, (cx, cy + s - 8), 3)

    return surf


def criar_asteroide_surface(raio, cor_base):
    """Cria um asteroide poligonal irregular."""
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
    # Detalhes internos
    for _ in range(3):
        ox = random.randint(cx - raio // 2, cx + raio // 2)
        oy = random.randint(cy - raio // 2, cy + raio // 2)
        pygame.draw.circle(surf, (cor_base[0] // 2, cor_base[1] // 2, cor_base[2] // 2), (ox, oy), random.randint(3, 6))
    return surf


def criar_projetil_surface():
    surf = pygame.Surface((8, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, AMARELO, (0, 0, 8, 20))
    pygame.draw.ellipse(surf, BRANCO, (2, 2, 4, 16))
    return surf


def criar_estrelas(n=120):
    estrelas = []
    for _ in range(n):
        x = random.randint(0, LARGURA)
        y = random.randint(0, ALTURA)
        brilho = random.randint(80, 255)
        raio   = random.choice([1, 1, 1, 2])
        vel    = random.uniform(0.2, 1.0)
        estrelas.append([x, y, brilho, raio, vel])
    return estrelas


# ─────────────────────────────────────────────
#  CLASSES
# ─────────────────────────────────────────────

class Nave:
    """
    Nave controlada pelo jogador.

    Transformações aplicadas:
      - TRANSLAÇÃO  : movimentação via teclas de seta / WASD
      - ROTAÇÃO     : Q/E para girar (pygame.transform.rotate)
      - ESCALA      : +/- para aumentar/diminuir (pygame.transform.scale)
      - REFLEXÃO    : F (flip horizontal) / V (flip vertical)
                      (pygame.transform.flip)
    """

    ESCALA_MIN = 0.5
    ESCALA_MAX = 2.2
    VEL_BASE   = 5

    def __init__(self):
        self.x = LARGURA // 2
        self.y = ALTURA  // 2
        self.angulo        = 0       # graus (rotação)
        self.escala        = 1.0     # fator de escala
        self.flip_h        = False   # reflexão horizontal
        self.flip_v        = False   # reflexão vertical
        self.tamanho_base  = 40
        self.surf_original = criar_nave_surface(self.tamanho_base)
        self.surf_atual    = self.surf_original
        self.rect          = self.surf_atual.get_rect(center=(self.x, self.y))
        self.vidas         = 3
        self.pontos        = 0
        self.invencivel    = 0       # frames de invencibilidade após dano
        self.efeito_motor  = 0       # animação do propulsor

    # ── Getters de estado ──────────────────────
    @property
    def tamanho_atual(self):
        return int(self.tamanho_base * self.escala)

    def _recalcular_surface(self):
        """Aplica ESCALA → ROTAÇÃO → REFLEXÃO na ordem correta."""
        s = max(10, self.tamanho_atual)
        # 1. ESCALA — redimensiona a surface base
        surf = pygame.transform.scale(
            self.surf_original,
            (s * 2, s * 2)
        )
        # 2. ROTAÇÃO — gira a surface escalada
        surf = pygame.transform.rotate(surf, self.angulo)

        # 3. REFLEXÃO — espelha conforme flags
        surf = pygame.transform.flip(surf, self.flip_h, self.flip_v)

        self.surf_atual = surf
        self.rect = surf.get_rect(center=(self.x, self.y))

    # ── Atualização por frame ──────────────────
    def update(self, teclas):
        vel = self.VEL_BASE

        # ── TRANSLAÇÃO ────────────────────────
        # Movimentação direta em X e Y (espaço 2D)
        dx, dy = 0, 0
        if teclas[pygame.K_LEFT]  or teclas[pygame.K_a]: dx -= vel
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += vel
        if teclas[pygame.K_UP]    or teclas[pygame.K_w]: dy -= vel
        if teclas[pygame.K_DOWN]  or teclas[pygame.K_s]: dy += vel

        # Normaliza diagonal
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        # Aplica translação e mantém dentro da tela
        self.x = max(30, min(LARGURA - 30, self.x + dx))
        self.y = max(30, min(ALTURA  - 30, self.y + dy))

        if self.invencivel > 0:
            self.invencivel -= 1
        self.efeito_motor = (self.efeito_motor + 1) % 10

        self._recalcular_surface()

    def rotacionar(self, delta):
        """ROTAÇÃO: incrementa o ângulo de rotação."""
        self.angulo = (self.angulo + delta) % 360

    def escalar(self, delta):
        """ESCALA: ajusta o fator de escala com limites."""
        self.escala = max(self.ESCALA_MIN,
                         min(self.ESCALA_MAX, self.escala + delta))

    def alternar_flip_h(self):
        """REFLEXÃO HORIZONTAL."""
        self.flip_h = not self.flip_h

    def alternar_flip_v(self):
        """REFLEXÃO VERTICAL."""
        self.flip_v = not self.flip_v

    def atirar(self):
        """Cria um projétil na direção atual da nave."""
        rad = math.radians(self.angulo + 90)
        # Ajusta para flip
        if self.flip_v:
            rad = math.radians(-self.angulo + 90)
        vx = -math.sin(math.radians(self.angulo)) * 12
        vy = -math.cos(math.radians(self.angulo)) * 12
        return Projetil(self.x, self.y, vx, vy)

    def receber_dano(self):
        if self.invencivel == 0:
            self.vidas -= 1
            self.invencivel = 90  # 1.5s de invencibilidade
            return True
        return False

    def draw(self, surface):
        # Pisca quando invencível
        if self.invencivel > 0 and (self.invencivel // 6) % 2 == 0:
            return
        # Efeito de motor/propulsor
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
    """
    Asteroide inimigo que se move pela tela.
    Também utiliza ROTAÇÃO contínua e diferentes tamanhos (ESCALA).
    """
    CORES = [
        (160, 120,  80),
        (130,  90,  60),
        ( 90,  90, 110),
        (100, 110,  80),
    ]

    def __init__(self, nivel=1):
        # Spawna nas bordas
        lado = random.choice(["top", "bottom", "left", "right"])
        if lado == "top":
            self.x, self.y = random.randint(0, LARGURA), -40
        elif lado == "bottom":
            self.x, self.y = random.randint(0, LARGURA), ALTURA + 40
        elif lado == "left":
            self.x, self.y = -40, random.randint(0, ALTURA)
        else:
            self.x, self.y = LARGURA + 40, random.randint(0, ALTURA)

        # ESCALA variada: define o raio do asteroide
        self.raio = random.randint(20, 45) + nivel * 2
        cor = random.choice(self.CORES)
        self.surf_original = criar_asteroide_surface(self.raio, cor)
        self.surf_atual    = self.surf_original
        self.angulo        = 0
        self.vel_rotacao   = random.uniform(-2, 2)  # rotação própria
        self.pontos_valor  = max(10, 60 - self.raio)

        # Velocidade em direção ao centro da tela
        ang = math.atan2(ALTURA // 2 - self.y, LARGURA // 2 - self.x)
        vel = random.uniform(1.5, 2.5 + nivel * 0.3)
        self.vx = math.cos(ang) * vel + random.uniform(-0.5, 0.5)
        self.vy = math.sin(ang) * vel + random.uniform(-0.5, 0.5)

    def update(self):
        # TRANSLAÇÃO: move o asteroide
        self.x += self.vx
        self.y += self.vy

        # ROTAÇÃO contínua do asteroide
        self.angulo = (self.angulo + self.vel_rotacao) % 360
        self.surf_atual = pygame.transform.rotate(self.surf_original, self.angulo)

    @property
    def rect(self):
        return self.surf_atual.get_rect(center=(int(self.x), int(self.y)))

    def fora_da_tela(self):
        margem = self.raio + 60
        return (self.x < -margem or self.x > LARGURA + margem or
                self.y < -margem or self.y > ALTURA + margem)

    def colidir_com(self, outro_rect, outra_mask):
        r = self.rect
        offset = (outro_rect.x - r.x, outro_rect.y - r.y)
        minha_mask = pygame.mask.from_surface(self.surf_atual)
        return minha_mask.overlap(outra_mask, offset) is not None

    def draw(self, surface):
        surface.blit(self.surf_atual, self.rect.topleft)


class Projetil:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.surf = criar_projetil_surface()
        self.vida = 80

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1

    @property
    def rect(self):
        return self.surf.get_rect(center=(int(self.x), int(self.y)))

    def fora_da_tela(self):
        return (self.x < -20 or self.x > LARGURA + 20 or
                self.y < -20 or self.y > ALTURA + 20)

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


# ─────────────────────────────────────────────
#  FUNÇÕES DE INTERFACE
# ─────────────────────────────────────────────

def desenhar_hud(surface, nave, nivel, tempo_restante):
    """Barra superior com HUD do jogo."""
    # Fundo semi-transparente
    painel = pygame.Surface((LARGURA, 48), pygame.SRCALPHA)
    painel.fill((0, 0, 20, 190))
    surface.blit(painel, (0, 0))

    # Pontuação
    txt = fonte_hud.render(f"PONTOS: {nave.pontos:06d}", True, AMARELO)
    surface.blit(txt, (10, 14))

    # Vidas (ícones)
    surface.blit(fonte_hud.render("VIDAS:", True, CINZA_CLARO), (220, 14))
    mini_nave = pygame.transform.scale(nave.surf_original, (22, 22))
    for i in range(nave.vidas):
        surface.blit(mini_nave, (295 + i * 28, 12))

    # Nível
    txt_n = fonte_hud.render(f"NIVEL: {nivel}", True, VERDE)
    surface.blit(txt_n, (LARGURA // 2 - 50, 14))

    # Tempo
    txt_t = fonte_hud.render(f"TEMPO: {max(0, tempo_restante):03d}s", True, CIANO)
    surface.blit(txt_t, (LARGURA - 180, 14))


def desenhar_painel_transformacoes(surface, nave):
    """
    Painel lateral direito mostrando o estado atual de cada transformação.
    Serve como feedback visual e didático para o relatório.
    """
    pw, ph = 198, 200
    px, py = LARGURA - pw - 4, 56
    painel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    painel.fill((0, 10, 30, 200))
    pygame.draw.rect(painel, CIANO, (0, 0, pw, ph), 1)
    surface.blit(painel, (px, py))

    def linha(texto, valor, cor, linha_num):
        t = fonte_info.render(texto, True, CINZA_CLARO)
        v = fonte_info.render(valor, True, cor)
        surface.blit(t, (px + 8,  py + 8 + linha_num * 22))
        surface.blit(v, (px + 118, py + 8 + linha_num * 22))

    surface.blit(fonte_info.render("── TRANSFORMAÇÕES ──", True, CIANO),
                 (px + 6, py + 4))

    linha("Translação X:", f"{int(nave.x):4d}px", VERDE,  1)
    linha("Translação Y:", f"{int(nave.y):4d}px", VERDE,  2)
    linha("Rotação:",      f"{int(nave.angulo):3d}°",  AMARELO, 3)
    linha("Escala:",       f"{nave.escala:.2f}x", LARANJA, 4)
    linha("Flip H:",       "SIM" if nave.flip_h else "NÃO", ROXO,  5)
    linha("Flip V:",       "SIM" if nave.flip_v else "NÃO", ROXO,  6)

    # Mini-hint de controles
    hints = [
        "Setas/WASD → mover",
        "Q/E → rotacionar",
        "+/- → escalar",
        "F → flip H | V → flip V",
        "ESPAÇO → atirar",
    ]
    for i, h in enumerate(hints):
        t = fonte_info.render(h, True, (140, 140, 160))
        surface.blit(t, (px + 6, py + ph + 4 + i * 16))


def tela_game_over(surface, pontos, nivel):
    surface.fill(AZUL_ESC)
    _desenhar_estrelas_estaticas(surface)

    txt = fonte_grande.render("GAME OVER", True, VERMELHO)
    surface.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 180))

    t2 = fonte_titulo.render(f"Pontuação final: {pontos}", True, AMARELO)
    surface.blit(t2, (LARGURA // 2 - t2.get_width() // 2, 270))

    t3 = fonte_titulo.render(f"Nível alcançado: {nivel}", True, VERDE)
    surface.blit(t3, (LARGURA // 2 - t3.get_width() // 2, 320))

    t4 = fonte_hud.render("Pressione  R  para reiniciar   ou   ESC para sair", True, CINZA_CLARO)
    surface.blit(t4, (LARGURA // 2 - t4.get_width() // 2, 420))

    pygame.display.flip()


def tela_inicio(surface):
    surface.fill(AZUL_ESC)
    _desenhar_estrelas_estaticas(surface)

    titulo = fonte_grande.render("MISSÃO CÓSMICA", True, CIANO)
    surface.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 90))

    sub = fonte_titulo.render("Transformações Geométricas", True, AMARELO)
    surface.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 160))

    controles = [
        ("Setas / WASD",  "Translação — mover a nave"),
        ("Q / E",          "Rotação — girar a nave"),
        ("+ / -",          "Escala — aumentar/diminuir"),
        ("F",              "Reflexão Horizontal (flip H)"),
        ("V",              "Reflexão Vertical  (flip V)"),
        ("ESPAÇO",         "Atirar projéteis"),
        ("ESC",            "Sair"),
    ]
    surface.blit(fonte_hud.render("CONTROLES:", True, VERDE), (LARGURA // 2 - 140, 230))
    for i, (k, v) in enumerate(controles):
        cor_k = LARANJA
        cor_v = CINZA_CLARO
        tk = fonte_info.render(k, True, cor_k)
        tv = fonte_info.render(f"→  {v}", True, cor_v)
        base_x = LARGURA // 2 - 200
        y = 260 + i * 26
        surface.blit(tk, (base_x, y))
        surface.blit(tv, (base_x + 110, y))

    ini = fonte_hud.render("Pressione  ENTER  para iniciar", True, AMARELO)
    surface.blit(ini, (LARGURA // 2 - ini.get_width() // 2, 480))
    pygame.display.flip()


def _desenhar_estrelas_estaticas(surface):
    random.seed(42)
    for _ in range(120):
        x = random.randint(0, LARGURA)
        y = random.randint(0, ALTURA)
        b = random.randint(80, 255)
        r = random.choice([1, 1, 2])
        pygame.draw.circle(surface, (b, b, b), (x, y), r)
    random.seed()


# ─────────────────────────────────────────────
#  LÓGICA DO JOGO
# ─────────────────────────────────────────────

def criar_explosao(x, y, particulas, n=25, cor_base=LARANJA):
    cores = [LARANJA, VERMELHO, AMARELO, BRANCO]
    for _ in range(n):
        particulas.append(ParticulaExplosao(x, y, random.choice(cores)))


def novo_jogo():
    nave        = Nave()
    asteroides  = []
    projeteis   = []
    particulas  = []
    estrelas    = criar_estrelas()
    nivel       = 1
    spawn_timer = 0
    tempo_nivel = 45          # segundos por nível
    fps         = 60
    frames_nivel = tempo_nivel * fps
    frame_count = 0
    atirando    = False
    cooldown_tiro = 0
    return {
        "nave":         nave,
        "asteroides":   asteroides,
        "projeteis":    projeteis,
        "particulas":   particulas,
        "estrelas":     estrelas,
        "nivel":        nivel,
        "spawn_timer":  spawn_timer,
        "frames_nivel": frames_nivel,
        "frame_count":  frame_count,
        "cooldown_tiro": cooldown_tiro,
    }


def run():
    # ── Tela de Início ──
    aguardando = True
    while aguardando:
        tela_inicio(tela)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    aguardando = False
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
        relogio.tick(30)

    # ── Loop Principal ──
    estado = novo_jogo()

    while True:
        dt = relogio.tick(60)
        estado["frame_count"] += 1
        nave       = estado["nave"]
        nivel      = estado["nivel"]
        asteroides = estado["asteroides"]
        projeteis  = estado["projeteis"]
        particulas = estado["particulas"]
        estrelas   = estado["estrelas"]

        # Tempo restante no nível atual
        frames_no_nivel = estado["frame_count"] - (nivel - 1) * estado["frames_nivel"]
        tempo_restante  = max(0, estado["frames_nivel"] - frames_no_nivel) // 60

        # ── Avanço de Nível ──
        if frames_no_nivel >= estado["frames_nivel"]:
            estado["nivel"] += 1
            nivel = estado["nivel"]
            estado["frame_count"] = 0
            # Bônus de pontos ao passar de nível
            nave.pontos += 500 * (nivel - 1)

        # ── Eventos ──
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                # ROTAÇÃO
                if evento.key == pygame.K_q:
                    nave.rotacionar(+10)
                if evento.key == pygame.K_e:
                    nave.rotacionar(-10)

                # ESCALA
                if evento.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    nave.escalar(+0.1)
                if evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    nave.escalar(-0.1)

                # REFLEXÃO
                if evento.key == pygame.K_f:
                    nave.alternar_flip_h()
                if evento.key == pygame.K_v:
                    nave.alternar_flip_v()

        # Tiro contínuo com cooldown
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_SPACE] and estado["cooldown_tiro"] <= 0:
            projeteis.append(nave.atirar())
            estado["cooldown_tiro"] = 14

        if estado["cooldown_tiro"] > 0:
            estado["cooldown_tiro"] -= 1

        # Rotação contínua por tecla pressionada
        if teclas[pygame.K_q]:
            nave.rotacionar(+1.5)
        if teclas[pygame.K_e]:
            nave.rotacionar(-1.5)

        # ── Spawn de Asteroides ──
        estado["spawn_timer"] += 1
        intervalo_spawn = max(30, 90 - nivel * 6)
        if estado["spawn_timer"] >= intervalo_spawn:
            estado["spawn_timer"] = 0
            for _ in range(random.randint(1, 1 + nivel // 3)):
                asteroides.append(Asteroide(nivel))

        # ── Update ──
        nave.update(teclas)

        for a in asteroides:
            a.update()
        for p in projeteis:
            p.update()
        for part in particulas:
            part.update()

        # Limpa fora da tela
        asteroides[:] = [a for a in asteroides if not a.fora_da_tela()]
        projeteis[:]  = [p for p in projeteis  if not p.fora_da_tela() and p.vida > 0]
        particulas[:] = [p for p in particulas  if p.vida > 0]

        # ── Colisões Projétil ↔ Asteroide ──
        for p in projeteis[:]:
            for a in asteroides[:]:
                if p.rect.colliderect(a.rect):
                    criar_explosao(a.x, a.y, particulas, n=20)
                    nave.pontos += a.pontos_valor
                    if p in projeteis:  projeteis.remove(p)
                    if a in asteroides: asteroides.remove(a)
                    break

        # ── Colisões Nave ↔ Asteroide ──
        nave_mask = nave.get_mask()
        for a in asteroides[:]:
            if a.colidir_com(nave.rect, nave_mask):
                if nave.receber_dano():
                    criar_explosao(nave.x, nave.y, particulas, n=30, cor_base=CIANO)
                    # Não remove o asteroide — apenas dano

        # ── Game Over ──
        if nave.vidas <= 0:
            tela_game_over(tela, nave.pontos, nivel)
            esperando = True
            while esperando:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_r:
                            estado = novo_jogo()
                            esperando = False
                        if ev.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()
                relogio.tick(30)
            continue

        # ───────── Rolagem do Fundo (estrelas) ─────────
        for estrela in estrelas:
            estrela[1] += estrela[4]
            if estrela[1] > ALTURA:
                estrela[1] = 0
                estrela[0] = random.randint(0, LARGURA)

        # ─────────────────────────────────────
        #  RENDERIZAÇÃO
        # ─────────────────────────────────────
        tela.fill(AZUL_ESC)

        # Estrelas
        for est in estrelas:
            b = est[2]
            pygame.draw.circle(tela, (b, b, b), (int(est[0]), int(est[1])), est[3])

        # Asteroides
        for a in asteroides:
            a.draw(tela)

        # Partículas de explosão
        for p in particulas:
            p.draw(tela)

        # Projéteis
        for p in projeteis:
            p.draw(tela)

        # Nave
        nave.draw(tela)

        # HUD e painel
        desenhar_hud(tela, nave, nivel, tempo_restante)
        desenhar_painel_transformacoes(tela, nave)

        pygame.display.flip()


# ─────────────────────────────────────────────
#  ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    run()