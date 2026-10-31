#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NAIL STUDIO - Jogo de manicure em Python + Pygame
=================================================
Execute com:   python nail_studio.py        (requer:  pip install pygame)

Como jogar
  * Escolha um esmalte na paleta (esquerda) e clique em uma unha para pintar.
  * Escolha uma decoração (direita) e clique em uma unha:
        Francesinha / Glitter  -> liga/desliga na unha clicada
        Coração, Pedrinha, Flor, Estrela, Pérolas, Fio dourado
                               -> colocados exatamente onde você clicar
  * Botão direito numa unha: remove a última decoração (ou o esmalte).
  * Ferramenta "Removedor" limpa uma unha; "Remover esmalte" limpa todas.
  * "Formato" muda o formato de todas as unhas.
  * Ctrl+Z desfaz.  "Finalizar look" mostra o resultado e salva uma foto.

Tudo é desenhado por código (curvas, gradientes, transparências e
supersampling) - nenhuma imagem externa é necessária.
"""
import math
import os
import random
import sys
import time

import pygame

# --------------------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# --------------------------------------------------------------------------
WIN_W, WIN_H = 1280, 800
FPS = 60
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HAND_K = 1.3            # escala da mão na tela
HAND_SS = 3             # supersampling da mão (qualidade x tempo de abertura)
HX0, HY0 = 0, 90        # origem do "espaço da mão"
HW, HH = 580, 720       # tamanho do "espaço da mão"
HAND_CX = 645           # centro horizontal da mão na tela

TEXT = (112, 52, 84)
TEXT_SOFT = (176, 124, 150)
PINK = (255, 122, 170)
PINK_DEEP = (236, 70, 130)
PINK_LIGHT = (255, 214, 230)
SKIN_DARK = (222, 156, 136)
SKIN_MID = (241, 193, 170)
SKIN_LIGHT = (255, 227, 208)

POLISHES = [
    ("Rosa Chiclete", (255, 140, 190)), ("Rosé Clássico", (230, 130, 155)),
    ("Nude Seda", (226, 180, 160)), ("Pêssego", (255, 175, 145)),
    ("Coral Vivo", (255, 102, 98)), ("Vermelho Cereja", (205, 20, 48)),
    ("Vinho Intenso", (120, 18, 52)), ("Pink Neon", (255, 50, 140)),
    ("Laranja Sorbet", (255, 140, 50)), ("Amarelo Manteiga", (255, 226, 120)),
    ("Menta Gelada", (150, 228, 200)), ("Verde Esmeralda", (20, 128, 90)),
    ("Turquesa", (50, 198, 205)), ("Azul Bebê", (150, 200, 246)),
    ("Azul Royal", (40, 76, 205)), ("Lavanda", (192, 164, 235)),
    ("Lilás Místico", (162, 100, 200)), ("Ameixa", (88, 38, 98)),
    ("Branco Pérola", (250, 244, 244)), ("Preto Noir", (28, 24, 32)),
]

DECOR_COLORS = [
    ("Branco", (255, 255, 255)), ("Dourado", (235, 190, 70)),
    ("Rosa", (255, 130, 175)), ("Vermelho", (220, 30, 60)),
    ("Prata", (205, 212, 225)), ("Azul", (90, 150, 240)),
    ("Lilás", (180, 130, 230)), ("Preto", (30, 28, 34)),
]

FINISHES = [("gloss", "Brilho"), ("matte", "Fosco"), ("shimmer", "Perolado")]

DECORS = [
    ("french", "Francesinha"), ("glitter", "Glitter"), ("heart", "Coração"),
    ("gem", "Pedrinha"), ("flower", "Florzinha"), ("star", "Estrelinha"),
    ("dots", "Pérolas"), ("line", "Fio dourado"),
]

# Formatos de unha: pontos de controle normalizados (x de -1..1, y de 0..1,
# sendo y=0 a cutícula e y=1 a ponta) + fator de comprimento.
_BASE_TOP = [(0, 0.02), (-0.62, 0.08), (-0.95, 0.30)]
_BASE_TOP_R = [(0.95, 0.30), (0.62, 0.08)]
SHAPES = [
    ("oval", "Oval", 1.00,
     _BASE_TOP + [(-1.0, 0.60), (-0.85, 0.85), (-0.45, 0.99), (0, 1.02),
                  (0.45, 0.99), (0.85, 0.85), (1.0, 0.60)] + _BASE_TOP_R),
    ("round", "Redonda", 0.84,
     _BASE_TOP + [(-1.0, 0.58), (-0.88, 0.84), (-0.48, 0.99), (0, 1.02),
                  (0.48, 0.99), (0.88, 0.84), (1.0, 0.58)] + _BASE_TOP_R),
    ("square", "Quadrada", 0.95,
     _BASE_TOP + [(-1.0, 0.62), (-1.0, 0.96), (-0.70, 1.0), (0, 1.0),
                  (0.70, 1.0), (1.0, 0.96), (1.0, 0.62)] + _BASE_TOP_R),
    ("squoval", "Squoval", 0.98,
     _BASE_TOP + [(-1.0, 0.62), (-0.95, 0.90), (-0.68, 0.99), (0, 1.01),
                  (0.68, 0.99), (0.95, 0.90), (1.0, 0.62)] + _BASE_TOP_R),
    ("almond", "Amêndoa", 1.22,
     [(0, 0.02), (-0.62, 0.08), (-0.95, 0.28), (-0.95, 0.55), (-0.72, 0.80),
      (-0.32, 0.96), (0, 1.03), (0.32, 0.96), (0.72, 0.80), (0.95, 0.55),
      (0.95, 0.28), (0.62, 0.08)]),
    ("coffin", "Bailarina", 1.25,
     _BASE_TOP + [(-0.85, 0.60), (-0.62, 0.90), (-0.40, 1.0), (0, 1.0),
                  (0.40, 1.0), (0.62, 0.90), (0.85, 0.60)] + _BASE_TOP_R),
    ("stiletto", "Stiletto", 1.45,
     [(0, 0.02), (-0.62, 0.08), (-0.92, 0.30), (-0.70, 0.60), (-0.35, 0.88),
      (-0.08, 1.05), (0, 1.12), (0.08, 1.05), (0.35, 0.88), (0.70, 0.60),
      (0.92, 0.30), (0.62, 0.08)]),
]
SHAPE_BY_KEY = {k: {"label": l, "hs": h, "pts": p} for k, l, h, p in SHAPES}

# Dedos: base (x, y) no espaço da mão, inclinação em graus, comprimento,
# largura na base/ponta e curvatura.
FINGERS = [
    dict(name="Polegar", base=(215, 590), lean=-50, length=215, w0=66, w1=52, bend=-14, nail=0.86),
    dict(name="Indicador", base=(270, 442), lean=-7, length=252, w0=60, w1=46, bend=-5, nail=0.84),
    dict(name="Médio", base=(337, 427), lean=-1, length=284, w0=62, w1=47, bend=0, nail=0.84),
    dict(name="Anelar", base=(404, 440), lean=6, length=256, w0=58, w1=44, bend=5, nail=0.84),
    dict(name="Mindinho", base=(463, 477), lean=14, length=200, w0=48, w1=38, bend=8, nail=0.85),
]
PALM_PTS = [(262, 812), (238, 730), (205, 664), (188, 610), (196, 545), (222, 470),
            (262, 425), (337, 408), (404, 418), (452, 442), (490, 482), (496, 545),
            (482, 625), (456, 705), (436, 812)]


# --------------------------------------------------------------------------
# FUNÇÕES UTILITÁRIAS
# --------------------------------------------------------------------------
def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp_col(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(len(c1)))


def shade(c, f):
    return tuple(clamp(int(v * f), 0, 255) for v in c[:3])


def tint(c, t, target=(255, 255, 255)):
    return lerp_col(c[:3], target, t)


def catmull(points, closed=True, n=10):
    """Curva suave (Catmull-Rom) passando pelos pontos dados."""
    out = []
    count = len(points)
    rng = range(count) if closed else range(count - 1)
    for i in rng:
        if closed:
            p0, p1 = points[(i - 1) % count], points[i]
            p2, p3 = points[(i + 1) % count], points[(i + 2) % count]
        else:
            p0 = points[max(i - 1, 0)]
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[min(i + 2, count - 1)]
        for j in range(n):
            t = j / float(n)
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


def blur(surf, f=6):
    """Desfoque rápido (reduz e amplia a imagem)."""
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // f), max(1, h // f)))
    return pygame.transform.smoothscale(small, (w, h))


def new_layer(size, color=(255, 236, 242)):
    s = pygame.Surface(size, pygame.SRCALPHA)
    s.fill(tuple(color[:3]) + (0,))
    return s


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def make_font(size, bold=False, italic=False, serif=False):
    names = "georgia,palatinolinotype,times new roman,dejavuserif" if serif else \
        "segoeui,helveticaneue,arial,dejavusans,verdana"
    return pygame.font.SysFont(names, size, bold=bold, italic=italic)


# --------------------------------------------------------------------------
# ELEMENTOS DE DECORAÇÃO (desenhados em camadas ampliadas)
# --------------------------------------------------------------------------
def _circle(layer, col, c, r):
    pygame.draw.circle(layer, tuple(col[:3]) + (255,) if len(col) == 3 else col,
                       (int(c[0]), int(c[1])), max(1, int(r)))


def sphere(layer, cx, cy, r, col, steps=8, spec=True):
    """Esfera com gradiente (pérola, miolo de flor, etc.)."""
    dark, light = shade(col, 0.60), tint(col, 0.55)
    for i in range(steps):
        u = i / (steps - 1.0)
        k = 1 - 0.80 * u
        off = (1 - k) * r * 0.40
        c = lerp_col(dark, col, u / 0.55) if u < 0.55 else lerp_col(col, light, (u - 0.55) / 0.45)
        _circle(layer, c, (cx - off, cy - off), r * k)
    if spec:
        _circle(layer, (255, 255, 255), (cx - r * 0.36, cy - r * 0.40), r * 0.17)


def shaded_poly(layer, pts, cx, cy, col, r, steps=7):
    dark, light = shade(col, 0.62), tint(col, 0.50)
    for i in range(steps):
        u = i / (steps - 1.0)
        k = 1 - 0.78 * u
        off = (1 - k) * r * 0.30
        c = lerp_col(dark, col, u / 0.5) if u < 0.5 else lerp_col(col, light, (u - 0.5) / 0.5)
        poly = [(cx + (x - cx) * k - off, cy + (y - cy) * k - off) for x, y in pts]
        pygame.draw.polygon(layer, c + (255,), poly)


def _rot(x, y, a):
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def heart_pts(cx, cy, r, rot):
    pts = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) - 2
        rx, ry = _rot(x / 17.0 * r, y / 17.0 * r, rot)
        pts.append((cx + rx, cy + ry))
    return pts


def star4(layer, cx, cy, r, col=(255, 255, 255)):
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.22
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    pygame.draw.polygon(layer, tuple(col[:3]) + (255,), pts)


def draw_sticker(layer, kind, cx, cy, unit, col, size, rot):
    """Desenha uma decoração. unit = largura da unha em pixels ampliados."""
    base = {"heart": 0.21, "star": 0.21, "flower": 0.19, "gem": 0.105,
            "dots": 0.07, "line": 0.30}[kind]
    r = unit * base * size
    if kind == "heart":
        shaded_poly(layer, heart_pts(cx, cy, r, rot), cx, cy, col, r)
        hx, hy = _rot(-r * 0.38, -r * 0.40, rot)
        _circle(layer, (255, 255, 255), (cx + hx, cy + hy), r * 0.12)
    elif kind == "star":
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5 + rot
            rad = r if i % 2 == 0 else r * 0.46
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        shaded_poly(layer, pts, cx, cy, col, r)
        _circle(layer, (255, 255, 255), (cx - r * 0.18, cy - r * 0.25), r * 0.09)
    elif kind == "flower":
        petal = tint(col, 0.15) if col != (255, 255, 255) else (255, 246, 250)
        for i in range(5):
            ang = rot + i * 2 * math.pi / 5
            sphere(layer, cx + 0.58 * r * math.cos(ang), cy + 0.58 * r * math.sin(ang),
                   r * 0.50, petal, steps=5, spec=False)
        sphere(layer, cx, cy, r * 0.30, (245, 190, 60), steps=5)
    elif kind == "gem":
        _circle(layer, (206, 212, 224), (cx, cy), r)
        _circle(layer, shade(col, 0.55), (cx, cy), r * 0.88)
        for i in range(8):
            a0 = i * math.pi / 4 + rot
            a1 = a0 + math.pi / 4
            mid = (a0 + a1) / 2
            f = 0.5 + 0.5 * math.cos(mid + 2.36)
            c = lerp_col(shade(col, 0.70), tint(col, 0.60), f)
            pygame.draw.polygon(layer, c + (255,), [
                (cx, cy),
                (cx + r * 0.88 * math.cos(a0), cy + r * 0.88 * math.sin(a0)),
                (cx + r * 0.88 * math.cos(a1), cy + r * 0.88 * math.sin(a1))])
        table = [(cx + r * 0.46 * math.cos(math.pi / 4 * i + rot + math.pi / 8),
                  cy + r * 0.46 * math.sin(math.pi / 4 * i + rot + math.pi / 8)) for i in range(8)]
        pygame.draw.polygon(layer, tint(col, 0.55) + (255,), table)
        star4(layer, cx - r * 0.30, cy - r * 0.32, r * 0.55)
    elif kind == "dots":
        for k, oy in enumerate((-1.9, 0.0, 1.9)):
            dx, dy = _rot(0, oy * r, rot)
            sphere(layer, cx + dx, cy + dy, r * (1.0 - 0.12 * k), col)
    elif kind == "line":
        pts = []
        for j in range(-9, 10):
            u = j / 9.0
            x, y = u * r, 0.30 * r * math.sin(u * math.pi * 1.6)
            rx, ry = _rot(x, y, rot)
            pts.append((cx + rx, cy + ry))
        w = max(2, int(unit * 0.030 * size))
        pygame.draw.lines(layer, shade(col, 0.75) + (255,), False, pts, w)
        up = [(x, y - w * 0.25) for x, y in pts]
        pygame.draw.lines(layer, tint(col, 0.55) + (255,), False, up, max(1, w // 2))
        sphere(layer, pts[0][0], pts[0][1], w * 1.0, col, steps=4)
        sphere(layer, pts[-1][0], pts[-1][1], w * 1.0, col, steps=4)


# --------------------------------------------------------------------------
# RENDERIZAÇÃO DA UNHA 3D
# --------------------------------------------------------------------------
_NAIL_CACHE = {}
_ROT_CACHE = {}


def blank_state():
    return dict(polish=None, finish="gloss", french=None, glitter=None, decor=[])


def render_nail(shape, W, hn, st, seed=0, progress=1.0, scale=1.0):
    """Gera a imagem da unha (apontando para cima). Retorna (surface, (ox, oy))
    onde (ox, oy) é a posição da cutícula dentro da imagem."""
    key = (shape, round(W, 1), round(hn, 1), st["polish"], st["finish"], st["french"],
           st["glitter"], tuple(st["decor"]), seed, int(progress * 12), round(scale, 2))
    hit = _NAIL_CACHE.get(key)
    if hit:
        return hit
    if len(_NAIL_CACHE) > 600:
        _NAIL_CACHE.clear()
        _ROT_CACHE.clear()

    A = 3
    spec = SHAPE_BY_KEY[shape]
    H = hn * spec["hs"]
    pt, pb, pad = int(10 * scale) + 6, int(0.2 * H) + 8, int(8 * scale) + 6
    sw, sh = int(math.ceil(W + 2 * pad)), int(math.ceil(H + pt + pb))
    ox, oy = sw / 2.0, pt + H
    size = (sw * A, sh * A)

    def P(x, y):
        return ((ox + x) * A, (oy - y) * A)

    local = [(x * W / 2.0, y * H) for x, y in catmull(spec["pts"], True, 8)]
    outline = [P(x, y) for x, y in local]
    polish, finish = st["polish"], st["finish"]

    mask = new_layer(size, (255, 255, 255))
    pygame.draw.polygon(mask, (255, 255, 255, 255), outline)
    out = new_layer(size)

    # sombra projetada sobre o dedo
    shl = new_layer(size, (120, 50, 70))
    pygame.draw.polygon(shl, (120, 50, 70, 125),
                        [(x + 1.6 * scale * A, y + 2.6 * scale * A) for x, y in outline])
    out.blit(blur(shl, 4), (0, 0))

    cy = H * 0.5

    def concentric(lay, c_edge, c_mid, c_light, steps=14, depth=0.88):
        for s in range(steps):
            u = s / (steps - 1.0)
            k = 1 - depth * u
            sx, sy = -(1 - k) * W * 0.10, (1 - k) * H * 0.08
            pts = [P(sx + x * k, cy + (y - cy) * k + sy) for x, y in local]
            if u < 0.35:
                c = lerp_col(c_edge, c_mid, u / 0.35)
            else:
                c = lerp_col(c_mid, c_light, (u - 0.35) / 0.65)
            pygame.draw.polygon(lay, c + (255,), pts)

    body = new_layer(size)
    # --- unha natural (base)
    concentric(body, (232, 172, 166), (251, 208, 200), (255, 234, 228))
    lun = new_layer(size, (255, 244, 238))
    x0, y0 = P(-0.30 * W, 0.22 * H)
    x1, y1 = P(0.30 * W, -0.06 * H)
    pygame.draw.ellipse(lun, (255, 244, 238, 150), pygame.Rect(int(x0), int(y0), int(x1 - x0), int(y1 - y0)))
    body.blit(blur(lun, 4), (0, 0))
    tip = new_layer(size, (255, 248, 244))
    pygame.draw.polygon(tip, (255, 248, 244, 190),
                        [P(x, (0.90 + 0.06 * (x / (W / 2.0)) ** 2) * H) for x in
                         [(-W * 0.6 + i * W * 1.2 / 14) for i in range(15)]] +
                        [P(W * 0.7, 1.4 * H), P(-W * 0.7, 1.4 * H)])
    body.blit(blur(tip, 5), (0, 0))

    # --- esmalte
    if polish:
        if finish == "matte":
            ce, cm, cl = shade(polish, 0.86), polish, tint(polish, 0.10)
        else:
            ce, cm, cl = shade(polish, 0.60), polish, tint(polish, 0.40)
        pl = new_layer(size, polish)
        concentric(pl, ce, cm, cl)
        if progress < 1.0:
            yy = int(P(0, progress * 1.05 * H)[1])
            pygame.draw.rect(pl, tuple(polish) + (0,), (0, 0, size[0], max(0, yy)))
            pygame.draw.line(pl, tint(polish, 0.55) + (255,), (0, yy), (size[0], yy),
                             max(1, int(3 * A * scale)))
        body.blit(pl, (0, 0))
        cu = new_layer(size, shade(polish, 0.45))
        r = pygame.Rect(0, 0, int(W * 0.95 * A), int(H * 0.34 * A))
        r.center = (int(P(0, 0.01 * H)[0]), int(P(0, 0.01 * H)[1]))
        pygame.draw.ellipse(cu, shade(polish, 0.45) + (110,), r)
        body.blit(blur(cu, 5), (0, 0))
        if finish == "shimmer":
            rng = random.Random(seed + 11)
            sl = new_layer(size, (255, 255, 255))
            for _ in range(110):
                x, y = rng.uniform(-0.5, 0.5) * W, rng.random() * H
                c = rng.choice([tint(polish, 0.7), (255, 255, 255), tint(polish, 0.35)])
                px, py = P(x, y)
                pygame.draw.circle(sl, c + (255,), (int(px), int(py)), max(1, int(rng.uniform(0.5, 1.2) * A * scale)))
            body.blit(sl, (0, 0))

    # --- francesinha
    if st["french"]:
        fl = new_layer(size, st["french"])
        xs = [(-W * 0.62 + i * W * 1.24 / 20) for i in range(21)]
        pts = [P(x, (0.70 + 0.11 * (x / (W / 2.0)) ** 2) * H) for x in xs]
        pts += [P(W * 0.7, 1.5 * H), P(-W * 0.7, 1.5 * H)]
        pygame.draw.polygon(fl, tuple(st["french"]) + (255,), pts)
        body.blit(fl, (0, 0))

    # --- glitter
    if st["glitter"]:
        gc = st["glitter"]
        rng = random.Random(seed)
        wash = new_layer(size, gc)
        pygame.draw.polygon(wash, tuple(gc) + (45,), outline)
        body.blit(wash, (0, 0))
        gl = new_layer(size, gc)
        for _ in range(80):
            x, y = rng.uniform(-0.55, 0.55) * W, H * rng.random() ** 0.7
            c = rng.choice([gc, tint(gc, 0.55), (255, 255, 255), shade(gc, 0.8), (255, 236, 170)])
            px, py = P(x, y)
            pygame.draw.circle(gl, c + (255,), (int(px), int(py)), max(1, int(rng.uniform(0.8, 2.0) * A * scale)))
        for _ in range(5):
            px, py = P(rng.uniform(-0.4, 0.4) * W, rng.uniform(0.15, 0.95) * H)
            star4(gl, px, py, rng.uniform(2.5, 4.5) * A * scale, (255, 255, 255))
        body.blit(gl, (0, 0))

    # --- curvatura (sombra nas bordas = volume 3D)
    cv = new_layer(size, (90, 20, 50))
    for k, a in zip((1.0, 0.95, 0.90, 0.84, 0.78, 0.70), (80, 58, 40, 26, 14, 0)):
        sx, sy = -(1 - k) * W * 0.08, (1 - k) * H * 0.06
        pygame.draw.polygon(cv, (90, 20, 50, a), [P(sx + x * k, cy + (y - cy) * k + sy) for x, y in local])
    body.blit(cv, (0, 0))

    # --- brilho / reflexos
    ga = 1.0 if finish != "matte" else 0.22
    if not polish:
        ga = 0.55
    soft = new_layer(size, (255, 255, 255))
    hl = new_layer(size, (255, 255, 255))
    rim = new_layer(size, (255, 255, 255))
    left = sorted([(x, y) for x, y in local if x < 0 and 0.12 * H < y < 0.90 * H], key=lambda p: p[1])
    right = sorted([(x, y) for x, y in local if x > 0 and 0.12 * H < y < 0.90 * H], key=lambda p: p[1])
    if len(left) >= 4:
        n = len(left)
        outer = [P(x * 0.76, y) for x, y in left]
        inner = [P(x * (0.76 - 0.24 * math.sin(math.pi * i / (n - 1.0))), y) for i, (x, y) in enumerate(left)]
        pygame.draw.polygon(soft, (255, 255, 255, int(150 * ga)), outer + inner[::-1])
        inner2 = [P(x * (0.76 - 0.09 * math.sin(math.pi * i / (n - 1.0))), y) for i, (x, y) in enumerate(left)]
        pygame.draw.polygon(hl, (255, 255, 255, int(215 * ga)), outer + inner2[::-1])
    if len(right) >= 4:
        n = len(right)
        outer = [P(x * 0.86, y) for x, y in right]
        inner = [P(x * (0.86 - 0.10 * math.sin(math.pi * i / (n - 1.0))), y) for i, (x, y) in enumerate(right)]
        pygame.draw.polygon(rim, (255, 255, 255, int(70 * ga)), outer + inner[::-1])
    ex0, ey0 = P(-0.40 * W, 0.84 * H)
    ex1, ey1 = P(0.16 * W, 0.50 * H)
    pygame.draw.ellipse(soft, (255, 255, 255, int(80 * ga)),
                        pygame.Rect(int(ex0), int(ey0), int(ex1 - ex0), int(ey1 - ey0)))
    if ga > 0.5:
        sx0, sy0 = P(-0.30 * W, 0.78 * H)
        sx1, sy1 = P(-0.17 * W, 0.70 * H)
        pygame.draw.ellipse(hl, (255, 255, 255, 255),
                            pygame.Rect(int(sx0), int(sy0), int(sx1 - sx0), int(sy1 - sy0)))
        px, py = P(-0.09 * W, 0.64 * H)
        pygame.draw.circle(hl, (255, 255, 255, 255), (int(px), int(py)), max(1, int(1.1 * A * scale)))
    body.blit(blur(soft, 3), (0, 0))
    body.blit(hl, (0, 0))
    body.blit(rim, (0, 0))

    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(body, (0, 0))

    # --- decorações com sombra
    if st["decor"]:
        top = new_layer(size, (255, 255, 255))
        for kind, nx, ny, col, sz, rot in st["decor"]:
            px, py = P(nx * W / 2.0, ny * H)
            draw_sticker(top, kind, px, py, W * A, col, sz, rot)
        m = pygame.mask.from_surface(top)
        shd = m.to_surface(setcolor=(100, 30, 60, 120), unsetcolor=(100, 30, 60, 0))
        shd2 = new_layer(size, (100, 30, 60))
        shd2.blit(shd, (int(1.0 * scale * A), int(1.6 * scale * A)))
        out.blit(blur(shd2, 3), (0, 0))
        out.blit(top, (0, 0))

    ec = shade(polish, 0.50) + (150,) if polish else (205, 125, 130, 150)
    pygame.draw.polygon(out, ec, outline, max(1, int(1.3 * A * math.sqrt(scale))))

    final = pygame.transform.smoothscale(out, (sw, sh))
    res = (final, (ox, oy))
    _NAIL_CACHE[key] = res
    return res


# --------------------------------------------------------------------------
# A MÃO
# --------------------------------------------------------------------------
def build_finger_geo(f, n=40):
    bx, by = f["base"]
    a = math.radians(f["lean"])
    D = (math.sin(a), -math.cos(a))
    N = (-D[1], D[0])
    r = f["w1"] / 2.0
    C = (bx + D[0] * (f["length"] - r), by + D[1] * (f["length"] - r))
    M = ((bx + C[0]) / 2 + N[0] * f["bend"] * 2, (by + C[1]) / 2 + N[1] * f["bend"] * 2)
    pts, tan, wid = [], [], []
    for i in range(n + 1):
        t = i / float(n)
        x = (1 - t) ** 2 * bx + 2 * (1 - t) * t * M[0] + t * t * C[0]
        y = (1 - t) ** 2 * by + 2 * (1 - t) * t * M[1] + t * t * C[1]
        dx = 2 * (1 - t) * (M[0] - bx) + 2 * t * (C[0] - M[0])
        dy = 2 * (1 - t) * (M[1] - by) + 2 * t * (C[1] - M[1])
        ln = math.hypot(dx, dy) or 1.0
        pts.append((x, y))
        tan.append((dx / ln, dy / ln))
        wid.append(lerp(f["w0"], f["w1"], t ** 0.85))
    return dict(pts=pts, tan=tan, wid=wid)


def finger_poly(g, k=1.0, t0=0.0, shift=(0.0, 0.0)):
    pts, tan, wid = g["pts"], g["tan"], g["wid"]
    n = len(pts)
    i0 = int(round(t0 * (n - 1)))
    left, right = [], []
    for i in range(i0, n):
        p, t = pts[i], tan[i]
        nx, ny = -t[1], t[0]
        hw = wid[i] * 0.5 * k
        left.append((p[0] + nx * hw + shift[0], p[1] + ny * hw + shift[1]))
        right.append((p[0] - nx * hw + shift[0], p[1] - ny * hw + shift[1]))
    C, D = pts[-1], tan[-1]
    N = (-D[1], D[0])
    r = wid[-1] * 0.5 * k
    cap = []
    for j in range(1, 16):
        th = math.pi * j / 16.0
        cap.append((C[0] + r * (math.cos(th) * N[0] + math.sin(th) * D[0]) + shift[0],
                    C[1] + r * (math.cos(th) * N[1] + math.sin(th) * D[1]) + shift[1]))
    return left + cap + right[::-1]


def render_hand():
    """Desenha a mão (pele com volume, dobras e sombras). Retorna
    (mão, sombra, geometrias dos dedos)."""
    S = HAND_K * HAND_SS

    def T(p):
        return ((p[0] - HX0) * S, (p[1] - HY0) * S)

    size = (int(HW * S), int(HH * S))
    geos = [build_finger_geo(f) for f in FINGERS]
    palm = catmull(PALM_PTS, True, 8)
    order = [4, 3, 2, 1, 0]          # mindinho -> polegar (polegar por cima)

    # sombra projetada
    sil = new_layer(size, (90, 40, 60))
    pygame.draw.polygon(sil, (90, 40, 60, 255), [T(p) for p in palm])
    for g in geos:
        pygame.draw.polygon(sil, (90, 40, 60, 255), [T(p) for p in finger_poly(g)])
    shadow = blur(sil, 12)
    shadow.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_MULT)

    big = new_layer(size, SKIN_DARK)
    # palma com gradiente concentrico
    cx = sum(p[0] for p in PALM_PTS) / len(PALM_PTS)
    cy = sum(p[1] for p in PALM_PTS) / len(PALM_PTS)
    steps = 22
    for s in range(steps):
        u = s / (steps - 1.0)
        k = 0.99 - 0.85 * u
        sh = (-(1 - k) * 40, -(1 - k) * 25)
        col = lerp_col(SKIN_DARK, SKIN_MID, u / 0.55) if u < 0.55 else lerp_col(SKIN_MID, SKIN_LIGHT, (u - 0.55) / 0.45)
        poly = [T((cx + (x - cx) * k + sh[0], cy + (y - cy) * k + sh[1])) for x, y in palm]
        pygame.draw.polygon(big, col + (255,), poly)

    # dedos com gradiente cilíndrico
    for idx in order:
        g = geos[idx]
        hw0 = g["wid"][0] / 2.0
        steps = 20
        for s in range(steps):
            u = s / (steps - 1.0)
            k = 0.98 - 0.86 * u
            shift = (-(1 - k) * hw0 * 0.45, -(1 - k) * hw0 * 0.10)
            col = lerp_col(SKIN_DARK, SKIN_MID, u / 0.5) if u < 0.5 else lerp_col(SKIN_MID, SKIN_LIGHT, (u - 0.5) / 0.5)
            poly = finger_poly(g, k, (1 - k) * 0.30, shift)
            pygame.draw.polygon(big, col + (255,), [T(p) for p in poly])

    # suavização das junções dedo/palma
    jl = new_layer(size, SKIN_MID)
    for f, g in zip(FINGERS, geos):
        p = g["pts"][2]
        pygame.draw.circle(jl, SKIN_MID + (235,), (int(T(p)[0]), int(T(p)[1])), int(f["w0"] * 0.52 * S))
    big.blit(blur(jl, 10), (0, 0))

    # dobras das articulações
    cl = new_layer(size, (176, 112, 96))
    for f, g in zip(FINGERS, geos):
        lw = max(1, int(S * 0.8))
        for t, offs, hwf, curve in ((0.36, (-0.012, 0.0, 0.012), 0.60, 0.10),
                                    (0.68, (-0.010, 0.010), 0.55, 0.08)):
            for o in offs:
                i = int(clamp(t + o, 0, 1) * (len(g["pts"]) - 1))
                p, tn = g["pts"][i], g["tan"][i]
                nx, ny = -tn[1], tn[0]
                hw = g["wid"][i] * 0.5 * hwf
                line = []
                for j in range(-6, 7):
                    u = j / 6.0
                    bow = curve * g["wid"][i] * (1 - u * u) * 0.5
                    line.append(T((p[0] + nx * hw * u + tn[0] * bow, p[1] + ny * hw * u + tn[1] * bow)))
                pygame.draw.lines(cl, (176, 112, 96, 62), False, line, lw)
    big.blit(cl, (0, 0))

    final_size = (int(HW * HAND_K), int(HH * HAND_K))
    hand = pygame.transform.smoothscale(big, final_size)
    shadow = pygame.transform.smoothscale(shadow, final_size)
    return hand, shadow, geos


# --------------------------------------------------------------------------
# CLASSE UNHA
# --------------------------------------------------------------------------
class Nail:
    def __init__(self, name, origin, lean, width, hn):
        self.name = name
        self.origin = origin          # posição da cutícula na tela
        self.lean = lean              # graus (horário)
        self.width = width
        self.hn = hn
        self.state = blank_state()
        self.seed = random.randint(0, 100000)
        self.progress = 1.0
        self._local = {}

    # coordenadas ----------------------------------------------------------
    def local_outline(self, shape):
        if shape not in self._local:
            spec = SHAPE_BY_KEY[shape]
            H = self.hn * spec["hs"]
            self._local[shape] = [(x * self.width / 2.0, y * H) for x, y in catmull(spec["pts"], True, 8)]
        return self._local[shape]

    def height(self, shape):
        return self.hn * SHAPE_BY_KEY[shape]["hs"]

    def to_screen(self, lx, ly):
        a = math.radians(self.lean)
        rx, ry = math.cos(a), math.sin(a)
        dx, dy = math.sin(a), -math.cos(a)
        return (self.origin[0] + rx * lx + dx * ly, self.origin[1] + ry * lx + dy * ly)

    def to_local(self, pos):
        a = math.radians(self.lean)
        vx, vy = pos[0] - self.origin[0], pos[1] - self.origin[1]
        return (vx * math.cos(a) + vy * math.sin(a), vx * math.sin(a) - vy * math.cos(a))

    def screen_outline(self, shape):
        return [self.to_screen(x, y) for x, y in self.local_outline(shape)]

    def contains(self, pos, shape):
        lx, ly = self.to_local(pos)
        H = self.height(shape)
        cy = H * 0.5
        pt = (lx / 1.12, cy + (ly - cy) / 1.08)
        return point_in_poly(pt, self.local_outline(shape))

    def center(self, shape):
        return self.to_screen(0, self.height(shape) * 0.5)

    # desenho --------------------------------------------------------------
    def draw(self, screen, shape):
        surf, (ox, oy) = render_nail(shape, self.width, self.hn, self.state, self.seed, self.progress)
        key = (id(surf), round(self.lean, 1))
        rot = _ROT_CACHE.get(key)
        if rot is None:
            rot = pygame.transform.rotozoom(surf, -self.lean, 1.0)
            _ROT_CACHE[key] = rot
        w, h = surf.get_size()
        vy = oy - h / 2.0
        a = math.radians(-self.lean)
        vx2, vy2 = vy * math.sin(a), vy * math.cos(a)
        rect = rot.get_rect(center=(self.origin[0] - vx2, self.origin[1] - vy2))
        screen.blit(rot, rect)


# --------------------------------------------------------------------------
# ELEMENTOS DE INTERFACE
# --------------------------------------------------------------------------
_UI_CACHE = {}


def grad_round(size, top, bottom, radius, border=None, bw=2):
    key = ("gr", size, top, bottom, radius, border, bw)
    if key in _UI_CACHE:
        return _UI_CACHE[key]
    w, h = size
    s = pygame.Surface(size, pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(s, lerp_col(top, bottom, y / max(1.0, h - 1.0)), (0, y), (w, y))
    m = new_layer(size, (255, 255, 255))
    pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    s.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    if border:
        pygame.draw.rect(s, border, (0, 0, w, h), bw, border_radius=radius)
    _UI_CACHE[key] = s
    return s


def soft_shadow(size, radius, blur_px=10, alpha=70, color=(200, 90, 130)):
    key = ("ss", size, radius, blur_px, alpha, color)
    if key in _UI_CACHE:
        return _UI_CACHE[key]
    pad = blur_px * 2
    s = new_layer((size[0] + pad * 2, size[1] + pad * 2), color)
    pygame.draw.rect(s, color + (alpha,), (pad, pad, size[0], size[1]), border_radius=radius)
    s = blur(s, 4)
    _UI_CACHE[key] = (s, pad)
    return _UI_CACHE[key]


def make_swatch(color, r=19):
    key = ("sw", color, r)
    if key in _UI_CACHE:
        return _UI_CACHE[key]
    A = 3
    size = (2 * r + 14, 2 * r + 14)
    big = new_layer((size[0] * A, size[1] * A), color)
    c = (size[0] * A / 2.0, size[1] * A / 2.0 - 2 * A)
    sh = new_layer(big.get_size(), (150, 60, 90))
    pygame.draw.ellipse(sh, (150, 60, 90, 90), pygame.Rect(int(c[0] - r * A * 0.9), int(c[1] + r * A * 0.55),
                                                           int(r * A * 1.8), int(r * A * 0.8)))
    big.blit(blur(sh, 5), (0, 0))
    ring = shade(color, 0.55)
    pygame.draw.circle(big, ring + (255,), (int(c[0]), int(c[1])), r * A)
    sphere(big, c[0], c[1], r * A - 2 * A, color, steps=10, spec=False)
    hl = new_layer(big.get_size(), (255, 255, 255))
    pygame.draw.ellipse(hl, (255, 255, 255, 150), pygame.Rect(int(c[0] - r * A * 0.62), int(c[1] - r * A * 0.72),
                                                              int(r * A * 0.8), int(r * A * 0.46)))
    big.blit(blur(hl, 3), (0, 0))
    pygame.draw.circle(big, (255, 255, 255, 255), (int(c[0] - r * A * 0.30), int(c[1] - r * A * 0.46)), int(r * A * 0.09))
    surf = pygame.transform.smoothscale(big, size)
    _UI_CACHE[key] = surf
    return surf


def make_bottle(color):
    key = ("bt", color)
    if key in _UI_CACHE:
        return _UI_CACHE[key]
    A = 3
    w, h = 78, 118
    big = new_layer((w * A, h * A), color)

    def R(x, y, ww, hh):
        return pygame.Rect(int(x * A), int(y * A), int(ww * A), int(hh * A))

    sh = new_layer(big.get_size(), (150, 60, 90))
    pygame.draw.ellipse(sh, (150, 60, 90, 90), R(8, 104, 62, 12))
    big.blit(blur(sh, 4), (0, 0))
    pygame.draw.rect(big, (225, 205, 215, 255), R(10, 44, 58, 70), border_radius=16 * A)
    for i in range(9):
        u = i / 8.0
        c = lerp_col(shade(color, 0.62), color, u / 0.6) if u < 0.6 else lerp_col(color, tint(color, 0.35), (u - 0.6) / 0.4)
        pygame.draw.rect(big, c + (255,), R(12 + i * 1.1, 46 + i * 0.6, 54 - i * 1.6, 66 - i * 1.6), border_radius=int((14 - i * 0.8) * A))
    lab = new_layer(big.get_size(), (255, 255, 255))
    pygame.draw.rect(lab, (255, 255, 255, 215), R(20, 66, 38, 28), border_radius=8 * A)
    big.blit(lab, (0, 0))
    hp = [(39 * A + x, 80 * A + y) for x, y in heart_pts(0, 0, 9 * A, 0)]
    pygame.draw.polygon(big, (255, 120, 170, 255), hp)
    st = new_layer(big.get_size(), (255, 255, 255))
    pygame.draw.rect(st, (255, 255, 255, 120), R(15, 52, 5, 52), border_radius=3 * A)
    big.blit(blur(st, 2), (0, 0))
    pygame.draw.rect(big, (242, 236, 242, 255), R(27, 33, 24, 14), border_radius=3 * A)
    pygame.draw.rect(big, (50, 40, 48, 255), R(22, 4, 34, 32), border_radius=7 * A)
    for i in range(5):
        c = lerp_col((40, 32, 40), (96, 82, 94), i / 4.0)
        pygame.draw.rect(big, c + (255,), R(24 + i * 0.5, 6 + i * 0.5, 30 - i * 2.6, 28 - i), border_radius=int(6 * A))
    gl = new_layer(big.get_size(), (255, 255, 255))
    pygame.draw.rect(gl, (255, 255, 255, 110), R(27, 8, 5, 24), border_radius=2 * A)
    big.blit(gl, (0, 0))
    surf = pygame.transform.smoothscale(big, (w, h))
    _UI_CACHE[key] = surf
    return surf


def make_star_sprite(size, color=(255, 238, 248)):
    A = 4
    n = size * 2 * A
    s = new_layer((n, n), color)
    c = n // 2
    pygame.draw.circle(s, color + (70,), (c, c), int(n * 0.30))
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rad = n * 0.47 if i % 2 == 0 else n * 0.10
        pts.append((c + rad * math.cos(ang), c + rad * math.sin(ang)))
    pygame.draw.polygon(s, color + (255,), pts)
    return pygame.transform.smoothscale(s, (size * 2, size * 2))


# --------------------------------------------------------------------------
# JOGO
# --------------------------------------------------------------------------
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.f_title = make_font(34, bold=True, italic=True, serif=True)
        self.f_h = make_font(16, bold=True)
        self.f_b = make_font(14, bold=True)
        self.f_s = make_font(13)
        self.f_xs = make_font(11)
        self.f_big = make_font(40, bold=True, italic=True, serif=True)

        self.splash("Preparando seu salão...")
        self.shape = "oval"
        self.color_idx = 0
        self.finish = "gloss"
        self.decor_color = 0
        self.tool = ("polish",)
        self.mode = "edit"
        self.undo_stack = []
        self.particles = []
        self.toast = ("", 0.0)
        self.focus = None
        self.hover = None
        self.snapshot = None
        self.want_snapshot = False
        self.fx_time = 0.0

        self.sprites = [make_star_sprite(s) for s in (5, 8, 11, 15)]
        self.twinkles = [(random.randint(20, WIN_W - 20), random.randint(20, WIN_H - 20),
                          random.random() * 6.28, random.uniform(0.6, 1.6), random.randint(0, 3))
                         for _ in range(26)]
        self.build_background()
        self.build_hand()
        self.build_ui()
        self.build_decor_icons()

    # ------------------------------------------------------------------ setup
    def splash(self, text):
        self.screen.fill((255, 238, 246))
        t = self.f_big.render(text, True, PINK_DEEP)
        self.screen.blit(t, t.get_rect(center=(WIN_W // 2, WIN_H // 2)))
        pygame.display.flip()
        pygame.event.pump()

    def build_background(self):
        bg = pygame.Surface((WIN_W, WIN_H))
        for y in range(WIN_H):
            pygame.draw.line(bg, lerp_col((255, 245, 249), (249, 210, 228), y / float(WIN_H)), (0, y), (WIN_W, y))
        over = new_layer((WIN_W, WIN_H), (255, 255, 255))
        rng = random.Random(7)
        for _ in range(30):
            x, y, r = rng.randint(0, WIN_W), rng.randint(0, WIN_H), rng.randint(18, 70)
            c = rng.choice([(255, 255, 255), (255, 200, 222), (255, 228, 240)])
            a = rng.randint(30, 70)
            tmp = new_layer((r * 2 + 4, r * 2 + 4), c)
            pygame.draw.circle(tmp, c + (a,), (r + 2, r + 2), r)
            pygame.draw.circle(tmp, c + (min(255, a + 40),), (r + 2, r + 2), r, 2)
            over.blit(tmp, (x - r, y - r))
        bg.blit(over, (0, 0))
        # luz suave vindo do canto superior esquerdo
        glow = new_layer((WIN_W // 4, WIN_H // 4), (255, 255, 255))
        for i in range(40):
            rr = int(WIN_W * 0.30 * (1 - i / 40.0) / 1.0)
            pygame.draw.circle(glow, (255, 255, 255, int(2 + i * 1.3)), (WIN_W // 12, 0), max(1, rr // 4))
        bg.blit(pygame.transform.smoothscale(glow, (WIN_W, WIN_H)), (0, 0))
        # toalha onde a mão repousa
        tw, th = 600, WIN_H + 120
        tx = HAND_CX - tw // 2
        sh, pad = soft_shadow((tw, th), 60, 16, 90)
        bg.blit(sh, (tx - pad, -60 - pad + 8))
        tow = grad_round((tw, th), (255, 253, 254), (253, 230, 240), 60, (244, 196, 214), 4)
        bg.blit(tow, (tx, -60))
        lines = new_layer((tw, th), (244, 200, 216))
        for x in (22, 32):
            pygame.draw.line(lines, (244, 200, 216, 150), (x, 40), (x, th - 10), 2)
            pygame.draw.line(lines, (244, 200, 216, 150), (tw - x, 40), (tw - x, th - 10), 2)
        for y in range(70, th, 16):
            pygame.draw.line(lines, (244, 200, 216, 22), (50, y), (tw - 50, y), 1)
        bg.blit(lines, (tx, -60))
        self.bg = bg

    def build_hand(self):
        t0 = time.time()
        self.hand, self.hand_shadow, geos = render_hand()
        self.hand_ox = int(HAND_CX - 271 * HAND_K)
        self.hand_oy = int(55 - (143 - HY0) * HAND_K)
        self.nails = []
        for f, g in zip(FINGERS, geos):
            C, D = g["pts"][-1], g["tan"][-1]
            r = f["w1"] / 2.0
            apex = (C[0] + D[0] * r, C[1] + D[1] * r)
            wh = f["nail"] * f["w1"]
            hnh = wh * 1.18
            org = (apex[0] - D[0] * (hnh + 4), apex[1] - D[1] * (hnh + 4))
            sx = self.hand_ox + (org[0] - HX0) * HAND_K
            sy = self.hand_oy + (org[1] - HY0) * HAND_K
            lean = math.degrees(math.atan2(D[0], -D[1]))
            self.nails.append(Nail(f["name"], (sx, sy), lean, wh * HAND_K, hnh * HAND_K))
        self.focus = self.nails[1]
        print("Mão renderizada em %.2fs" % (time.time() - t0))

    def build_ui(self):
        self.left = pygame.Rect(18, 18, 276, 764)
        self.right = pygame.Rect(986, 18, 276, 764)
        self.sw_rects = []
        for i in range(len(POLISHES)):
            cx, cy = 56 + 50 * (i % 5), 272 + 50 * (i // 5)
            self.sw_rects.append(pygame.Rect(cx - 22, cy - 22, 44, 44))
        self.fin_rects = [pygame.Rect(28 + 88 * i, 474, 80, 32) for i in range(3)]
        self.lupa = pygame.Rect(30, 524, 252, 246)
        self.shape_rects = []
        for i in range(len(SHAPES)):
            self.shape_rects.append(pygame.Rect(994 + 66 * (i % 4), 62 + 94 * (i // 4), 62, 88))
        self.decor_rects = []
        for i in range(len(DECORS)):
            self.decor_rects.append(pygame.Rect(994 + 66 * (i % 4), 282 + 76 * (i // 4), 62, 70))
        self.dcol_rects = [pygame.Rect(997 + 32 * i, 452, 28, 28) for i in range(len(DECOR_COLORS))]
        self.tool_rects = {
            "remove": pygame.Rect(996, 498, 80, 38),
            "undo": pygame.Rect(1082, 498, 80, 38),
            "all": pygame.Rect(1168, 498, 86, 38),
        }
        self.btn_clear = pygame.Rect(1000, 640, 248, 48)
        self.btn_finish = pygame.Rect(1000, 700, 248, 64)
        self.btn_save = pygame.Rect(WIN_W // 2 - 270, WIN_H - 96, 250, 56)
        self.btn_back = pygame.Rect(WIN_W // 2 + 20, WIN_H - 96, 250, 56)

    def build_decor_icons(self):
        self.decor_icons = {}
        unit = {"heart": 240, "star": 240, "flower": 250, "gem": 470, "dots": 380, "line": 230}
        for kind, _ in DECORS:
            if kind in ("french", "glitter"):
                continue
            big = new_layer((160, 160), (255, 255, 255))
            col = (255, 130, 175) if kind in ("heart", "star", "flower") else (110, 170, 245)
            if kind == "dots":
                col = (250, 244, 246)
            if kind == "line":
                col = (235, 190, 70)
            draw_sticker(big, kind, 80, 80, unit[kind], col, 1.0, 0.0)
            self.decor_icons[kind] = pygame.transform.smoothscale(big, (40, 40))

    # ------------------------------------------------------------------ estado
    @property
    def color(self):
        return POLISHES[self.color_idx][1]

    @property
    def dcolor(self):
        return DECOR_COLORS[self.decor_color][1]

    def snapshot_state(self):
        return [dict(polish=n.state["polish"], finish=n.state["finish"], french=n.state["french"],
                     glitter=n.state["glitter"], decor=list(n.state["decor"])) for n in self.nails]

    def push_undo(self):
        self.undo_stack.append(self.snapshot_state())
        if len(self.undo_stack) > 60:
            self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack:
            self.show_toast("Nada para desfazer")
            return
        snap = self.undo_stack.pop()
        for n, s in zip(self.nails, snap):
            n.state = s
            n.progress = 1.0

    def show_toast(self, text):
        self.toast = (text, 2.6)

    def sparkle(self, pos, count=12, spread=70):
        for _ in range(count):
            ang = random.uniform(0, 6.283)
            sp = random.uniform(20, spread)
            self.particles.append(dict(x=pos[0], y=pos[1], vx=math.cos(ang) * sp, vy=math.sin(ang) * sp - 20,
                                       life=random.uniform(0.6, 1.3), max=1.3, s=random.randint(0, 3)))

    # ------------------------------------------------------------------ ações
    def apply_tool(self, nail, pos):
        kind = self.tool[0]
        self.focus = nail
        self.push_undo()
        st = nail.state
        if kind == "polish":
            st["polish"], st["finish"] = self.color, self.finish
            nail.progress = 0.0
            self.sparkle(nail.center(self.shape), 14)
        elif kind == "remove":
            nail.state = blank_state()
            nail.progress = 1.0
            self.sparkle(nail.center(self.shape), 8, 50)
        elif kind == "decor":
            d = self.tool[1]
            if d == "french":
                st["french"] = None if st["french"] == self.dcolor else self.dcolor
            elif d == "glitter":
                st["glitter"] = None if st["glitter"] == self.dcolor else self.dcolor
            else:
                lx, ly = nail.to_local(pos)
                H = nail.height(self.shape)
                nx = clamp(lx / (nail.width / 2.0), -0.62, 0.62)
                ny = clamp(ly / H, 0.14, 0.86)
                st["decor"].append((d, round(nx, 3), round(ny, 3), self.dcolor,
                                    1.0, round(random.uniform(-0.25, 0.25), 2)))
                if len(st["decor"]) > 7:
                    st["decor"].pop(0)
            self.sparkle(pos, 8, 45)

    def right_click(self, nail):
        st = nail.state
        if st["decor"]:
            self.push_undo()
            st["decor"].pop()
        elif st["french"] or st["glitter"]:
            self.push_undo()
            st["french"] = st["glitter"] = None
        elif st["polish"]:
            self.push_undo()
            st["polish"] = None
        self.sparkle(nail.center(self.shape), 6, 40)

    def paint_all(self):
        self.push_undo()
        for n in self.nails:
            n.state["polish"], n.state["finish"] = self.color, self.finish
            n.progress = 0.0
            self.sparkle(n.center(self.shape), 8)
        self.show_toast("Todas as unhas pintadas de %s" % POLISHES[self.color_idx][0])

    def remove_polish(self):
        self.push_undo()
        for n in self.nails:
            n.state = blank_state()
            n.progress = 1.0
            self.sparkle(n.center(self.shape), 6, 50)
        self.show_toast("Esmalte removido")

    def finish_look(self):
        self.mode = "final"
        self.want_snapshot = True
        for n in self.nails:
            self.sparkle(n.center(self.shape), 22, 120)

    def save_image(self):
        if self.snapshot is None:
            return
        folder = os.path.join(BASE_DIR, "looks")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "look_%s.png" % time.strftime("%Y%m%d_%H%M%S"))
        pygame.image.save(self.snapshot, path)
        self.show_toast("Foto salva em: looks/" + os.path.basename(path))

    # ------------------------------------------------------------------ eventos
    def handle_click(self, pos, button):
        if self.mode == "final":
            if button == 1:
                if self.btn_save.collidepoint(pos):
                    self.save_image()
                elif self.btn_back.collidepoint(pos):
                    self.mode = "edit"
            return
        if button == 1:
            for i, rc in enumerate(self.sw_rects):
                if rc.collidepoint(pos):
                    self.color_idx, self.tool = i, ("polish",)
                    self.sparkle(rc.center, 5, 30)
                    return
            for i, rc in enumerate(self.fin_rects):
                if rc.collidepoint(pos):
                    self.finish = FINISHES[i][0]
                    return
            for i, rc in enumerate(self.shape_rects):
                if rc.collidepoint(pos):
                    self.shape = SHAPES[i][0]
                    for n in self.nails:
                        self.sparkle(n.center(self.shape), 4, 35)
                    return
            for i, rc in enumerate(self.decor_rects):
                if rc.collidepoint(pos):
                    self.tool = ("decor", DECORS[i][0])
                    return
            for i, rc in enumerate(self.dcol_rects):
                if rc.collidepoint(pos):
                    self.decor_color = i
                    return
            if self.tool_rects["remove"].collidepoint(pos):
                self.tool = ("remove",)
                return
            if self.tool_rects["undo"].collidepoint(pos):
                self.undo()
                return
            if self.tool_rects["all"].collidepoint(pos):
                self.paint_all()
                return
            if self.btn_clear.collidepoint(pos):
                self.remove_polish()
                return
            if self.btn_finish.collidepoint(pos):
                self.finish_look()
                return
        for n in self.nails:
            if n.contains(pos, self.shape):
                if button == 1:
                    self.apply_tool(n, pos)
                elif button == 3:
                    self.right_click(n)
                return

    # ------------------------------------------------------------------ desenho
    def text(self, font, s, color, pos, anchor="topleft", shadow=None):
        img = font.render(s, True, color)
        r = img.get_rect()
        setattr(r, anchor, pos)
        if shadow:
            sh = font.render(s, True, shadow)
            self.screen.blit(sh, r.move(1, 1))
        self.screen.blit(img, r)
        return r

    def panel(self, rect):
        sh, pad = soft_shadow(rect.size, 28, 14, 70)
        self.screen.blit(sh, (rect.x - pad, rect.y - pad + 6))
        surf = grad_round(rect.size, (255, 255, 255, 232), (255, 238, 246, 232), 28, (255, 205, 224, 255), 2)
        self.screen.blit(surf, rect)
        inner = grad_round((rect.w - 14, rect.h - 14), (255, 255, 255, 0), (255, 255, 255, 0), 22, (255, 226, 238, 255), 1)
        self.screen.blit(inner, (rect.x + 7, rect.y + 7))

    def button(self, rect, label, mouse, active=False, primary=False, font=None, icon=None):
        font = font or self.f_b
        hover = rect.collidepoint(mouse)
        rad = rect.h // 2 if rect.h <= 48 else 22
        sh, pad = soft_shadow(rect.size, rad, 8, 95 if (active or primary) else 55)
        self.screen.blit(sh, (rect.x - pad, rect.y - pad + (5 if not hover else 7)))
        if primary:
            top, bot = (255, 160, 198), (234, 66, 128)
        elif active:
            top, bot = (255, 170, 204), (242, 100, 152)
        else:
            top, bot = (255, 255, 255), (255, 232, 241)
        if hover:
            top, bot = tint(top, 0.15), tint(bot, 0.10)
        r = rect.move(0, -2 if hover else 0)
        self.screen.blit(grad_round(rect.size, top, bot, rad, (255, 255, 255) if (active or primary) else (255, 190, 214), 2), r)
        shine = grad_round((rect.w - 12, rect.h // 2 - 2), (255, 255, 255, 120), (255, 255, 255, 10), max(2, rad - 4))
        self.screen.blit(shine, (r.x + 6, r.y + 3))
        col = (255, 255, 255) if (active or primary) else TEXT
        if label:
            self.text(font, label, col, r.center, "center", shadow=(190, 60, 110) if (active or primary) else None)
        return r

    def square_button(self, rect, mouse, active, label, content=None, base_y=None):
        hover = rect.collidepoint(mouse)
        sh, pad = soft_shadow(rect.size, 16, 8, 90 if active else 45)
        self.screen.blit(sh, (rect.x - pad, rect.y - pad + 4))
        top, bot = ((255, 176, 208), (246, 112, 160)) if active else ((255, 255, 255), (255, 236, 244))
        if hover:
            top, bot = tint(top, 0.15), tint(bot, 0.1)
        r = rect.move(0, -2 if hover else 0)
        self.screen.blit(grad_round(rect.size, top, bot, 16, (255, 255, 255) if active else (255, 196, 218), 2), r)
        if content is not None:
            if base_y is None:
                self.screen.blit(content, content.get_rect(center=(r.centerx, r.y + 28)))
            else:
                self.screen.blit(content[0], (r.centerx - content[1][0], r.y + base_y - content[1][1]))
        self.text(self.f_xs, label, (255, 255, 255) if active else TEXT, (r.centerx, r.bottom - 11), "center",
                  shadow=(200, 70, 120) if active else None)

    def draw_ui(self, mouse):
        self.panel(self.left)
        self.panel(self.right)
        # título
        self.text(self.f_title, "Nail Studio", PINK_DEEP, (self.left.centerx, 52), "center", shadow=(255, 220, 235))
        self.text(self.f_xs, "SALÃO DE MANICURE", TEXT_SOFT, (self.left.centerx, 82), "center")
        pygame.draw.line(self.screen, (255, 200, 222), (60, 96), (252, 96), 2)
        pygame.draw.circle(self.screen, PINK, (156, 96), 4)
        # frasco com cor atual
        self.screen.blit(make_bottle(self.color), (44, 104))
        self.text(self.f_xs, "COR ATUAL", TEXT_SOFT, (140, 126))
        name = POLISHES[self.color_idx][0]
        self.text(self.f_h, name, TEXT, (140, 144))
        fin = dict(FINISHES)[self.finish]
        self.text(self.f_s, "Acabamento: " + fin, TEXT_SOFT, (140, 168))
        # paleta
        self.text(self.f_h, "Esmaltes", TEXT, (36, 226))
        for i, rc in enumerate(self.sw_rects):
            sw = make_swatch(POLISHES[i][1])
            hov = rc.collidepoint(mouse)
            sel = (i == self.color_idx and self.tool[0] == "polish")
            c = (rc.centerx, rc.centery)
            pos = sw.get_rect(center=(c[0], c[1] + (-2 if hov else 0)))
            self.screen.blit(sw, pos)
            if sel:
                pygame.draw.circle(self.screen, (255, 255, 255), c, 25, 4)
                pygame.draw.circle(self.screen, PINK_DEEP, c, 25, 2)
            elif hov:
                pygame.draw.circle(self.screen, (255, 190, 214), c, 25, 2)
        # acabamento
        self.text(self.f_h, "Acabamento", TEXT, (36, 450))
        for i, rc in enumerate(self.fin_rects):
            self.button(rc, FINISHES[i][1], mouse, active=(self.finish == FINISHES[i][0]), font=self.f_s)
        # lupa
        sh, pad = soft_shadow(self.lupa.size, 22, 10, 50)
        self.screen.blit(sh, (self.lupa.x - pad, self.lupa.y - pad + 4))
        self.screen.blit(grad_round(self.lupa.size, (255, 255, 255), (255, 232, 242), 22, (255, 196, 218), 2), self.lupa)
        n = self.hover or self.focus
        self.text(self.f_xs, "LUPA  -  " + n.name.upper(), TEXT_SOFT, (self.lupa.centerx, self.lupa.y + 18), "center")
        hmax = 175.0
        sc = min(2.8, hmax / n.height(self.shape))
        surf, org = render_nail(self.shape, n.width * sc, n.hn * sc, n.state, n.seed, n.progress, sc)
        self.screen.blit(surf, (self.lupa.centerx - org[0], self.lupa.y + 36 + hmax - org[1] + 4))

        # direita: formatos
        self.text(self.f_h, "Formato das unhas", TEXT, (1004, 36))
        demo = dict(blank_state())
        demo["polish"] = self.color
        for i, rc in enumerate(self.shape_rects):
            icon = render_nail(SHAPES[i][0], 26, 28, demo, 3, 1.0, 1.0)
            self.square_button(rc, mouse, self.shape == SHAPES[i][0], SHAPES[i][1], icon, base_y=64)
        # decorações
        self.text(self.f_h, "Decoração", TEXT, (1004, 254))
        demo2 = blank_state()
        demo2["polish"] = (255, 214, 226)
        for i, rc in enumerate(self.decor_rects):
            kind, label = DECORS[i]
            act = self.tool == ("decor", kind)
            if kind == "french":
                st = blank_state()
                st["french"] = self.dcolor
                content = render_nail("oval", 22, 30, st, 5, 1.0, 1.0)
                self.square_button(rc, mouse, act, label, content, base_y=50)
            elif kind == "glitter":
                st = blank_state()
                st["glitter"] = self.dcolor
                st["polish"] = (255, 190, 214)
                content = render_nail("oval", 22, 30, st, 5, 1.0, 1.0)
                self.square_button(rc, mouse, act, label, content, base_y=50)
            else:
                self.square_button(rc, mouse, act, label, self.decor_icons[kind])
        self.text(self.f_s, "Cor da decoração: " + DECOR_COLORS[self.decor_color][0], TEXT_SOFT, (1004, 432))
        for i, rc in enumerate(self.dcol_rects):
            c = DECOR_COLORS[i][1]
            self.screen.blit(make_swatch(c, 11), make_swatch(c, 11).get_rect(center=rc.center))
            if i == self.decor_color:
                pygame.draw.circle(self.screen, (255, 255, 255), rc.center, 15, 3)
                pygame.draw.circle(self.screen, PINK_DEEP, rc.center, 15, 1)
        # ferramentas
        self.button(self.tool_rects["remove"], "Removedor", mouse, active=(self.tool[0] == "remove"), font=self.f_s)
        self.button(self.tool_rects["undo"], "Desfazer", mouse, font=self.f_s)
        self.button(self.tool_rects["all"], "Pintar todas", mouse, font=self.f_s)
        hint = ["Clique numa unha para aplicar.", "Botão direito: remove o último detalhe.", "Ctrl+Z: desfazer."]
        for i, h in enumerate(hint):
            self.text(self.f_xs, h, TEXT_SOFT, (1004, 556 + i * 18))
        self.button(self.btn_clear, "Remover esmalte", mouse)
        self.button(self.btn_finish, "Finalizar look", mouse, primary=True, font=self.f_h)

        # faixa de dica
        if self.tool[0] == "polish":
            msg = "Pincel: %s  -  clique em uma unha" % POLISHES[self.color_idx][0]
        elif self.tool[0] == "remove":
            msg = "Removedor: clique na unha para limpar"
        else:
            msg = "Decoração: %s  -  clique em uma unha" % dict(DECORS)[self.tool[1]]
        w = max(300, self.f_b.size(msg)[0] + 50)
        r = pygame.Rect(0, 0, w, 36)
        r.center = (WIN_W // 2, 34)
        self.screen.blit(soft_shadow(r.size, 18, 8, 50)[0], (r.x - 16, r.y - 16 + 4))
        self.screen.blit(grad_round(r.size, (255, 255, 255, 235), (255, 236, 245, 235), 18, (255, 196, 218), 2), r)
        self.text(self.f_b, msg, TEXT, r.center, "center")

    def draw_hand_scene(self, mouse):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.hand_shadow, (self.hand_ox + 10, self.hand_oy + 14))
        self.screen.blit(self.hand, (self.hand_ox, self.hand_oy))
        for n in self.nails:
            n.draw(self.screen, self.shape)
        if self.mode == "edit" and self.hover:
            pts = self.hover.screen_outline(self.shape)
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            x0, y0 = int(min(xs)) - 14, int(min(ys)) - 14
            w, h = int(max(xs) - min(xs)) + 28, int(max(ys) - min(ys)) + 28
            glow = new_layer((w, h), (255, 255, 255))
            shifted = [(x - x0, y - y0) for x, y in pts]
            pygame.draw.polygon(glow, (255, 255, 255, 120), shifted, 7)
            glow = blur(glow, 2)
            pygame.draw.polygon(glow, (255, 255, 255, 235), shifted, 2)
            self.screen.blit(glow, (x0, y0))

    def draw_particles(self, dt):
        t = self.fx_time
        for (x, y, ph, sp, si) in self.twinkles:
            a = 0.5 + 0.5 * math.sin(t * sp + ph)
            spr = self.sprites[si]
            spr.set_alpha(int(40 + 150 * a))
            self.screen.blit(spr, spr.get_rect(center=(x, y)))
        alive = []
        for p in self.particles:
            p["life"] -= dt
            if p["life"] <= 0:
                continue
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 60 * dt
            spr = self.sprites[p["s"]]
            spr.set_alpha(int(255 * clamp(p["life"] / p["max"], 0, 1)))
            self.screen.blit(spr, spr.get_rect(center=(p["x"], p["y"])))
            alive.append(p)
        self.particles = alive

    def draw_cursor(self, pos):
        x, y = pos
        in_stage = 300 < x < 980 and self.mode == "edit"
        if in_stage and self.tool[0] == "polish":
            c = self.color
            pygame.draw.line(self.screen, (255, 255, 255), (x + 4, y - 12), (x + 26, y - 56), 9)
            pygame.draw.line(self.screen, (255, 160, 200), (x + 4, y - 12), (x + 26, y - 56), 3)
            pygame.draw.line(self.screen, (214, 214, 224), (x + 2, y - 5), (x + 5, y - 13), 8)
            pygame.draw.line(self.screen, c, (x, y), (x + 3, y - 8), 7)
            pygame.draw.circle(self.screen, tint(c, 0.5), (x, y), 3)
        elif in_stage and self.tool[0] == "remove":
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 8, y - 8), 16)
            pygame.draw.circle(self.screen, (255, 170, 205), (x + 8, y - 8), 16, 3)
            pygame.draw.circle(self.screen, (255, 225, 238), (x + 4, y - 12), 6)
        elif in_stage and self.tool[0] == "decor":
            k = self.tool[1]
            if k in self.decor_icons:
                self.screen.blit(self.decor_icons[k], (x - 10, y - 38))
            pygame.draw.circle(self.screen, PINK_DEEP, (x, y), 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 5, 1)
        else:
            pts = [(x, y), (x, y + 20), (x + 5, y + 15), (x + 9, y + 23), (x + 13, y + 21), (x + 9, y + 13), (x + 16, y + 13)]
            pygame.draw.polygon(self.screen, (255, 255, 255), pts)
            pygame.draw.polygon(self.screen, PINK_DEEP, pts, 2)

    def draw_final_overlay(self, mouse):
        veil = new_layer((WIN_W, 150), (255, 240, 247))
        for yy in range(150):
            pygame.draw.line(veil, (255, 240, 247, int(220 * (1 - yy / 150.0))), (0, yy), (WIN_W, yy))
        self.screen.blit(veil, (0, 0))
        self.text(self.f_big, "Seu look está pronto!", PINK_DEEP, (WIN_W // 2, 56), "center", shadow=(255, 255, 255))
        self.text(self.f_s, "Gostou? Salve uma foto ou volte para continuar criando.", TEXT, (WIN_W // 2, 98), "center")
        self.button(self.btn_save, "Salvar foto", mouse, primary=True, font=self.f_h)
        self.button(self.btn_back, "Continuar editando", mouse, font=self.f_h)

    def draw_toast(self, dt):
        text, life = self.toast
        if life <= 0:
            return
        self.toast = (text, life - dt)
        a = int(255 * clamp(life / 0.6, 0, 1))
        img = self.f_b.render(text, True, (255, 255, 255))
        r = pygame.Rect(0, 0, img.get_width() + 44, 40)
        r.center = (WIN_W // 2, WIN_H - 30 if self.mode == "edit" else WIN_H - 120)
        box = grad_round(r.size, (244, 100, 150), (226, 70, 124), 20)
        box.set_alpha(a)
        img.set_alpha(a)
        self.screen.blit(box, r)
        self.screen.blit(img, img.get_rect(center=r.center))

    # ------------------------------------------------------------------ loop
    def update_nails(self, dt):
        for n in self.nails:
            if n.progress < 1.0:
                n.progress = min(1.0, n.progress + dt / 0.45)

    def run(self):
        pygame.mouse.set_visible(False)
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.fx_time += dt
            mouse = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_z and (e.mod & pygame.KMOD_CTRL) and self.mode == "edit":
                        self.undo()
                    elif e.key == pygame.K_ESCAPE:
                        if self.mode == "final":
                            self.mode = "edit"
                        else:
                            running = False
                    elif e.key == pygame.K_s and self.mode == "final":
                        self.save_image()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button in (1, 3):
                    self.handle_click(e.pos, e.button)

            self.hover = None
            if self.mode == "edit" and 300 < mouse[0] < 980:
                for n in self.nails:
                    if n.contains(mouse, self.shape):
                        self.hover = n
                        break
            self.update_nails(dt)

            self.draw_hand_scene(mouse)
            if self.want_snapshot:
                self.snapshot = self.screen.subsurface(pygame.Rect(340, 0, 610, WIN_H)).copy()
                self.want_snapshot = False
            self.draw_particles(dt)
            if self.mode == "edit":
                self.draw_ui(mouse)
            else:
                self.draw_final_overlay(mouse)
            self.draw_toast(dt)
            self.draw_cursor(mouse)
            pygame.display.flip()
        pygame.quit()


def main():
    pygame.init()
    pygame.display.set_caption("Nail Studio - Jogo de Manicure")
    try:
        screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.SCALED | pygame.RESIZABLE)
    except pygame.error:
        screen = pygame.display.set_mode((WIN_W, WIN_H))
    Game(screen).run()


if __name__ == "__main__":
    main()
    sys.exit(0)