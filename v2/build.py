# Assemble v2.html : sections nouvelles + blocs communs repris tels quels de index.html (v1).
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
v1 = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()

def cut(a, b):
    i = v1.index(a); j = v1.index(b, i)
    return v1[i:j]

symbols = cut('<svg width="0" height="0"', '<header')
header = cut('<header class="bar"', '<main>').replace('index.html#', '#')
common = cut('  <!-- SPONSORS ACTUELS -->', '</main>')
common = common.replace('<p>Slide Session · association étudiante du Pôle Léonard de Vinci, La Défense · depuis 1999</p>',
  '<p>Slide Session · association étudiante du Pôle Léonard de Vinci, La Défense · depuis 1999 · <a class="x-switch" href="index.html">Voir la version 1</a></p>')
cart = cut('    <aside class="cart"', '  </section>\n\n  <!-- SPONSORS')

MTN_FAR = 'M0 220V120l90-48 70 30 110-80 80 52 90-38 120 70 100-60 110 46 90-30 120 74 100-54 110 40 90-22 140 60V220Z'
MTN_NEAR = 'M0 160V92c120-40 220-30 330 6s210 36 330-10 230-60 360-24 220 52 340 30 160-20 220-12V160Z'

page = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Slide Session · l'asso de ski du Pôle Léonard de Vinci</title>
<meta name="description" content="Slide Session, l'association de ski du Pôle Léonard de Vinci depuis 1999 : GEM Altigliss Challenge, palmarès, goodies, sponsors et partenariats.">
<link rel="icon" href="assets/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Jost:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="preload" as="image" href="v2/img/skis/skis-000.webp">
<link rel="stylesheet" href="scrollcraft.css">
<link rel="stylesheet" href="site.css">
<link rel="stylesheet" href="v2/v2.css">
</head>
<body class="v2">

