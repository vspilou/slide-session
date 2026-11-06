(function () {
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var CONTACT = 'yohann.baduy@edu.devinci.fr';

  /* ---------- menu mobile ---------- */
  var bar = document.querySelector('.bar'), menu = bar.querySelector('.bar__menu');
  menu.addEventListener('click', function () {
    var open = bar.classList.toggle('is-open');
    menu.setAttribute('aria-expanded', open);
  });
  bar.querySelectorAll('.bar__nav a').forEach(function (a) {
    a.addEventListener('click', function () { bar.classList.remove('is-open'); menu.setAttribute('aria-expanded', false); });
  });

  /* ---------- vidéo du héros : version légère sur mobile, rien en mouvement réduit (le poster reste) ---------- */
  var vid = document.querySelector('.hero__bg');
  if (vid && !reduce) {
    vid.src = matchMedia('(max-width: 860px)').matches ? vid.dataset.srcMobile : vid.dataset.src;
    vid.play().catch(function () {});
  }

  /* ---------- neige du héros (plan avant) ---------- */
  [].forEach.call(reduce ? [] : document.querySelectorAll('.hero__snow'), function (cv) {
    var ctx = cv.getContext('2d'), flakes = [], run = false, W, H;
    var size = function () {
      var d = Math.min(devicePixelRatio || 1, 2);
      W = cv.clientWidth; H = cv.clientHeight; cv.width = W * d; cv.height = H * d; ctx.setTransform(d, 0, 0, d, 0, 0);
    };
    size(); addEventListener('resize', size);
    for (var i = 0; i < 90; i++) flakes.push({ x: Math.random(), y: Math.random(), r: Math.random() * 2.2 + .6, s: Math.random() * .4 + .25, w: Math.random() * 6.28 });
    var tick = function () {
      if (!run) return;
      ctx.clearRect(0, 0, W, H); ctx.fillStyle = 'rgba(255,255,255,.85)';
      flakes.forEach(function (f) {
        f.y += f.s * f.r / H * 1.6; f.w += .01; if (f.y > 1.02) { f.y = -.02; f.x = Math.random(); }
        ctx.beginPath(); ctx.arc(f.x * W + Math.sin(f.w) * 14, f.y * H, f.r, 0, 6.28); ctx.fill();
      });
      requestAnimationFrame(tick);
    };
    new IntersectionObserver(function (e) { run = e[0].isIntersecting; if (run) tick(); }).observe(cv);
  });

  /* ---------- SLIDE SESSION en 3D : 40 images Blender transparentes, pilotées par le scroll ---------- */
  var sk = document.querySelector('.sk');
  if (sk) {
    var skStage = sk.querySelector('.sk__stage'), skCv = sk.querySelector('.sk__skis'), skCtx = skCv.getContext('2d'),
        SKN = 40, skFrames = [], skReady = 0, skDrawn = -1;
    var skDraw = function () {
      var r = sk.getBoundingClientRect(), span = r.height - innerHeight;
      var p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
      skStage.style.setProperty('--p', p.toFixed(4));
      if (skReady < SKN) return;
      var idx = Math.round(p * (SKN - 1));
      if (idx === skDrawn) return;
      skCtx.clearRect(0, 0, skCv.width, skCv.height);
      skCtx.drawImage(skFrames[idx], 0, 0, skCv.width, skCv.height);
      skDrawn = idx;
    };
    // les images ne se chargent qu'à l'approche de la section, pour ne pas ralentir l'arrivée sur le site
    var skLoad = function () {
      for (var k = 0; k < SKN; k++) {
        var im = new Image();
        im.decoding = 'async';
        im.onload = function () { if (++skReady === SKN) { sk.classList.add('is-live'); skDraw(); } };
        im.src = 'assets/skis/skis-' + String(k).padStart(3, '0') + '.webp';
        skFrames.push(im);
      }
    };
    if (!reduce) {
      var skIo = new IntersectionObserver(function (e) { if (e[0].isIntersecting) { skIo.disconnect(); skLoad(); } }, { rootMargin: '100% 0px' });
      skIo.observe(sk);
      var skQ = false;
      addEventListener('scroll', function () { if (!skQ) { skQ = true; requestAnimationFrame(function () { skQ = false; skDraw(); }); } }, { passive: true });
      addEventListener('resize', skDraw);
      skDraw();
    }
  }

  /* ---------- palmarès : la piste se trace avec le scroll ---------- */
  var sl = document.querySelector('.slalom');
  if (sl) {
    var stage = sl.querySelector('.slalom__stage'), trace = sl.querySelector('.slalom__trace'),
        ghost = sl.querySelector('.slalom__ghost'), svg = sl.querySelector('.slalom__svg'),
        skier = sl.querySelector('.slalom__skier'), gates = [].slice.call(sl.querySelectorAll('.gate')),
        len = 0, marks = [];
    var layout = function () {
      var w = stage.clientWidth, h = stage.clientHeight, mob = w < 860;
      // départ en haut, puis une porte par année, en zigzag
      var xs = mob ? [.16, .30, .12, .30, .14] : [.56, .78, .5, .74, .52];
      var ys = mob ? [.27, .42, .57, .72, .87] : [.22, .37, .52, .67, .8];
      var pts = [[mob ? .5 : .62, mob ? .3 : .12]];
      gates.forEach(function (g, i) {
        g.style.setProperty('--x', xs[i]); g.style.setProperty('--y', ys[i]);
        g.dataset.side = mob ? 'r' : (xs[i] > .65 ? 'r' : 'l');
        pts.push([xs[i], ys[i]]);
      });
      pts.push([mob ? .5 : .6, 1.04]);
      pts = pts.map(function (p) { return [p[0] * w, p[1] * h]; });
      // Catmull-Rom vers Bézier : une courbe qui passe par chaque porte
      var d = 'M' + pts[0];
      for (var i = 0; i < pts.length - 1; i++) {
        var p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
        d += 'C' + [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]].join(' ');
      }
      svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
      trace.setAttribute('d', d); ghost.setAttribute('d', d);
      len = trace.getTotalLength();
      trace.style.strokeDasharray = len;
      // longueur de piste à laquelle on passe chaque porte
      marks = gates.map(function (g, i) {
        var best = 0, bd = 1e9, gx = pts[i + 1][0], gy = pts[i + 1][1];
        for (var s = 0; s <= len; s += 4) {
          var q = trace.getPointAtLength(s), dd = (q.x - gx) * (q.x - gx) + (q.y - gy) * (q.y - gy);
          if (dd < bd) { bd = dd; best = s; }
        }
        return best;
      });
      draw();
    };
    var draw = function () {
      var r = sl.getBoundingClientRect(), span = r.height - innerHeight;
      var p = reduce ? 1 : Math.min(1, Math.max(0, -r.top / (span || 1) * 1.08));
      var at = p * len;
      trace.style.strokeDashoffset = len - at;
      var q = trace.getPointAtLength(Math.max(at, 0.01));
      // le skieur suit la pente : il regarde vers où il va et se penche avec elle
      var a = trace.getPointAtLength(Math.max(at - 6, 0)), b = trace.getPointAtLength(Math.min(at + 6, len));
      var dx = b.x - a.x, dy = b.y - a.y, dir = dx < 0 ? -1 : 1;
      var tilt = Math.min(55, Math.atan2(Math.max(dy, 0), Math.abs(dx) || .001) * 57.3);
      skier.style.transform = 'translate(' + q.x + 'px,' + q.y + 'px) scaleX(' + dir + ') rotate(' + tilt + 'deg)';
      gates.forEach(function (g, i) { g.classList.toggle('is-on', at >= marks[i] - 2); });
    };
    var queued = false;
    addEventListener('scroll', function () { if (!queued) { queued = true; requestAnimationFrame(function () { queued = false; draw(); }); } }, { passive: true });
    addEventListener('resize', layout);
    document.fonts && document.fonts.ready.then(layout);
    layout();
  }

  /* ---------- boutique : le merch de l'asso, photos en carrousel ---------- */
  // prix: null = « Prix à confirmer » (seul le pull a un prix connu). Modifier ici.
  var TAILLES = ['XS', 'S', 'M', 'L', 'XL'];
  var PRODUITS = [
    { id: 'pull', nom: 'Pull Slide x Altigliss', prix: 45, tailles: TAILLES,
      txt: 'Noir. GEM Altigliss Challenge et Slide devant, la licorne Slide dans le dos.',
      photos: [['pull-1', 'Pull noir vu de face : logos GEM Altigliss Challenge et Slide Session'], ['pull-2', 'Pull noir vu de dos : grande licorne Slide']] },
    { id: 'tee-alt', nom: 'T-shirt Alt. 2 000 m', prix: null, tailles: TAILLES,
      txt: 'Marine. Logo Slide devant, skieur « Slide Session, Alt. 2,000 m » dans le dos.',
      photos: [['tee-alt-1', 'T-shirt marine vu de face : logo Slide Session'], ['tee-alt-2', 'T-shirt marine vu de dos : skieur et inscription Slide Session Alt. 2,000 m']] },
    { id: 'tee-masque', nom: 'T-shirt Slide masque', prix: null, tailles: TAILLES,
      txt: 'Écru. Masque de ski « Slide » brodé devant, en grand dans le dos.',
      photos: [['tee-masque-1', 'T-shirt écru, devant et dos, sur cintres'], ['tee-masque-2', 'Gros plan de la broderie du devant : masque de ski Slide'], ['tee-masque-3', 'Gros plan du dos : masque Slide, montagne et skis croisés']] },
    { id: 'tee-blanc', nom: 'T-shirt Slide blanc', prix: null, tailles: TAILLES,
      txt: 'Blanc. Logo Slide Session brodé côté cœur.',
      photos: [['tee-blanc-1', 'T-shirt blanc, logo Slide Session côté cœur']] },
    { id: 'debardeur', nom: 'Débardeur Slide', prix: null, tailles: TAILLES,
      txt: 'Blanc. Logo Slide Session brodé côté cœur.',
      photos: [['debardeur-1', 'Débardeur blanc, logo Slide Session côté cœur']] },
    { id: 'bob', nom: 'Bob Slide Session', prix: null, tailles: null,
      txt: 'Beige. Logo Slide Session brodé, cordon réglable. Taille unique.',
      photos: [['bob-1', 'Bob beige avec le logo Slide Session brodé'], ['bob-2', 'Gros plan de la broderie Slide Session sur le bob']] }
  ];
  var cart = [], shop = document.querySelector('.shop'),
      fab = document.querySelector('.cart__fab'), drawer = document.querySelector('.cart'),
      list = drawer.querySelector('.cart__list'), total = drawer.querySelector('.cart__total');
  var eur = function (n) { return n.toLocaleString('fr-FR') + ' €'; };
  var prixTxt = function (n) { return n == null ? 'Prix à confirmer' : eur(n); };

  shop.innerHTML = PRODUITS.map(function (p) {
    var many = p.photos.length > 1;
    return '<article class="item" data-id="' + p.id + '">' +
      '<div class="gal"' + (many ? ' role="group" aria-roledescription="carrousel" aria-label="Photos : ' + p.nom + '"' : '') + '>' +
        '<div class="gal__track">' + p.photos.map(function (ph, i) {
          return '<img src="assets/merch/' + ph[0] + '.webp" alt="' + ph[1] + '" width="1000" height="1000" loading="lazy"' + (many ? ' aria-label="' + (i + 1) + ' sur ' + p.photos.length + '"' : '') + '>';
        }).join('') + '</div>' +
        (many ? '<button type="button" class="gal__nav gal__nav--prev" aria-label="Photo précédente">‹</button>' +
                '<button type="button" class="gal__nav gal__nav--next" aria-label="Photo suivante">›</button>' +
                '<div class="gal__dots">' + p.photos.map(function (ph, i) {
                  return '<button type="button" aria-label="Photo ' + (i + 1) + ' sur ' + p.photos.length + '"' + (i ? '' : ' aria-current="true"') + '></button>';
                }).join('') + '</div>' : '') +
      '</div>' +
      '<div class="item__body"><h3 class="caps">' + p.nom + '</h3><p>' + p.txt + '</p><div class="item__row">' +
      '<span class="item__price' + (p.prix == null ? ' item__price--tbc' : '') + '">' + prixTxt(p.prix) + '</span>' +
      (p.tailles ? '<select aria-label="Taille ' + p.nom + '">' + p.tailles.map(function (t) { return '<option' + (t === 'M' ? ' selected' : '') + '>' + t + '</option>'; }).join('') + '</select>' : '') +
      '<button type="button" class="btn">Ajouter</button></div></div></article>';
  }).join('');

  // carrousels : défilement natif (doigt, trackpad), flèches et points synchronisés
  [].forEach.call(shop.querySelectorAll('.gal'), function (g) {
    var track = g.querySelector('.gal__track'), dots = [].slice.call(g.querySelectorAll('.gal__dots button'));
    if (!dots.length) return;
    var go = function (i) { track.scrollTo({ left: i * track.clientWidth, behavior: reduce ? 'auto' : 'smooth' }); };
    var cur = function () { return Math.round(track.scrollLeft / track.clientWidth); };
    g.querySelector('.gal__nav--prev').addEventListener('click', function () { go(Math.max(0, cur() - 1)); });
    g.querySelector('.gal__nav--next').addEventListener('click', function () { go(Math.min(dots.length - 1, cur() + 1)); });
    dots.forEach(function (d, i) { d.addEventListener('click', function () { go(i); }); });
    var sync = function () {
      var i = cur();
      dots.forEach(function (d, k) { if (k === i) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current'); });
      g.classList.toggle('is-first', i === 0); g.classList.toggle('is-last', i === dots.length - 1);
    };
    track.addEventListener('scroll', function () { requestAnimationFrame(sync); }, { passive: true });
    sync();
  });

  var totalTxt = function () {
    var known = cart.reduce(function (s, l) { return s + (l.prix == null ? 0 : l.q * l.prix); }, 0);
    var tbc = cart.some(function (l) { return l.prix == null; });
    return 'Total : ' + eur(known) + (tbc ? ' + articles à prix à confirmer' : '');
  };
  var render = function () {
    var n = cart.reduce(function (s, l) { return s + l.q; }, 0);
    fab.hidden = n === 0; fab.querySelector('.cart__count').textContent = n;
    list.innerHTML = cart.map(function (l, i) {
      return '<li><span>' + l.q + ' × ' + l.nom + (l.taille ? ' (' + l.taille + ')' : '') + '</span><span>' + (l.prix == null ? 'à confirmer' : eur(l.q * l.prix)) + ' <button type="button" data-i="' + i + '">Retirer</button></span></li>';
    }).join('') || '<li>Ton panier est vide.</li>';
    total.textContent = totalTxt();
    if (!n) drawer.hidden = true;
  };
  shop.addEventListener('click', function (e) {
    var b = e.target.closest('.item__row .btn'); if (!b) return;
    var el = b.closest('.item'), p = PRODUITS.filter(function (x) { return x.id === el.dataset.id; })[0];
    var sel = el.querySelector('select'), taille = sel ? sel.value : '';
    var line = cart.filter(function (l) { return l.id === p.id && l.taille === taille; })[0];
    if (line) line.q++; else cart.push({ id: p.id, nom: p.nom, prix: p.prix, taille: taille, q: 1 });
    b.textContent = 'Ajouté ✓'; b.classList.add('is-added');
    setTimeout(function () { b.textContent = 'Ajouter'; b.classList.remove('is-added'); }, 1400);
    render();
  });
  list.addEventListener('click', function (e) { var i = e.target.dataset.i; if (i != null) { cart.splice(+i, 1); render(); } });
  fab.addEventListener('click', function () { drawer.hidden = false; drawer.querySelector('.cart__close').focus(); });
  drawer.querySelector('.cart__close').addEventListener('click', function () { drawer.hidden = true; fab.focus(); });
  drawer.addEventListener('click', function (e) { if (e.target === drawer) drawer.hidden = true; });
  addEventListener('keydown', function (e) { if (e.key === 'Escape' && !drawer.hidden) drawer.hidden = true; });

  var mail = function (sujet, lignes) {
    location.href = 'mailto:' + CONTACT + '?subject=' + encodeURIComponent(sujet) + '&body=' + encodeURIComponent(lignes.join('\n'));
  };
  drawer.querySelector('.cart__form').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target;
    mail('Commande goodies Slide Session · ' + f.nom.value, ['Bonjour,', '', 'Je souhaite commander :'].concat(
      cart.map(function (l) { return '- ' + l.q + ' × ' + l.nom + (l.taille ? ' (taille ' + l.taille + ')' : '') + ' : ' + (l.prix == null ? 'prix à confirmer' : eur(l.q * l.prix)); }),
      [totalTxt(), '', 'Nom : ' + f.nom.value, 'E-mail : ' + f.email.value, 'École : ' + f.ecole.value]));
  });

  /* ---------- demande de partenariat ---------- */
  document.querySelector('.pform').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target;
    mail('Demande de partenariat · ' + f.entreprise.value, ['Bonjour,', '', 'Nous souhaitons devenir partenaire de Slide Session.', '',
      'Entreprise : ' + f.entreprise.value, 'Contact : ' + f.nom.value, 'E-mail : ' + f.email.value, 'Téléphone : ' + (f.tel.value || 'non précisé'),
      'Pack envisagé : ' + f.pack.value, '', f.message.value]);
  });

  /* ---------- calcul du don ---------- */
  var din = document.querySelector('.don__calc input'), dout = document.querySelector('.don__out');
  var calc = function () {
    var v = Math.max(0, +din.value || 0);
    dout.innerHTML = 'Coût réel après la réduction de 66 % : <b>' + eur(Math.round(v * .34)) + '</b>.';
  };
  din.addEventListener('input', calc); calc();
  ScrollCraft.mount(document.body);
})();
