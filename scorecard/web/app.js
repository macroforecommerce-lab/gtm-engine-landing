/* Scorecard page behaviour. Everything the server or a scanned site can influence
   is inserted with textContent, never as HTML: evidence strings quote the visitor's
   own site, so treating them as markup would let a hostile page inject script. */
(() => {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const PRIORITY = ['Conversion path', 'Proof for outbound', 'Positioning', 'ICP clarity', 'Founder signal'];
  const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid'];
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const state = { url: '', email: '', result: null, config: { pixelId: '', bookingUrl: '', contactEmail: 'info@scalient-ai.com' } };

  // --- helpers --------------------------------------------------------------
  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  };
  const show = (id, on = true) => { $(id).hidden = !on; };
  const store = {
    get(k) { try { return window.sessionStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { window.sessionStorage.setItem(k, v); } catch (e) { /* storage can be blocked */ } },
  };

  // --- ad attribution -------------------------------------------------------
  (function captureUtm() {
    const found = {};
    const q = new URLSearchParams(window.location.search);
    UTM_KEYS.forEach((k) => { if (q.get(k)) found[k] = q.get(k).slice(0, 200); });
    if (Object.keys(found).length) store.set('sc_utm', JSON.stringify(found));
  })();
  const getUtm = () => { try { return JSON.parse(store.get('sc_utm') || '{}'); } catch (e) { return {}; } };

  // --- Meta Pixel: loaded only when a valid id is configured -----------------
  function loadPixel(id) {
    if (!id || window.fbq) return;
    const n = (window.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); });
    if (!window._fbq) window._fbq = n;
    n.push = n; n.loaded = true; n.version = '2.0'; n.queue = [];
    const s = document.createElement('script');
    s.async = true; s.src = 'https://connect.facebook.net/en_US/fbevents.js';
    document.head.appendChild(s);
    window.fbq('init', id);
    window.fbq('track', 'PageView');
  }
  function track(name, params, custom) {
    if (!window.fbq) return;
    window.fbq(custom ? 'trackCustom' : 'track', name, params || {});
  }

  (function loadConfig() {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 3000);
    fetch('/api/config', { signal: ctrl.signal })
      .then((r) => (r.ok ? r.json() : null))
      .then((c) => { if (c) { state.config = Object.assign(state.config, c); loadPixel(c.pixelId); } })
      .catch(() => { /* the page works without config */ })
      .finally(() => clearTimeout(t));
  })();

  function bookHref() {
    if (state.config.bookingUrl) return state.config.bookingUrl;
    const subject = encodeURIComponent('Scorecard call');
    const body = encodeURIComponent('Hi, I ran the GTM scorecard for ' + (state.url || 'my website') + ' and would like to talk it through.');
    return 'mailto:' + state.config.contactEmail + '?subject=' + subject + '&body=' + body;
  }
  const bookLabel = () => (state.config.bookingUrl ? 'Book a 20-minute call' : 'Email us to book a call');

  // --- states ---------------------------------------------------------------
  const PANELS = ['result-loading', 'result-error', 'result-unscored', 'result-ok'];
  function showPanel(id) {
    show('result', true);
    PANELS.forEach((p) => show(p, p === id));
  }
  function reveal(focusId) {
    $('result').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    const f = $(focusId);
    if (f) f.focus({ preventScroll: true });
  }
  function focusUrl() {
    window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    const u = $('url'); u.focus({ preventScroll: true }); u.select();
  }

  let cycle = null;
  const MESSAGES = ['Reading your homepage…', 'Checking your headline and opening…', 'Looking for proof and calls to action…', 'Scoring…'];
  function startCycle() {
    let i = 0; $('loading-text').textContent = MESSAGES[0];
    cycle = setInterval(() => { i = Math.min(i + 1, MESSAGES.length - 1); $('loading-text').textContent = MESSAGES[i]; }, 2200);
  }
  const stopCycle = () => { if (cycle) { clearInterval(cycle); cycle = null; } };

  // --- audit ----------------------------------------------------------------
  function urlError(msg) {
    const e = $('url-error');
    e.textContent = msg || ''; e.hidden = !msg;
    $('url').setAttribute('aria-invalid', msg ? 'true' : 'false');
  }

  async function runAudit(raw) {
    urlError('');
    const url = raw.trim();
    if (!url || /\s/.test(url) || !url.includes('.')) {
      urlError('Enter your website address, like yourcompany.com.');
      $('url').focus();
      return;
    }
    state.url = url;
    $('audit-btn').disabled = true;
    showPanel('result-loading'); startCycle(); reveal('result-loading');

    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 25000);
    try {
      const res = await fetch('/api/audit', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }), signal: ctrl.signal,
      });
      const data = await res.json().catch(() => null);
      if (!res.ok || !data || !data.ok) throw new Error((data && data.error) || 'Something went wrong. Please try again.');
      state.result = data;
      track('ScorecardRun', { scored: !!data.scorable }, true);
      data.scorable ? renderResult(data) : renderUnscored(data);
    } catch (err) {
      renderError(err.name === 'AbortError' ? 'That took too long. The site may be slow to respond. Please try again.' : err.message);
    } finally {
      clearTimeout(timer); stopCycle(); $('audit-btn').disabled = false;
    }
  }

  function renderError(message) {
    $('error-text').textContent = message;
    showPanel('result-error'); reveal('error-title');
  }

  function renderUnscored(data) {
    $('unscored-reason').textContent = data.reason;
    const list = $('unscored-neutral'); list.replaceChildren();
    (data.neutral || []).forEach((t) => list.appendChild(el('li', '', t)));
    const cta = $('unscored-cta');
    cta.href = bookHref(); cta.textContent = bookLabel();
    showPanel('result-unscored'); reveal('unscored-title');
  }

  const weakest = (dims) =>
    dims.filter((d) => d.score < d.max)
      .sort((a, b) => a.score - b.score || PRIORITY.indexOf(a.dimension) - PRIORITY.indexOf(b.dimension))
      .slice(0, 3);

  function renderResult(data) {
    let host = data.url;
    try { host = new URL(data.url).hostname.replace(/^www\./, ''); } catch (e) { /* keep as given */ }
    $('result-title').textContent = host;
    $('result-total').textContent = String(data.total);

    const rows = $('result-rows'); rows.replaceChildren();
    data.dimensions.forEach((d, i) => {
      const li = el('li');
      const head = el('div', 'rowhead');
      head.append(el('span', 'dim', d.dimension), el('span', 'num', d.score + '/' + d.max));
      const track = el('div', 'track'); const fill = el('div', 'fill');
      fill.style.width = (d.score / d.max) * 100 + '%';
      fill.style.animationDelay = (0.05 + i * 0.07) + 's';
      track.appendChild(fill);
      const by = el('p', 'fix'); by.append(el('b', '', 'Fixed by'), document.createTextNode(' ' + d.fixed_by));
      const ev = el('ul', 'evidence'); d.evidence.forEach((t) => ev.appendChild(el('li', '', t)));
      li.append(head, track, by, ev);
      rows.appendChild(li);
    });

    const low = [...data.dimensions].sort((a, b) => a.score - b.score);
    $('result-lowest').textContent = low[0].score === low[0].max
      ? 'Every dimension scored full marks.'
      : 'Lowest: ' + low[0].dimension + ' (' + low[0].score + '/' + low[0].max + ')';

    // Locked fixes: the dimensions are already public in the scores; the actions are not sent until an email is given.
    const fixes = $('fix-list'); fixes.replaceChildren();
    const weak = weakest(data.dimensions);
    if (!weak.length) {
      const li = el('li'); li.appendChild(el('p', 'fx-act', 'Nothing to fix on the homepage. The call is where we look at the parts a homepage cannot show.'));
      fixes.appendChild(li);
      show('lead-form', false); show('route', true);
    } else {
      weak.forEach((d) => {
        const li = el('li');
        li.append(el('span', 'fx-dim', d.dimension + ' · ' + d.score + '/' + d.max), document.createElement('br'),
          el('span', 'fx-by', 'Fixed by ' + d.fixed_by), el('span', 'locked'), el('span', 'locked'));
        fixes.appendChild(li);
      });
      show('lead-form', true); show('route', false);
    }
    show('path', false);
    $('lead-form').reset(); emailError('');
    showPanel('result-ok'); reveal('result-title');
  }

  // --- email gate -----------------------------------------------------------
  const EMAIL = /^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$/;
  function emailError(msg) {
    const e = $('email-error'); e.textContent = msg || ''; e.hidden = !msg;
    $('email').setAttribute('aria-invalid', msg ? 'true' : 'false');
  }

  async function post(path, payload) {
    const res = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await res.json().catch(() => null);
    if (!res.ok || !data || !data.ok) throw new Error((data && data.error) || 'Something went wrong. Please try again.');
    return data;
  }

  async function submitLead(ev) {
    ev.preventDefault();
    const form = $('lead-form');
    const email = form.email.value.trim();
    if (!EMAIL.test(email)) { emailError('Enter a valid email address.'); $('email').focus(); return; }
    emailError('');
    $('lead-btn').disabled = true;
    try {
      const data = await post('/api/lead', { event: 'lead', email, url: state.url, hp: form.hp.value, utm: getUtm() });
      state.email = email;
      track('Lead', { content_name: 'scorecard' });
      unlockFixes(data.fixes || []);
      show('lead-form', false); show('route', true);
      $('route').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
    } catch (err) {
      emailError(err.message);
    } finally {
      $('lead-btn').disabled = false;
    }
  }

  function unlockFixes(fixes) {
    const list = $('fix-list'); list.replaceChildren();
    if (!fixes.length) {
      const li = el('li'); li.appendChild(el('p', 'fx-act', 'We could not generate your fixes just now, but we have your email. Book the call and we will go through them together.'));
      list.appendChild(li); return;
    }
    fixes.forEach((f) => {
      const li = el('li');
      li.append(el('span', 'fx-dim', f.dimension + ' · ' + f.score + '/5'), document.createElement('br'),
        el('span', 'fx-by', 'Fixed by ' + f.fixed_by), el('p', 'fx-act', f.action));
      list.appendChild(li);
    });
  }

  // --- routing question -----------------------------------------------------
  const PATHS = {
    'gtm-install': ['GTM Install fits best', 'You already have someone running growth, so the fastest route is a fixed-scope build and training your team to run it.'],
    'done-for-you': ['Done-for-you fits best', 'Nobody owns growth in-house yet, so we run the system for you each month.'],
  };
  async function route(inhouse) {
    document.querySelectorAll('#route button').forEach((b) => { b.disabled = true; });
    let path = inhouse === 'yes' ? 'gtm-install' : 'done-for-you';
    try {
      const data = await post('/api/lead', { event: 'route', email: state.email, inhouse, utm: getUtm() });
      path = data.path || path;
    } catch (e) { /* the recommendation does not depend on the network */ }
    $('path-title').textContent = PATHS[path][0];
    $('path-text').textContent = PATHS[path][1];
    const cta = $('path-cta'); cta.href = bookHref(); cta.textContent = bookLabel();
    const fb = $('path-fallback');
    fb.hidden = !!state.config.bookingUrl;
    fb.textContent = 'Online booking opens soon. For now, send us a note and we will find a time.';
    show('route', false); show('path', true);
    $('path').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest' });
  }

  // --- wiring ---------------------------------------------------------------
  $('audit-form').addEventListener('submit', (e) => { e.preventDefault(); runAudit($('url').value); });
  $('lead-form').addEventListener('submit', submitLead);
  $('error-retry').addEventListener('click', focusUrl);
  document.querySelectorAll('#route button').forEach((b) => b.addEventListener('click', () => route(b.dataset.inhouse)));
  ['path-cta', 'unscored-cta'].forEach((id) => $(id).addEventListener('click', () => track('Schedule', { content_name: 'scorecard' })));
  $('final-cta').addEventListener('click', (e) => { e.preventDefault(); focusUrl(); });
})();
