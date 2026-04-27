import React from "react";
// wiz_gallery.jsx — Galeria Infografik (modal)
// 4 kategorie aktywne (po 4-6 szablonów), 3 kategorie disabled (produkcja)
// Każdy szablon to funkcja zwracająca HTML string z data-atrybutami
// kompatybilnymi z toolbarem (data-editable-infographic, data-infographic-item,
// data-infographic-circle, data-infographic-line).
//
// UŻYCIE: window.openInfographicGallery({ onPick: (html) => ... })
//        — otwiera modal, po wyborze woła onPick(htmlString)
//
// UWAGA: Kolory są brane z CSS var --mint / --ink / --cream jeśli są;
// inaczej fallback do stałych. Szablony używają placeholderów {{mint}} itp.
// które Gallery podmienia przed wstawieniem.

const { useState, useMemo } = React;

// ====== PALETA DOPASOWANA DO BRANDU (Miętowa) ======
const GALLERY_PALETTE = {
  mint: '#6FAE8C',
  mintLight: '#C8DDCE',
  mintDark: '#4A8268',
  cream: '#FAF6EF',
  ink: '#2D3A33',
  muted: '#6B7770',
  line: '#E7E5E0',
  accent: '#E0A84F',
  white: '#fff',
};

// Helper: zamienia placeholdery w szablonie
const apply = (tpl) => tpl
  .replaceAll('{{mint}}', GALLERY_PALETTE.mint)
  .replaceAll('{{mintLight}}', GALLERY_PALETTE.mintLight)
  .replaceAll('{{mintDark}}', GALLERY_PALETTE.mintDark)
  .replaceAll('{{cream}}', GALLERY_PALETTE.cream)
  .replaceAll('{{ink}}', GALLERY_PALETTE.ink)
  .replaceAll('{{muted}}', GALLERY_PALETTE.muted)
  .replaceAll('{{line}}', GALLERY_PALETTE.line)
  .replaceAll('{{accent}}', GALLERY_PALETTE.accent);

// ====== SZABLONY ======
// Każdy: { id, name, preview (SVG inline), html (funkcja → string) }

