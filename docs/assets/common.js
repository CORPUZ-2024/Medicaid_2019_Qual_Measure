/* Shared helpers for the Child and Adult Health Care Quality Measures site. */
const CS = {
  async json(name){
    const r = await fetch(`data/${name}`, {cache:'no-cache'});
    if(!r.ok) throw new Error(`${name}: ${r.status}`);
    return r.json();
  },
  fmt(n, d=1){
    if(n===null||n===undefined||Number.isNaN(n)) return '–';
    return Number(n).toLocaleString(undefined,{minimumFractionDigits:d,maximumFractionDigits:d});
  },
  pct(x, d=0){ return x===null||x===undefined ? '–' : (100*x).toFixed(d)+'%'; },
  pill(kind, text){ return `<span class="pill ${kind}">${text}</span>`; },
  classPill(c){
    const m = {Improving:'good', Declining:'bad', Stable:'stable',
               'Not comparable':'na', 'Persistent Bottom Quartile':'warn'};
    return CS.pill(m[c]||'na', c);
  },
  regionName(r){ return r ? `Region ${r}` : '–'; },
  // Section 1 "above the median" = CMS Eval "On Track": the state rate is at least as
  // good as the CMS median, direction-aware (lower is better for some measures).
  above(b){ return b.eval==='On Track'; },
  // Measure titles: several rate series share one CMS measure name (e.g. FUM-CH has a
  // 7-day and a 30-day rate). When a name is not unique within its program, append the
  // follow-up period (or the distinguishing age band) from the rate definition.
  qualifier(rd, name){
    let m;
    if((m = rd.match(/(Alcohol Use Disorder|Opioid Use Disorder|Other SUD|Total SUD) with (Initiation|Engagement) of SUD Treatment within (\d+) Days/i)))
      return `${m[1]}: ${m[2]} Within ${m[3]} Days`;
    if(/Postpartum Care Visit on or Between 7 and 84 Days/i.test(rd)) return 'Postpartum Visit Within 7 to 84 Days after Delivery';
    if(/Prenatal Care Visit in the First Trimester/i.test(rd)) return 'Prenatal Visit in First Trimester or Within 42 Days of Enrollment';
    if(/for 12 Weeks/i.test(rd)) return 'Acute Phase, 12 Weeks';
    if(/Continuation Phase \(6 Months\)/i.test(rd)) return 'Continuation Phase, 6 Months';
    if((m = rd.match(/in (Poor )?Control \(([<>][\d.]+%)\)/i))) return `${m[1]?'Poor Control ':'Control '}${m[2]}`;
    m = rd.match(/within \d+ days[^:]*/i) ||
        rd.match(/\d+-Day Initiation Phase|9-Month Continuation and Maintenance Phase/i);
    if(m){
      let q = m[0].replace(/^within/i,'Within').trim();
      if(/Long-Acting Reversible/i.test(rd)) q = 'LARC, ' + q;
      else if(/Most Effective or Moderately/i.test(rd)) q = 'Most/Moderately Effective, ' + q;
      return q;
    }
    const age = rd.match(/Ages? \d+(?: to \d+| and Older)?\s*$/i);
    if(age && !name.includes(age[0].trim())) return age[0].trim();
    return '';
  },
  displayNames(measures){
    const n = {}, k = m => m.program+'|'+m.measure_name;
    measures.forEach(m=>{ n[k(m)]=(n[k(m)]||0)+1; });
    measures.forEach(m=>{
      const q = n[k(m)]>1 ? CS.qualifier(m.rate_definition, m.measure_name) : '';
      m.display_name = q ? `${m.measure_name} (${q})` : m.measure_name;
    });
    // a qualifier that still collides (e.g. only the age band differs across several
    // sub-rates) does not help; fall back to the plain name + rate-definition line
    const d = {};
    measures.forEach(m=>{ const key=m.program+'|'+m.display_name; d[key]=(d[key]||0)+1; });
    measures.forEach(m=>{ if(d[m.program+'|'+m.display_name]>1) m.display_name=m.measure_name; });
  },
  sortable(table){
    table.querySelectorAll('th[data-k]').forEach((th,ci)=>{
      th.addEventListener('click',()=>{
        const tb=table.tBodies[0], rows=[...tb.rows];
        const num=th.classList.contains('num');
        const dir=th.dataset.dir==='asc'?'desc':'asc'; th.dataset.dir=dir;
        rows.sort((a,b)=>{
          let x=a.cells[ci].dataset.v ?? a.cells[ci].textContent;
          let y=b.cells[ci].dataset.v ?? b.cells[ci].textContent;
          if(num){x=parseFloat(x)||0;y=parseFloat(y)||0;return dir==='asc'?x-y:y-x;}
          return dir==='asc'?String(x).localeCompare(y):String(y).localeCompare(x);
        });
        rows.forEach(r=>tb.appendChild(r));
      });
    });
  }
};

/* shared header: one nav for every page */
const NAV = [
  ['index.html','Policy Context'],
  ['state-domain.html','(A) 2024 Measures by State and Domain'],
  ['measures.html','(B) 2024 Across all States by Measure Type and Domain'],
  ['trends.html','Trends 2022–24'],
  ['limitations.html','Limitations'],
  ['methodology.html','Methodology'],
  ['v1/index.html','V1 archive ↗'],
];
document.addEventListener('DOMContentLoaded',()=>{
  const h=document.querySelector('header.site');
  if(h && !h.children.length){
    h.innerHTML = '<h1>Child and Adult Health Care Quality Measures</h1><nav>'+
      NAV.map(([href,t])=>`<a href="${href}">${t}</a>`).join('')+'</nav>';
  }
  const here=(location.pathname.split('/').pop()||'index.html');
  document.querySelectorAll('header.site nav a').forEach(a=>{
    if(a.getAttribute('href')===here) a.classList.add('active');
  });
});
