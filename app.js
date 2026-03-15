(function () {
  const whatsappNumber = '919335874326';
  const state = { projects: [], social: [], packages: [], locations: [], map: null, markers: [], activeLocation: null };

  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const escapeHtml = (str) => String(str || '').replace(/[&<>"']/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

  function bindNav() {
    const navToggle = $('#navToggle');
    const navLinks = $('#navLinks');
    navToggle?.addEventListener('click', () => navLinks.classList.toggle('open'));
    $$('.nav-links a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));
  }

  function bindWhatsApp() {
    const panel = $('#waPanel');
    $('#waToggleBtn')?.addEventListener('click', () => panel.classList.toggle('open'));
    $('#scrollTopBtn')?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    $$('.wa-quick').forEach(btn => btn.addEventListener('click', () => openWa(btn.dataset.waText || 'Hello, I want to discuss a video shoot in Varanasi.')));
    $('#quickWaBtn')?.addEventListener('click', () => openWa('Hello, I want to discuss a video shoot in Varanasi.'));
    $('#waFormBtn')?.addEventListener('click', () => {
      const msg = [
        'Video Project Enquiry',
        'Name: ' + ($('#clientName')?.value || ''),
        'Phone: ' + ($('#clientPhone')?.value || ''),
        'Project Type: ' + ($('#projectType')?.value || ''),
        'Shoot Date: ' + ($('#projectDate')?.value || ''),
        'Brief: ' + ($('#projectMessage')?.value || '')
      ].join('\n');
      openWa(msg);
    });
  }

  function openWa(text) {
    window.open('https://wa.me/' + whatsappNumber + '?text=' + encodeURIComponent(text), '_blank');
  }

  function bindForm() {
    const form = $('#bookingForm');
    const success = $('#formSuccess');
    form?.addEventListener('submit', (e) => {
      e.preventDefault();
      const payload = {
        name: $('#clientName').value.trim(),
        phone: $('#clientPhone').value.trim(),
        projectType: $('#projectType').value,
        projectDate: $('#projectDate').value,
        brief: $('#projectMessage').value.trim(),
        submittedAt: new Date().toISOString()
      };
      const old = JSON.parse(localStorage.getItem('kashiFramesEnquiries') || '[]');
      old.push(payload);
      localStorage.setItem('kashiFramesEnquiries', JSON.stringify(old));
      success.style.display = 'block';
      form.reset();
      setTimeout(() => { success.style.display = 'none'; }, 3500);
    });
  }

  function bindVideoModal() {
    const modal = $('#videoModal');
    const frame = $('#videoFrame');
    const closeBtn = $('#videoClose');
    const backdrop = $('#videoBackdrop');

    function openVideo(url) {
      if (!url) return;
      if (url.endsWith('.mp4') || url.includes('/assets/videos/')) {
        frame.outerHTML = '<video id="videoFrame" controls autoplay playsinline style="position:absolute;inset:0;width:100%;height:100%;background:#000"><source src="' + url + '" type="video/mp4"></video>';
      } else {
        const oldFrame = $('#videoFrame');
        if (oldFrame.tagName.toLowerCase() !== 'iframe') {
          oldFrame.outerHTML = '<iframe id="videoFrame" src="" title="Project video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
        }
        $('#videoFrame').src = url + (url.includes('?') ? '&' : '?') + 'autoplay=1';
      }
      modal.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }

    function closeVideo() {
      const current = $('#videoFrame');
      if (!current) return;
      if (current.tagName.toLowerCase() === 'iframe') current.src = '';
      else current.pause?.();
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }

    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.open-video-btn');
      if (btn) openVideo(btn.dataset.videoUrl);
    });
    closeBtn?.addEventListener('click', closeVideo);
    backdrop?.addEventListener('click', closeVideo);
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeVideo(); });
  }

  async function loadData() {
    const res = await fetch('data.json');
    const data = await res.json();
    state.projects = data.portfolio || [];
    state.social = data.social || [];
    state.packages = data.packages || [];
    state.locations = data.locations || [];
    renderProjectFilters();
    renderPortfolio('all');
    renderSocial();
    renderPackages();
    initMap();
  }

  function projectGradient(type) {
    const map = {
      wedding: 'linear-gradient(135deg,#7c2d12,#c2410c 45%,#fb923c)',
      reel: 'linear-gradient(135deg,#4c1d95,#7c3aed 45%,#a78bfa)',
      event: 'linear-gradient(135deg,#065f46,#059669 45%,#34d399)',
      commercial: 'linear-gradient(135deg,#1e3a8a,#2563eb 45%,#60a5fa)',
      documentary: 'linear-gradient(135deg,#92400e,#d97706 45%,#fbbf24)'
    };
    return map[type] || map.reel;
  }

  function renderProjectFilters() {
    const box = $('#projectFilters');
    const filters = ['all', 'wedding', 'reel', 'event', 'commercial', 'documentary'];
    box.innerHTML = filters.map((f, i) => '<button class="filter-btn ' + (i === 0 ? 'active' : '') + '" data-filter="' + f + '">' + (f === 'all' ? 'All' : f[0].toUpperCase() + f.slice(1)) + '</button>').join('');
    box.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-filter]');
      if (!btn) return;
      $$('.filter-btn', box).forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderPortfolio(btn.dataset.filter);
    });
  }

  function renderPortfolio(filter) {
    const grid = $('#portfolioGrid');
    const projects = state.projects.filter(p => p.visible !== false).filter(p => filter === 'all' || p.type === filter);
    grid.innerHTML = projects.map((project) => {
      const thumbStyle = project.thumbnail ? `background-image:linear-gradient(180deg,rgba(15,23,42,.12),rgba(15,23,42,.72)),url('${project.thumbnail}')` : `background-image:${projectGradient(project.type)}`;
      const cardSize = project.cardSize === 'tall' ? 'tall' : (project.cardSize === 'medium' ? 'medium' : '');
      return `
        <article class="masonry-item card project-card">
          <div class="project-thumb ${cardSize}" style="${thumbStyle}">
            <button class="project-play open-video-btn" data-video-url="${escapeHtml(project.videoUrl)}">▶</button>
            <div class="project-overlay">
              <div class="tag-row">${(project.tags || []).map(t => `<span>${escapeHtml(t)}</span>`).join('')}</div>
              <h3>${escapeHtml(project.title)}</h3>
            </div>
          </div>
          <div class="project-body">
            <p>${escapeHtml(project.description)}</p>
            <div class="project-meta"><span>${escapeHtml(project.location)}</span><span>${escapeHtml(project.deliverable)}</span></div>
          </div>
        </article>`;
    }).join('') || '<article class="card muted-card">No projects in this category.</article>';
  }

  function renderSocial() {
    const grid = $('#socialGrid');
    grid.innerHTML = state.social.map((item, idx) => {
      const bg = item.thumbnail ? `background-image:linear-gradient(180deg,rgba(15,23,42,.08),rgba(15,23,42,.52)),url('${item.thumbnail}')` : `background:${projectGradient(item.type)}`;
      return `<article class="card social-card"><div class="social-thumb" style="${bg}"></div><div class="social-content"><div class="eyebrow">${escapeHtml(item.platform)}</div><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.caption)}</p></div></article>`;
    }).join('');
  }

  function renderPackages() {
    const grid = $('#packagesGrid');
    grid.innerHTML = state.packages.map((pkg) => `
      <article class="card">
        <div class="eyebrow">Package</div>
        <h3>${escapeHtml(pkg.name)}</h3>
        <div class="map-mini-list">
          <div class="location-chip"><strong>Hours:</strong> ${escapeHtml(pkg.hours)}</div>
          <div class="location-chip"><strong>Cameras:</strong> ${escapeHtml(pkg.cameras)}</div>
          <div class="location-chip"><strong>Edit:</strong> ${escapeHtml(pkg.edit)}</div>
          <div class="location-chip"><strong>Delivery:</strong> ${escapeHtml(pkg.delivery)}</div>
          <div class="location-chip"><strong>Price:</strong> ${escapeHtml(pkg.price)}</div>
        </div>
      </article>`).join('');
  }

  function initMap() {
    const select = $('#locationSelect');
    const chips = $('#locationChips');
    if (!select || !window.L) return;
    select.innerHTML = state.locations.map((loc, i) => `<option value="${i}">${escapeHtml(loc.name)}</option>`).join('');
    chips.innerHTML = state.locations.map((loc, i) => `<button class="location-chip ${i===0?'active':''}" data-index="${i}">${escapeHtml(loc.name)}</button>`).join('');

    const first = state.locations[0];
    state.map = L.map('shootMap').setView([first.lat, first.lng], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(state.map);

    state.markers = state.locations.map((loc, i) => {
      const marker = L.marker([loc.lat, loc.lng]).addTo(state.map).bindPopup(`<strong>${escapeHtml(loc.name)}</strong><br>${escapeHtml(loc.bestFor)}`);
      marker.on('click', () => setActiveLocation(i));
      return marker;
    });

    select.addEventListener('change', () => setActiveLocation(Number(select.value)));
    chips.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-index]');
      if (!btn) return;
      setActiveLocation(Number(btn.dataset.index));
    });
    setActiveLocation(0);
  }

  function setActiveLocation(index) {
    const loc = state.locations[index];
    if (!loc || !state.map) return;
    state.activeLocation = index;
    $('#locationSelect').value = String(index);
    $$('#locationChips .location-chip').forEach((b, i) => b.classList.toggle('active', i === index));
    $('#locationInfo').innerHTML = `<strong>${escapeHtml(loc.name)}</strong>Mood: <b>${escapeHtml(loc.mood)}</b><br>Best for: <b>${escapeHtml(loc.bestFor)}</b><br>${escapeHtml(loc.description)}`;
    state.map.setView([loc.lat, loc.lng], 13, { animate: true });
    state.markers[index].openPopup();
  }

  function pulseRise(target) {
    if (!target) return;
    target.classList.remove('is-risen');
    void target.offsetWidth;
    target.classList.add('is-risen');
  }

  function clearRise(target) {
    if (!target) return;
    target.classList.remove('is-risen');
  }

  function initIntersectionVideos() {
    const localVideos = $$('.auto-play-video');
    const localObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const video = entry.target;
        const card = video.closest('.video-showcase-card') || video;
        if (entry.isIntersecting && entry.intersectionRatio >= 0.25) {
          pulseRise(card);
          const playNow = () => video.play().catch(() => {});
          if (video.readyState >= 2) playNow();
          else video.addEventListener('loadeddata', playNow, { once: true });
        } else {
          video.pause();
          clearRise(card);
        }
      });
    }, { threshold: [0, 0.25, 0.6] });
    localVideos.forEach((video) => localObserver.observe(video));

    const ytBlocks = $$('.youtube-observer-video');
    const ytObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const box = entry.target;
        const card = box.closest('.video-showcase-card') || box;
        const ytId = box.dataset.youtubeId;
        if (!ytId) return;
        if (entry.isIntersecting && entry.intersectionRatio >= 0.35) {
          pulseRise(card);
          pulseRise(box);
          if (!box.dataset.loaded) {
            const iframe = document.createElement('iframe');
            iframe.src = `https://www.youtube.com/embed/${ytId}?autoplay=1&mute=1&playsinline=1&rel=0&modestbranding=1&enablejsapi=1`;
            iframe.title = 'YouTube video';
            iframe.allow = 'autoplay; encrypted-media; picture-in-picture';
            iframe.allowFullscreen = true;
            box.appendChild(iframe);
            box.dataset.loaded = 'true';
            box.classList.add('is-loaded');
          }
        } else if (box.dataset.loaded) {
          const iframe = $('iframe', box);
          if (iframe) iframe.remove();
          box.dataset.loaded = '';
          box.classList.remove('is-loaded');
          clearRise(card);
          clearRise(box);
        } else {
          clearRise(card);
          clearRise(box);
        }
      });
    }, { threshold: [0, 0.35, 0.7] });

    ytBlocks.forEach((box) => {
      const poster = box.dataset.poster;
      if (poster) box.style.backgroundImage = `linear-gradient(180deg, rgba(15,23,42,.18), rgba(15,23,42,.62)), url('${poster}')`;
      ytObserver.observe(box);
    });
  }

  function initCarousels() {
    $$('[data-carousel]').forEach((carousel) => {
      const slides = $$('.carousel-image', carousel);
      const dotsBox = $('.carousel-dots', carousel);
      let index = 0;
      let interval = null;
      let audio = null;
      const audioSrc = carousel.dataset.audio;
      if (audioSrc) {
        audio = new Audio(audioSrc);
        audio.loop = true;
        audio.volume = 0.35;
      }

      function render() {
        slides.forEach((img, i) => img.classList.toggle('active', i === index));
        $$('.carousel-dot', carousel).forEach((dot, i) => dot.classList.toggle('active', i === index));
      }
      function next() { index = (index + 1) % slides.length; render(); }
      function prev() { index = (index - 1 + slides.length) % slides.length; render(); }
      function start() {
        clearInterval(interval);
        interval = setInterval(next, 3500);
      }
      function stop() { clearInterval(interval); }

      dotsBox.innerHTML = slides.map((_, i) => `<button class="carousel-dot ${i===0?'active':''}" data-dot="${i}"></button>`).join('');
      $('.next', carousel)?.addEventListener('click', () => { stop(); prev(); next(); start(); pulseRise(carousel); });
      $('.prev', carousel)?.addEventListener('click', () => { stop(); prev(); start(); pulseRise(carousel); });
      dotsBox.addEventListener('click', (e) => {
        const dot = e.target.closest('[data-dot]');
        if (!dot) return;
        stop(); index = Number(dot.dataset.dot); render(); start(); pulseRise(carousel);
      });

      const soundBtn = $('.sound-toggle', carousel);
      soundBtn?.addEventListener('click', async () => {
        if (!audio) return;
        if (audio.paused) {
          try { await audio.play(); soundBtn.textContent = 'Mute sound'; pulseRise(carousel); } catch (e) {}
        } else { audio.pause(); soundBtn.textContent = 'Play sound'; }
      });

      carousel.addEventListener('mouseenter', stop);
      carousel.addEventListener('mouseleave', () => { if (carousel.classList.contains('is-risen')) start(); });

      const carouselObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.3) {
            pulseRise(carousel);
            start();
          } else {
            stop();
            clearRise(carousel);
            if (audio) {
              audio.pause();
              if (soundBtn) soundBtn.textContent = 'Play sound';
            }
          }
        });
      }, { threshold: [0, 0.3, 0.65] });

      carouselObserver.observe(carousel);
      render();
    });
  }


  function initParallaxTilt() {
    const targets = $$('.video-showcase-card, .carousel-card, .hero-feature-panel, .project-card, .social-card, .youtube-observer-video');
    targets.forEach((el) => {
      el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const px = (e.clientX - rect.left) / rect.width;
        const py = (e.clientY - rect.top) / rect.height;
        const rotateY = (px - 0.5) * 10;
        const rotateX = (0.5 - py) * 10;
        const lift = el.classList.contains('is-risen') ? 16 : 8;
        el.style.transform = `perspective(1200px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-${lift}px) scale3d(1.01,1.01,1.01)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = '';
      });
    });
  }

  bindNav();
  bindWhatsApp();
  bindForm();
  bindVideoModal();
  initIntersectionVideos();
  initCarousels();
  initParallaxTilt();
  loadData();
})();
