const list = document.getElementById('list');
const totalEl = document.getElementById('total');
const errorEl = document.getElementById('error');

let coffees = [];

async function api(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    let msg = 'Something went wrong.';
    try { msg = (await res.json()).error || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

function render() {
  const total = coffees.reduce((s, c) => s + c.votes, 0);
  const max = Math.max(1, ...coffees.map(c => c.votes));
  totalEl.textContent = total;
  list.replaceChildren();

  coffees.forEach((c, i) => {
    const li = document.createElement('li');
    li.className = 'item' + (i === 0 && c.votes > 0 ? ' leader' : '');

    const rank = el('span', 'rank', String(i + 1));

    const info = el('div', 'info');
    const title = el('h2', '', c.name);
    title.append(el('span', 'origin', c.origin));
    const desc = el('p', 'desc', c.description);
    const bar = el('div', 'bar');
    const fill = el('span', 'fill');
    fill.style.width = (c.votes / max * 100) + '%';
    bar.append(fill);
    info.append(title, desc, bar);

    const side = el('div', 'side');
    const count = el('span', 'count', String(c.votes));
    const btn = el('button', '', 'Vote');
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Vote for ' + c.name);
    btn.onclick = () => vote(c.id, btn);
    side.append(count, btn);

    li.append(rank, info, side);
    list.append(li);
  });
}

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;   // textContent: no HTML injection
  return n;
}

async function vote(id, btn) {
  errorEl.textContent = '';
  btn.disabled = true;
  try {
    const updated = await api('/api/coffees/' + id + '/vote', { method: 'POST' });
    coffees = coffees.map(c => c.id === updated.id ? updated : c);
    // Re-sort like the backend does: votes desc, then name.
    coffees.sort((a, b) => b.votes - a.votes || a.name.localeCompare(b.name));
    render();
  } catch (e) {
    errorEl.textContent = e.message;
    btn.disabled = false;
  }
}

async function load() {
  try { coffees = await api('/api/coffees'); render(); }
  catch (e) { errorEl.textContent = e.message; }
}

load();
