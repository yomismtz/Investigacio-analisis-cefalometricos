const analyses = [
  {name:"Steiner",category:"Esqueletal",tag:"Esqueletal · dental",desc:"SNA, SNB, ANB, incisivos y patrón vertical."},
  {name:"Downs",category:"Esqueletal",tag:"Esqueletal · dental",desc:"Perfil dentofacial y dirección de crecimiento."},
  {name:"Tweed",category:"Dental",tag:"Dental · vertical",desc:"Triángulo diagnóstico FMA, FMIA e IMPA."},
  {name:"Ricketts",category:"Crecimiento",tag:"Esqueletal · crecimiento",desc:"Eje facial, profundidades y relación A–Pg."},
  {name:"Björk–Jarabak",category:"Crecimiento",tag:"Crecimiento",desc:"Rotación mandibular y proporciones faciales."},
  {name:"Wits",category:"Esqueletal",tag:"Sagital",desc:"Discrepancia maxilomandibular sobre plano oclusal."},
  {name:"McNamara",category:"Esqueletal",tag:"Esqueletal · vía aérea",desc:"Longitudes, N-perpendicular y dimensiones faríngeas."},
  {name:"Holdaway",category:"Tejidos blandos",tag:"Tejidos blandos",desc:"Perfil, línea H y espesor mentoniano."},
  {name:"Burstone COGS",category:"Quirúrgico",tag:"Quirúrgico",desc:"23 mediciones ortognáticas con referencias por sexo."},
  {name:"Legan–Burstone",category:"Tejidos blandos",tag:"Tejidos blandos",desc:"Proporciones y relaciones faciales para cirugía ortognática."},
  {name:"Sassouni",category:"Crecimiento",tag:"Arquitectura facial",desc:"Convergencia de planos, arcos y relaciones arquitectónicas."},
  {name:"Powell",category:"Tejidos blandos",tag:"Estética facial",desc:"Ángulos nasofrontal, nasofacial, nasomental y mentocervical."},
  {name:"Vía aérea",category:"Vía aérea",tag:"Faríngeo · edad",desc:"McNamara superior/inferior con referencias pediátricas publicadas a 6, 8, 10 y 12 años; sin interpolar edades faltantes."},
  {name:"Cráneo-cervical",category:"Cervical",tag:"Postura · contexto",desc:"SN-OPT, SN-CVT, OPT-CVT, espacios y triángulo hioideo con contexto de edad/población cuando existe evidencia compatible."},
  {name:"CVM C2–C4",category:"Cervical",tag:"Maduración",desc:"Estadios CS1–CS6 por morfología cervical."},
  {name:"Alineación C2–C4",category:"Cervical",tag:"Postura",desc:"Lordosis, rectificación, cifosis e hiperlordosis cualitativas."},
  {name:"Lordosis C1–C7",category:"Cervical",tag:"Cervical · edad y sexo",desc:"Ángulo C1–C7 con referencias publicadas por grupos de edad y sexo; sin corte universal 35–45° ni interpolación anual."},
];

