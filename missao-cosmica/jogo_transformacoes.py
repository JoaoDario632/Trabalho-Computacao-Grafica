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
import random
import sys

from entidades import (
    LARGURA,
    ALTURA,
    AZUL_ESC,
    CIANO,
    LARANJA,
    VERMELHO,
    AMARELO,
    BRANCO,
    Nave,
    Asteroide,
    ParticulaExplosao,
    criar_estrelas,
)
from interface import (
    configurar_fontes,
    desenhar_hud,
    desenhar_painel_transformacoes,
    tela_game_over,
    tela_inicio,
)

pygame.init()

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Missão Cósmica — Transformações Geométricas")
relogio = pygame.time.Clock()
configurar_fontes()


def criar_explosao(x, y, particulas, n=25, cor_base=LARANJA):
    cores = [LARANJA, VERMELHO, AMARELO, BRANCO]
    for _ in range(n):
        particulas.append(ParticulaExplosao(x, y, random.choice(cores)))


def novo_jogo():
    nave = Nave()
    asteroides = []
    projeteis = []
    particulas = []
    estrelas = criar_estrelas()
    nivel = 1
    spawn_timer = 0
    tempo_nivel = 45
    fps = 60
    frames_nivel = tempo_nivel * fps
    frame_count = 0
    cooldown_tiro = 0

    return {
        "nave": nave,
        "asteroides": asteroides,
        "projeteis": projeteis,
        "particulas": particulas,
        "estrelas": estrelas,
        "nivel": nivel,
        "spawn_timer": spawn_timer,
        "frames_nivel": frames_nivel,
        "frame_count": frame_count,
        "cooldown_tiro": cooldown_tiro,
    }


def run():
    aguardando = True
    while aguardando:
        tela_inicio(tela)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    aguardando = False
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        relogio.tick(30)

    estado = novo_jogo()

    while True:
        relogio.tick(60)
        estado["frame_count"] += 1

        nave = estado["nave"]
        nivel = estado["nivel"]
        asteroides = estado["asteroides"]
        projeteis = estado["projeteis"]
        particulas = estado["particulas"]
        estrelas = estado["estrelas"]

        frames_no_nivel = estado["frame_count"] - (nivel - 1) * estado["frames_nivel"]
        tempo_restante = max(0, estado["frames_nivel"] - frames_no_nivel) // 60

        if frames_no_nivel >= estado["frames_nivel"]:
            estado["nivel"] += 1
            nivel = estado["nivel"]
            estado["frame_count"] = 0
            nave.pontos += 500 * (nivel - 1)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if evento.key == pygame.K_q:
                    nave.rotacionar(+10)
                if evento.key == pygame.K_e:
                    nave.rotacionar(-10)

                if evento.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    nave.escalar(+0.1)
                if evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    nave.escalar(-0.1)

                if evento.key == pygame.K_f:
                    nave.alternar_flip_h()
                if evento.key == pygame.K_v:
                    nave.alternar_flip_v()

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_SPACE] and estado["cooldown_tiro"] <= 0:
            projeteis.append(nave.atirar())
            estado["cooldown_tiro"] = 14

        if estado["cooldown_tiro"] > 0:
            estado["cooldown_tiro"] -= 1

        if teclas[pygame.K_q]:
            nave.rotacionar(+1.5)
        if teclas[pygame.K_e]:
            nave.rotacionar(-1.5)

        estado["spawn_timer"] += 1
        intervalo_spawn = max(30, 90 - nivel * 6)
        if estado["spawn_timer"] >= intervalo_spawn:
            estado["spawn_timer"] = 0
            for _ in range(random.randint(1, 1 + nivel // 3)):
                asteroides.append(Asteroide(nivel))

        nave.update(teclas)

        for a in asteroides:
            a.update()
        for p in projeteis:
            p.update()
        for part in particulas:
            part.update()

        asteroides[:] = [a for a in asteroides if not a.fora_da_tela()]
        projeteis[:] = [p for p in projeteis if not p.fora_da_tela() and p.vida > 0]
        particulas[:] = [p for p in particulas if p.vida > 0]

        for p in projeteis[:]:
            for a in asteroides[:]:
                if p.rect.colliderect(a.rect):
                    criar_explosao(a.x, a.y, particulas, n=20)
                    nave.pontos += a.pontos_valor
                    if p in projeteis:
                        projeteis.remove(p)
                    if a in asteroides:
                        asteroides.remove(a)
                    break

        nave_mask = nave.get_mask()
        for a in asteroides[:]:
            if a.colidir_com(nave.rect, nave_mask):
                if nave.receber_dano():
                    criar_explosao(nave.x, nave.y, particulas, n=30, cor_base=CIANO)

        if nave.vidas <= 0:
            tela_game_over(tela, nave.pontos, nivel)
            esperando = True
            while esperando:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_r:
                            estado = novo_jogo()
                            esperando = False
                        if ev.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                relogio.tick(30)
            continue

        for estrela in estrelas:
            estrela[1] += estrela[4]
            if estrela[1] > ALTURA:
                estrela[1] = 0
                estrela[0] = random.randint(0, LARGURA)

        tela.fill(AZUL_ESC)

        for est in estrelas:
            b = est[2]
            pygame.draw.circle(tela, (b, b, b), (int(est[0]), int(est[1])), est[3])

        for a in asteroides:
            a.draw(tela)

        for p in particulas:
            p.draw(tela)

        for p in projeteis:
            p.draw(tela)

        nave.draw(tela)

        desenhar_hud(tela, nave, nivel, tempo_restante)
        desenhar_painel_transformacoes(tela, nave)

        pygame.display.flip()


if __name__ == "__main__":
    run()