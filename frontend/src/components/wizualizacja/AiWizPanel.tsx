import React from "react";
// Wiz AI — panel czatu po prawej, z historią w localStorage,
// groundingiem na faktycznej treści strony i możliwością zastosowania propozycji.

const AI_HISTORY_KEY = 'wiz_ai_history_v2';

// Wyciąga snapshot DOM z widokiem sekcji i ich ID
function getPageSnapshot(root) {
  if (!root) return { text: '', sections: [] };
  const sections = [];
  const secEls = root.querySelectorAll('section, nav, footer, header');
  secEls.forEach((s, i) => {
    if (!s.dataset.aiId) s.dataset.aiId = `sec_${i + 1}`;
    const headings = Array.from(s.querySelectorAll('h1, h2, h3')).map(h => h.innerText.trim()).filter(Boolean);
    const title = headings[0] || s.tagName.toLowerCase();
    const txt = s.innerText.trim().replace(/\n{3,}/g, '\n\n').slice(0, 600);
    sections.push({ id: s.dataset.aiId, idx: i + 1, title, text: txt, el: s });
  });
  return { sections };
}

// Parsuje odpowiedź AI w szukaniu konkretnych propozycji zmian
// Format oczekiwany (z promptu):  [[ZMIANA sec_3 "nowy tekst nagłówka"]]
function parseProposals(text) {
  const proposals = [];
  const re = /\[\[ZMIANA\s+(sec_\d+)\s+"([^"]+)"\]\]/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    proposals.push({ secId: m[1], newText: m[2] });
  }
  return proposals;
}

// Usuwa znaczniki [[ZMIANA ...]] z tekstu do wyświetlenia
function cleanAIText(text) {
  return text.replace(/\[\[ZMIANA[^\]]+\]\]/g, '').replace(/\n{3,}/g, '\n\n').trim();
}