const palettes = [
  {name:"Agaporni",glyph:"A",desc:"Violeta, ciruela y turquesa. Equilibrado para lectura y ayuda general.",primary:"#5A246F",dark:"#32103F",soft:"#D9C3EE",secondary:"#17A8A2",accent:"#65D8BC",bg:"#F8F3FC"},
  {name:"Tucán",glyph:"T",desc:"Turquesa tropical, naranja y amarillo. Más energético y contrastado.",primary:"#D96816",dark:"#7C3511",soft:"#FFD0A3",secondary:"#15AFA5",accent:"#F4C542",bg:"#FFF8E8"},
  {name:"Pavorreal",glyph:"P",desc:"Azul pavo real, petróleo, violeta y oro. Sobrio y profundo.",primary:"#15517A",dark:"#082F4B",soft:"#BDD6E5",secondary:"#138F85",accent:"#D6A82B",bg:"#F1F7FA"},
  {name:"Ninfa",glyph:"N",desc:"Perla, crema, amarillo suave y ciruela. Una paleta clara y delicada.",primary:"#7A587F",dark:"#4A344E",soft:"#E0D2E4",secondary:"#D8A82E",accent:"#E6A0AD",bg:"#FAF8F5"},
  {name:"Faisán",glyph:"F",desc:"Ciruela, borgoña, cobre y oliva. Cálido y académico.",primary:"#7B294B",dark:"#48152B",soft:"#E7BFD0",secondary:"#9B5A32",accent:"#B49B42",bg:"#FBF6F2"},
  {name:"Quetzal",glyph:"Q",desc:"Esmeralda, turquesa profundo y rubí. Verde intenso con alto contraste.",primary:"#087D64",dark:"#06483D",soft:"#B9E6D8",secondary:"#0BA39B",accent:"#BB3545",bg:"#F2FAF7"},
  {name:"Guacamaya Roja",glyph:"R",desc:"Escarlata, amarillo y azul. La paleta más vibrante del conjunto.",primary:"#B52632",dark:"#70141D",soft:"#F2BBC0",secondary:"#185CB7",accent:"#F0B82E",bg:"#FFF6F4"},
  {name:"Guacamaya Azul",glyph:"G",desc:"Cobalto, cyan y dorado. Fresca, técnica y muy visible.",primary:"#176BB4",dark:"#0A3C70",soft:"#B9D8F2",secondary:"#1AA6C7",accent:"#F2C54D",bg:"#F1F7FD"},
];

const birdSignatures = {
  "Agaporni":[920,1180,1020,1320],
  "Tucán":[520,680,480,760],
  "Pavorreal":[410,540,660,510],
  "Ninfa":[1260,1480,1370,1580],
  "Faisán":[460,590,720,610],
  "Quetzal":[840,1120,1460,1210],
  "Guacamaya Roja":[620,930,740,1090],
  "Guacamaya Azul":[700,1040,1360,970],
};

const assistantHints = [
  {keys:["individual","caso individual","medidas","ángulos","angulos","puntos"],text:"En Caso individual el flujo es análisis → medidas/ángulos → puntos. Yornis calcula los landmarks mínimos necesarios y conserva sólo los resultados que seleccionaste."},
  {keys:["via aérea","vía aérea","airway","mcnamara"],text:"El asistente puede localizar la tabla de vía aérea, mostrar referencias de McNamara y recordarte que las edades pediátricas publicadas son 6, 8, 10 y 12 años sin interpolación."},
  {keys:["cvm","c2","c3","c4","maduración"],text:"Puede explicarte cómo revisar CVM C2–C4, localizar la guía de maduración cervical y abrir la referencia correspondiente."},
  {keys:["lordosis","c1","c7","cervical"],text:"Puede llevarte a C1–C7, mostrar el contexto por edad/sexo disponible y recordar que Yornis no usa 35–45° como normalidad universal."},
  {keys:["calibrar","calibración","escala","mm"],text:"Puede explicarte el flujo de calibración paso a paso antes de interpretar medidas lineales en milímetros."},
  {keys:["landmark","punto","marcar","trazado"],text:"Puede ayudarte a colocar, corregir y revisar landmarks, además de localizar qué puntos necesita cada medición."},
  {keys:["steiner","sna","snb","anb"],text:"Puede encontrar Steiner y sus mediciones relacionadas, además de abrir la tabla de referencia desde la ayuda."},
  {keys:["exportar","spss","csv","excel","pdf"],text:"Puede guiarte hacia las exportaciones científicas, incluyendo CSV, sintaxis SPSS, Excel/PDF y salidas pseudonimizadas."},
  {keys:["respaldo","backup","restaurar"],text:"Puede mostrarte el flujo de respaldo/restauración y explicar cómo conservar la base de investigación de forma consistente."},
];

let audioContext = null;

