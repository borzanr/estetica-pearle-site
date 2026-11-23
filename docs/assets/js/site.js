// Pearle: menu do celular, cabeçalho ao rolar, botão flutuante, contadores, movimento da foto
// do topo e entrada suave das seções. Mesmo pacote do site da Regiane (2026).
// "?semanim" na URL desliga tudo (para capturas de tela).
(function () {
  var root = document.documentElement;
  var semAnim = location.search.indexOf('semanim') !== -1;
  var calm = semAnim || (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  // Menu do celular
  var btn = document.querySelector('.abre-menu');
  var menu = document.getElementById('menu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      var aberto = menu.classList.toggle('aberto');
      btn.setAttribute('aria-expanded', aberto ? 'true' : 'false');
      btn.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
    });
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        menu.classList.remove('aberto');
        btn.setAttribute('aria-expanded', 'false');
        btn.setAttribute('aria-label', 'Abrir menu');
      });
    });
  }

  // Submenu "Tratamentos": abre no clique (celular e teclado); no computador também abre ao passar o mouse.
  document.querySelectorAll('.sub').forEach(function (sub) {
    var b = sub.querySelector('.sub-btn');
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      var aberto = sub.classList.toggle('aberto');
      b.setAttribute('aria-expanded', aberto ? 'true' : 'false');
    });
  });
  document.addEventListener('click', function (e) {
    if (window.innerWidth <= 1000) return;   // no celular o submenu fica dentro do menu aberto
    document.querySelectorAll('.sub.aberto').forEach(function (s) {
      if (!s.contains(e.target)) { s.classList.remove('aberto'); s.querySelector('.sub-btn').setAttribute('aria-expanded', 'false'); }
    });
  });
  var fechaSubs = function (devolveFoco) {
    document.querySelectorAll('.sub.aberto').forEach(function (s) {
      var b = s.querySelector('.sub-btn');
      s.classList.remove('aberto'); b.setAttribute('aria-expanded', 'false');
      if (devolveFoco) b.focus(); else b.blur();
    });
  };
  window.addEventListener('scroll', function () { if (window.innerWidth > 1000) fechaSubs(false); }, { passive: true });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    fechaSubs(true);
    if (menu && menu.classList.contains('aberto')) { menu.classList.remove('aberto'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); }
  });

  // Cabeçalho ganha sombra ao rolar; WhatsApp flutuante aparece depois do topo.
  var onScroll = function () {
    var y = window.scrollY;
    root.classList.toggle('rolou', y > 8);
    root.classList.toggle('mostra-zap', semAnim || y > window.innerHeight * 0.6);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (calm) { root.classList.add('semanim'); return; }

  // Contadores ("22 anos", "5 anos") quando aparecem na tela.
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        co.unobserve(e.target);
        var el = e.target, fim = +el.dataset.count, t0 = null;
        var passo = function (t) {
          if (!t0) t0 = t;
          var p = Math.min((t - t0) / 1400, 1);
          el.textContent = Math.round(fim * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(passo);
        };
        el.textContent = '0';
        requestAnimationFrame(passo);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { co.observe(c); });
  }

  // Foto do topo: movimento leve ao rolar (só em telas largas).
  var heroImg = document.querySelector('.heroi .foto img, .pagina-foto img');
  if (heroImg && window.matchMedia('(min-width: 961px)').matches) {
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = Math.min(window.scrollY, 700);
        heroImg.style.transform = 'translateY(' + (y * 0.06).toFixed(1) + 'px) scale(1.04)';
        ticking = false;
      });
    }, { passive: true });
  }

  // Entrada suave do que está abaixo da dobra. Só esconde depois de confirmar que o navegador
  // desenha quadros (requestAnimationFrame); se não desenhar, tudo fica visível, sem animação.
  if ('IntersectionObserver' in window) requestAnimationFrame(function () {
    var els = document.querySelectorAll('.revela, .cartao, .caminho, .trat, .valor, .passo, .depo, .galeria .foto, .faq details, .duas > *, .sobre .foto, .cabeca, .aviso-parceria');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add('reveal'); io.observe(el); }
    });
    root.classList.add('reveal-ready');
  });
})();