// --- PROCESY (strzałki poziome) ---
const PROCESSES = [
  {
    id: 'proc-arrows-5',
    name: 'Strzałki poziome 5 kroków',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      ${[0,1,2,3,4].map(i => {
        const x = 8 + i*38;
        const color = ['#6FAE8C','#E0A84F','#8B9CC4','#C47B6D','#6B7770'][i];
        return `<path d="M${x} 25 L${x+28} 25 L${x+34} 40 L${x+28} 55 L${x} 55 L${x+6} 40 Z" fill="${color}"/><text x="${x+17}" y="44" text-anchor="middle" fill="white" font-size="11" font-weight="700" font-family="Inter">${i+1}</text>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="arrows5" style="display:flex;gap:0;padding:40px 0;align-items:center;justify-content:center">
      ${['Odkrywanie','Planowanie','Projektowanie','Wdrożenie','Rozwój'].map((t, i) => {
        const colors = ['{{mint}}','{{accent}}','#8B9CC4','#C47B6D','{{mintDark}}'];
        return `<div data-infographic-item="true" style="position:relative;flex:1;max-width:180px;background:${colors[i]};color:#fff;padding:28px 20px 28px 40px;clip-path:polygon(0 0,calc(100% - 20px) 0,100% 50%,calc(100% - 20px) 100%,0 100%,20px 50%);margin-right:-12px">
          <div data-infographic-circle="true" style="font-family:Fraunces,serif;font-size:32px;font-weight:700;line-height:1;margin-bottom:6px">${i+1}</div>
          <div style="font-family:Inter,sans-serif;font-size:13px;font-weight:600;line-height:1.3">${t}</div>
        </div>`;
      }).join('')}
    </div>`),
  },
  {
    id: 'proc-arrows-3',
    name: 'Strzałki 3 kroki (duże)',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      ${[0,1,2].map(i => {
        const x = 10 + i*60;
        const color = ['#6FAE8C','#E0A84F','#C47B6D'][i];
        return `<path d="M${x} 20 L${x+48} 20 L${x+58} 40 L${x+48} 60 L${x} 60 L${x+10} 40 Z" fill="${color}"/><text x="${x+29}" y="45" text-anchor="middle" fill="white" font-size="14" font-weight="700" font-family="Inter">${i+1}</text>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="arrows3" style="display:flex;gap:0;padding:40px 0;align-items:center;justify-content:center">
      ${['Zamów','Przygotowujemy','Smakujesz'].map((t, i) => {
        const colors = ['{{mint}}','{{accent}}','#C47B6D'];
        return `<div data-infographic-item="true" style="position:relative;flex:1;max-width:260px;background:${colors[i]};color:#fff;padding:40px 28px 40px 56px;clip-path:polygon(0 0,calc(100% - 28px) 0,100% 50%,calc(100% - 28px) 100%,0 100%,28px 50%);margin-right:-16px">
          <div data-infographic-circle="true" style="font-family:Fraunces,serif;font-size:48px;font-weight:700;line-height:1;margin-bottom:12px">${i+1}</div>
          <h3 style="font-family:Fraunces,serif;font-size:22px;margin:0 0 6px;font-weight:600">${t}</h3>
          <p style="font-family:Inter,sans-serif;font-size:13px;margin:0;opacity:.85;line-height:1.4">Krótki opis etapu</p>
        </div>`;
      }).join('')}
    </div>`),
  },
  {
    id: 'proc-dots-4',
    name: 'Linia czasu 4 punkty',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <line x1="20" y1="40" x2="180" y2="40" stroke="#6FAE8C" stroke-width="2"/>
      ${[0,1,2,3].map(i => {
        const x = 28 + i*48;
        return `<circle cx="${x}" cy="40" r="10" fill="#6FAE8C"/><text x="${x}" y="44" text-anchor="middle" fill="white" font-size="10" font-weight="700" font-family="Inter">${i+1}</text>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="timeline4" style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;position:relative;padding:40px 0">
      ${['Etap 1','Etap 2','Etap 3','Etap 4'].map((t, i) => `<div data-infographic-item="true" style="text-align:center;position:relative">
        <div data-infographic-circle="true" style="width:56px;height:56px;border-radius:50%;background:{{mint}};color:#fff;display:grid;place-items:center;font-family:Fraunces,serif;font-size:24px;margin:0 auto 16px;position:relative;z-index:2">${i+1}</div>
        <h3 style="font-family:Fraunces,serif;font-size:18px;color:{{ink}};margin:0 0 6px">${t}</h3>
        <p style="font-family:Inter,sans-serif;font-size:13px;color:{{muted}};margin:0">Krótki opis</p>
      </div>`).join('')}
      <div data-infographic-line="true" style="position:absolute;top:68px;left:12.5%;right:12.5%;height:2px;background:{{mintLight}};z-index:1"></div>
    </div>`),
  },
  {
    id: 'proc-chevrons',
    name: 'Chevrony wypełnione',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      ${[0,1,2,3].map(i => {
        const x = 10 + i*46;
        const color = ['#C8DDCE','#98C3AA','#6FAE8C','#4A8268'][i];
        return `<path d="M${x} 25 L${x+36} 25 L${x+44} 40 L${x+36} 55 L${x} 55 Z" fill="${color}"/>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="chevrons" style="display:flex;gap:4px;padding:40px 0;align-items:stretch;justify-content:center">
      ${['Analiza','Koncept','Produkcja','Launch'].map((t, i) => {
        const colors = ['{{mintLight}}','#98C3AA','{{mint}}','{{mintDark}}'];
        const textColor = i < 2 ? '{{ink}}' : '#fff';
        return `<div data-infographic-item="true" style="position:relative;flex:1;max-width:200px;background:${colors[i]};color:${textColor.replace('{{ink}}','#2D3A33')};padding:32px 24px 32px 44px;clip-path:polygon(0 0,calc(100% - 16px) 0,100% 50%,calc(100% - 16px) 100%,0 100%)">
          <div style="font-family:Inter,sans-serif;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;opacity:.7;margin-bottom:8px">Faza ${i+1}</div>
          <h3 style="font-family:Fraunces,serif;font-size:20px;margin:0">${t}</h3>
        </div>`;
      }).join('')}
    </div>`),
  },
];

// --- KOŁOWE (segmenty, koncentryczne) ---
const CIRCULAR = [
  {
    id: 'circ-pie-4',
    name: 'Diagram kołowy 4 segmenty',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <g transform="translate(100,40)">
        <path d="M0,-30 A30,30 0 0,1 30,0 L0,0 Z" fill="#6FAE8C"/>
        <path d="M30,0 A30,30 0 0,1 0,30 L0,0 Z" fill="#E0A84F"/>
        <path d="M0,30 A30,30 0 0,1 -30,0 L0,0 Z" fill="#C47B6D"/>
        <path d="M-30,0 A30,30 0 0,1 0,-30 L0,0 Z" fill="#8B9CC4"/>
      </g>
    </svg>`,
    html: () => apply(`<div data-editable-infographic="pie4" style="display:grid;grid-template-columns:280px 1fr;gap:56px;align-items:center;padding:40px 0;max-width:720px;margin:0 auto">
      <div style="position:relative;width:280px;height:280px">
        <svg viewBox="0 0 100 100" style="width:100%;height:100%;transform:rotate(-90deg)">
          <circle cx="50" cy="50" r="40" fill="transparent" stroke="{{mint}}" stroke-width="20" stroke-dasharray="62.8 251.2"/>
          <circle cx="50" cy="50" r="40" fill="transparent" stroke="{{accent}}" stroke-width="20" stroke-dasharray="62.8 251.2" stroke-dashoffset="-62.8"/>
          <circle cx="50" cy="50" r="40" fill="transparent" stroke="#C47B6D" stroke-width="20" stroke-dasharray="62.8 251.2" stroke-dashoffset="-125.6"/>
          <circle cx="50" cy="50" r="40" fill="transparent" stroke="#8B9CC4" stroke-width="20" stroke-dasharray="62.8 251.2" stroke-dashoffset="-188.4"/>
        </svg>
      </div>
      <div style="display:grid;gap:16px">
        ${[['{{mint}}','Kawa','25%'],['{{accent}}','Śniadania','25%'],['#C47B6D','Obiady','25%'],['#8B9CC4','Desery','25%']].map(([c,t,p]) => `<div data-infographic-item="true" style="display:flex;align-items:center;gap:14px">
          <div data-infographic-circle="true" style="width:16px;height:16px;border-radius:4px;background:${c};flex-shrink:0"></div>
          <div style="flex:1"><div style="font-family:Fraunces,serif;font-size:18px;color:{{ink}};font-weight:600">${t}</div></div>
          <div style="font-family:Fraunces,serif;font-size:20px;color:{{ink}};font-weight:600">${p}</div>
        </div>`).join('')}
      </div>
    </div>`),
  },
  {
    id: 'circ-concentric',
    name: 'Koła koncentryczne',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <circle cx="100" cy="40" r="30" fill="none" stroke="#C8DDCE" stroke-width="6"/>
      <circle cx="100" cy="40" r="22" fill="none" stroke="#6FAE8C" stroke-width="6"/>
      <circle cx="100" cy="40" r="14" fill="none" stroke="#4A8268" stroke-width="6"/>
      <circle cx="100" cy="40" r="6" fill="#2D3A33"/>
    </svg>`,
    html: () => apply(`<div data-editable-infographic="concentric" style="display:grid;grid-template-columns:320px 1fr;gap:56px;align-items:center;padding:40px 0;max-width:820px;margin:0 auto">
      <div style="position:relative;width:320px;height:320px;display:grid;place-items:center">
        <div data-infographic-circle="true" style="position:absolute;width:320px;height:320px;border-radius:50%;background:{{mintLight}};display:grid;place-items:start center;padding-top:28px;font-family:Fraunces,serif;font-size:14px;color:{{ink}};font-weight:600">Społeczność</div>
        <div data-infographic-circle="true" style="position:absolute;width:220px;height:220px;border-radius:50%;background:{{mint}};display:grid;place-items:start center;padding-top:22px;font-family:Fraunces,serif;font-size:14px;color:#fff;font-weight:600">Goście</div>
        <div data-infographic-circle="true" style="position:absolute;width:130px;height:130px;border-radius:50%;background:{{mintDark}};display:grid;place-items:start center;padding-top:16px;font-family:Fraunces,serif;font-size:14px;color:#fff;font-weight:600">Stali</div>
        <div data-infographic-circle="true" style="position:absolute;width:60px;height:60px;border-radius:50%;background:{{ink}};display:grid;place-items:center;font-family:Fraunces,serif;font-size:14px;color:#fff;font-weight:700">Ty</div>
      </div>
      <div style="display:grid;gap:16px">
        ${[['{{ink}}','Ty — rdzeń'],['{{mintDark}}','Stali goście'],['{{mint}}','Wszyscy goście'],['{{mintLight}}','Społeczność lokalna']].map(([c,t]) => `<div data-infographic-item="true" style="display:flex;align-items:center;gap:14px">
          <div style="width:16px;height:16px;border-radius:4px;background:${c};flex-shrink:0"></div>
          <div style="font-family:Inter,sans-serif;font-size:15px;color:{{ink}}">${t}</div>
        </div>`).join('')}
      </div>
    </div>`),
  },
  {
    id: 'circ-progress',
    name: 'Koła z procentem',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      ${[0,1,2].map(i => {
        const cx = 40 + i*60;
        return `<circle cx="${cx}" cy="40" r="18" fill="none" stroke="#E7E5E0" stroke-width="4"/><circle cx="${cx}" cy="40" r="18" fill="none" stroke="#6FAE8C" stroke-width="4" stroke-dasharray="${80+i*10} 113" transform="rotate(-90 ${cx} 40)"/><text x="${cx}" y="44" text-anchor="middle" font-family="Inter" font-size="11" font-weight="700" fill="#2D3A33">${[70,80,90][i]}%</text>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="circProgress" style="display:grid;grid-template-columns:repeat(3,1fr);gap:40px;padding:40px 0;max-width:820px;margin:0 auto">
      ${[['Zadowolenie','92'],['Powroty','78'],['Poleceni','85']].map(([t,p]) => `<div data-infographic-item="true" style="text-align:center">
        <div style="position:relative;width:140px;height:140px;margin:0 auto 16px">
          <svg data-infographic-circle="true" viewBox="0 0 100 100" style="width:100%;height:100%;transform:rotate(-90deg);border-radius:50%">
            <circle cx="50" cy="50" r="42" fill="none" stroke="{{mintLight}}" stroke-width="8"/>
            <circle cx="50" cy="50" r="42" fill="none" stroke="{{mint}}" stroke-width="8" stroke-dasharray="${p*2.64} 264" stroke-linecap="round"/>
          </svg>
          <div style="position:absolute;inset:0;display:grid;place-items:center;font-family:Fraunces,serif;font-size:32px;color:{{ink}};font-weight:600">${p}%</div>
        </div>
        <h3 style="font-family:Fraunces,serif;font-size:20px;color:{{ink}};margin:0">${t}</h3>
      </div>`).join('')}
    </div>`),
  },
  {
    id: 'circ-hub',
    name: 'Hub centralny + satelity',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <circle cx="100" cy="40" r="14" fill="#6FAE8C"/>
      ${[0,1,2,3].map(i => {
        const angle = (i*90 - 45) * Math.PI/180;
        const x = 100 + Math.cos(angle)*30;
        const y = 40 + Math.sin(angle)*22;
        return `<line x1="100" y1="40" x2="${x}" y2="${y}" stroke="#C8DDCE" stroke-width="1.5"/><circle cx="${x}" cy="${y}" r="6" fill="#E0A84F"/>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="hub" style="position:relative;width:480px;height:480px;margin:40px auto">
      <div data-infographic-circle="true" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:140px;height:140px;border-radius:50%;background:{{mint}};color:#fff;display:grid;place-items:center;font-family:Fraunces,serif;font-size:22px;font-weight:600;text-align:center;z-index:2">Kawiarnia Miętowa</div>
      ${['Kawa','Śniadania','Obiady','Desery'].map((t, i) => {
        const angle = (i*90 - 45) * Math.PI/180;
        const r = 170;
        const x = 240 + Math.cos(angle)*r;
        const y = 240 + Math.sin(angle)*r;
        return `<div data-infographic-item="true" style="position:absolute;left:${x}px;top:${y}px;transform:translate(-50%,-50%);width:100px;height:100px;border-radius:50%;background:{{cream}};border:2px solid {{mint}};display:grid;place-items:center;font-family:Fraunces,serif;font-size:15px;color:{{ink}};font-weight:600;text-align:center;z-index:2">${t}</div>
        <div data-infographic-line="true" style="position:absolute;left:50%;top:50%;width:${r-50}px;height:2px;background:{{mintLight}};transform-origin:0 50%;transform:translateY(-50%) rotate(${i*90 - 45}deg);z-index:1"></div>`;
      }).join('')}
    </div>`),
  },
];

// --- PIRAMIDY / HIERARCHIE ---
const PYRAMIDS = [
  {
    id: 'pyr-3',
    name: 'Piramida 3-poziomowa',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <polygon points="100,10 150,60 50,60" fill="#C8DDCE"/>
      <polygon points="100,10 128,38 72,38" fill="#6FAE8C"/>
      <polygon points="100,10 110,22 90,22" fill="#4A8268"/>
    </svg>`,
    html: () => apply(`<div data-editable-infographic="pyramid3" style="display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center;padding:40px 0;max-width:880px;margin:0 auto">
      <div data-infographic-container-visual="true" style="display:flex;flex-direction:column;align-items:center;gap:2px">
        <div data-infographic-item="true" style="width:140px;height:60px;background:{{mintDark}};color:#fff;display:grid;place-items:center;font-family:Fraunces,serif;font-size:16px;clip-path:polygon(50% 0,100% 100%,0 100%);font-weight:600">Wizja</div>
        <div data-infographic-item="true" style="width:240px;height:60px;background:{{mint}};color:#fff;display:grid;place-items:center;font-family:Fraunces,serif;font-size:16px;clip-path:polygon(22% 0,78% 0,100% 100%,0 100%);font-weight:600">Strategia</div>
        <div data-infographic-item="true" style="width:340px;height:60px;background:{{mintLight}};color:{{ink}};display:grid;place-items:center;font-family:Fraunces,serif;font-size:16px;clip-path:polygon(15% 0,85% 0,100% 100%,0 100%);font-weight:600">Codzienność</div>
      </div>
      <div style="display:grid;gap:20px">
        ${[['Wizja','Dokąd zmierzamy'],['Strategia','Jak tam dotrzeć'],['Codzienność','Co robimy każdego dnia']].map(([t,d]) => `<div data-infographic-item="true">
          <h3 style="font-family:Fraunces,serif;font-size:20px;color:{{ink}};margin:0 0 4px">${t}</h3>
          <p style="font-family:Inter,sans-serif;font-size:14px;color:{{muted}};margin:0">${d}</p>
        </div>`).join('')}
      </div>
    </div>`),
  },
  {
    id: 'pyr-4',
    name: 'Piramida 4-poziomowa',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <polygon points="100,5 170,70 30,70" fill="#C8DDCE" stroke="#fff" stroke-width="1.5"/>
      <polygon points="100,5 150,50 50,50" fill="#98C3AA" stroke="#fff" stroke-width="1.5"/>
      <polygon points="100,5 130,35 70,35" fill="#6FAE8C" stroke="#fff" stroke-width="1.5"/>
      <polygon points="100,5 112,20 88,20" fill="#4A8268"/>
    </svg>`,
    html: () => apply(`<div data-editable-infographic="pyramid4" style="padding:40px 0;max-width:720px;margin:0 auto">
      <div data-infographic-container-visual="true" style="display:flex;flex-direction:column;align-items:center;gap:4px">
        ${[
          ['Mistrzostwo','{{mintDark}}','#fff',160,50],
          ['Zaangażowanie','{{mint}}','#fff',260,50],
          ['Wiedza','#98C3AA','{{ink}}',360,50],
          ['Fundament','{{mintLight}}','{{ink}}',460,50],
        ].map(([t,bg,tc,w,h]) => `<div data-infographic-item="true" style="width:${w}px;height:${h}px;background:${bg};color:${tc};display:grid;place-items:center;font-family:Fraunces,serif;font-size:16px;clip-path:polygon(10% 0,90% 0,100% 100%,0 100%);font-weight:600">${t}</div>`).join('')}
      </div>
    </div>`),
  },
  {
    id: 'pyr-inverted',
    name: 'Lejek konwersji',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <polygon points="30,15 170,15 140,35 60,35" fill="#C8DDCE"/>
      <polygon points="60,35 140,35 120,55 80,55" fill="#6FAE8C"/>
      <polygon points="80,55 120,55 105,70 95,70" fill="#4A8268"/>
    </svg>`,
    html: () => apply(`<div data-editable-infographic="funnel" style="padding:40px 0;max-width:640px;margin:0 auto">
      <div data-infographic-container-visual="true" style="display:flex;flex-direction:column;align-items:center;gap:2px">
        ${[
          ['Odwiedzający','10 000','{{mintLight}}','{{ink}}',520,60],
          ['Zainteresowani','3 200','#98C3AA','{{ink}}',420,60],
          ['Rezerwujący','1 100','{{mint}}','#fff',320,60],
          ['Powracający','680','{{mintDark}}','#fff',220,60],
        ].map(([t,n,bg,tc,w,h]) => `<div data-infographic-item="true" style="width:${w}px;height:${h}px;background:${bg};color:${tc};display:flex;align-items:center;justify-content:space-between;padding:0 36px;font-family:Fraunces,serif;font-size:16px;clip-path:polygon(8% 0,92% 0,100% 100%,0 100%);font-weight:600">
          <span>${t}</span><span style="font-size:20px;font-weight:700">${n}</span>
        </div>`).join('')}
      </div>
    </div>`),
  },
  {
    id: 'pyr-maslow',
    name: 'Piramida 5 poziomów (Maslov)',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      ${[0,1,2,3,4].map(i => {
        const colors = ['#C8DDCE','#98C3AA','#6FAE8C','#4A8268','#2D5040'];
        const w = 140 - i*22;
        const x = 100 - w/2;
        const y = 70 - i*13;
        return `<rect x="${x}" y="${y-12}" width="${w}" height="12" fill="${colors[i]}" rx="1"/>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="pyramid5" style="padding:40px 0;max-width:720px;margin:0 auto">
      <div data-infographic-container-visual="true" style="display:flex;flex-direction:column-reverse;align-items:center;gap:3px">
        ${[
          ['Spełnienie','{{mintDark}}','#fff',200],
          ['Uznanie','{{mint}}','#fff',280],
          ['Przynależność','#98C3AA','{{ink}}',360],
          ['Bezpieczeństwo','{{mintLight}}','{{ink}}',440],
          ['Podstawy','{{cream}}','{{ink}}',520],
        ].map(([t,bg,tc,w]) => `<div data-infographic-item="true" style="width:${w}px;height:54px;background:${bg};color:${tc};display:grid;place-items:center;font-family:Fraunces,serif;font-size:16px;font-weight:600;border:1px solid {{line}}">${t}</div>`).join('')}
      </div>
    </div>`),
  },
];

// --- OSIE CZASU ---
const TIMELINES = [
  {
    id: 'tl-horizontal',
    name: 'Pozioma z datami',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <line x1="20" y1="50" x2="180" y2="50" stroke="#6FAE8C" stroke-width="2"/>
      ${[0,1,2,3].map(i => {
        const x = 32 + i*45;
        return `<circle cx="${x}" cy="50" r="6" fill="#6FAE8C"/><line x1="${x}" y1="44" x2="${x}" y2="28" stroke="#6FAE8C" stroke-width="1.5"/><rect x="${x-12}" y="18" width="24" height="8" rx="1" fill="#E0A84F"/>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="timeline-h" style="padding:40px 0;max-width:960px;margin:0 auto;position:relative">
      <div data-infographic-line="true" style="position:absolute;left:10%;right:10%;top:50%;height:2px;background:{{mint}}"></div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:32px;position:relative">
        ${[
          ['2020','Otwarcie','Pierwszy stolik'],
          ['2022','Rozwój','Nowa kuchnia'],
          ['2024','Społeczność','100 stałych gości'],
          ['2026','Przyszłość','Druga lokalizacja'],
        ].map(([date,t,d], i) => {
          const top = i % 2 === 0;
          return `<div data-infographic-item="true" style="text-align:center;position:relative">
            ${top ? `<div style="margin-bottom:40px">
              <div style="font-family:Fraunces,serif;font-size:14px;color:{{accent}};font-weight:700;margin-bottom:4px">${date}</div>
              <h3 style="font-family:Fraunces,serif;font-size:18px;color:{{ink}};margin:0 0 4px">${t}</h3>
              <p style="font-family:Inter,sans-serif;font-size:13px;color:{{muted}};margin:0">${d}</p>
            </div>` : ''}
            <div data-infographic-circle="true" style="width:20px;height:20px;border-radius:50%;background:{{mint}};margin:0 auto;position:relative;z-index:2;border:4px solid #fff;box-shadow:0 0 0 2px {{mint}}"></div>
            ${!top ? `<div style="margin-top:40px">
              <div style="font-family:Fraunces,serif;font-size:14px;color:{{accent}};font-weight:700;margin-bottom:4px">${date}</div>
              <h3 style="font-family:Fraunces,serif;font-size:18px;color:{{ink}};margin:0 0 4px">${t}</h3>
              <p style="font-family:Inter,sans-serif;font-size:13px;color:{{muted}};margin:0">${d}</p>
            </div>` : ''}
          </div>`;
        }).join('')}
      </div>
    </div>`),
  },
  {
    id: 'tl-vertical',
    name: 'Pionowa z lewej',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <line x1="40" y1="12" x2="40" y2="68" stroke="#6FAE8C" stroke-width="2"/>
      ${[0,1,2].map(i => {
        const y = 22 + i*20;
        return `<circle cx="40" cy="${y}" r="5" fill="#6FAE8C"/><rect x="52" y="${y-5}" width="110" height="10" rx="1" fill="#FAF6EF"/>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="timeline-v" style="padding:40px 0;max-width:560px;margin:0 auto;position:relative">
      <div data-infographic-line="true" style="position:absolute;left:24px;top:12px;bottom:12px;width:2px;background:{{mint}}"></div>
      <div style="display:grid;gap:32px">
        ${[
          ['7:00','Otwarcie — pierwsza kawa'],
          ['10:00','Śniadanie — świeże wypieki'],
          ['12:30','Obiad — zupa dnia'],
          ['16:00','Popołudnie — ciasto i spokój'],
          ['20:00','Zamknięcie — do jutra'],
        ].map(([time,t]) => `<div data-infographic-item="true" style="display:grid;grid-template-columns:50px 1fr;gap:20px;position:relative">
          <div data-infographic-circle="true" style="width:24px;height:24px;border-radius:50%;background:{{mint}};border:4px solid #fff;box-shadow:0 0 0 2px {{mint}};position:relative;z-index:2;margin-left:12px"></div>
          <div style="background:{{cream}};padding:16px 20px;border-radius:8px">
            <div style="font-family:Fraunces,serif;font-size:14px;color:{{accent}};font-weight:700;margin-bottom:4px">${time}</div>
            <div style="font-family:Fraunces,serif;font-size:16px;color:{{ink}}">${t}</div>
          </div>
        </div>`).join('')}
      </div>
    </div>`),
  },
  {
    id: 'tl-cards',
    name: 'Karty z strzałkami',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      ${[0,1,2].map(i => {
        const x = 10 + i*62;
        return `<rect x="${x}" y="22" width="50" height="36" rx="3" fill="#fff" stroke="#6FAE8C" stroke-width="1.5"/><path d="M${x+50} 40 L${x+58} 40 M${x+55} 36 L${x+58} 40 L${x+55} 44" stroke="#6FAE8C" stroke-width="1.5" fill="none" stroke-linecap="round"/>`;
      }).join('')}
    </svg>`,
    html: () => apply(`<div data-editable-infographic="timeline-cards" style="padding:40px 0;max-width:1040px;margin:0 auto">
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px;align-items:stretch">
        ${[
          ['Q1','Start','Otwieramy'],
          ['Q2','Menu','Rozszerzamy'],
          ['Q3','Events','Wieczory autorskie'],
          ['Q4','Plany','Nowe projekty'],
        ].map(([q,t,d], i, arr) => `<div data-infographic-item="true" style="position:relative;background:#fff;border:2px solid {{mint}};padding:24px;border-radius:8px">
          <div style="font-family:Fraunces,serif;font-size:32px;color:{{mint}};font-weight:700;margin-bottom:8px">${q}</div>
          <h3 style="font-family:Fraunces,serif;font-size:18px;color:{{ink}};margin:0 0 6px">${t}</h3>
          <p style="font-family:Inter,sans-serif;font-size:13px;color:{{muted}};margin:0">${d}</p>
          ${i < arr.length - 1 ? `<div style="position:absolute;right:-16px;top:50%;transform:translateY(-50%);width:28px;height:28px;background:{{mint}};border-radius:50%;display:grid;place-items:center;color:#fff;z-index:2"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M9 18l6-6-6-6"/></svg></div>` : ''}
        </div>`).join('')}
      </div>
    </div>`),
  },
  {
    id: 'tl-zigzag',
    name: 'Zygzak — alternujące karty',
    preview: `<svg viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg">
      <line x1="100" y1="10" x2="100" y2="70" stroke="#6FAE8C" stroke-width="2"/>
      <rect x="20" y="15" width="60" height="18" rx="2" fill="#FAF6EF"/>
      <circle cx="100" cy="24" r="4" fill="#6FAE8C"/>
      <rect x="120" y="32" width="60" height="18" rx="2" fill="#FAF6EF"/>
      <circle cx="100" cy="41" r="4" fill="#6FAE8C"/>
      <rect x="20" y="49" width="60" height="18" rx="2" fill="#FAF6EF"/>
      <circle cx="100" cy="58" r="4" fill="#6FAE8C"/>
    </svg>`,
    html: () => apply(`<div data-editable-infographic="timeline-zigzag" style="padding:40px 0;max-width:920px;margin:0 auto;position:relative">
      <div data-infographic-line="true" style="position:absolute;left:50%;top:20px;bottom:20px;width:2px;background:{{mint}};transform:translateX(-50%)"></div>
      <div style="display:grid;gap:32px">
        ${[
          ['Poniedziałek','Otwarcie tygodnia','Świeża kawa o 7:00', true],
          ['Środa','Wieczór autorski','Czytanie prozy o 19:00', false],
          ['Piątek','Akustyczny koncert','Muzyka na żywo o 20:00', true],
          ['Niedziela','Brunch rodzinny','Długie stoły od 10:00', false],
        ].map(([day,t,d,left]) => `<div data-infographic-item="true" style="display:grid;grid-template-columns:1fr 40px 1fr;gap:16px;align-items:center">
          <div style="background:{{cream}};padding:20px 24px;border-radius:8px;${left ? '' : 'grid-column:3;'}text-align:${left ? 'right' : 'left'}">
            <div style="font-family:Fraunces,serif;font-size:13px;color:{{accent}};font-weight:700;margin-bottom:4px">${day}</div>
            <h3 style="font-family:Fraunces,serif;font-size:18px;color:{{ink}};margin:0 0 4px">${t}</h3>
            <p style="font-family:Inter,sans-serif;font-size:13px;color:{{muted}};margin:0">${d}</p>
          </div>
          <div data-infographic-circle="true" style="width:20px;height:20px;border-radius:50%;background:{{mint}};border:4px solid #fff;box-shadow:0 0 0 2px {{mint}};grid-column:2;position:relative;z-index:2;margin:0 auto"></div>
        </div>`).join('')}
      </div>
    </div>`),
  },
];

// ====== WSZYSTKIE KATEGORIE ======
const CATEGORIES = [
  { id: 'processes', name: 'Procesy', desc: 'Strzałki, etapy, flow', templates: PROCESSES, active: true },
  { id: 'circular', name: 'Kołowe', desc: 'Segmenty, koncentryczne', templates: CIRCULAR, active: true },
  { id: 'pyramids', name: 'Piramidy', desc: 'Hierarchie, lejki', templates: PYRAMIDS, active: true },
  { id: 'timelines', name: 'Osie czasu', desc: 'Chronologia, historia', templates: TIMELINES, active: true },
  { id: 'venn', name: 'Diagramy Venna', desc: 'Przecięcia, zależności', templates: [], active: false },
  { id: 'comparison', name: 'Porównania', desc: 'Tabele, vs', templates: [], active: false },
  { id: 'maps', name: 'Mapy i sieci', desc: 'Grafy, relacje', templates: [], active: false },
];

// ====== MODAL ======

function InfographicGallery({ onPick, onClose }) {
  const [activeCat, setActiveCat] = useState('processes');
  const [hoverTpl, setHoverTpl] = useState(null);
  const cat = CATEGORIES.find(c => c.id === activeCat);

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      style={{
        position: 'fixed', inset: 0, zIndex: 9999999,
        background: 'rgba(15,23,42,.6)', backdropFilter: 'blur(4px)',
        display: 'grid', placeItems: 'center', padding: 24,
        animation: 'fadeIn .16s ease',
      }}
    >
      <div style={{
        width: 'min(1180px, 100%)', height: 'min(760px, 92vh)',
        background: '#fff', borderRadius: 14,
        boxShadow: '0 24px 80px rgba(0,0,0,.35)',
        display: 'grid', gridTemplateColumns: '240px 1fr',
        gridTemplateRows: 'auto 1fr',
        overflow: 'hidden',
      }}>
        {/* HEADER */}
        <div style={{
          gridColumn: '1 / -1',
          padding: '18px 24px', borderBottom: '1px solid #E2E8F0',
          display: 'flex', alignItems: 'center', gap: 16,
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: 'Fraunces, serif', fontSize: 22, fontWeight: 600, color: '#0F172A' }}>
              Galeria infografik
            </div>
            <div style={{ fontSize: 13, color: '#64748B', marginTop: 2 }}>
              Wybierz szablon — podmieni obecną infografikę w sekcji.
            </div>
          </div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '6px 12px', background: '#FEF3C7', borderRadius: 20,
            fontSize: 12, color: '#92400E', fontWeight: 600,
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            Makieta — integracja w wersji produkcyjnej
          </div>
          <button
            onClick={onClose}
            style={{
              width: 36, height: 36, border: 'none', background: '#F1F5F9',
              borderRadius: 8, cursor: 'pointer', display: 'grid', placeItems: 'center',
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 6l12 12M18 6L6 18"/>
            </svg>
          </button>
        </div>

        {/* SIDEBAR */}
        <div style={{
          borderRight: '1px solid #E2E8F0', padding: '20px 12px',
          background: '#FAFBFC', overflow: 'auto',
        }}>
          <div style={{
            fontSize: 10, fontWeight: 700, color: '#94A3B8',
            textTransform: 'uppercase', letterSpacing: 0.8,
            padding: '0 10px', marginBottom: 8,
          }}>Kategorie</div>
          {CATEGORIES.map(c => (
            <button
              key={c.id}
              disabled={!c.active}
              onClick={() => c.active && setActiveCat(c.id)}
              title={!c.active ? 'Dostępne w wersji produkcyjnej — integracja z biblioteką ~500 szablonów' : ''}
              style={{
                width: '100%', textAlign: 'left', padding: '12px 14px',
                border: 'none', borderRadius: 8, cursor: c.active ? 'pointer' : 'not-allowed',
                background: activeCat === c.id ? '#fff' : 'transparent',
                boxShadow: activeCat === c.id ? '0 1px 3px rgba(0,0,0,.08)' : 'none',
                marginBottom: 2,
                opacity: c.active ? 1 : 0.45,
                display: 'block',
              }}
            >
              <div style={{
                fontFamily: 'Inter, sans-serif', fontSize: 14, fontWeight: 600,
                color: '#0F172A', marginBottom: 2,
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                {c.name}
                {!c.active && (
                  <span style={{
                    fontSize: 9, fontWeight: 700, padding: '2px 6px',
                    background: '#E2E8F0', color: '#64748B', borderRadius: 10,
                    textTransform: 'uppercase', letterSpacing: 0.5,
                  }}>Soon</span>
                )}
              </div>
              <div style={{ fontSize: 12, color: '#64748B' }}>
                {c.desc} {c.active && `· ${c.templates.length}`}
              </div>
            </button>
          ))}

          <div style={{
            marginTop: 20, padding: '14px 14px',
            background: '#EFF6FF', borderRadius: 8, border: '1px solid #DBEAFE',
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#1E40AF', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
              </svg>
              W wersji produkcyjnej
            </div>
            <div style={{ fontSize: 11, color: '#1E3A8A', lineHeight: 1.5 }}>
              Integracja z biblioteką szablonów (~500), 200k+ ikon z Iconify, wyszukiwanie, ulubione i upload własnych.
            </div>
          </div>
        </div>

        {/* GRID */}
        <div style={{ overflow: 'auto', padding: 24 }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
            gap: 16,
          }}>
            {cat.templates.map(tpl => (
              <button
                key={tpl.id}
                onClick={() => onPick(tpl.html())}
                onMouseEnter={() => setHoverTpl(tpl.id)}
                onMouseLeave={() => setHoverTpl(null)}
                style={{
                  background: '#fff', border: '1px solid #E2E8F0',
                  borderRadius: 10, padding: 0, cursor: 'pointer',
                  overflow: 'hidden', display: 'flex', flexDirection: 'column',
                  transition: 'all .14s ease',
                  transform: hoverTpl === tpl.id ? 'translateY(-2px)' : 'translateY(0)',
                  boxShadow: hoverTpl === tpl.id
                    ? '0 8px 24px rgba(15,23,42,.12), 0 0 0 2px #6366F1'
                    : '0 1px 2px rgba(0,0,0,.04)',
                  fontFamily: 'inherit',
                }}
              >
                <div style={{
                  background: '#FAFBFC', aspectRatio: '200 / 80',
                  borderBottom: '1px solid #E2E8F0',
                  display: 'grid', placeItems: 'center', padding: 12,
                }} dangerouslySetInnerHTML={{ __html: tpl.preview }}/>
                <div style={{
                  padding: '12px 14px', textAlign: 'left',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#0F172A' }}>
                    {tpl.name}
                  </div>
                  {hoverTpl === tpl.id && (
                    <div style={{
                      fontSize: 11, fontWeight: 700, color: '#6366F1',
                      display: 'flex', alignItems: 'center', gap: 4,
                    }}>
                      Wstaw
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 18l6-6-6-6"/></svg>
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ====== PUBLIC API ======
// window.openInfographicGallery({ onPick: (htmlString) => void })
let _galleryRoot = null;
let _galleryEl = null;

export function openInfographicGallery ({ onPick }) {
  closeGallery();
  _galleryEl = document.createElement('div');
  document.body.appendChild(_galleryEl);
  _galleryRoot = ReactDOM.createRoot(_galleryEl);
  _galleryRoot.render(
    <InfographicGallery
      onPick={(html) => {
        onPick?.(html);
        closeGallery();
      }}
      onClose={closeGallery}
    />
  );
};

function closeGallery() {
  if (_galleryRoot) {
    try { _galleryRoot.unmount(); } catch {}
    _galleryRoot = null;
  }
  if (_galleryEl) {
    try { document.body.removeChild(_galleryEl); } catch {}
    _galleryEl = null;
  }
}

export { closeGallery as closeInfographicGallery };
