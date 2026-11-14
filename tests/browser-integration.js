(async () => {
  const checks = [];
  const assert = (ok, label) => { if (!ok) throw new Error(label); checks.push(label); };
  const wait = async condition => {
    for (let i = 0; i < 150; i++) { if (condition()) return; await new Promise(r => setTimeout(r, 40)); }
    throw new Error('Timed out waiting for UI');
  };
  const button = label => [...document.querySelectorAll('button')].find(b => b.textContent.includes(label));
  const setInput = (id, value) => {
    const el = document.getElementById(id);
    Object.getOwnPropertyDescriptor(el.tagName === 'SELECT' ? HTMLSelectElement.prototype : HTMLInputElement.prototype, 'value').set.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };
  await wait(() => document.querySelectorAll('.comunas button').length === 54);
  if (!button('Historial por plataforma')) document.querySelector('button[aria-label=Language]').click();
  await wait(() => document.querySelector('#observed-platform'));
  assert(document.querySelector('.view-switch button[aria-pressed=true]').textContent.includes('FireChronos'), 'observed view selected');
  const blobMap = new Map(), downloads = [];
  const oldCreate = URL.createObjectURL, oldClick = HTMLAnchorElement.prototype.click;
  URL.createObjectURL = blob => { const u = oldCreate(blob); blobMap.set(u, blob); return u; };
  HTMLAnchorElement.prototype.click = function () { downloads.push({ name: this.download, blob: blobMap.get(this.href) }); };
  try {
    for (const [cut, name, sourceId, start, end] of [
      ['08109','Santa Juana','aqua-history','2023-01','2023-03'],
      ['08109','Santa Juana','snpp-history','2012-01','2013-06'],
      ['08109','Santa Juana','noaa20-history','2023-01','2023-03'],
      ['16107','Quillón','snpp-history','2022-07','2023-06'],
      ['08107','Penco','aqua-history','2002-07','2003-06'],
      ['08107','Penco','noaa20-history','2025-01','2025-12'],
    ]) {
      const commune = [...document.querySelectorAll('.comunas button')].find(b => b.querySelector('span').textContent === name);
      commune.click();
      await wait(() => document.querySelector('#observed-title')?.textContent.includes('CUT ' + cut) && document.querySelector('#observed-platform'));
      setInput('observed-platform', sourceId);
      await wait(() => document.querySelector('#observed-platform').value === sourceId && document.querySelector('#observed-start').min === (sourceId === 'aqua-history' ? '2002-07' : sourceId === 'snpp-history' ? '2012-01' : '2018-04'));
      setInput('observed-start', start); setInput('observed-end', end);
      await wait(() => document.querySelector('#observed-start').value === start && document.querySelector('#observed-end').value === end);
      await new Promise(r => setTimeout(r, 70));
      const doc = await (await fetch('/observed/data/publication/' + cut + '.json')).json();
      const source = doc.sources.find(s => s.id === sourceId);
      const expected = source.series.filter(r => r.month >= start && r.month <= end);
      for (const r of expected) {
        const cell = document.querySelector(`[data-testid=observed-calendar] [data-month="${r.month}"]`);
        assert(cell && cell.textContent === (r.cell_days?.toLocaleString('es-CL') ?? '—'), `${cut}/${sourceId}/${r.month} calendar equals publication`);
      }
      button('CSV de la consulta').click(); button('Metadatos de la consulta').click();
      const csv = await downloads.at(-2).blob.text(); const metadata = JSON.parse(await downloads.at(-1).blob.text());
      assert(downloads.at(-2).name.includes(cut + '_' + sourceId + '_' + start + '_' + end), `${cut}/${sourceId} export filename scope`);
      assert(csv.trim().split('\r\n').length === expected.length + 1, `${cut}/${sourceId} exported monthly count`);
      for (const r of expected) assert(csv.includes(`"${r.month}","${r.detections ?? ''}","${r.cell_days ?? ''}"`), `${cut}/${sourceId}/${r.month} export equals publication`);
      assert(metadata.commune.cut === cut && metadata.source.id === sourceId && metadata.query.start === start && metadata.query.end === end && metadata.harmonization === 'none', `${cut}/${sourceId} metadata scope`);
      assert(document.querySelector('.observed-exports a').getAttribute('href') === source.csv.url, `${cut}/${sourceId} raw CSV source`);
    }
    setInput('observed-start','2025-12'); setInput('observed-end','2025-01');
    await wait(() => document.querySelector('.observed-history [role=alert]'));
    assert(button('CSV de la consulta').disabled && !document.querySelector('[data-testid=observed-calendar]'), 'invalid dates block stale calendar and exports');
    button('Calendario armonizado').click();
    await wait(() => document.querySelector('section.season'));
    assert(document.querySelector('.season .kpi.big strong').textContent === '3', 'harmonized Penco current season preserved');
    assert(document.querySelector('.comunas button.sel span').textContent === 'Penco', 'commune survives view switch');
    document.querySelector('button[aria-label=Language]').click();
    await wait(() => document.documentElement.lang === 'en');
    button('Platform history').click();
    await wait(() => document.querySelector('#observed-platform'));
    assert(document.querySelector('#observed-title').textContent.includes('Penco'), 'English view retains commune');
    assert(document.body.textContent.includes('These values') || document.body.textContent.includes('these values are not harmonized'), 'English scientific scope');
    document.querySelector('button[aria-label=Language]').click();
    await wait(() => document.documentElement.lang === 'es');
    // A corrupted response must replace the prior results with an error, not stale exports.
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const response = await originalFetch(...args);
      if (String(args[0]).endsWith('/08109.json') && String(args[0]).includes('/publication/')) return new Response((await response.text()) + ' ');
      return response;
    };
    [...document.querySelectorAll('.comunas button')].find(b => b.querySelector('span').textContent === 'Santa Juana').click();
    await wait(() => document.querySelector('main [role=alert]'));
    assert(!document.querySelector('.observed-exports'), 'corrupt SHA blocks result and exports');
    window.fetch = originalFetch;
    button('Reintentar').click();
    await wait(() => document.querySelector('#observed-title')?.textContent.includes('Santa Juana'));
    assert(document.querySelector('[data-testid=observed-calendar]'), 'retry recovers verified data');
    assert(document.documentElement.scrollWidth <= innerWidth, 'desktop has no page overflow');
    return { status: 'passed', checks: checks.length, details: checks };
  } finally { URL.createObjectURL = oldCreate; HTMLAnchorElement.prototype.click = oldClick; }
})()
