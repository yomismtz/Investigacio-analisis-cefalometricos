const analyses = [
  ["Steiner","Esqueletal · dental","SNA, SNB, ANB, incisivos y patrón vertical."],
  ["Downs","Esqueletal · dental","Perfil dentofacial y dirección de crecimiento."],
  ["Tweed","Dental · vertical","Triángulo diagnóstico FMA, FMIA e IMPA."],
  ["Ricketts","Esqueletal · crecimiento","Eje facial, profundidades y relación A–Pg."],
  ["Björk–Jarabak","Crecimiento","Rotación mandibular y proporciones faciales."],
  ["Wits","Sagital","Discrepancia maxilomandibular sobre plano oclusal."],
  ["McNamara","Esqueletal · vía aérea","Longitudes, N-perpendicular y dimensiones faríngeas."],
  ["Holdaway","Tejidos blandos","Perfil, línea H y espesor mentoniano."],
  ["Burstone COGS","Quirúrgico","23 mediciones ortognáticas con referencias por sexo."],
  ["Legan–Burstone","Tejidos blandos","Proporciones y relaciones faciales para cirugía ortognática."],
  ["Sassouni","Arquitectura facial","Convergencia de planos, arcos y relaciones arquitectónicas."],
  ["Powell","Estética facial","Ángulos nasofrontal, nasofacial, nasomental y mentocervical."],
  ["Vía aérea","Faríngeo","Dimensiones nasofaríngea y orofaríngea orientativas."],
  ["Cráneo-cervical","Postura","SN-OPT, SN-CVT, OPT-CVT, espacios y triángulo hioideo."],
  ["CVM C2–C4","Maduración","Estadios CS1–CS6 por morfología cervical."],
  ["Alineación C2–C4","Postura","Lordosis, rectificación, cifosis e hiperlordosis cualitativas."],
  ["Lordosis C1–C7","Cervical","Ángulo cervical y rango orientativo 35°–45°."],
];
const grid=document.querySelector('#analysis-grid');const search=document.querySelector('#analysis-search');const count=document.querySelector('#analysis-count');
function render(filter=''){const q=filter.trim().toLowerCase();const items=analyses.filter(a=>a.join(' ').toLowerCase().includes(q));grid.innerHTML=items.map(([name,tag,desc])=>`<article class="analysis-card reveal visible"><span class="tag">${tag}</span><h3>${name}</h3><p>${desc}</p></article>`).join('');count.textContent=`${items.length} ${items.length===1?'disponible':'disponibles'}`}
render();search?.addEventListener('input',e=>render(e.target.value));
const toggle=document.querySelector('.menu-toggle'),links=document.querySelector('#nav-links');toggle?.addEventListener('click',()=>{const open=links.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open))});links?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{links.classList.remove('open');toggle?.setAttribute('aria-expanded','false')}));
const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target)}}),{threshold:.08});document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
