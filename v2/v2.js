/* Slide Session v2 : rotation 3D des skis au scroll, teaser qui s'ouvre, palmarès en onglets.
   Le menu, la neige, la boutique et les formulaires viennent de ../site.js. */
(function () {
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var clamp01 = function (x) { return x < 0 ? 0 : x > 1 ? 1 : x; };

  /* ---------- héros : 40 images Blender, transparentes, pilotées par le scroll ---------- */
  var hero = document.querySelector('.x-hero'), stage = hero.querySelector('.x-hero__stage'),
      cv = hero.querySelector('.x-skis'), ctx = cv.getContext('2d'), N = 40, frames = [], ready = 0, drawn = -1;
  // les 40 images arrivent après l'affichage de l'affiche, pour ne pas ralentir le premier écran
  var loadFrames = function () {
    for (var i = 0; i < N; i++) {
      var im = new Image();
      im.decoding = 'async';
      im.onload = function () { if (++ready === N) { hero.classList.add('is-live'); drawn = -1; tick(); } };
      im.src = 'v2/img/skis/skis-' + String(i).padStart(3, '0') + '.webp';
      frames.push(im);
    }
  };
  if (!reduce) {
    if (document.readyState === 'complete') setTimeout(loadFrames, 200);
    else addEventListener('load', function () { setTimeout(loadFrames, 200); });
  }
  var heroP = function () {
    var r = hero.getBoundingClientRect(), span = r.height - innerHeight;
    return span > 0 ? clamp01(-r.top / span) : 0;
  };
  var draw = function (p) {
    if (ready < N) return;
    var idx = Math.min(N - 1, Math.round(p * (N - 1) * 1.0));
    if (idx === drawn) return;
    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.drawImage(frames[idx], 0, 0, cv.width, cv.height);
    drawn = idx;
  };

  /* ---------- teaser : la fenêtre grandit, la vidéo ne se charge qu'à l'approche ---------- */
  var tz = document.querySelector('.x-teaser'), vid = tz.querySelector('video'), btn = tz.querySelector('.x-play'), userPaused = false;
  var setPlaying = function (on) {
    btn.setAttribute('aria-pressed', on);
    btn.querySelector('span').textContent = on ? 'Pause' : 'Lecture';
  };
  var load = function () {
    if (vid.src) return;
    vid.src = matchMedia('(max-width: 860px)').matches ? vid.dataset.srcMobile : vid.dataset.src;
  };
  new IntersectionObserver(function (e) {
    if (e[0].isIntersecting) {
      load();
      if (!reduce && !userPaused) vid.play().then(function () { setPlaying(true); }).catch(function () {});
    } else if (!vid.paused) { vid.pause(); }
  }, { rootMargin: '200px 0px' }).observe(tz);
  btn.addEventListener('click', function () {
    load();
    userPaused = !vid.paused;
    if (vid.paused) { vid.play().then(function () { setPlaying(true); }).catch(function () {}); }
    else { vid.pause(); setPlaying(false); }
  });
  setPlaying(false);

  /* ---------- une seule boucle de scroll pour les deux effets ---------- */
  var queued = false;
  var tick = function () {
    queued = false;
    var p = heroP();
    stage.style.setProperty('--p', reduce ? 0 : p.toFixed(4));
    draw(p);
    var r = tz.getBoundingClientRect();
    tz.style.setProperty('--g', reduce ? 1 : clamp01((innerHeight - r.top) / (innerHeight * 0.9)).toFixed(4));
  };
  addEventListener('scroll', function () { if (!queued) { queued = true; requestAnimationFrame(tick); } }, { passive: true });
  addEventListener('resize', tick);
  tick();

  /* ---------- palmarès : onglets par année (flèches du clavier comprises) ---------- */
  var DATA = {
    2023: { ski: '11<small>e/33</small>', mont: '7<small>e/16</small>', vil: '3<small>e/13</small>', best: 'vil', note: '30 riders au départ.' },
    2024: { ski: '19<small>e/38</small>', mont: '6<small>e/16</small>', vil: '5<small>e/30</small>', best: 'mont', note: '30 riders, et un village qui passe à 30 équipes.' },
    2025: { ski: '13<small>e/40</small>', mont: '4<small>e/18</small>', vil: '4<small>e/30</small>', best: 'mont', note: '30 riders, deux tops 5.' },
    2026: { ski: '16<small>e/45</small>', mont: '3<small>e/24</small>', vil: '2<small>e/30</small>', best: 'vil', note: 'Podium au village et en montagne : notre meilleure édition.' },
    2027: { ski: 'Top 10', mont: 'Top 3', vil: '1<small>re</small>', best: 'vil', note: 'Les objectifs : 2 équipes de 10 en ski, 2 en montagne, 1 au village.' }
  };
  var tabs = [].slice.call(document.querySelectorAll('.x-tabs button')), ranks = document.querySelector('.x-ranks'), note = document.querySelector('.x-palm__note');
  var show = function (year) {
    var d = DATA[year];
    tabs.forEach(function (t) { var on = t.dataset.y === year; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; });
    ranks.classList.add('is-swapping');
    setTimeout(function () {
      ranks.innerHTML = [['ski', 'Challenge Ski'], ['mont', 'Challenge Montagne'], ['vil', 'Challenge Village']].map(function (c) {
        return '<li class="' + (d.best === c[0] ? 'is-best' : '') + '"><span>' + c[1] + '</span><b>' + d[c[0]] + '</b></li>';
      }).join('');
      note.textContent = d.note;
      ranks.classList.remove('is-swapping');
    }, reduce ? 0 : 160);
  };
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { show(t.dataset.y); });
    t.addEventListener('keydown', function (e) {
      var k = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!k) return;
      var n = tabs[(i + k + tabs.length) % tabs.length];
      n.focus(); show(n.dataset.y);
    });
  });
  show('2026');
})();
