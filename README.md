# 🚀 Missão Cósmica

> Jogo 2D desenvolvido em Python + Pygame como atividade avaliativa da disciplina de **Computação Gráfica**.  
> Demonstra na prática as quatro transformações geométricas fundamentais: **Translação, Rotação, Escala e Reflexão**.

---

## 📋 Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Transformações Geométricas](#transformações-geométricas)
- [Demonstração](#demonstração)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Controles](#controles)
- [Estrutura do Código](#estrutura-do-código)
- [Implementação Técnica](#implementação-técnica)
- [Disciplina](#disciplina)
- [Licença](#licença)

---

## Sobre o Projeto

**Missão Cósmica** é um jogo no estilo *space shooter* onde o jogador pilota uma nave espacial, desvia e destrói asteroides em ondas progressivas. Cada mecânica de jogo foi projetada para exercitar uma transformação geométrica distinta, tornando os conceitos teóricos visíveis e interativos em tempo real.

Um **painel de diagnóstico** exibido na tela mostra continuamente os valores de posição (X, Y), ângulo de rotação, fator de escala e estado das reflexões — conectando diretamente a teoria com o que acontece na tela.

### Principais características

- Ondas de asteroides com dificuldade crescente por nível
- Sistema de colisão por máscara de pixel (`pygame.mask`) — preciso mesmo após rotação e escala
- Efeitos de partículas para explosões
- Fundo de estrelas com paralaxe simples
- HUD completo com pontuação, vidas e nível
- Painel lateral exibindo o estado das transformações em tempo real

---

## Transformações Geométricas

Todas as quatro transformações exigidas pela atividade estão implementadas na classe `Nave`, método `_recalcular_surface()`, que aplica as operações sempre sobre a `surf_original` — evitando a degradação de qualidade causada por transformações acumuladas.

### 🔵 Translação

Movimentação da nave no plano 2D por incremento direto das coordenadas `(x, y)`.  
A diagonal é normalizada pelo fator `0.707` (√2 / 2) para manter velocidade constante em movimento oblíquo.

```python
# Classe Nave — método update()
self.x = max(30, min(LARGURA - 30, self.x + dx))
self.y = max(30, min(ALTURA  - 30, self.y + dy))
```

**Teclas:** `←↑↓→` ou `W A S D`

---

### 🟡 Rotação

Rotação da nave em torno do seu próprio centro usando `pygame.transform.rotate()`.  
O ângulo é acumulado continuamente e pode ser controlado passo a passo (tecla) ou de forma contínua (tecla pressionada).

```python
# Classe Nave — método _recalcular_surface()
surf = pygame.transform.rotate(surf, self.angulo)
```

```python
# Classe Nave — método rotacionar()
def rotacionar(self, delta):
    self.angulo = (self.angulo + delta) % 360
```

Os asteroides também exibem rotação contínua e automática, cada um com velocidade angular própria sorteada no momento do spawn.

**Teclas:** `Q` (sentido anti-horário) / `E` (sentido horário)

---

### 🟠 Escala

Redimensionamento da nave por um fator multiplicativo aplicado sobre o tamanho base de `40px`.  
O fator é limitado entre `0.5×` e `2.2×` para manter a jogabilidade.

```python
# Classe Nave — método _recalcular_surface()
s = max(10, self.tamanho_atual)   # tamanho_base * escala
surf = pygame.transform.scale(self.surf_original, (s * 2, s * 2))
```

```python
# Classe Nave — método escalar()
def escalar(self, delta):
    self.escala = max(self.ESCALA_MIN,
                     min(self.ESCALA_MAX, self.escala + delta))
```

**Teclas:** `+` (aumentar) / `-` (diminuir)

---

### 🟣 Reflexão

Espelhamento da nave nos eixos horizontal e/ou vertical usando `pygame.transform.flip()`.  
Dois estados booleanos independentes (`flip_h`, `flip_v`) são alternados e aplicados após a rotação.

```python
# Classe Nave — método _recalcular_surface()
surf = pygame.transform.flip(surf, self.flip_h, self.flip_v)
```

```python
# Classe Nave — métodos de reflexão
def alternar_flip_h(self):
    self.flip_h = not self.flip_h

def alternar_flip_v(self):
    self.flip_v = not self.flip_v
```

**Teclas:** `F` (flip horizontal) / `V` (flip vertical)

---

### Ordem das transformações

As três operações do `pygame.transform` são aplicadas em sequência sobre a `surf_original` a cada frame:

```
surf_original  →  scale()  →  rotate()  →  flip()  →  surf_atual
```

Trabalhar sempre a partir da superfície original garante que cada frame produza um resultado limpo, sem os artefatos visuais gerados por transformações sucessivas.

---

## Demonstração

```
Janela: 900 × 650 px
FPS:    60
```

```
┌──────────────────────────────────────────────────────────────┐
│  PONTOS: 001240   VIDAS: ♦ ♦ ♦   NÍVEL: 2   TEMPO: 033s      │
├──────────────────────────────────────────────┬───────────────┤
│                                              │TRANSFORMAÇÕES:│
│        *    .        *        .      *       │Translação X:  │
│                  ☄️        ☄️               │Translação Y:  │
│     .       ✦                       ☄️      │Rotação:       │
│                    🚀      ☄️               │Escala:        │
│          ☄️                          ☄️     │Flip H:        │
│    *           .       .        *    .       │Flip V:        │
│                                              ├───────────────┤
│                  ☄️        .   ☄️           │  controles    │
└──────────────────────────────────────────────┴───────────────┘
```

---

## Pré-requisitos

- Python **3.8** ou superior
- Pygame **2.x**

Verifique sua versão do Python:

```bash
python3 --version
```

---

## Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/JoaoDario632/Trabalho-Computacao-Grafica
cd missao-cosmica
```

### 2. (Opcional) Crie um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Instale as dependências

```bash
pip install pygame
```

### 4. Execute o jogo

```bash
python jogo_transformacoes.py
```

---

## Controles

| Tecla | Ação | Transformação |
|-------|------|---------------|
| `←` `↑` `↓` `→` ou `W` `A` `S` `D` | Mover a nave | **Translação** |
| `Q` | Rotacionar no sentido anti-horário | **Rotação** |
| `E` | Rotacionar no sentido horário | **Rotação** |
| `+` | Aumentar a nave | **Escala** |
| `-` | Diminuir a nave | **Escala** |
| `F` | Espelhar horizontalmente | **Reflexão H** |
| `V` | Espelhar verticalmente | **Reflexão V** |
| `ESPAÇO` | Atirar projéteis | — |
| `R` | Reiniciar (após Game Over) | — |
| `ESC` | Sair do jogo | — |

---

## Estrutura do Código

```
missao-cosmica/
│
├── jogo_transformacoes.py   # Arquivo principal — jogo completo
README.md
LICENSE
```

### Classes principais

| Classe | Responsabilidade |
|--------|-----------------|
| `Nave` | Entidade do jogador; contém e aplica todas as transformações geométricas |
| `Asteroide` | Inimigos; rotação contínua automática e tamanhos variados |
| `Projetil` | Projéteis disparados pela nave |
| `ParticulaExplosao` | Partículas físicas para efeitos visuais de explosão |

### Funções auxiliares

| Função | Descrição |
|--------|-----------|
| `criar_nave_surface()` | Desenha a nave vetorialmente em uma `Surface` com alpha |
| `criar_asteroide_surface()` | Gera asteroides poligonais irregulares proceduralmente |
| `desenhar_painel_transformacoes()` | Exibe o estado em tempo real de cada transformação |
| `desenhar_hud()` | Renderiza pontuação, vidas, nível e tempo |
| `criar_explosao()` | Instancia partículas de explosão |
| `novo_jogo()` | Inicializa ou reinicia todo o estado do jogo |

---

## Implementação Técnica

### Renderização procedural

Todos os elementos visuais (nave, asteroides, projéteis) são desenhados programaticamente com as primitivas do Pygame (`polygon`, `circle`, `ellipse`). Nenhuma imagem externa é carregada — o projeto é completamente autossuficiente.

### Colisão por máscara de pixel

A detecção de colisão entre a nave e os asteroides utiliza `pygame.mask`, que opera sobre os pixels transparentes da surface após todas as transformações. Isso garante precisão mesmo quando a nave está rotacionada ou escalada.

```python
def colidir_com(self, outro_rect, outra_mask):
    offset = (outro_rect.x - self.rect.x, outro_rect.y - self.rect.y)
    minha_mask = pygame.mask.from_surface(self.surf_atual)
    return minha_mask.overlap(outra_mask, offset) is not None
```

### Dificuldade progressiva

O intervalo entre spawns de asteroides diminui a cada nível (`max(30, 90 - nivel * 6)` frames), e os asteroides passam a ser maiores e mais rápidos conforme o nível aumenta.

---

## Disciplina

| Campo | Informação |
|-------|-----------|
| **Disciplina** | Computação Gráfica |
| **Professor(a)** | Suzana Sousa |
| **Linguagem** | Python 3 |
| **Biblioteca** | Pygame 2.x |

---

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [`LICENSE`](LICENSE) para mais informações.
