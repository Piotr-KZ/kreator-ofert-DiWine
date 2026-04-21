"""
Infographic HTML/CSS templates for Lab Creator.
8 templates — each responsive, using CSS variables (--primary, --secondary).
Slots use {{SLOT_NAME}} pattern.
"""

TEMPLATES = {

    "steps_horizontal": """<div style="display:flex;gap:2rem;flex-wrap:wrap;justify-content:center;padding:2rem 0;">
  {{#each steps}}
  <div style="flex:1;min-width:150px;max-width:220px;text-align:center;">
    <div style="width:48px;height:48px;border-radius:50%;background:var(--color-primary,#4F46E5);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1.2rem;margin:0 auto 0.75rem;">{{this.number}}</div>
    <h4 style="font-size:1rem;font-weight:600;margin-bottom:0.25rem;">{{this.title}}</h4>
    <p style="font-size:0.875rem;color:#6b7280;">{{this.description}}</p>
  </div>
  {{/each}}
</div>""",

    "steps_vertical": """<div style="max-width:600px;margin:0 auto;padding:2rem 0;">
  {{#each steps}}
  <div style="display:flex;gap:1.25rem;margin-bottom:2rem;align-items:flex-start;">
    <div style="flex-shrink:0;width:40px;height:40px;border-radius:50%;background:var(--color-primary,#4F46E5);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;">{{this.number}}</div>
    <div>
      <h4 style="font-size:1rem;font-weight:600;margin-bottom:0.25rem;">{{this.title}}</h4>
      <p style="font-size:0.875rem;color:#6b7280;">{{this.description}}</p>
    </div>
  </div>
  {{/each}}
</div>""",

    "numbers_row": """<div style="display:flex;gap:2rem;flex-wrap:wrap;justify-content:center;padding:2rem 0;">
  {{#each stats}}
  <div style="text-align:center;flex:1;min-width:120px;">
    <div style="font-size:2.5rem;font-weight:800;color:var(--color-primary,#4F46E5);line-height:1;">{{this.value}}</div>
    <div style="font-size:0.875rem;color:#6b7280;margin-top:0.5rem;">{{this.label}}</div>
  </div>
  {{/each}}
</div>""",

    "numbers_cards": """<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;padding:2rem 0;">
  {{#each stats}}
  <div style="background:#fff;border-radius:0.75rem;padding:1.5rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);text-align:center;">
    <div style="font-size:2rem;font-weight:800;color:var(--color-primary,#4F46E5);">{{this.value}}</div>
    <div style="font-size:0.875rem;color:#6b7280;margin-top:0.5rem;">{{this.label}}</div>
  </div>
  {{/each}}
</div>""",

    "before_after": """<div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;padding:2rem 0;">
  <div style="padding:1.5rem;border-radius:0.75rem;border:2px solid #e5e7eb;">
    <h4 style="font-size:1.1rem;font-weight:700;color:#ef4444;margin-bottom:1rem;">{{before_title}}</h4>
    {{#each before_items}}
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
      <span style="color:#ef4444;font-weight:700;">✕</span>
      <span style="font-size:0.875rem;color:#6b7280;">{{this.text}}</span>
    </div>
    {{/each}}
  </div>
  <div style="padding:1.5rem;border-radius:0.75rem;border:2px solid var(--color-primary,#4F46E5);background:rgba(79,70,229,0.03);">
    <h4 style="font-size:1.1rem;font-weight:700;color:var(--color-primary,#4F46E5);margin-bottom:1rem;">{{after_title}}</h4>
    {{#each after_items}}
    <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
      <span style="color:var(--color-primary,#4F46E5);font-weight:700;">✓</span>
      <span style="font-size:0.875rem;color:#374151;">{{this.text}}</span>
    </div>
    {{/each}}
  </div>
</div>""",

    "timeline": """<div style="max-width:600px;margin:0 auto;padding:2rem 0;position:relative;">
  <div style="position:absolute;left:19px;top:0;bottom:0;width:2px;background:#e5e7eb;"></div>
  {{#each events}}
  <div style="display:flex;gap:1.25rem;margin-bottom:2rem;position:relative;">
    <div style="flex-shrink:0;width:40px;height:40px;border-radius:50%;background:var(--color-primary,#4F46E5);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.75rem;z-index:1;">{{this.year}}</div>
    <div>
      <h4 style="font-size:1rem;font-weight:600;">{{this.title}}</h4>
      <p style="font-size:0.875rem;color:#6b7280;">{{this.description}}</p>
    </div>
  </div>
  {{/each}}
</div>""",

    "icons_grid": """<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1.5rem;padding:2rem 0;">
  {{#each items}}
  <div style="text-align:center;padding:1.5rem;">
    <div style="font-size:2rem;margin-bottom:0.75rem;">{{this.icon}}</div>
    <h4 style="font-size:1rem;font-weight:600;margin-bottom:0.25rem;">{{this.title}}</h4>
    <p style="font-size:0.875rem;color:#6b7280;">{{this.description}}</p>
  </div>
  {{/each}}
</div>""",

    "process_circle": """<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:1rem;padding:2rem 0;">
  {{#each steps}}
  <div style="position:relative;text-align:center;width:140px;">
    <div style="width:80px;height:80px;border-radius:50%;border:3px solid var(--color-primary,#4F46E5);display:flex;align-items:center;justify-content:center;margin:0 auto 0.75rem;font-weight:800;font-size:1.25rem;color:var(--color-primary,#4F46E5);">{{this.number}}</div>
    <h4 style="font-size:0.875rem;font-weight:600;">{{this.title}}</h4>
  </div>
  {{/each}}
</div>""",

}


def get_infographic_template(template_name: str) -> str:
    """Get infographic HTML template by name."""
    return TEMPLATES.get(template_name, "")


def get_available_templates() -> list[str]:
    """Get list of available infographic template names."""
    return list(TEMPLATES.keys())
