/* ═══════════════════════════════════════════════
   TOMATO LOVE MARKET — script.js
   Handles: AOS init, stamp spin click, cursor dot
═══════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── AOS init ──────────────────────────────────
  AOS.init({
    once: true,
    easing: 'ease-out-quart',
    offset: 60,
  });

  // ── Stamp click burst ─────────────────────────
  const stamp = document.getElementById('stamp');
  if (stamp) {
    stamp.addEventListener('click', () => {
      burst(stamp);
    });
  }

  // ── Burst helper ──────────────────────────────
  function burst(origin) {
    const emojis = ['🍅', '✨', '🌿', '❤️', '🌱', '⭐'];
    const rect = origin.getBoundingClientRect();
    const cx = rect.left + rect.width / 2 + window.scrollX;
    const cy = rect.top  + rect.height / 2 + window.scrollY;
    const count = 14;

    for (let i = 0; i < count; i++) {
      const el = document.createElement('span');
      el.textContent = emojis[Math.floor(Math.random() * emojis.length)];
      Object.assign(el.style, {
        position:  'absolute',
        left:      cx + 'px',
        top:       cy + 'px',
        fontSize:  (1 + Math.random() * .8) + 'rem',
        pointerEvents: 'none',
        zIndex:    '9999',
        userSelect: 'none',
        transition: 'none',
      });
      document.body.appendChild(el);

      const angle = (Math.PI * 2 / count) * i + (Math.random() - .5) * .4;
      const dist  = 70 + Math.random() * 90;
      const tx = Math.cos(angle) * dist;
      const ty = Math.sin(angle) * dist;

      // Animate via requestAnimationFrame
      let start = null;
      const dur = 650 + Math.random() * 200;
      function step(ts) {
        if (!start) start = ts;
        const p = Math.min((ts - start) / dur, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        el.style.transform = `translate(${tx * ease}px, ${ty * ease}px) scale(${1 - p * .4})`;
        el.style.opacity   = 1 - p;
        if (p < 1) requestAnimationFrame(step);
        else el.remove();
      }
      requestAnimationFrame(step);
    }
  }

  // ── Subtle cursor tomato dot ──────────────────
  const dot = document.createElement('div');
  Object.assign(dot.style, {
    position:     'fixed',
    width:        '10px',
    height:       '10px',
    borderRadius: '50%',
    background:   '#c0392b',
    opacity:      '.35',
    pointerEvents:'none',
    zIndex:       '9999',
    transition:   'transform .12s ease, opacity .2s',
    transform:    'translate(-50%, -50%)',
    mixBlendMode: 'multiply',
  });
  document.body.appendChild(dot);

  document.addEventListener('mousemove', (e) => {
    dot.style.left = e.clientX + 'px';
    dot.style.top  = e.clientY + 'px';
  });

  document.addEventListener('mousedown', () => {
    dot.style.transform = 'translate(-50%, -50%) scale(2)';
    dot.style.opacity   = '.5';
  });
  document.addEventListener('mouseup', () => {
    dot.style.transform = 'translate(-50%, -50%) scale(1)';
    dot.style.opacity   = '.35';
  });

});
