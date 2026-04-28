"""
Infographic HTML/SVG templates for Lab Creator.
20 templates — each responsive, using CSS variables (--color-primary, --color-secondary).
Slots use {{SLOT_NAME}} pattern. Lists use {{#each items}}...{{/each}}.

Categories:
  A. Process & steps (4): steps_horizontal, steps_vertical, steps_circle, funnel
  B. Numbers & stats (3): stats_rings, stats_cards, stats_bars
  C. Comparisons (3): before_after, pricing_table, vs_comparison
  D. Features & values (3): features_grid_2x3, features_grid_1x4, features_numbers
  E. Timeline (2): timeline_vertical, timeline_horizontal
  F. People & testimonials (2): team_cards, testimonials_stars
  G. Special (3): checklist, faq_visual, cta_banner
"""

# ─── Shared CSS fragments ───

_BRAND = "var(--color-primary, #4F46E5)"
_BRAND_LIGHT = "var(--color-primary-light, rgba(79,70,229,0.08))"
_BRAND_DARK = "var(--color-primary-dark, #3730A3)"
_SECONDARY = "var(--color-secondary, #F59E0B)"
_TEXT = "#1f2937"
_TEXT_MUTED = "#6b7280"
_CARD_SHADOW = "0 1px 3px rgba(0,0,0,0.08)"
_RADIUS = "0.75rem"