function playBirdSignature(name) {
  const signature = birdSignatures[name];
  const status = document.querySelector('#sound-status');
  const pulse = document.querySelector('#sound-pulse');
  if (!signature || !(window.AudioContext || window.webkitAudioContext)) {
    if (status) status.textContent = `${name} seleccionado. Tu navegador no habilitó la demostración de audio.`;
    return;
  }
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    audioContext ||= new AudioCtx();
    if (audioContext.state === 'suspended') audioContext.resume();
    const start = audioContext.currentTime + 0.015;
    signature.forEach((frequency,index) => {
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      const t = start + index * 0.105;
      oscillator.type = index % 2 ? 'sine' : 'triangle';
      oscillator.frequency.setValueAtTime(frequency, t);
      oscillator.frequency.exponentialRampToValueAtTime(Math.max(180, frequency * 1.08), t + 0.07);
      gain.gain.setValueAtTime(0.0001, t);
      gain.gain.exponentialRampToValueAtTime(0.055, t + 0.012);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.085);
      oscillator.connect(gain).connect(audioContext.destination);
      oscillator.start(t);
      oscillator.stop(t + 0.09);
    });
    if (status) status.textContent = `${name}: firma sonora reproducida.`;
    if (pulse) {
      pulse.classList.remove('playing');
      void pulse.offsetWidth;
      pulse.classList.add('playing');
    }
  } catch (_) {
    if (status) status.textContent = `${name} seleccionado. No fue posible reproducir audio en este navegador.`;
  }
}

function setPalette(palette) {
  const root = document.documentElement;
  root.style.setProperty('--assistant-primary', palette.primary);
  root.style.setProperty('--assistant-dark', palette.dark);
  root.style.setProperty('--assistant-soft', palette.soft);
  root.style.setProperty('--assistant-secondary', palette.secondary);
  root.style.setProperty('--assistant-accent', palette.accent);
  root.style.setProperty('--assistant-bg', palette.bg);
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', palette.dark);
  const name = document.querySelector('#assistant-name');
  const desc = document.querySelector('#assistant-description');
  const avatar = document.querySelector('#assistant-avatar');
  const chip = document.querySelector('#assistant-chip');
  const status = document.querySelector('#palette-status');
  if (name) name.textContent = palette.name;
  if (desc) desc.textContent = palette.desc;
  if (avatar) avatar.textContent = palette.glyph;
  if (chip) chip.textContent = `Paleta activa · ${palette.name}`;
  if (status) status.textContent = `${palette.name} seleccionado`;
  document.querySelectorAll('.palette-card').forEach(card => card.classList.toggle('active', card.dataset.palette === palette.name));
}

function renderPalettes() {
  const host = document.querySelector('#palette-grid');
  if (!host) return;
  host.innerHTML = palettes.map((p,index) => `<button type="button" class="palette-card ${index===0?'active':''}" data-palette="${p.name}" aria-pressed="${index===0}" aria-label="Seleccionar ${p.name} y reproducir su firma sonora"><strong>${p.name}</strong><small>${p.desc}</small><span class="swatches" aria-hidden="true"><i style="background:${p.primary}"></i><i style="background:${p.secondary}"></i><i style="background:${p.accent}"></i><i style="background:${p.dark}"></i></span></button>`).join('');
  host.querySelectorAll('.palette-card').forEach(card => card.addEventListener('click', () => {
    const palette = palettes.find(p => p.name === card.dataset.palette) || palettes[0];
    host.querySelectorAll('.palette-card').forEach(b => b.setAttribute('aria-pressed', String(b === card)));
    setPalette(palette);
    playBirdSignature(palette.name);
  }));
}

