/* =====================================================
   Community Builders Network - Sierra Leone
   Global JavaScript
   ===================================================== */

(function () {
  'use strict';

  /* ---------- Mobile menu toggle ---------- */
  const toggle  = document.querySelector('.menu-toggle');
  const navList = document.querySelector('.nav-list');

  if (toggle && navList) {
    toggle.addEventListener('click', function () {
      toggle.classList.toggle('is-active');
      navList.classList.toggle('is-open');
      const expanded = toggle.classList.contains('is-active');
      toggle.setAttribute('aria-expanded', expanded);
    });
  }

  /* ---------- Dropdown behaviour (click on mobile, hover on desktop) ---------- */
  const dropdownItems = document.querySelectorAll('.nav-list > li.has-mega > a');

  dropdownItems.forEach(function (link) {
    link.addEventListener('click', function (e) {
      // On mobile widths, hijack the click to expand the mega menu
      if (window.innerWidth <= 860) {
        e.preventDefault();
        const parent = link.parentElement;

        // Close siblings
        parent.parentElement.querySelectorAll('li.has-mega').forEach(function (li) {
          if (li !== parent) li.classList.remove('is-open');
        });
        parent.classList.toggle('is-open');
      }
    });
  });

  /* ---------- Close mobile menu when clicking a real link ---------- */
  document.querySelectorAll('.nav-list a').forEach(function (a) {
    if (a.classList.contains('has-mega')) return;
    a.addEventListener('click', function () {
      if (window.innerWidth <= 860 && !a.parentElement.classList.contains('has-mega')) {
        if (toggle) toggle.classList.remove('is-active');
        if (navList) navList.classList.remove('is-open');
      }
    });
  });

  /* ---------- Reset mobile state on resize ---------- */
  let resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      if (window.innerWidth > 860) {
        if (toggle)  toggle.classList.remove('is-active');
        if (navList) navList.classList.remove('is-open');
        document.querySelectorAll('.nav-list > li.is-open').forEach(function (li) {
          li.classList.remove('is-open');
        });
      }
    }, 150);
  });

  /* ---------- Simple search stub ---------- */
  const searchBtn = document.querySelector('.util-search');
  if (searchBtn) {
    searchBtn.addEventListener('click', function () {
      const q = prompt('Search Community Builders Network:');
      if (q && q.trim()) {
        alert('Search results for "' + q.trim() + '" would appear here.');
      }
    });
  }

  /* ---------- Animated impact counters ---------- */
  const counters = document.querySelectorAll('.impact-num[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const runCounter = function (el) {
      const target   = parseInt(el.dataset.count, 10);
      const suffix   = el.dataset.suffix || '';
      const duration = 1600;
      const start    = performance.now();

      const step = function (now) {
        const p = Math.min((now - start) / duration, 1);
        // ease-out cubic
        const val = Math.floor(target * (1 - Math.pow(1 - p, 3)));
        el.textContent = val.toLocaleString() + suffix;
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = target.toLocaleString() + suffix;
      };
      requestAnimationFrame(step);
    };

    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          runCounter(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    counters.forEach(function (c) { io.observe(c); });
  }

  /* ---------- Fade-in on scroll (progressive enhancement) ---------- */
  const revealables = document.querySelectorAll('.project-card, .value-card, .team-card, .mv-card, .tl-item');
  if (revealables.length && 'IntersectionObserver' in window) {
    revealables.forEach(function (el) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(18px)';
      el.style.transition = 'opacity .55s ease, transform .55s ease';
    });
    const io2 = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'none';
          io2.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealables.forEach(function (el) { io2.observe(el); });
  }

  /* ---------- Set current year in footer ---------- */
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- Category filter tabs (Projects + Blog pages) ---------- */
  document.querySelectorAll('.filter-tabs').forEach(function (tabBar) {
    const buttons = tabBar.querySelectorAll('button[data-filter]');
    // Grid to filter = the next sibling with a data-category child, else search common IDs
    let grid = tabBar.nextElementSibling;
    while (grid && !grid.querySelector('[data-category]')) {
      grid = grid.nextElementSibling;
    }
    if (!grid) return;

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        buttons.forEach(function (b) { b.classList.remove('is-active'); });
        btn.classList.add('is-active');

        const filter = btn.dataset.filter;
        const cards  = grid.querySelectorAll('[data-category]');

        cards.forEach(function (card) {
          const cats = (card.dataset.category || '').split(/\s+/);
          if (filter === 'all' || cats.indexOf(filter) !== -1) {
            card.classList.remove('is-hidden');
          } else {
            card.classList.add('is-hidden');
          }
        });
      });
    });
  });

  /* ---------- Backend form submissions (POST to /api/*) ---------- */

  // Generic helper: POST JSON, show success/error inside .form-msg element
  async function submitForm(form, endpoint, msgEl, extraFields) {
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    // Serialise the form into a plain object
    const payload = {};
    const fd = new FormData(form);
    fd.forEach(function (v, k) { payload[k] = typeof v === 'string' ? v.trim() : v; });
    if (extraFields) Object.assign(payload, extraFields);

    const btn = form.querySelector('button[type="submit"]');
    const originalLabel = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      });
      const data = await res.json().catch(function () { return { ok: false, error: 'Bad response' }; });

      if (msgEl) {
        msgEl.classList.remove('error');
        msgEl.style.background = '';
        msgEl.style.color = '';
        msgEl.style.borderLeftColor = '';
        if (data.ok) {
          msgEl.textContent = '✓ ' + (data.message || 'Thank you!');
          msgEl.classList.add('show');
          form.reset();
        } else {
          msgEl.textContent = '✗ ' + (data.error || 'Something went wrong. Please try again.');
          msgEl.classList.add('show');
          msgEl.style.background = '#fee2e2';
          msgEl.style.color = '#991b1b';
          msgEl.style.borderLeftColor = '#dc2626';
        }
        msgEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        alert(data.ok ? (data.message || 'Thank you!') : (data.error || 'Error'));
        if (data.ok) form.reset();
      }
    } catch (err) {
      if (msgEl) {
        msgEl.textContent = '✗ Network error. Please check your connection and try again.';
        msgEl.classList.add('show');
        msgEl.style.background = '#fee2e2';
        msgEl.style.color = '#991b1b';
        msgEl.style.borderLeftColor = '#dc2626';
      } else {
        alert('Network error. Please try again.');
      }
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = originalLabel; }
    }
  }

  // Volunteer form (get-involved.html)
  const volForm = document.getElementById('volunteerForm');
  if (volForm) {
    volForm.addEventListener('submit', function (e) {
      e.preventDefault();
      submitForm(volForm, '/api/volunteer', document.getElementById('formMsg'));
    });
  }

  // Contact form (contact.html)
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      submitForm(contactForm, '/api/contact', document.getElementById('contactMsg'));
    });
  }

  // Newsletter form (news.html)
  const newsForm = document.getElementById('newsletterForm');
  if (newsForm) {
    newsForm.addEventListener('submit', function (e) {
      e.preventDefault();
      // The newsletter form's email field is unnamed — grab the first input
      const emailInput = newsForm.querySelector('input[type="email"]');
      submitForm(newsForm, '/api/newsletter',
        document.getElementById('newsMsg'),
        { email: emailInput ? emailInput.value.trim() : '' });
    });
  }

  /* ---------- Projects page: animate progress bars on scroll ---------- */
  const progressBars = document.querySelectorAll('.progress > span');
  if (progressBars.length && 'IntersectionObserver' in window) {
    // Store target and reset to 0 so it can animate in
    progressBars.forEach(function (bar) {
      bar.dataset.target = bar.style.width || '0%';
      bar.style.width = '0%';
    });
    const pio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const bar = entry.target;
          // slight delay for nicer effect
          setTimeout(function () {
            bar.style.width = bar.dataset.target;
          }, 120);
          pio.unobserve(bar);
        }
      });
    }, { threshold: 0.4 });
    progressBars.forEach(function (bar) { pio.observe(bar); });
  }

})();