TEMPLATES = {

    # ═══════════════════════════════════════════
    # A. PROCESS & STEPS
    # ═══════════════════════════════════════════

    "steps_horizontal": f"""<div style="padding:2rem 0;">
  <div style="display:flex;align-items:flex-start;justify-content:center;gap:0;flex-wrap:wrap;position:relative;">
    {{{{#each steps}}}}
    <div style="flex:1;min-width:140px;max-width:200px;text-align:center;padding:0 0.75rem;position:relative;">
      <div style="width:52px;height:52px;border-radius:50%;background:{_BRAND};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:1.1rem;margin:0 auto 1rem;position:relative;z-index:1;">{{{{this.number}}}}</div>
      <h4 style="font-size:0.95rem;font-weight:600;color:{_TEXT};margin-bottom:0.35rem;">{{{{this.title}}}}</h4>
      <p style="font-size:0.82rem;color:{_TEXT_MUTED};line-height:1.5;">{{{{this.description}}}}</p>
      {{{{#if this.timeline}}}}<div style="font-size:0.75rem;color:{_BRAND};font-weight:500;margin-top:0.5rem;">{{{{this.timeline}}}}</div>{{{{/if}}}}
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "steps_vertical": f"""<div style="max-width:560px;margin:0 auto;padding:2rem 0;">
  {{{{#each steps}}}}
  <div style="display:flex;gap:1.25rem;margin-bottom:2rem;align-items:flex-start;position:relative;">
    <div style="flex-shrink:0;display:flex;flex-direction:column;align-items:center;">
      <div style="width:44px;height:44px;border-radius:50%;background:{_BRAND};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:1rem;">{{{{this.number}}}}</div>
      <div style="width:2px;flex:1;background:linear-gradient({_BRAND}, transparent);min-height:20px;margin-top:4px;"></div>
    </div>
    <div style="padding-top:8px;">
      <h4 style="font-size:1rem;font-weight:600;color:{_TEXT};margin-bottom:0.25rem;">{{{{this.title}}}}</h4>
      <p style="font-size:0.85rem;color:{_TEXT_MUTED};line-height:1.55;">{{{{this.description}}}}</p>
    </div>
  </div>
  {{{{/each}}}}
</div>""",

    "steps_circle": f"""<div style="padding:2rem 0;">
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:1.5rem;">
    {{{{#each steps}}}}
    <div style="text-align:center;width:130px;">
      <div style="width:76px;height:76px;border-radius:50%;border:3px solid {_BRAND};display:flex;align-items:center;justify-content:center;margin:0 auto 0.75rem;">
        <span style="font-weight:700;font-size:1.3rem;color:{_BRAND};">{{{{this.number}}}}</span>
      </div>
      <h4 style="font-size:0.88rem;font-weight:600;color:{_TEXT};">{{{{this.title}}}}</h4>
      <p style="font-size:0.78rem;color:{_TEXT_MUTED};margin-top:0.2rem;line-height:1.4;">{{{{this.description}}}}</p>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "funnel": f"""<div style="max-width:480px;margin:0 auto;padding:2rem 0;">
  {{{{#each steps}}}}
  <div style="background:{_BRAND_LIGHT};border-left:4px solid {_BRAND};padding:1rem 1.25rem;margin-bottom:2px;border-radius:0 {_RADIUS} {_RADIUS} 0;margin-left:calc({{{{this.number}}}} * 12px);margin-right:calc({{{{this.number}}}} * 12px);">
    <div style="display:flex;align-items:center;gap:0.75rem;">
      <span style="font-weight:700;font-size:1.1rem;color:{_BRAND};">{{{{this.number}}}}</span>
      <div>
        <h4 style="font-size:0.95rem;font-weight:600;color:{_TEXT};">{{{{this.title}}}}</h4>
        <p style="font-size:0.82rem;color:{_TEXT_MUTED};margin-top:0.15rem;">{{{{this.description}}}}</p>
      </div>
    </div>
  </div>
  {{{{/each}}}}
</div>""",

    # ═══════════════════════════════════════════
    # B. NUMBERS & STATS
    # ═══════════════════════════════════════════

    "stats_rings": f"""<div style="padding:2rem 0;">
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:2.5rem;">
    {{{{#each stats}}}}
    <div style="text-align:center;min-width:140px;">
      <svg width="100" height="100" viewBox="0 0 100 100" style="display:block;margin:0 auto;">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#e5e7eb" stroke-width="6"/>
        <circle cx="50" cy="50" r="42" fill="none" stroke="{_BRAND}" stroke-width="6" stroke-linecap="round" stroke-dasharray="264" stroke-dashoffset="66" transform="rotate(-90 50 50)"/>
        <text x="50" y="46" text-anchor="middle" dominant-baseline="central" fill="{_TEXT}" font-size="22" font-weight="600">{{{{this.value}}}}</text>
        <text x="50" y="66" text-anchor="middle" fill="{_TEXT_MUTED}" font-size="10">{{{{this.unit}}}}</text>
      </svg>
      <h4 style="font-size:0.9rem;font-weight:600;color:{_TEXT};margin-top:0.75rem;">{{{{this.title}}}}</h4>
      <p style="font-size:0.8rem;color:{_TEXT_MUTED};margin-top:0.2rem;">{{{{this.description}}}}</p>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "stats_cards": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1.25rem;">
    {{{{#each stats}}}}
    <div style="background:#fff;border-radius:{_RADIUS};padding:1.5rem;box-shadow:{_CARD_SHADOW};text-align:center;border-top:3px solid {_BRAND};">
      <div style="font-size:2.2rem;font-weight:700;color:{_BRAND};line-height:1;">{{{{this.value}}}}</div>
      <div style="font-size:0.82rem;color:{_TEXT_MUTED};margin-top:0.5rem;">{{{{this.label}}}}</div>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "stats_bars": f"""<div style="max-width:500px;margin:0 auto;padding:2rem 0;">
  {{{{#each stats}}}}
  <div style="margin-bottom:1.25rem;">
    <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;">
      <span style="font-size:0.88rem;font-weight:500;color:{_TEXT};">{{{{this.label}}}}</span>
      <span style="font-size:0.88rem;font-weight:600;color:{_BRAND};">{{{{this.value}}}}</span>
    </div>
    <div style="height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden;">
      <div style="height:100%;width:{{{{this.percent}}}}%;background:{_BRAND};border-radius:4px;"></div>
    </div>
  </div>
  {{{{/each}}}}
</div>""",

    # ═══════════════════════════════════════════
    # C. COMPARISONS
    # ═══════════════════════════════════════════

    "before_after": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
    <div style="border-radius:{_RADIUS};border:1.5px solid #fca5a5;padding:1.5rem;background:rgba(239,68,68,0.03);">
      <h4 style="font-size:1rem;font-weight:600;color:#dc2626;margin-bottom:1.25rem;display:flex;align-items:center;gap:0.5rem;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
        {{{{before_title}}}}
      </h4>
      {{{{#each before_items}}}}
      <div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.75rem;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" style="flex-shrink:0;margin-top:2px;"><path d="M12 8v4m0 4h.01"/></svg>
        <div>
          <div style="font-size:0.88rem;font-weight:500;color:{_TEXT};">{{{{this.title}}}}</div>
          {{{{#if this.description}}}}<div style="font-size:0.78rem;color:{_TEXT_MUTED};margin-top:0.1rem;">{{{{this.description}}}}</div>{{{{/if}}}}
        </div>
      </div>
      {{{{/each}}}}
    </div>
    <div style="border-radius:{_RADIUS};border:1.5px solid #86efac;padding:1.5rem;background:rgba(16,185,129,0.03);">
      <h4 style="font-size:1rem;font-weight:600;color:#059669;margin-bottom:1.25rem;display:flex;align-items:center;gap:0.5rem;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>
        {{{{after_title}}}}
      </h4>
      {{{{#each after_items}}}}
      <div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.75rem;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" style="flex-shrink:0;margin-top:2px;"><path d="M9 12l2 2 4-4"/></svg>
        <div>
          <div style="font-size:0.88rem;font-weight:500;color:{_TEXT};">{{{{this.title}}}}</div>
          {{{{#if this.description}}}}<div style="font-size:0.78rem;color:{_TEXT_MUTED};margin-top:0.1rem;">{{{{this.description}}}}</div>{{{{/if}}}}
        </div>
      </div>
      {{{{/each}}}}
    </div>
  </div>
</div>""",

    "pricing_table": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.25rem;">
    {{{{#each plans}}}}
    <div style="border-radius:{_RADIUS};border:1.5px solid #e5e7eb;padding:1.75rem;text-align:center;position:relative;background:#fff;">
      {{{{#if this.recommended}}}}<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:{_BRAND};color:#fff;font-size:0.72rem;font-weight:600;padding:0.2rem 0.75rem;border-radius:1rem;">POLECANY</div>{{{{/if}}}}
      <h4 style="font-size:1.1rem;font-weight:600;color:{_TEXT};">{{{{this.name}}}}</h4>
      <div style="font-size:2rem;font-weight:700;color:{_BRAND};margin:0.75rem 0;">{{{{this.price}}}}</div>
      <div style="font-size:0.8rem;color:{_TEXT_MUTED};margin-bottom:1.25rem;">{{{{this.period}}}}</div>
      {{{{#each this.features}}}}
      <div style="display:flex;align-items:center;gap:0.5rem;padding:0.35rem 0;font-size:0.82rem;color:{_TEXT};">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{_BRAND}" stroke-width="2.5" stroke-linecap="round"><path d="M20 6L9 17l-5-5"/></svg>
        {{{{this.text}}}}
      </div>
      {{{{/each}}}}
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "vs_comparison": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0;max-width:560px;margin:0 auto;">
    <div style="padding:1.5rem;border-radius:{_RADIUS} 0 0 {_RADIUS};background:{_BRAND_LIGHT};border:1.5px solid {_BRAND};">
      <h4 style="font-size:1rem;font-weight:600;color:{_BRAND};margin-bottom:1rem;text-align:center;">{{{{left_title}}}}</h4>
      {{{{#each left_items}}}}
      <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0;font-size:0.85rem;color:{_TEXT};">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{_BRAND}" stroke-width="2.5" stroke-linecap="round"><path d="M20 6L9 17l-5-5"/></svg>
        {{{{this.text}}}}
      </div>
      {{{{/each}}}}
    </div>
    <div style="padding:1.5rem;border-radius:0 {_RADIUS} {_RADIUS} 0;border:1.5px solid #e5e7eb;border-left:none;">
      <h4 style="font-size:1rem;font-weight:600;color:{_TEXT_MUTED};margin-bottom:1rem;text-align:center;">{{{{right_title}}}}</h4>
      {{{{#each right_items}}}}
      <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0;font-size:0.85rem;color:{_TEXT_MUTED};">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        {{{{this.text}}}}
      </div>
      {{{{/each}}}}
    </div>
  </div>
</div>""",

    # ═══════════════════════════════════════════
    # D. FEATURES & VALUES
    # ═══════════════════════════════════════════

    "features_grid_2x3": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;">
    {{{{#each items}}}}
    <div style="text-align:center;padding:1.25rem 0.75rem;">
      <div style="width:56px;height:56px;border-radius:50%;background:{_BRAND_LIGHT};display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;">
        <span style="color:{_BRAND};font-size:1.4rem;">{{{{this.icon}}}}</span>
      </div>
      <h4 style="font-size:0.95rem;font-weight:600;color:{_TEXT};margin-bottom:0.35rem;">{{{{this.title}}}}</h4>
      <p style="font-size:0.82rem;color:{_TEXT_MUTED};line-height:1.5;">{{{{this.description}}}}</p>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "features_grid_1x4": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.25rem;">
    {{{{#each items}}}}
    <div style="text-align:center;padding:1rem 0.5rem;">
      <div style="width:48px;height:48px;border-radius:{_RADIUS};background:{_BRAND_LIGHT};display:flex;align-items:center;justify-content:center;margin:0 auto 0.75rem;">
        <span style="color:{_BRAND};font-size:1.2rem;">{{{{this.icon}}}}</span>
      </div>
      <h4 style="font-size:0.88rem;font-weight:600;color:{_TEXT};">{{{{this.title}}}}</h4>
      <p style="font-size:0.78rem;color:{_TEXT_MUTED};margin-top:0.2rem;line-height:1.45;">{{{{this.description}}}}</p>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "features_numbers": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1.5rem;">
    {{{{#each items}}}}
    <div style="padding:1.25rem;">
      <div style="font-size:2.5rem;font-weight:700;color:{_BRAND};line-height:1;margin-bottom:0.5rem;">{{{{this.value}}}}</div>
      <h4 style="font-size:0.95rem;font-weight:600;color:{_TEXT};margin-bottom:0.25rem;">{{{{this.title}}}}</h4>
      <p style="font-size:0.82rem;color:{_TEXT_MUTED};line-height:1.5;">{{{{this.description}}}}</p>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    # ═══════════════════════════════════════════
    # E. TIMELINE
    # ═══════════════════════════════════════════

    "timeline_vertical": f"""<div style="max-width:540px;margin:0 auto;padding:2rem 0;">
  {{{{#each events}}}}
  <div style="display:flex;gap:1.25rem;margin-bottom:0;position:relative;">
    <div style="flex-shrink:0;display:flex;flex-direction:column;align-items:center;">
      <div style="width:40px;height:40px;border-radius:50%;background:{_BRAND};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.72rem;z-index:1;">{{{{this.year}}}}</div>
      <div style="width:2px;flex:1;background:#e5e7eb;min-height:24px;"></div>
    </div>
    <div style="padding-bottom:2rem;">
      <h4 style="font-size:0.95rem;font-weight:600;color:{_TEXT};">{{{{this.title}}}}</h4>
      <p style="font-size:0.82rem;color:{_TEXT_MUTED};margin-top:0.2rem;line-height:1.5;">{{{{this.description}}}}</p>
    </div>
  </div>
  {{{{/each}}}}
</div>""",

    "timeline_horizontal": f"""<div style="padding:2rem 0;overflow-x:auto;">
  <div style="display:flex;align-items:flex-start;gap:0;min-width:max-content;padding:0 1rem;">
    {{{{#each events}}}}
    <div style="text-align:center;min-width:140px;max-width:180px;position:relative;padding:0 0.5rem;">
      <div style="font-size:0.82rem;font-weight:600;color:{_BRAND};margin-bottom:0.5rem;">{{{{this.year}}}}</div>
      <div style="width:14px;height:14px;border-radius:50%;background:{_BRAND};margin:0 auto 0.5rem;position:relative;z-index:1;"></div>
      <h4 style="font-size:0.88rem;font-weight:600;color:{_TEXT};">{{{{this.title}}}}</h4>
      {{{{#if this.description}}}}<p style="font-size:0.78rem;color:{_TEXT_MUTED};margin-top:0.15rem;line-height:1.4;">{{{{this.description}}}}</p>{{{{/if}}}}
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    # ═══════════════════════════════════════════
    # F. PEOPLE & TESTIMONIALS
    # ═══════════════════════════════════════════

    "team_cards": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1.5rem;">
    {{{{#each members}}}}
    <div style="text-align:center;padding:1.5rem 1rem;background:#fff;border-radius:{_RADIUS};box-shadow:{_CARD_SHADOW};">
      <div style="width:72px;height:72px;border-radius:50%;background:{_BRAND_LIGHT};display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;overflow:hidden;">
        {{{{#if this.avatar}}}}<img src="{{{{this.avatar}}}}" style="width:100%;height:100%;object-fit:cover;" alt="{{{{this.name}}}}"/>{{{{/if}}}}
        {{{{#if this.initials}}}}<span style="font-size:1.2rem;font-weight:600;color:{_BRAND};">{{{{this.initials}}}}</span>{{{{/if}}}}
      </div>
      <h4 style="font-size:0.95rem;font-weight:600;color:{_TEXT};">{{{{this.name}}}}</h4>
      <div style="font-size:0.82rem;color:{_BRAND};font-weight:500;margin-top:0.15rem;">{{{{this.role}}}}</div>
      {{{{#if this.bio}}}}<p style="font-size:0.78rem;color:{_TEXT_MUTED};margin-top:0.5rem;line-height:1.45;">{{{{this.bio}}}}</p>{{{{/if}}}}
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "testimonials_stars": f"""<div style="padding:2rem 0;">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem;">
    {{{{#each testimonials}}}}
    <div style="padding:1.5rem;background:#fff;border-radius:{_RADIUS};box-shadow:{_CARD_SHADOW};border-left:3px solid {_BRAND};">
      <div style="color:{_SECONDARY};font-size:0.85rem;margin-bottom:0.75rem;">
        &#9733;&#9733;&#9733;&#9733;&#9733;
      </div>
      <p style="font-size:0.88rem;color:{_TEXT};line-height:1.6;font-style:italic;margin-bottom:1rem;">"{{{{this.quote}}}}"</p>
      <div style="display:flex;align-items:center;gap:0.75rem;">
        <div style="width:36px;height:36px;border-radius:50%;background:{_BRAND_LIGHT};display:flex;align-items:center;justify-content:center;overflow:hidden;">
          {{{{#if this.avatar}}}}<img src="{{{{this.avatar}}}}" style="width:100%;height:100%;object-fit:cover;" alt=""/>{{{{/if}}}}
          {{{{#if this.initials}}}}<span style="font-size:0.75rem;font-weight:600;color:{_BRAND};">{{{{this.initials}}}}</span>{{{{/if}}}}
        </div>
        <div>
          <div style="font-size:0.82rem;font-weight:600;color:{_TEXT};">{{{{this.name}}}}</div>
          <div style="font-size:0.75rem;color:{_TEXT_MUTED};">{{{{this.company}}}}</div>
        </div>
      </div>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    # ═══════════════════════════════════════════
    # G. SPECIAL
    # ═══════════════════════════════════════════

    "checklist": f"""<div style="max-width:520px;margin:0 auto;padding:2rem 0;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem 2rem;">
    {{{{#each items}}}}
    <div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0;">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{_BRAND}" stroke-width="2.5" stroke-linecap="round" style="flex-shrink:0;">
        <path d="M20 6L9 17l-5-5"/>
      </svg>
      <span style="font-size:0.88rem;color:{_TEXT};">{{{{this.text}}}}</span>
    </div>
    {{{{/each}}}}
  </div>
</div>""",

    "faq_visual": f"""<div style="max-width:580px;margin:0 auto;padding:2rem 0;">
  {{{{#each questions}}}}
  <div style="border-bottom:1px solid #e5e7eb;padding:1.25rem 0;">
    <div style="display:flex;align-items:flex-start;gap:0.75rem;">
      <div style="width:28px;height:28px;border-radius:50%;background:{_BRAND};color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:0.82rem;font-weight:600;">?</div>
      <div>
        <h4 style="font-size:0.95rem;font-weight:600;color:{_TEXT};margin-bottom:0.35rem;">{{{{this.question}}}}</h4>
        <p style="font-size:0.85rem;color:{_TEXT_MUTED};line-height:1.6;">{{{{this.answer}}}}</p>
      </div>
    </div>
  </div>
  {{{{/each}}}}
</div>""",

    "cta_banner": f"""<div style="padding:2.5rem;background:{_BRAND};border-radius:{_RADIUS};text-align:center;color:#fff;">
  <h3 style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;">{{{{heading}}}}</h3>
  <p style="font-size:1rem;opacity:0.9;margin-bottom:1.5rem;max-width:480px;margin-left:auto;margin-right:auto;">{{{{subheading}}}}</p>
  <div style="display:flex;justify-content:center;gap:2.5rem;margin-bottom:1.5rem;">
    {{{{#each stats}}}}
    <div>
      <div style="font-size:1.75rem;font-weight:700;">{{{{this.value}}}}</div>
      <div style="font-size:0.8rem;opacity:0.8;">{{{{this.label}}}}</div>
    </div>
    {{{{/each}}}}
  </div>
  {{{{#if cta_text}}}}<a href="{{{{cta_url}}}}" style="display:inline-block;background:#fff;color:{_BRAND};font-weight:600;padding:0.75rem 2rem;border-radius:0.5rem;text-decoration:none;font-size:0.95rem;">{{{{cta_text}}}}</a>{{{{/if}}}}
</div>""",

}


def get_infographic_template(template_name: str) -> str:
    """Get infographic HTML template by name."""
    return TEMPLATES.get(template_name, "")


def get_available_templates() -> list[str]:
    """Get list of available infographic template names."""
    return list(TEMPLATES.keys())


def get_template_categories() -> dict[str, list[str]]:
    """Get templates grouped by category."""
    return {
        "process": ["steps_horizontal", "steps_vertical", "steps_circle", "funnel"],
        "stats": ["stats_rings", "stats_cards", "stats_bars"],
        "comparison": ["before_after", "pricing_table", "vs_comparison"],
        "features": ["features_grid_2x3", "features_grid_1x4", "features_numbers"],
        "timeline": ["timeline_vertical", "timeline_horizontal"],
        "people": ["team_cards", "testimonials_stars"],
        "special": ["checklist", "faq_visual", "cta_banner"],
    }
