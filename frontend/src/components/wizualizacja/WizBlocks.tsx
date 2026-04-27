import React from "react";
// Biblioteka klocków do dodawania nowych sekcji w Wizualizacji
// Każdy klocek to HTML string który wstawiamy do DOM

const MIETOWA_C = {
  ink: '#1F2937', mint: '#6FAE8C', mintLight: '#A8D5BA',
  accent: '#C2410C', cream: '#FAF6EF', line: '#E7E5E0', muted: '#6B7280',
};

const BLOCKS = [
  {
    id: 'hero-center',
    cat: 'Hero',
    name: 'Hero wyśrodkowany',
    thumb: `<rect x="10" y="20" width="60" height="4" rx="2" fill="#6FAE8C"/><rect x="20" y="30" width="40" height="8" rx="1" fill="#1F2937"/><rect x="25" y="42" width="30" height="3" rx="1" fill="#94A3B8"/><rect x="30" y="50" width="20" height="5" rx="2" fill="#1F2937"/>`,
    html: () => `<section style="background:${MIETOWA_C.cream};padding:100px 0;text-align:center">
      <div style="max-width:760px;margin:0 auto;padding:0 32px">
        <div style="display:inline-block;padding:6px 14px;background:${MIETOWA_C.mintLight};color:#2F6F50;border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-family:Inter,sans-serif;margin-bottom:20px">Nowa sekcja</div>
        <h2 style="font-family:Fraunces,serif;font-size:56px;color:${MIETOWA_C.ink};margin:0 0 20px;line-height:1.05">Napisz swój nagłówek tutaj</h2>
        <p style="font-family:Inter,sans-serif;font-size:17px;color:${MIETOWA_C.muted};line-height:1.6;max-width:520px;margin:0 auto 32px">Krótki opis — powiedz odwiedzającym co tu znajdą i dlaczego warto zostać.</p>
        <button style="padding:13px 24px;background:${MIETOWA_C.ink};color:#fff;border:none;border-radius:8px;font-family:Inter,sans-serif;font-size:14px;font-weight:600;cursor:pointer">Zarezerwuj stolik</button>
      </div>
    </section>`,
  },
  {
    id: 'features-3',
    cat: 'Features',
    name: '3 kolumny — cechy',
    thumb: `<rect x="30" y="10" width="20" height="4" rx="1" fill="#1F2937"/><g fill="#E7E5E0"><rect x="6" y="24" width="20" height="30" rx="2"/><rect x="30" y="24" width="20" height="30" rx="2"/><rect x="54" y="24" width="20" height="30" rx="2"/></g>`,
    html: () => `<section style="background:#fff;padding:100px 0">
      <div style="max-width:1120px;margin:0 auto;padding:0 32px">
        <div style="text-align:center;margin-bottom:56px">
          <h2 style="font-family:Fraunces,serif;font-size:44px;color:${MIETOWA_C.ink};margin:0">Dlaczego my.</h2>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px">
          ${[1,2,3].map(i => `<div style="background:${MIETOWA_C.cream};padding:32px;border-radius:12px;border:1px solid ${MIETOWA_C.line}">
            <div style="width:44px;height:44px;border-radius:10px;background:${MIETOWA_C.mint};margin-bottom:16px"></div>
            <h3 style="font-family:Fraunces,serif;font-size:22px;color:${MIETOWA_C.ink};margin:0 0 10px">Tytuł ${i}</h3>
            <p style="font-family:Inter,sans-serif;font-size:15px;color:${MIETOWA_C.muted};line-height:1.6;margin:0">Krótki opis tego czym się wyróżniacie w tej konkretnej sprawie.</p>
          </div>`).join('')}
        </div>
      </div>
    </section>`,
  },
  {
    id: 'stats',
    cat: 'Liczby',
    name: 'Statystyki 4 kolumny',
    thumb: `<g font-family="Fraunces" font-size="12" fill="#1F2937" font-weight="600"><text x="15" y="30">12+</text><text x="35" y="30">4.9</text><text x="55" y="30">300+</text><text x="75" y="30">1k</text></g><g fill="#94A3B8" font-size="4"><text x="13" y="42">Lat</text><text x="35" y="42">Ocena</text><text x="54" y="42">Gości</text><text x="74" y="42">Kaw</text></g>`,
    html: () => `<section style="background:${MIETOWA_C.ink};padding:80px 0;color:#fff">
      <div style="max-width:1120px;margin:0 auto;padding:0 32px">
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:40px;text-align:center">
          ${[['12+','Lat działalności'],['4.9★','Ocena Google'],['300+','Gości dziennie'],['1000+','Kaw w tygodniu']].map(([n,l]) => `<div>
            <div style="font-family:Fraunces,serif;font-size:56px;color:${MIETOWA_C.mintLight};margin-bottom:6px;line-height:1">${n}</div>
            <div style="font-family:Inter,sans-serif;font-size:13px;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:.08em">${l}</div>
          </div>`).join('')}
        </div>
      </div>
    </section>`,
  },
  {
    id: 'cta-banner',
    cat: 'CTA',
    name: 'Baner CTA',
    thumb: `<rect x="8" y="15" width="64" height="40" rx="3" fill="#1F2937"/><rect x="20" y="25" width="40" height="4" rx="1" fill="#fff"/><rect x="28" y="40" width="24" height="5" rx="2" fill="#6FAE8C"/>`,
    html: () => `<section style="background:${MIETOWA_C.ink};padding:80px 0;text-align:center">
      <div style="max-width:720px;margin:0 auto;padding:0 32px">
        <h2 style="font-family:Fraunces,serif;font-size:48px;color:#fff;margin:0 0 16px">Gotowy żeby zacząć?</h2>
        <p style="font-family:Inter,sans-serif;font-size:16px;color:rgba(255,255,255,.7);margin:0 0 28px">Zarezerwuj stolik już teraz — odpowiadamy w 15 minut.</p>
        <button style="padding:14px 28px;background:${MIETOWA_C.mint};color:${MIETOWA_C.ink};border:none;border-radius:8px;font-family:Inter,sans-serif;font-size:15px;font-weight:600;cursor:pointer">Zarezerwuj</button>
      </div>
    </section>`,
  },
  {
    id: 'infographic-steps',
    cat: 'Infografika',
    name: 'Kroki 1-2-3-4',
    thumb: `<g><circle cx="15" cy="35" r="6" fill="#6FAE8C"/><circle cx="35" cy="35" r="6" fill="#6FAE8C"/><circle cx="55" cy="35" r="6" fill="#6FAE8C"/><circle cx="75" cy="35" r="6" fill="#6FAE8C"/><line x1="21" y1="35" x2="29" y2="35" stroke="#6FAE8C" stroke-width="1"/><line x1="41" y1="35" x2="49" y2="35" stroke="#6FAE8C" stroke-width="1"/><line x1="61" y1="35" x2="69" y2="35" stroke="#6FAE8C" stroke-width="1"/></g>`,
    html: () => `<section data-section-kind="infographic" style="background:#fff;padding:100px 0">
      <div style="max-width:1120px;margin:0 auto;padding:0 32px">
        <div style="text-align:center;margin-bottom:56px">
          <h2 style="font-family:Fraunces,serif;font-size:44px;color:${MIETOWA_C.ink};margin:0">Jak to działa</h2>
        </div>
        <div data-editable-infographic="steps" style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;position:relative">
          ${[['1','Zadzwoń','Albo napisz'],['2','Zarezerwuj','Wybierz godzinę'],['3','Przyjdź','Stolik czeka'],['4','Ciesz się','Kawa i spokój']].map(([n,t,d]) => `<div data-infographic-item="true" style="text-align:center;position:relative">
            <div data-infographic-circle="true" style="width:64px;height:64px;border-radius:50%;background:${MIETOWA_C.mint};color:#fff;display:grid;place-items:center;font-family:Fraunces,serif;font-size:28px;margin:0 auto 16px;position:relative;z-index:2">${n}</div>
            <h3 style="font-family:Fraunces,serif;font-size:20px;color:${MIETOWA_C.ink};margin:0 0 6px">${t}</h3>
            <p style="font-family:Inter,sans-serif;font-size:14px;color:${MIETOWA_C.muted};margin:0">${d}</p>
          </div>`).join('')}
          <div data-infographic-line="true" style="position:absolute;top:32px;left:12.5%;right:12.5%;height:2px;background:${MIETOWA_C.mintLight};z-index:1"></div>
        </div>
      </div>
    </section>`,
  },
  {
    id: 'infographic-circular',
    cat: 'Infografika',
    name: 'Okręgi z ikoną',
    thumb: `<g fill="#FAF6EF" stroke="#6FAE8C" stroke-width="1.5"><circle cx="25" cy="35" r="10"/><circle cx="55" cy="35" r="10"/></g><g fill="#6FAE8C" font-family="Inter" font-size="8" font-weight="700" text-anchor="middle"><text x="25" y="38">A</text><text x="55" y="38">B</text></g>`,
    html: () => `<section data-section-kind="infographic" style="background:${MIETOWA_C.cream};padding:100px 0">
      <div style="max-width:1120px;margin:0 auto;padding:0 32px">
        <div style="text-align:center;margin-bottom:56px">
          <h2 style="font-family:Fraunces,serif;font-size:44px;color:${MIETOWA_C.ink};margin:0">Dwie filozofie</h2>
        </div>
        <div data-editable-infographic="circles" style="display:grid;grid-template-columns:repeat(3,1fr);gap:32px">
          ${[['Rzemiosło','Każda kawa parzona ręcznie'],['Pochodzenie','Tylko świeży wypał'],['Rytm','Kawiarnia bez pośpiechu']].map(([t,d]) => `<div data-infographic-item="true" style="background:#fff;padding:40px 28px;border-radius:16px;text-align:center;border:1px solid ${MIETOWA_C.line}">
            <div data-infographic-circle="true" style="width:88px;height:88px;border-radius:50%;background:${MIETOWA_C.mintLight};margin:0 auto 20px;display:grid;place-items:center;color:${MIETOWA_C.ink};font-family:Fraunces,serif;font-size:36px">${t[0]}</div>
            <h3 style="font-family:Fraunces,serif;font-size:22px;color:${MIETOWA_C.ink};margin:0 0 8px">${t}</h3>
            <p style="font-family:Inter,sans-serif;font-size:14px;color:${MIETOWA_C.muted};margin:0">${d}</p>
          </div>`).join('')}
        </div>
      </div>
    </section>`,
  },
  {
    id: 'infographic-bars',
    cat: 'Infografika',
    name: 'Wykres słupkowy',
    thumb: `<g fill="#6FAE8C"><rect x="15" y="45" width="8" height="12"/><rect x="28" y="35" width="8" height="22"/><rect x="41" y="25" width="8" height="32"/><rect x="54" y="30" width="8" height="27"/><rect x="67" y="20" width="8" height="37"/></g>`,
    html: () => `<section data-section-kind="infographic" style="background:#fff;padding:100px 0">
      <div style="max-width:960px;margin:0 auto;padding:0 32px">
        <div style="text-align:center;margin-bottom:56px">
          <h2 style="font-family:Fraunces,serif;font-size:44px;color:${MIETOWA_C.ink};margin:0 0 12px">Rytm tygodnia</h2>
          <p style="font-family:Inter,sans-serif;font-size:15px;color:${MIETOWA_C.muted};margin:0">Średnia liczba gości dziennie</p>
        </div>
        <div data-editable-infographic="bars" style="display:flex;gap:24px;align-items:end;justify-content:center;height:260px;padding:0 20px">
          ${[['Pn',60],['Wt',55],['Śr',70],['Cz',75],['Pt',95],['So',100],['Nd',80]].map(([d,h]) => `<div data-infographic-item="true" style="flex:1;display:flex;flex-direction:column;align-items:center;gap:10px;height:100%;justify-content:flex-end">
            <div style="font-family:Fraunces,serif;font-size:14px;color:${MIETOWA_C.ink};font-weight:600">${h*3}</div>
            <div data-infographic-bar="true" style="width:100%;max-width:50px;height:${h}%;background:${MIETOWA_C.mint};border-radius:6px 6px 0 0"></div>
            <div style="font-family:Inter,sans-serif;font-size:13px;color:${MIETOWA_C.muted}">${d}</div>
          </div>`).join('')}
        </div>
      </div>
    </section>`,
  },
  {
    id: 'testimonials-3',
    cat: 'Opinie',
    name: '3 opinie',
    thumb: `<g fill="#fff" stroke="#E7E5E0"><rect x="6" y="15" width="20" height="35" rx="2"/><rect x="30" y="15" width="20" height="35" rx="2"/><rect x="54" y="15" width="20" height="35" rx="2"/></g><g fill="#E0A84F"><circle cx="14" cy="22" r="1.5"/><circle cx="18" cy="22" r="1.5"/></g>`,
    html: () => `<section style="background:${MIETOWA_C.cream};padding:100px 0">
      <div style="max-width:1120px;margin:0 auto;padding:0 32px">
        <div style="text-align:center;margin-bottom:56px">
          <h2 style="font-family:Fraunces,serif;font-size:44px;color:${MIETOWA_C.ink};margin:0">Opinie gości</h2>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:28px">
          ${[1,2,3].map(() => `<div data-component="testimonial" style="background:#fff;padding:32px;border-radius:12px;border:1px solid ${MIETOWA_C.line}">
            <div style="color:#E0A84F;margin-bottom:14px">★★★★★</div>
            <p style="font-family:Inter,sans-serif;font-size:15px;color:${MIETOWA_C.ink};line-height:1.6;margin:0 0 20px">„Świetna kawa, miła atmosfera, z chęcią wrócę."</p>
            <div style="display:flex;gap:12px;align-items:center">
              <div style="width:40px;height:40px;border-radius:50%;background:${MIETOWA_C.mintLight}"></div>
              <div>
                <div style="font-family:Inter,sans-serif;font-size:14px;font-weight:600;color:${MIETOWA_C.ink}">Imię Nazwisko</div>
                <div style="font-family:Inter,sans-serif;font-size:12px;color:${MIETOWA_C.muted}">Klient od 2023</div>
              </div>
            </div>
          </div>`).join('')}
        </div>
      </div>
    </section>`,
  },
  {
    id: 'form-simple',
    cat: 'Formularz',
    name: 'Formularz kontaktowy',
    thumb: `<rect x="18" y="12" width="44" height="46" rx="3" fill="#FAF6EF" stroke="#E7E5E0"/><rect x="23" y="20" width="34" height="4" rx="1" fill="#fff" stroke="#E7E5E0"/><rect x="23" y="28" width="34" height="4" rx="1" fill="#fff" stroke="#E7E5E0"/><rect x="23" y="36" width="34" height="10" rx="1" fill="#fff" stroke="#E7E5E0"/><rect x="23" y="49" width="18" height="5" rx="1" fill="#1F2937"/>`,
    html: () => `<section style="background:#fff;padding:100px 0">
      <div style="max-width:560px;margin:0 auto;padding:0 32px">
        <div style="text-align:center;margin-bottom:40px">
          <h2 style="font-family:Fraunces,serif;font-size:40px;color:${MIETOWA_C.ink};margin:0 0 12px">Napisz do nas</h2>
          <p style="font-family:Inter,sans-serif;font-size:15px;color:${MIETOWA_C.muted};margin:0">Odpowiadamy w 24h</p>
        </div>
        <div data-component="form" style="background:${MIETOWA_C.cream};padding:32px;border-radius:12px;border:1px solid ${MIETOWA_C.line}">
          ${[['Imię','Jan Kowalski'],['Email','jan@mail.pl'],['Telefon','+48 601 234 567']].map(([l,v]) => `<div style="margin-bottom:14px">
            <div style="font-family:Inter,sans-serif;font-size:12px;color:${MIETOWA_C.muted};margin-bottom:5px">${l}</div>
            <div data-form-field="true" style="padding:11px 14px;background:#fff;border:1px solid ${MIETOWA_C.line};border-radius:8px;font-family:Inter,sans-serif;font-size:14px;color:${MIETOWA_C.ink}">${v}</div>
          </div>`).join('')}
          <div style="margin-bottom:14px">
            <div style="font-family:Inter,sans-serif;font-size:12px;color:${MIETOWA_C.muted};margin-bottom:5px">Wiadomość</div>
            <div data-form-field="true" style="padding:11px 14px;background:#fff;border:1px solid ${MIETOWA_C.line};border-radius:8px;font-family:Inter,sans-serif;font-size:14px;color:${MIETOWA_C.ink};min-height:80px">Treść wiadomości…</div>
          </div>
          <button style="width:100%;padding:13px;background:${MIETOWA_C.ink};color:#fff;border:none;border-radius:8px;font-family:Inter,sans-serif;font-size:14px;font-weight:600;cursor:pointer">Wyślij</button>
        </div>
      </div>
    </section>`,
  },
  {
    id: 'gallery-4',
    cat: 'Galeria',
    name: 'Galeria 4 zdjęcia',
    thumb: `<g fill="#A8D5BA"><rect x="6" y="18" width="18" height="18" rx="2"/><rect x="27" y="18" width="18" height="18" rx="2"/><rect x="48" y="18" width="18" height="18" rx="2"/><rect x="69" y="18" width="18" height="18" rx="2"/></g>`,
    html: () => `<section style="background:#fff;padding:100px 0">
      <div style="max-width:1120px;margin:0 auto;padding:0 32px">
        <div style="text-align:center;margin-bottom:40px">
          <h2 style="font-family:Fraunces,serif;font-size:40px;color:${MIETOWA_C.ink};margin:0">Kadry z miejsca</h2>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
          ${[1,2,3,4].map(() => `<div style="aspect-ratio:1;background:${MIETOWA_C.mintLight};border-radius:10px;display:grid;place-items:center;color:${MIETOWA_C.ink};font-family:Inter,sans-serif;font-size:12px">Zdjęcie</div>`).join('')}
        </div>
      </div>
    </section>`,
  },
  {
    id: 'split-image-text',
    cat: 'Split',
    name: 'Zdjęcie + tekst',
    thumb: `<rect x="6" y="15" width="35" height="40" rx="2" fill="#A8D5BA"/><g fill="#1F2937"><rect x="46" y="20" width="30" height="4" rx="1"/><rect x="46" y="28" width="25" height="3" rx="1" fill="#94A3B8"/><rect x="46" y="34" width="28" height="3" rx="1" fill="#94A3B8"/><rect x="46" y="45" width="15" height="4" rx="1"/></g>`,
    html: () => `<section style="background:#fff;padding:100px 0">
      <div style="max-width:1120px;margin:0 auto;padding:0 32px;display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center">
        <div style="aspect-ratio:4/5;background:${MIETOWA_C.mintLight};border-radius:12px"></div>
        <div>
          <div style="display:inline-block;padding:6px 12px;background:${MIETOWA_C.cream};color:${MIETOWA_C.accent};border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;font-family:Inter,sans-serif;margin-bottom:16px">Historia</div>
          <h2 style="font-family:Fraunces,serif;font-size:44px;color:${MIETOWA_C.ink};margin:0 0 20px;line-height:1.1">Tytuł sekcji z historią</h2>
          <p style="font-family:Inter,sans-serif;font-size:16px;color:${MIETOWA_C.muted};line-height:1.7;margin:0 0 24px">Dwa, trzy zdania o tym o czym jest ta sekcja. Opowiedz historię, wartości, albo konkretną cechę produktu.</p>
          <button style="padding:12px 22px;background:${MIETOWA_C.ink};color:#fff;border:none;border-radius:8px;font-family:Inter,sans-serif;font-size:14px;font-weight:600;cursor:pointer">Dowiedz się więcej</button>
        </div>
      </div>
    </section>`,
  },
];

