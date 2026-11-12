/* Shared helpers for the Core Set View B Extension site. */
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

/* active nav link */
document.addEventListener('DOMContentLoaded',()=>{
  const here=(location.pathname.split('/').pop()||'index.html');
  document.querySelectorAll('header.site nav a').forEach(a=>{
    if(a.getAttribute('href')===here) a.classList.add('active');
  });
});
