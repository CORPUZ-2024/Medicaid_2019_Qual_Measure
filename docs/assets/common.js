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
  // follow-up period, or the sub-rate that tells the series apart, from the rate definition.
  SUBRATES: [
    // follow-up / time windows
    [/(Alcohol Use Disorder|Opioid Use Disorder|Other SUD|Total SUD) with (Initiation|Engagement) of SUD Treatment within (\d+) Days/i,
      m=>`${m[1]}: ${m[2]} Within ${m[3]} Days`],
    [/Postpartum Care Visit on or Between 7 and 84 Days/i, ()=>'Postpartum Visit Within 7 to 84 Days after Delivery'],
    [/Prenatal Care Visit in the First Trimester/i, ()=>'Prenatal Visit in First Trimester or Within 42 Days of Enrollment'],
    [/for 12 Weeks/i, ()=>'Acute Phase, 12 Weeks'],
    [/Continuation Phase \(6 Months\)/i, ()=>'Continuation Phase, 6 Months'],
    [/(\d+) or More Well-Child Visits .*during the (First 15 Months|15th to 30th Months) of Life/i,
      m=>`${m[1]}+ Visits ${m[2]==='First 15 Months'?'in the First 15 Months':'from 15 to 30 Months'}`],
    [/(Long-Acting Reversible|Most Effective or Moderately Effective) Method of Contraception(?: (Within \d+ Days of Delivery))?/i,
      m=>(/Long/i.test(m[1])?'LARC':'Most/Moderately Effective')+(m[2]?', '+m[2]:'')],
    [/within \d+ days[^:]*/i, m=>m[0].replace(/^within/i,'Within').trim()],
    [/\d+-Day Initiation Phase|9-Month Continuation and Maintenance Phase/i, m=>m[0]],
    // other sub-rates
    [/in (Poor )?Control \(([<>][\d.]+%)\)/i, m=>`${m[1]?'Poor Control ':'Control '}${m[2]}`],
    [/Advised to Quit/i, ()=>'Advised to Quit'],
    [/Recommended Cessation Medications/i, ()=>'Cessation Medications'],
    [/Other Cessation Methods/i, ()=>'Other Cessation Strategies'],
    [/Life Decisions/i, ()=>'Makes Life Decisions'],
    [/Way to Get Places/i, ()=>'Has Transportation'],
    [/Daily Schedule/i, ()=>'Decides Daily Schedule and Spending'],
    [/Dispensed (?:an )?FDA-Approved Medication.*Total Rate/i, ()=>'Any Medication, Total Rate'],
    [/Dispensed (Buprenorphine|Long-acting Injectable Naltrexone|Methadone|Oral Naltrexone)/i, m=>m[1]],
    [/\(Combination (\d+)\)/i, m=>`Combination ${m[1]}`],
    [/Measles, Mumps, and Rubella/i, ()=>'MMR'],
    [/Two Flu Vaccinations/i, ()=>'2+ Flu Vaccinations'],
    [/Human Papillomavirus/i, ()=>'HPV Series'],
    [/Sealants on All Four/i, ()=>'All Four Molars'],
    [/Sealant on at Least One/i, ()=>'At Least One Molar'],
    [/Body Mass Index Percentile/i, ()=>'BMI Percentile'],
    [/Counseling for Nutrition/i, ()=>'Nutrition Counseling'],
    [/Counseling for Physical Activity/i, ()=>'Physical Activity Counseling'],
    [/Metabolic Testing for (Blood Glucose and Cholesterol|Blood Glucose|Cholesterol)/i, m=>m[1].replace('Blood ','')],
    // CAHPS survey items (+ child population)
    [/Rated (Their|the) (Health Care|Health Plan|Personal Doctor|Specialist)/i, m=>`Rated ${m[2]} 9–10`],
    [/Informed and Up-to-Date/i, ()=>'Doctor Informed about Other Care'],
    [/Got Care Quickly/i, ()=>'Always Got Care Quickly'],
    [/Got Needed Care/i, ()=>'Always Got Needed Care'],
    [/Communicates Well/i, ()=>'Doctor Always Communicates Well'],
    [/Customer Service/i, ()=>'Customer Service'],
  ],
  qualifier(rd, name, withAge){
    const parts=[];
    for(const [re,f] of CS.SUBRATES){ const m=rd.match(re); if(m){ parts.push(f(m)); break; } }
    if(/Children with Chronic Conditions \(CCC\)/i.test(rd)) parts.push('Chronic Conditions');
    else if(/General Child \(GC\)/i.test(rd)) parts.push('General Child');
    // age band, when it differs from the band already in the measure name
    const age = rd.match(/(?:Ages? \d+(?: to \d+| and Older)?|Under Age \d+)\s*$/i);
    if(withAge && age) parts.push(age[0].trim() + (name.includes(age[0].trim()) ? ', Total' : ''));
    return parts.join(', ');
  },
  displayNames(measures){
    const n = {}, k = m => m.program+'|'+m.measure_name;
    measures.forEach(m=>{ n[k(m)]=(n[k(m)]||0)+1; });
    const label = withAge => measures.forEach(m=>{
      if(n[k(m)]<2 || (withAge && !m._clash)) return;
      const q = CS.qualifier(m.rate_definition, m.measure_name, withAge);
      m.display_name = q ? `${m.measure_name} (${q})` : m.measure_name;
    });
    measures.forEach(m=>{ m.display_name=m.measure_name; });
    label(false);
    // second pass: add the age band only where titles still collide (e.g. AMR 5–11 vs 12–18)
    const d = {};
    measures.forEach(m=>{ const key=m.program+'|'+m.display_name; d[key]=(d[key]||0)+1; });
    measures.forEach(m=>{ m._clash = d[m.program+'|'+m.display_name]>1; });
    label(true);
    measures.forEach(m=>{ delete m._clash; });
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
