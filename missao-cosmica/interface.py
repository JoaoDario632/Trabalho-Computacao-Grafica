import pygame
import random

from entidades import (
    LARGURA,
    ALTURA,
    AZUL_ESC,
    AMARELO,
    CIANO,
    VERDE,
    VERMELHO,
    LARANJA,
    ROXO,
    CINZA_CLARO,
)

fonte_hud = None
fonte_titulo = None
fonte_info = None
fonte_grande = None


def configurar_fontes():
    global fonte_hud, fonte_titulo, fonte_info, fonte_grande
    fonte_hud = pygame.font.SysFont("consolas", 16, bold=True)
    fonte_titulo = pygame.font.SysFont("consolas", 28, bold=True)
    fonte_info = pygame.font.SysFont("consolas", 13)
    fonte_grande = pygame.font.SysFont("consolas", 46, bold=True)


def desenhar_hud(surface, nave, nivel, tempo_restante):
    painel = pygame.Surface((LARGURA, 48), pygame.SRCALPHA)
    painel.fill((0, 0, 20, 190))
    surface.blit(painel, (0, 0))

    txt = fonte_hud.render(f"PONTOS: {nave.pontos:06d}", True, AMARELO)
    surface.blit(txt, (10, 14))

    surface.blit(fonte_hud.render("VIDAS:", True, CINZA_CLARO), (220, 14))
    mini_nave = pygame.transform.scale(nave.surf_original, (22, 22))
    for i in range(nave.vidas):
        surface.blit(mini_nave, (295 + i * 28, 12))

    txt_n = fonte_hud.render(f"NIVEL: {nivel}", True, VERDE)
    surface.blit(txt_n, (LARGURA // 2 - 50, 14))

    txt_t = fonte_hud.render(f"TEMPO: {max(0, tempo_restante):03d}s", True, CIANO)
    surface.blit(txt_t, (LARGURA - 180, 14))


def desenhar_painel_transformacoes(surface, nave):
    pw, ph = 198, 260
    px, py = LARGURA - pw - 4, 56
    painel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    painel.fill((0, 10, 30, 200))
    pygame.draw.rect(painel, CIANO, (0, 0, pw, ph), 1)
    surface.blit(painel, (px, py))

    def linha(texto, valor, cor, linha_num):
        t = fonte_info.render(texto, True, CINZA_CLARO)
        v = fonte_info.render(valor, True, cor)
        surface.blit(t, (px + 8, py + 8 + linha_num * 22))
        surface.blit(v, (px + 118, py + 8 + linha_num * 22))

    surface.blit(fonte_info.render("── TRANSFORMAÇÕES ──", True, CIANO), (px + 6, py + 4))

    linha("Translação X:", f"{int(nave.x):4d}px", VERDE, 1)
    linha("Translação Y:", f"{int(nave.y):4d}px", VERDE, 2)
    linha("Rotação:", f"{int(nave.angulo_visual):3d}°", AMARELO, 3)
    linha("Escala:", f"{nave.escala:.2f}x", LARANJA, 4)
    linha("Flip H:", "SIM" if nave.flip_h else "NÃO", ROXO, 5)
    linha("Flip V:", "SIM" if nave.flip_v else "NÃO", ROXO, 6)

    tempo_bonus_tiro = nave.bonus_tiro_timer // 60
    linha("Boost Tiro:", f"{tempo_bonus_tiro:02d}s", AMARELO, 7)

    tempo_bonus_vida = nave.bonus_vida_timer // 60
    linha("Boost Vida:", f"{tempo_bonus_vida:02d}s", VERDE, 8)

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

    t4 = fonte_hud.render(
        "Pressione  R  para reiniciar   ou   ESC para sair", True, CINZA_CLARO
    )
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
        ("Setas / WASD", "Translação — mover a nave"),
        ("Q / E", "Rotação — girar a nave"),
        ("+ / -", "Escala — aumentar/diminuir"),
        ("F", "Reflexão Horizontal (flip H)"),
        ("V", "Reflexão Vertical  (flip V)"),
        ("ESPAÇO", "Atirar projéteis"),
        ("ESC", "Sair"),
    ]
    surface.blit(fonte_hud.render("CONTROLES:", True, VERDE), (LARGURA // 2 - 140, 230))
    for i, (k, v) in enumerate(controles):
        tk = fonte_info.render(k, True, LARANJA)
        tv = fonte_info.render(f"→  {v}", True, CINZA_CLARO)
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