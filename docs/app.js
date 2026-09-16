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

const grid = document.querySelector('#analysis-grid');
const search = document.querySelector('#analysis-search');
const count = document.querySelector('#analysis-count');
const filters = document.querySelector('#analysis-filters');
let activeCategory = 'Todos';

const categories = ['Todos', ...new Set(analyses.map(a => a.category))];

function renderFilters() {
  if (!filters) return;
  filters.innerHTML = categories.map(category => `
    <button type="button" class="filter-chip ${category === activeCategory ? 'active' : ''}" data-category="${category}" aria-pressed="${category === activeCategory}">${category}</button>
  `).join('');
  filters.querySelectorAll('.filter-chip').forEach(button => {
    button.addEventListener('click', () => {
      activeCategory = button.dataset.category || 'Todos';
      renderFilters();
      render();
    });
  });
}

function matches(item, query) {
  const q = query.trim().toLocaleLowerCase('es');
  const categoryOk = activeCategory === 'Todos' || item.category === activeCategory;
  const textOk = !q || `${item.name} ${item.category} ${item.tag} ${item.desc}`.toLocaleLowerCase('es').includes(q);
  return categoryOk && textOk;
}

function render() {
  if (!grid || !count) return;
  const query = search?.value || '';
  const items = analyses.filter(item => matches(item, query));
  grid.innerHTML = items.length
    ? items.map(item => `<article class="analysis-card reveal visible"><span class="tag">${item.tag}</span><h3>${item.name}</h3><p>${item.desc}</p></article>`).join('')
    : '<div class="empty-state" role="status"><strong>No encontramos coincidencias.</strong><br>Prueba otro término o cambia el filtro.</div>';
  count.textContent = `${items.length} ${items.length === 1 ? 'disponible' : 'disponibles'}`;
}

renderFilters();
render();
search?.addEventListener('input', render);
search?.addEventListener('keydown', event => {
  if (event.key === 'Escape' && search.value) {
    search.value = '';
    render();
  }
});

const toggle = document.querySelector('.menu-toggle');
const links = document.querySelector('#nav-links');
function closeMenu() {
  links?.classList.remove('open');
  toggle?.setAttribute('aria-expanded', 'false');
}

toggle?.addEventListener('click', () => {
  const open = links?.classList.toggle('open') ?? false;
  toggle.setAttribute('aria-expanded', String(open));
});
links?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') closeMenu();
  if ((event.ctrlKey || event.metaKey) && event.key.toLocaleLowerCase('es') === 'k') {
    event.preventDefault();
    search?.focus();
  }
});
document.addEventListener('click', event => {
  if (!links?.classList.contains('open')) return;
  if (links.contains(event.target) || toggle?.contains(event.target)) return;
  closeMenu();
});
window.addEventListener('resize', () => {
  if (window.innerWidth > 1050) closeMenu();
});

const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      io.unobserve(entry.target);
    }
  }), {threshold: 0.08, rootMargin: '0px 0px -24px 0px'});
  revealItems.forEach(el => io.observe(el));
} else {
  revealItems.forEach(el => el.classList.add('visible'));
}
