/* DesigXner — Theme toggle + announcement bar
   Included before </body> on every page (DOM is ready when this runs) */
(function () {
  var DURATION = 560;
  var MOON = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  var SUN  = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';
  var BG   = { dark: '#05050F', light: '#F5F7FF' };

  var html    = document.documentElement;
  var curtain = document.getElementById('theme-curtain');
  var btn     = document.getElementById('theme-tog');
  var theme   = html.getAttribute('data-theme') || 'dark';
  var busy    = false;

  /* Fix ann-cta href based on page depth (works for any nesting level) */
  var parts  = window.location.pathname.split('/').filter(Boolean);
  var prefix = parts.length > 1 ? '../' : '';
  document.querySelectorAll('.ann-cta').forEach(function (el) {
    if (el.getAttribute('href') === '#') el.href = prefix + 'contact.html';
  });

  /* Theme toggle */
  function setIcon() {
    if (!btn) return;
    btn.innerHTML = theme === 'dark' ? SUN : MOON;
    btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  function applyTheme(t) {
    html.setAttribute('data-theme', t);
    theme = t;
    setIcon();
    localStorage.setItem('dx-theme', t);
  }

  function toggle() {
    if (busy) return;
    busy = true;
    var next = theme === 'dark' ? 'light' : 'dark';

    if (curtain) {
      curtain.classList.remove('tc-anim');
      curtain.style.transform  = 'scaleY(0)';
      curtain.style.background = BG[next];
      curtain.getBoundingClientRect(); /* force reflow */
      curtain.classList.add('tc-anim');
      curtain.style.transform = 'scaleY(1)';

      setTimeout(function () {
        applyTheme(next);
        curtain.style.transform = 'scaleY(0)';
        setTimeout(function () {
          curtain.classList.remove('tc-anim');
          busy = false;
        }, DURATION + 60);
      }, DURATION);
    } else {
      applyTheme(next);
      busy = false;
    }
  }

  setIcon();
  if (btn) btn.addEventListener('click', toggle);

  /* Navbar scroll effect (shared with all pages) */
  var navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', function () {
      navbar.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });
  }
}());