export { BLOCKS as WizBlocks };

// Modal wyboru klocka
function WizBlocksModal({ open, onClose, onPick }) {
  const [cat, setCat] = React.useState('all');
  if (!open) return null;
  const cats = ['all', ...new Set(BLOCKS.map(b => b.cat))];
  const filtered = cat === 'all' ? BLOCKS : BLOCKS.filter(b => b.cat === cat);
  return (
    <div onClick={onClose} data-no-edit
      style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,.5)', backdropFilter: 'blur(4px)', zIndex: 10000, display: 'grid', placeItems: 'center', padding: 32 }}>
      <div onClick={e => e.stopPropagation()}
        style={{ background: '#fff', borderRadius: 16, maxWidth: 1000, width: '100%', maxHeight: '85vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', fontFamily: 'Inter, sans-serif' }}>
        <div style={{ padding: '20px 28px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: '#0F172A' }}>Dodaj sekcję</h2>
            <div style={{ fontSize: 13, color: '#64748B', marginTop: 2 }}>Wybierz gotowy klocek — potem edytuj go w locie.</div>
          </div>
          <button onClick={onClose} style={{ width: 32, height: 32, border: '1px solid #E2E8F0', background: '#fff', borderRadius: 8, cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div style={{ padding: '12px 28px', borderBottom: '1px solid #E2E8F0', display: 'flex', gap: 6, overflowX: 'auto' }}>
          {cats.map(c => (
            <button key={c} onClick={() => setCat(c)}
              style={{
                padding: '6px 14px', border: '1px solid', borderColor: cat === c ? '#0F172A' : '#E2E8F0',
                background: cat === c ? '#0F172A' : '#fff', color: cat === c ? '#fff' : '#334155',
                borderRadius: 999, cursor: 'pointer', fontSize: 13, fontWeight: 500, fontFamily: 'inherit', whiteSpace: 'nowrap',
              }}>{c === 'all' ? 'Wszystkie' : c}</button>
          ))}
        </div>
        <div style={{ padding: 28, overflowY: 'auto', flex: 1, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          {filtered.map(b => (
            <button key={b.id} onClick={() => { onPick(b); onClose(); }}
              style={{
                border: '1px solid #E2E8F0', background: '#fff', borderRadius: 12, padding: 0, cursor: 'pointer',
                fontFamily: 'inherit', textAlign: 'left', transition: 'all .15s', overflow: 'hidden',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.boxShadow = '0 4px 16px rgba(99,102,241,.15)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.boxShadow = 'none'; }}>
              <div style={{ height: 140, background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', display: 'grid', placeItems: 'center' }}>
                <svg width="180" height="110" viewBox="0 0 80 70" xmlns="http://www.w3.org/2000/svg" dangerouslySetInnerHTML={{ __html: b.thumb }}/>
              </div>
              <div style={{ padding: 14 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>{b.cat}</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#0F172A' }}>{b.name}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export { WizBlocksModal };

// Wstawianie klocka po podanej sekcji
export function wizInsertBlockAfter(sectionEl, block) {
  if (!sectionEl || !block) return;
  const wrap = document.createElement('div');
  wrap.innerHTML = block.html().trim();
  const newSec = wrap.firstElementChild;
  if (!newSec) return;
  sectionEl.parentNode.insertBefore(newSec, sectionEl.nextSibling);
  // Highlight bez scrollIntoView — znajdź scrollowalny kontener i przewiń ręcznie
  try {
    let scroller = newSec.parentElement;
    while (scroller && scroller !== document.body) {
      const cs = getComputedStyle(scroller);
      if (/(auto|scroll)/.test(cs.overflowY)) break;
      scroller = scroller.parentElement;
    }
    if (scroller && scroller !== document.body) {
      const secRect = newSec.getBoundingClientRect();
      const scRect = scroller.getBoundingClientRect();
      const offset = secRect.top - scRect.top + scroller.scrollTop - 80;
      scroller.scrollTo({ top: Math.max(0, offset), behavior: 'smooth' });
    }
  } catch {}
  newSec.style.outline = '3px solid #6366F1';
  newSec.style.outlineOffset = '-6px';
  setTimeout(() => { newSec.style.outline = ''; newSec.style.outlineOffset = ''; }, 1400);
};