{symbols}{header}<main>

  <!-- HÉROS 3D : « SLIDE » derrière, skis Blender au milieu, « SESSION » devant, neige -->
  <section class="x-hero" id="haut-page">
    <div class="x-hero__stage">
      <div class="x-sky" aria-hidden="true"></div>
      <svg class="x-mtn x-mtn--far" viewBox="0 0 1420 220" preserveAspectRatio="none" aria-hidden="true"><path d="{MTN_FAR}"/></svg>
      <p class="x-word x-word--back" aria-hidden="true">Slide</p>
      <img class="x-skis-poster" src="v2/img/skis/skis-000.webp" alt="" width="720" height="960" fetchpriority="high">
      <canvas class="x-skis" width="720" height="960" aria-hidden="true"></canvas>
      <svg class="x-mtn x-mtn--near" viewBox="0 0 1580 160" preserveAspectRatio="none" aria-hidden="true"><path d="{MTN_NEAR}"/></svg>
      <p class="x-word x-word--front" aria-hidden="true">Session</p>
      <canvas class="hero__snow" aria-hidden="true"></canvas>
      <div class="x-hero__copy">
        <h1 class="sr-only">Slide Session, l'asso de ski du Pôle Léonard de Vinci</h1>
        <p class="x-kicker">L'asso de ski du Pôle Léonard de Vinci · depuis 1999</p>
        <p class="x-lead">Rendez-vous du 13 au 20 mars 2027 à La Plagne pour notre 11<sup>e</sup> GEM Altigliss Challenge.</p>
        <div class="band__cta">
          <a class="btn btn--solid" href="#partenaire">Devenir partenaire</a>
          <a class="btn btn--ghost" href="#goodies">Les goodies</a>
        </div>
      </div>
    </div>
  </section>

  <!-- TEASER -->
  <section class="x-teaser" aria-labelledby="teaser-titre">
    <div class="x-teaser__frame">
      <video muted loop playsinline preload="none" poster="assets/teaser-poster.webp" data-src="assets/teaser.mp4" data-src-mobile="assets/teaser-m.mp4"
             aria-label="Teaser vidéo de Slide Session : ski, Altigliss et soirées"></video>
    </div>
    <div class="x-teaser__bar">
      <div>
        <h2 class="caps caps--lg" id="teaser-titre">Le teaser 2026-2027</h2>
        <p>Une saison de poudreuse, de courses et d'après-ski en une minute et demie.</p>
      </div>
      <button type="button" class="x-play" aria-pressed="false"><span>Lecture</span></button>
    </div>
  </section>

  <!-- L'ASSO -->
  <section class="x-asso wrap" id="asso" data-sc-act="flow">
    <div class="x-asso__text" data-sc-in data-sc-stagger="80">
      <h2 class="caps caps--lg">Une famille depuis 1999</h2>
      <p class="lead">Slide Session est l'association de ski du Pôle Léonard de Vinci, à La Défense, et l'une des plus anciennes du pôle.</p>
      <p>Elle réunit les étudiants d'EMLV, ESILV et IIM autour du voyage au ski, des soirées et, chaque année, du GEM Altigliss Challenge, la coupe du monde étudiante de ski et de snowboard.</p>
      <ul class="x-facts">
        <li><b>1999</b><span>année de création</span></li>
        <li><b>60</b><span>membres actifs</span></li>
        <li><b>3</b><span>écoles : EMLV, ESILV, IIM</span></li>
        <li><b>11<sup>e</sup></b><span>Altigliss d'affilée</span></li>
      </ul>
    </div>
    <div class="x-asso__visual">
      <img class="x-asso__photo" data-sc-parallax="0.05" src="assets/team-flag.webp" alt="La team Slide Session avec son drapeau en haut des pistes" loading="lazy">
      <img class="x-asso__skier" data-sc-parallax="-0.14" src="v2/img/skieur.webp" alt="Skieur Slide Session modélisé en 3D, casque jaune et veste bleue, en position de descente" loading="lazy">
      <span class="x-asso__tag">60 riders</span>
    </div>
  </section>

  <!-- LES 3 CHALLENGES -->
  <section class="x-chal" id="challenges">
    <div class="wrap">
      <div class="x-chal__head" data-sc-in>
        <h2 class="caps caps--lg">Le GEM Altigliss Challenge</h2>
        <p>Organisé depuis plus de 25 ans par Grenoble École de Management : 1 000 étudiants, 30 nationalités, 90 équipes. La 27<sup>e</sup> édition se court à La Plagne.</p>
      </div>
      <ol data-sc-in data-sc-stagger="90">
        <li><img src="assets/ch-ski.webp" alt="" width="84" height="84" loading="lazy"><h3>Challenge Ski</h3><p>Face aux meilleurs skieurs étudiants, sur les épreuves phares de la coupe du monde.<small>Géant · Spécial Rossignol · Skicross · Parallèle</small></p></li>
        <li><img src="assets/ch-montagne.webp" alt="" width="84" height="84" loading="lazy"><h3>Challenge Montagne</h3><p>Des épreuves sportives au cœur du domaine de La Plagne.<small>Biathlon · Recherche DVA · Ski de rando · Raquettes</small></p></li>
        <li><img src="assets/ch-village.webp" alt="" width="84" height="84" loading="lazy"><h3>Challenge Village</h3><p>Représenter son école : esprit d'équipe, détermination et beaucoup de bruit.<small>Snooc · Snow volley · Hockey · Épreuve mystère</small></p></li>
      </ol>
    </div>
  </section>

  <!-- PALMARÈS : podium 3D -->
  <section class="x-palm" id="palmares">
    <div class="wrap">
      <div class="x-palm__head">
        <h2 class="caps caps--lg">Notre palmarès</h2>
        <p>Toujours 30 riders au départ. Au village : 3<sup>e</sup>, 5<sup>e</sup>, 4<sup>e</sup>, 2<sup>e</sup>… la 1<sup>re</sup> place est pour 2027.</p>
      </div>
      <div class="x-tabs" role="tablist" aria-label="Choisir une année">
        <button type="button" role="tab" data-y="2023" aria-controls="palm-panel">2023</button>
        <button type="button" role="tab" data-y="2024" aria-controls="palm-panel">2024</button>
        <button type="button" role="tab" data-y="2025" aria-controls="palm-panel">2025</button>
        <button type="button" role="tab" data-y="2026" aria-controls="palm-panel">2026</button>
        <button type="button" role="tab" data-y="2027" aria-controls="palm-panel">2027</button>
      </div>
      <div class="x-palm__stage">
        <img class="x-palm__podium" src="v2/img/podium.webp" alt="Podium 3D aux couleurs Slide Session, drapeau de l'asso sur la 1re marche" loading="lazy">
        <div id="palm-panel" role="tabpanel" aria-live="polite">
          <ul class="x-ranks"></ul>
          <p class="x-palm__note"></p>
        </div>
      </div>
    </div>
  </section>

  <!-- PHOTOS -->
  <section class="x-photos wrap" id="galerie">
    <div class="x-photos__head">
      <h2 class="caps caps--lg">Photos phares</h2>
      <a class="btn" href="photos.html">Toutes les photos</a>
    </div>
    <div class="x-mosaic">
      <img class="t2" src="assets/unicorn.webp" alt="Rider déguisé en licorne en slalom géant" loading="lazy">
      <img class="w2" src="assets/hero.webp" alt="Le podium, drapeau Slide Session déployé" loading="lazy">
      <img src="assets/g-redbull.webp" alt="Skieur en l'air devant l'arche Red Bull" loading="lazy">
      <img class="t2" src="assets/g-gs.webp" alt="Slalom géant sous le télésiège" loading="lazy">
      <img src="assets/g-dj.webp" alt="DJ set sur scène devant l'écran Slide" loading="lazy">
      <img class="w2" src="assets/g-crew.webp" alt="L'équipe en vestes bleues au pied des pistes" loading="lazy">
      <img src="assets/g-friends.webp" alt="Membres déguisés au village" loading="lazy">
    </div>
  </section>

  <!-- GOODIES : le bonnet licorne 3D en vedette -->
  <section class="goodies x-goodies" id="goodies">
    <div class="wrap">
      <div class="x-goodies__hero">
        <img src="v2/img/bonnet.webp" alt="Bonnet licorne Slide Session modélisé en 3D : rose, corne dorée, bande bleue" loading="lazy">
        <div>
          <span class="x-pill">La star de la boutique</span>
          <h2 class="caps caps--lg">Les goodies</h2>
          <p>Le pull Slide × Altigliss, les tee-shirts, le débardeur et le bob. Tu choisis, tu envoies ta commande, on te recontacte pour le paiement et la remise en main propre au pôle.</p>
        </div>
      </div>
      <div class="shop"></div>
    </div>
{cart}  </section>

{common}</main>

<script src="scrollcraft.js"></script>
<script src="site.js"></script>
<script src="v2/v2.js"></script>
</body>
</html>
'''
open(os.path.join(ROOT, 'v2.html'), 'w', encoding='utf-8').write(page)
print('v2.html', len(page))
