# Textures pour Blender : dessus de ski Slide et drapeau Slide (à partir du logo de l'asso).
from PIL import Image, ImageDraw
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = Image.open(os.path.join(HERE, '..', '..', 'assets', 'logo.png')).convert('RGBA')
BLUE, VIOLET, YELLOW, INK = (42, 49, 180), (91, 63, 216), (255, 185, 55), (21, 23, 79)


def gradient(w, h, a, b):
    im = Image.new('RGB', (w, h))
    px = im.load()
    for x in range(w):
        t = x / (w - 1)
        c = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
        for y in range(h):
            px[x, y] = c
    return im


# Dessus de ski : u = longueur (talon à gauche, spatule à droite), v = largeur
W, H = 2048, 256
ski = gradient(W, H, INK, BLUE).convert('RGBA')
d = ImageDraw.Draw(ski)
for i in range(7):  # chevrons jaunes vers la spatule
    x = 1500 + i * 46
    d.polygon([(x, 0), (x + 22, 0), (x + 52, H // 2), (x + 22, H), (x, H), (x + 30, H // 2)], fill=YELLOW + (255,))
d.rectangle([0, 0, 120, H], fill=VIOLET + (255,))  # talon violet
d.rectangle([0, 0, W, 10], fill=YELLOW + (255,))
d.rectangle([0, H - 10, W, H], fill=YELLOW + (255,))
lg = LOGO.resize((int(LOGO.width * 210 / LOGO.height), 210), Image.LANCZOS)
ski.alpha_composite(lg, (620, (H - 210) // 2))
ski.convert('RGB').save(os.path.join(HERE, 'tex-ski.png'))

# Drapeau Slide : bleu-violet, logo au centre
flag = gradient(1024, 640, BLUE, VIOLET).convert('RGBA')
lg = LOGO.resize((int(LOGO.width * 420 / LOGO.height), 420), Image.LANCZOS)
flag.alpha_composite(lg, ((1024 - lg.width) // 2, 110))
flag.convert('RGB').save(os.path.join(HERE, 'tex-flag.png'))

# Bande du bonnet : bleu avec logo
band = Image.new('RGBA', (2048, 256), BLUE + (255,))
lg = LOGO.resize((int(LOGO.width * 200 / LOGO.height), 200), Image.LANCZOS)
for x in (380, 1280):
    band.alpha_composite(lg, (x, 28))
band.convert('RGB').save(os.path.join(HERE, 'tex-band.png'))
print('textures ok')