function assistantDemoSearch() {
  const input = document.querySelector('#assistant-demo-search');
  const answer = document.querySelector('#assistant-demo-answer');
  if (!input || !answer) return;
  const q = input.value.trim().toLocaleLowerCase('es');
  if (!q) { answer.textContent = 'Escribe un tema para ver qué tipo de ayuda encontrará tu ave dentro de Yornis.'; return; }
  const hint = assistantHints.find(item => item.keys.some(key => q.includes(key)));
  const analysis = analyses.find(item => `${item.name} ${item.category} ${item.tag} ${item.desc}`.toLocaleLowerCase('es').includes(q));
  if (hint) answer.textContent = hint.text;
  else if (analysis) answer.textContent = `El buscador interno puede localizar ${analysis.name}: ${analysis.desc}`;
  else answer.textContent = 'Dentro de Yornis, Ctrl+K busca el término entre guías de uso, 17 tablas de referencia y 102 mediciones. Si existe una tabla relacionada, puede abrirse directamente desde el resultado.';
}

renderPalettes();
setPalette(palettes[0]);
document.querySelector('#assistant-demo-button')?.addEventListener('click', assistantDemoSearch);
document.querySelector('#assistant-demo-search')?.addEventListener('keydown', event => {
  if (event.key === 'Enter') assistantDemoSearch();
  if (event.key === 'Escape') { event.currentTarget.value = ''; assistantDemoSearch(); }
});

const grid = document.querySelector('#analysis-grid');
const search = document.querySelector('#analysis-search');
const count = document.querySelector('#analysis-count');
const filters = document.querySelector('#analysis-filters');
let activeCategory = 'Todos';
const categories = ['Todos', ...new Set(analyses.map(a => a.category))];

function renderFilters() {
  if (!filters) return;
  filters.innerHTML = categories.map(category => `<button type="button" class="filter-chip ${category === activeCategory ? 'active' : ''}" data-category="${category}" aria-pressed="${category === activeCategory}">${category}</button>`).join('');
  filters.querySelectorAll('.filter-chip').forEach(button => button.addEventListener('click', () => {
    activeCategory = button.dataset.category || 'Todos';
    renderFilters();
    render();
  }));
}

function matches(item, query) {
  const q = query.trim().toLocaleLowerCase('es');
  return (activeCategory === 'Todos' || item.category === activeCategory) && (!q || `${item.name} ${item.category} ${item.tag} ${item.desc}`.toLocaleLowerCase('es').includes(q));
}

function render() {
  if (!grid || !count) return;
  const items = analyses.filter(item => matches(item, search?.value || ''));
  grid.innerHTML = items.length ? items.map(item => `<article class="analysis-card reveal visible"><span class="tag">${item.tag}</span><h3>${item.name}</h3><p>${item.desc}</p></article>`).join('') : '<div class="empty-state" role="status"><strong>No encontramos coincidencias.</strong><br>Prueba otro término o cambia el filtro.</div>';
  count.textContent = `${items.length} ${items.length === 1 ? 'disponible' : 'disponibles'}`;
}

renderFilters();
render();
search?.addEventListener('input', render);
search?.addEventListener('keydown', event => { if (event.key === 'Escape' && search.value) { search.value = ''; render(); } });

const toggle = document.querySelector('.menu-toggle');
const links = document.querySelector('#nav-links');
function closeMenu() { links?.classList.remove('open'); toggle?.setAttribute('aria-expanded', 'false'); }
toggle?.addEventListener('click', () => { const open = links?.classList.toggle('open') ?? false; toggle.setAttribute('aria-expanded', String(open)); });
links?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') closeMenu();
  if ((event.ctrlKey || event.metaKey) && event.key.toLocaleLowerCase('es') === 'k') {
    event.preventDefault();
    const assistantSearch = document.querySelector('#assistant-demo-search');
    assistantSearch?.focus();
    assistantSearch?.scrollIntoView({behavior:'smooth',block:'center'});
  }
});
document.addEventListener('click', event => { if (links?.classList.contains('open') && !links.contains(event.target) && !toggle?.contains(event.target)) closeMenu(); });
window.addEventListener('resize', () => { if (window.innerWidth > 1050) closeMenu(); });

const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) { entry.target.classList.add('visible'); io.unobserve(entry.target); }
  }), {threshold:0.08,rootMargin:'0px 0px -24px 0px'});
  revealItems.forEach(el => io.observe(el));
} else revealItems.forEach(el => el.classList.add('visible'));
