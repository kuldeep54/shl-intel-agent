// Automatically use local backend if running locally (including file:// protocol), otherwise production
const API = window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1' || 
            window.location.hostname === '' || 
            window.location.protocol === 'file:'
  ? 'http://127.0.0.1:8000'
  : 'https://shl-recommender-api.onrender.com';

let hist = [], turns = 0, busy = false;
const inp = document.getElementById('inp');
const sbtn = document.getElementById('sbtn');
const msgs = document.getElementById('msgs');

inp.addEventListener('input', () => {
  sbtn.disabled = !inp.value.trim() || turns >= 8 || busy;
});

function grow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}

function ky(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); go(); }
}

function use(t) {
  inp.value = t; grow(inp); inp.focus();
  sbtn.disabled = false;
}

function ts() {
  return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function toggleSidebar() {
  const b = document.querySelector('.body');
  b.classList.toggle('closed');
}

function killWelcome() {
  const w = document.getElementById('wlc');
  if (w) w.remove();
}

function setTurn(n) {
  document.getElementById('tn').textContent = n;
  document.getElementById('tf').style.width = (n / 8 * 100) + '%';
}

function addMsg(role, text, recs, eoc) {
  killWelcome();
  const row = document.createElement('div');
  row.className = 'mrow ' + role;

  const ava = document.createElement('div');
  ava.className = 'mava ' + role;
  ava.textContent = role === 'bot' ? 'S' : 'U';

  const body = document.createElement('div');
  body.className = 'mbody';

  const meta = document.createElement('div');
  meta.className = 'mmeta';
  meta.textContent = (role === 'bot' ? 'SHL Intel' : 'You') + ' · ' + ts();
  body.appendChild(meta);

  const bubble = document.createElement('div');
  bubble.className = 'mbubble';
  bubble.innerHTML = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
  body.appendChild(bubble);

  if (recs && recs.length > 0) {
    const rw = document.createElement('div');
    rw.className = 'recs';

    const ey = document.createElement('div');
    ey.className = 'rec-eyebrow';
    ey.textContent = recs.length + ' assessment' + (recs.length > 1 ? 's' : '') + ' recommended';
    rw.appendChild(ey);

    const list = document.createElement('div');
    list.className = 'rec-list';

    recs.forEach(r => {
      const a = document.createElement('a');
      a.className = 'rec';
      a.href = r.url || '#';
      a.target = '_blank';
      a.rel = 'noopener noreferrer';

      const dur = r.duration && r.duration !== 'N/A' && r.duration !== '-'
        ? `<span class="rtag">⏱ ${r.duration}</span>` : '';
      const rem = r.remote_testing === 'Yes'
        ? `<span class="rtag ok">remote ✓</span>` : '';
      const adp = r.adaptive === 'Yes'
        ? `<span class="rtag ok">adaptive</span>` : '';

      a.innerHTML = `
        <div class="rbadge">${r.test_type || '?'}</div>
        <div class="rinfo">
          <div class="rname">${r.name}</div>
          <div class="rmeta">${dur}${rem}${adp}</div>
        </div>
        <div class="rarrow">↗</div>`;
      list.appendChild(a);
    });

    rw.appendChild(list);
    body.appendChild(rw);
  }

  if (eoc) {
    const e = document.createElement('div');
    e.className = 'eoc';
    e.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg> Session complete — start a new chat to explore more.`;
    body.appendChild(e);
  }

  row.appendChild(ava);
  row.appendChild(body);
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
}

function showTyping() {
  killWelcome();
  const row = document.createElement('div');
  row.className = 'trow'; row.id = '__t__';
  row.innerHTML = `
    <div class="mava bot">S</div>
    <div class="tdots">
      <div class="td"></div><div class="td"></div><div class="td"></div>
    </div>`;
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
}

function hideTyping() {
  const t = document.getElementById('__t__');
  if (t) t.remove();
}

async function go() {
  const text = inp.value.trim();
  if (!text || turns >= 8 || busy) return;

  inp.value = ''; inp.style.height = 'auto';
  sbtn.disabled = true; busy = true;
  turns++; setTurn(turns);

  hist.push({ role: 'user', content: text });
  addMsg('user', text);
  showTyping();

  try {
    const res = await fetch(API + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: hist }),
      signal: AbortSignal.timeout(30000)
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const d = await res.json();
    hideTyping();
    hist.push({ role: 'assistant', content: d.reply });
    addMsg('bot', d.reply, d.recommendations || [], d.end_of_conversation);
    if (d.end_of_conversation || turns >= 8) {
      inp.disabled = true;
      inp.placeholder = 'Session ended — click New chat to start again.';
    }
  } catch (err) {
    hideTyping();
    turns--; setTurn(turns); hist.pop();
    const msg = err.name === 'TimeoutError' || err.message.includes('fetch')
      ? 'Could not reach the backend. Make sure your FastAPI server is running at <code>' + API + '</code>.'
      : 'Error: ' + err.message;
    addMsg('bot', msg);
  }

  busy = false;
  if (turns < 8 && !inp.disabled) {
    sbtn.disabled = !inp.value.trim();
  }
}

function reset() {
  hist = []; turns = 0; busy = false;
  setTurn(0);
  inp.disabled = false;
  inp.value = ''; inp.style.height = 'auto';
  inp.placeholder = 'Describe the role you\'re hiring for…';
  sbtn.disabled = true;
  msgs.innerHTML = `
    <div class="welcome" id="wlc">
      <div class="wlc-eyebrow">SHL Intel</div>
      <h1>Find the right<br><em>assessment</em></h1>
      <p>Describe the role you're hiring for and I'll match it to the SHL catalog — clarifying when needed, recommending up to 10 assessments, and comparing on request.</p>
      <div class="chips">
        <div class="chip" onclick="use('Hiring a Java developer')">Java developer</div>
        <div class="chip" onclick="use('Sales manager role')">Sales manager</div>
        <div class="chip" onclick="use('Graduate finance analyst')">Finance graduate</div>
        <div class="chip" onclick="use('Customer service contact centre')">Customer service</div>
        <div class="chip" onclick="use('Data scientist with Python')">Data scientist</div>
        <div class="chip" onclick="use('Executive leadership hire')">Executive hire</div>
        <div class="chip" onclick="use('Compare OPQ32r vs Verify G+')">Compare assessments</div>
      </div>
    </div>`;
}