function WizAIPanel({ onClose, getViewportEl, activePageName }) {
  const [messages, setMessages] = React.useState(() => {
    try {
      const raw = localStorage.getItem(AI_HISTORY_KEY);
      if (raw) return JSON.parse(raw);
    } catch (_) {}
    return [{
      role: 'ai',
      text: 'Cześć. Widzę Twoją stronę. Mogę przepisać konkretne sekcje, skrócić teksty, dopasować ton albo poprawić CTA. Napisz czego potrzebujesz — po polsku, zwykłym językiem.',
    }];
  });
  const [input, setInput] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const scrollRef = React.useRef(null);

  // Persist historii
  React.useEffect(() => {
    try { localStorage.setItem(AI_HISTORY_KEY, JSON.stringify(messages.slice(-40))); } catch (_) {}
  }, [messages]);

  React.useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loading]);

  const buildPrompt = (userMsg, snapshot) => {
    const sectionList = snapshot.sections.map(s =>
      `[${s.id}] ${s.title}\n${s.text}`
    ).join('\n\n---\n\n');

    return [
      'Jesteś polskojęzycznym asystentem edytorskim dla kreatora stron WWW.',
      '',
      'ZASADY ODPOWIEDZI — bezwzględne:',
      '1. Odpowiadaj WYŁĄCZNIE po polsku. Żadnych angielskich nagłówków typu "Strengths", "Areas to improve", "Summary".',
      '2. Nie używaj markdownowych nagłówków (##). Pisz płynnym tekstem lub krótką listą z myślnikami.',
      '3. Bądź maksymalnie zwięzły — 2–5 zdań, chyba że user prosi o więcej.',
      '4. NIE halucynuj sekcji — odwołuj się wyłącznie do tych, które są na liście poniżej (z identyfikatorami sec_1, sec_2…).',
      '5. Jeśli proponujesz konkretną zmianę tekstu, ZAWSZE podaj ją w formacie maszynowym:',
      '   [[ZMIANA sec_X "nowy tekst bez cudzysłowów w środku"]]',
      '   Ten znacznik będzie wycięty przed pokazaniem userowi — więc obok napisz też po ludzku "proponuję…"',
      '6. Jeśli user mówi "tak, zastosuj" / "ok" / "zrób to" — odpowiedz krótko "Gotowe." i jeszcze raz wypisz znaczniki [[ZMIANA ...]] dla zmian, które wcześniej zaproponowałeś. Nie zaczynaj oceny od nowa.',
      '7. Nie dodawaj treści niezwiązanych (np. "dodaj cytat z Gazety Wyborczej"), jeśli taka treść nie ma źródła w aktualnych sekcjach.',
      '',
      `Aktualna podstrona: ${activePageName}`,
      '',
      'SEKCJE NA STRONIE (to jedyne, do których możesz się odwoływać):',
      '',
      sectionList,
      '',
      `UŻYTKOWNIK: ${userMsg}`,
    ].join('\n');
  };

  const send = async (overrideMsg) => {
    const msg = (overrideMsg ?? input).trim();
    if (!msg || loading) return;
    setInput('');
    const newUserMsg = { role: 'user', text: msg };
    setMessages(m => [...m, newUserMsg]);
    setLoading(true);
    try {
      const root = getViewportEl?.();
      const snapshot = getPageSnapshot(root);
      const prompt = buildPrompt(msg, snapshot);

      // Krótka historia konwersacji (ostatnie 6) dla kontekstu
      const history = messages.slice(-6).map(m => ({
        role: m.role === 'ai' ? 'assistant' : 'user',
        content: m.role === 'ai' ? cleanAIText(m.text) : m.text,
      }));

      const reply = await window.claude.complete({
        messages: [
          ...history,
          { role: 'user', content: prompt },
        ],
      });

      const proposals = parseProposals(reply);
      const shown = cleanAIText(reply);
      setMessages(m => [...m, {
        role: 'ai',
        text: shown || 'Gotowe.',
        proposals: proposals.length ? proposals.map(p => ({ ...p, status: 'pending' })) : undefined,
      }]);
    } catch (e) {
      setMessages(m => [...m, { role: 'ai', text: 'Błąd połączenia z AI. Spróbuj ponownie.', error: true }]);
    }
    setLoading(false);
  };

  // Zastosuj propozycję: znajdź sekcję po ID, podmień główny nagłówek / p
  const applyProposal = (msgIdx, propIdx) => {
    setMessages(ms => {
      const copy = [...ms];
      const msg = { ...copy[msgIdx] };
      const props = [...(msg.proposals || [])];
      const p = props[propIdx];
      if (!p) return ms;

      const root = getViewportEl?.();
      if (!root) return ms;
      const sec = root.querySelector(`[data-ai-id="${p.secId}"]`);
      if (!sec) {
        props[propIdx] = { ...p, status: 'error' };
        msg.proposals = props;
        copy[msgIdx] = msg;
        return copy;
      }
      // Znajdź najlepszy cel: pierwszy H1-H3 jeśli propozycja wygląda na nagłówek, inaczej pierwszy p
      const isShort = p.newText.length < 90;
      const target = isShort
        ? (sec.querySelector('h1, h2, h3') || sec.querySelector('p'))
        : (sec.querySelector('p') || sec.querySelector('h1, h2, h3'));
      if (!target) {
        props[propIdx] = { ...p, status: 'error' };
        msg.proposals = props;
        copy[msgIdx] = msg;
        return copy;
      }
      target.innerText = p.newText;
      // Podświetlenie
      target.style.transition = 'background-color .6s';
      target.style.backgroundColor = 'rgba(168,213,186,.45)';
      setTimeout(() => { target.style.backgroundColor = ''; }, 1200);

      props[propIdx] = { ...p, status: 'applied' };
      msg.proposals = props;
      copy[msgIdx] = msg;
      return copy;
    });
  };

  const applyAll = (msgIdx) => {
    const msg = messages[msgIdx];
    msg?.proposals?.forEach((_, i) => applyProposal(msgIdx, i));
  };

  const clearHistory = () => {
    if (!window.confirm('Wyczyścić historię czatu z AI?')) return;
    try { localStorage.removeItem(AI_HISTORY_KEY); } catch (_) {}
    setMessages([{
      role: 'ai',
      text: 'Historia wyczyszczona. Napisz, co zmienić — widzę całą stronę.',
    }]);
  };

  const suggestions = [
    'Skróć sekcję hero o połowę',
    'Przepisz w cieplejszym tonie',
    'Mocniejsze CTA w sekcji kontakt',
    'Uprość opis menu',
  ];

  return (
    <div style={{
      position: 'fixed', top: 0, right: 0, bottom: 0, width: 440, zIndex: 360,
      background: '#fff', borderLeft: '1px solid #E2E8F0',
      boxShadow: '-10px 0 30px rgba(15,23,42,.08)',
      display: 'flex', flexDirection: 'column',
      fontFamily: 'Inter, sans-serif',
      animation: 'slideInRight .2s',
    }}>
      {/* Header */}
      <div style={{ padding: '14px 18px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 30, height: 30, borderRadius: 9,
          background: 'linear-gradient(135deg, #A8D5BA 0%, #6FAE8C 100%)',
          display: 'grid', placeItems: 'center', color: '#fff',
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0F172A' }}>Asystent AI</div>
          <div style={{ fontSize: 11, color: '#64748B' }}>Widzi całą stronę — {activePageName}</div>
        </div>
        <button onClick={clearHistory} title="Wyczyść historię" style={{
          width: 30, height: 30, border: 'none', background: 'transparent', color: '#94A3B8',
          borderRadius: 8, cursor: 'pointer', display: 'grid', placeItems: 'center',
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
          </svg>
        </button>
        <button onClick={onClose} style={{
          width: 30, height: 30, border: 'none', background: '#F1F5F9', borderRadius: 8, cursor: 'pointer', display: 'grid', placeItems: 'center',
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} style={{ flex: 1, overflow: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{
              maxWidth: '88%',
              background: m.role === 'user' ? '#0F172A' : (m.error ? '#FEF2F2' : '#F1F5F9'),
              color: m.role === 'user' ? '#fff' : (m.error ? '#991B1B' : '#0F172A'),
              padding: '10px 13px', borderRadius: 12,
              fontSize: 13, lineHeight: 1.55, whiteSpace: 'pre-wrap',
            }}>
              {m.text}
            </div>

            {/* Propozycje zmian — karty do zastosowania */}
            {m.proposals && m.proposals.length > 0 && (
              <div style={{ width: '88%', display: 'flex', flexDirection: 'column', gap: 6, marginTop: 2 }}>
                {m.proposals.map((p, pi) => (
                  <div key={pi} style={{
                    border: '1px solid #E2E8F0', borderRadius: 10,
                    background: p.status === 'applied' ? '#ECFDF5' : '#fff',
                    padding: 10, display: 'flex', flexDirection: 'column', gap: 6,
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{
                        fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                        letterSpacing: 0.4,
                        padding: '2px 6px', borderRadius: 4,
                        background: '#EEF2FF', color: '#4338CA',
                      }}>{p.secId}</span>
                      {p.status === 'applied' && (
                        <span style={{ fontSize: 10, fontWeight: 700, color: '#065F46', display: 'inline-flex', alignItems: 'center', gap: 3 }}>
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                          Zastosowano
                        </span>
                      )}
                      {p.status === 'error' && (
                        <span style={{ fontSize: 10, fontWeight: 700, color: '#991B1B' }}>Nie znaleziono sekcji</span>
                      )}
                    </div>
                    <div style={{ fontSize: 12.5, color: '#334155', lineHeight: 1.5, fontStyle: 'italic' }}>
                      „{p.newText}"
                    </div>
                    {p.status !== 'applied' && p.status !== 'error' && (
                      <button onClick={() => applyProposal(i, pi)} style={{
                        alignSelf: 'flex-start',
                        padding: '6px 12px', border: 'none', background: '#0F172A', color: '#fff',
                        borderRadius: 7, fontSize: 11.5, fontWeight: 600, cursor: 'pointer',
                        fontFamily: 'inherit',
                      }}>Zastosuj zmianę</button>
                    )}
                  </div>
                ))}
                {m.proposals.length > 1 && m.proposals.some(p => p.status !== 'applied') && (
                  <button onClick={() => applyAll(i)} style={{
                    alignSelf: 'flex-start',
                    padding: '5px 10px', border: '1px solid #0F172A', background: '#fff', color: '#0F172A',
                    borderRadius: 7, fontSize: 11, fontWeight: 600, cursor: 'pointer',
                    fontFamily: 'inherit',
                  }}>Zastosuj wszystkie</button>
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', padding: '10px 13px', background: '#F1F5F9', borderRadius: 12, fontSize: 13, color: '#64748B' }}>
            <span className="dots">Myślę</span>
          </div>
        )}
      </div>

      {/* Suggestions (tylko jak brak konwersacji) */}
      {messages.length <= 1 && (
        <div style={{ padding: '0 16px 10px', display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {suggestions.map(s => (
            <button key={s} onClick={() => send(s)} style={{
              padding: '6px 10px', border: '1px solid #E2E8F0', background: '#fff',
              borderRadius: 999, fontSize: 11.5, color: '#334155', cursor: 'pointer', fontFamily: 'inherit',
            }}>{s}</button>
          ))}
        </div>
      )}

      {/* Input */}
      <div style={{ padding: '10px 16px 14px', borderTop: '1px solid #E2E8F0' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
          <textarea
            value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Napisz co zmienić… (Enter = wyślij)" rows={1}
            style={{
              flex: 1, border: '1px solid #E2E8F0', borderRadius: 10,
              padding: '10px 12px', fontSize: 13, resize: 'none',
              fontFamily: 'inherit', outline: 'none', maxHeight: 120,
            }}/>
          <button onClick={() => send()} disabled={loading || !input.trim()} style={{
            padding: '10px 14px', border: 'none',
            background: (loading || !input.trim()) ? '#E2E8F0' : '#0F172A',
            color: '#fff', borderRadius: 10, fontSize: 13, fontWeight: 600,
            cursor: (loading || !input.trim()) ? 'not-allowed' : 'pointer', fontFamily: 'inherit',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

export { WizAIPanel };
