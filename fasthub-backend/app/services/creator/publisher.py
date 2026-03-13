"""
PublishingEngine — render, package, and publish a website.
Brief 35: step 9 — publish pipeline.
"""

import io
import logging
import zipfile
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.published_site import PublishedSite
from app.services.creator.renderer import PageRenderer

logger = logging.getLogger(__name__)


class PublishingEngine:
    """Publish a project: render → build full HTML → create/update PublishedSite."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.renderer = PageRenderer()

    async def publish(self, project: Project) -> PublishedSite:
        """Full publish pipeline."""
        html_body, css = await self.renderer.render_project_html(self.db, project)
        full_html = self._build_full_html(project, html_body, css)

        config = project.config_json or {}
        hosting = config.get("hosting", {})
        subdomain = hosting.get("subdomain") or project.domain or self._slugify(project.name)

        # Check existing
        result = await self.db.execute(
            select(PublishedSite).where(PublishedSite.project_id == project.id)
        )
        site = result.scalar_one_or_none()

        if site:
            site.html_snapshot = full_html
            site.css_snapshot = css
            site.seo_json = config.get("seo")
            site.tracking_json = (config.get("seo", {}) or {}).get("tracking")
            site.legal_json = config.get("legal")
            site.forms_json = config.get("forms")
            site.is_active = True
            site.last_updated_at = datetime.utcnow()
        else:
            site = PublishedSite(
                project_id=project.id,
                organization_id=project.organization_id,
                subdomain=subdomain,
                custom_domain=hosting.get("custom_domain"),
                html_snapshot=full_html,
                css_snapshot=css,
                seo_json=config.get("seo"),
                tracking_json=(config.get("seo", {}) or {}).get("tracking"),
                legal_json=config.get("legal"),
                forms_json=config.get("forms"),
                is_active=True,
            )
            self.db.add(site)

        project.status = "published"
        project.published_at = datetime.utcnow()
        project.domain = subdomain

        await self.db.flush()
        await self.db.refresh(site)
        return site

    async def unpublish(self, project: Project) -> None:
        """Take site offline."""
        result = await self.db.execute(
            select(PublishedSite).where(PublishedSite.project_id == project.id)
        )
        site = result.scalar_one_or_none()
        if site:
            site.is_active = False
        project.status = "draft"
        await self.db.flush()

    async def republish(self, project: Project) -> PublishedSite:
        """Update an existing published site."""
        return await self.publish(project)

    async def generate_zip(self, project: Project) -> bytes:
        """Generate ZIP with index.html, style.css, sitemap.xml, robots.txt, legal pages."""
        html_body, css = await self.renderer.render_project_html(self.db, project)
        full_html = self._build_full_html(project, html_body, css)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("index.html", full_html)
            zf.writestr("style.css", css)
            zf.writestr("sitemap.xml", self._generate_sitemap(project))
            zf.writestr("robots.txt", self._generate_robots(project))

            # Legal pages
            legal_pages = self._generate_legal_pages(project)
            for filename, content in legal_pages.items():
                zf.writestr(filename, content)

            # Thank-you pages
            ty_pages = self._generate_thank_you_pages(project)
            for filename, content in ty_pages.items():
                zf.writestr(filename, content)

        return buf.getvalue()

    # ─── HTML Builder ───

    def _build_full_html(self, project: Project, html_body: str, css: str) -> str:
        """Build complete <!DOCTYPE html> with tracking, cookies, OG tags."""
        config = project.config_json or {}
        seo = config.get("seo", {}) or {}
        tracking = seo.get("tracking", {}) or {}
        legal = config.get("legal", {}) or {}

        meta_title = seo.get("meta_title", project.name)
        meta_desc = seo.get("meta_description", "")
        og_title = seo.get("og_title", meta_title)
        og_desc = seo.get("og_description", meta_desc)
        og_image = seo.get("og_image", "")
        canonical = seo.get("canonical_url", "")

        # Head tracking scripts
        head_scripts = []

        # GA4
        ga4 = tracking.get("ga4_id")
        if ga4:
            head_scripts.append(
                f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga4}"></script>\n'
                f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}"
                f"gtag('js',new Date());gtag('config','{ga4}');</script>"
            )

        # GTM
        gtm = tracking.get("gtm_id")
        if gtm:
            head_scripts.append(
                f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),"
                f"event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?"
                f"'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
                f"f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{gtm}');</script>"
            )

        # FB Pixel
        fb_pixel = tracking.get("fb_pixel_id")
        if fb_pixel:
            head_scripts.append(
                f"<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?"
                f"n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;"
                f"n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
                f"t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}"
                f"(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');"
                f"fbq('init','{fb_pixel}');fbq('track','PageView');</script>"
            )

        # Hotjar
        hotjar = tracking.get("hotjar_id")
        if hotjar:
            head_scripts.append(
                f"<script>(function(h,o,t,j,a,r){{h.hj=h.hj||function(){{(h.hj.q=h.hj.q||[]).push(arguments)}};"
                f"h._hjSettings={{hjid:{hotjar},hjsv:6}};a=o.getElementsByTagName('head')[0];"
                f"r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;"
                f"a.appendChild(r)}})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');</script>"
            )

        # LinkedIn Insight
        linkedin = tracking.get("linkedin_id")
        if linkedin:
            head_scripts.append(
                f'<script>_linkedin_partner_id="{linkedin}";window._linkedin_data_partner_ids='
                f'window._linkedin_data_partner_ids||[];window._linkedin_data_partner_ids.push(_linkedin_partner_id);</script>'
            )

        # GSC verification
        gsc = tracking.get("gsc_verification")
        if gsc:
            head_scripts.append(f'<meta name="google-site-verification" content="{gsc}">')

        # Custom head
        custom_head = tracking.get("custom_head", "")

        # Body scripts
        body_scripts = []

        # GTM noscript
        if gtm:
            body_scripts.append(
                f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm}" '
                f'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
            )

        # Custom body
        custom_body = tracking.get("custom_body", "")

        # Cookie banner
        cookie_html = ""
        cb = legal.get("cookie_banner", {})
        if isinstance(cb, dict) and cb.get("enabled"):
            style = cb.get("style", "bar")
            text = cb.get("text", "Ta strona używa cookies. Kontynuując, akceptujesz ich użycie.")
            cookie_html = self._build_cookie_banner(style, text)

        # Build full document
        return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta_title}</title>
<meta name="description" content="{meta_desc}">
{f'<link rel="canonical" href="{canonical}">' if canonical else ''}
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
{f'<meta property="og:image" content="{og_image}">' if og_image else ''}
<meta property="og:type" content="website">
<style>{css}</style>
{''.join(head_scripts)}
{custom_head or ''}
</head>
<body>
{''.join(body_scripts)}
{custom_body or ''}
{html_body}
{cookie_html}
</body>
</html>"""

    def _build_cookie_banner(self, style: str, text: str) -> str:
        """Build cookie banner HTML."""
        if style == "modal":
            return (
                f'<div id="cookie-banner" style="position:fixed;inset:0;background:rgba(0,0,0,0.5);'
                f'display:flex;align-items:center;justify-content:center;z-index:9999">'
                f'<div style="background:#fff;padding:2rem;border-radius:var(--radius,8px);max-width:480px;text-align:center">'
                f'<p style="margin:0 0 1rem">{text}</p>'
                f'<button onclick="this.closest(\'#cookie-banner\').remove()" '
                f'style="background:var(--color-primary,#4F46E5);color:#fff;border:none;padding:.5rem 1.5rem;'
                f'border-radius:var(--radius,8px);cursor:pointer">Akceptuję</button></div></div>'
            )
        elif style == "corner":
            return (
                f'<div id="cookie-banner" style="position:fixed;bottom:1rem;right:1rem;background:#fff;'
                f'padding:1rem;border-radius:var(--radius,8px);box-shadow:0 4px 12px rgba(0,0,0,0.15);'
                f'max-width:320px;z-index:9999">'
                f'<p style="margin:0 0 .5rem;font-size:.875rem">{text}</p>'
                f'<button onclick="this.closest(\'#cookie-banner\').remove()" '
                f'style="background:var(--color-primary,#4F46E5);color:#fff;border:none;padding:.25rem 1rem;'
                f'border-radius:var(--radius,8px);cursor:pointer;font-size:.875rem">OK</button></div>'
            )
        else:  # bar (default)
            return (
                f'<div id="cookie-banner" style="position:fixed;bottom:0;left:0;right:0;background:#1f2937;'
                f'color:#fff;padding:1rem;display:flex;align-items:center;justify-content:center;gap:1rem;z-index:9999">'
                f'<p style="margin:0;font-size:.875rem">{text}</p>'
                f'<button onclick="this.closest(\'#cookie-banner\').remove()" '
                f'style="background:var(--color-primary,#4F46E5);color:#fff;border:none;padding:.5rem 1.5rem;'
                f'border-radius:var(--radius,8px);cursor:pointer;white-space:nowrap">Akceptuję</button></div>'
            )

    # ─── Generators ───

    def _generate_sitemap(self, project: Project) -> str:
        """Generate valid XML sitemap."""
        config = project.config_json or {}
        hosting = config.get("hosting", {}) or {}
        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain or "example.com"
        base_url = f"https://{domain}"
        now = datetime.utcnow().strftime("%Y-%m-%d")

        urls = [f"""  <url>
    <loc>{base_url}/</loc>
    <lastmod>{now}</lastmod>
    <priority>1.0</priority>
  </url>"""]

        # Legal pages
        legal = config.get("legal", {}) or {}
        if isinstance(legal.get("privacy_policy"), dict) and legal["privacy_policy"].get("html"):
            urls.append(f"""  <url>
    <loc>{base_url}/polityka-prywatnosci.html</loc>
    <lastmod>{now}</lastmod>
    <priority>0.3</priority>
  </url>""")

        if isinstance(legal.get("terms"), dict) and legal["terms"].get("html"):
            urls.append(f"""  <url>
    <loc>{base_url}/regulamin.html</loc>
    <lastmod>{now}</lastmod>
    <priority>0.3</priority>
  </url>""")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    def _generate_robots(self, project: Project) -> str:
        """Generate robots.txt."""
        config = project.config_json or {}
        hosting = config.get("hosting", {}) or {}
        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain or "example.com"

        return f"""User-agent: *
Allow: /
Sitemap: https://{domain}/sitemap.xml"""

    def _generate_legal_pages(self, project: Project) -> dict[str, str]:
        """Generate legal HTML pages from config."""
        pages = {}
        config = project.config_json or {}
        legal = config.get("legal", {}) or {}

        pp = legal.get("privacy_policy", {})
        if isinstance(pp, dict) and pp.get("html"):
            pages["polityka-prywatnosci.html"] = self._wrap_subpage(
                "Polityka prywatności", pp["html"], project
            )

        terms = legal.get("terms", {})
        if isinstance(terms, dict) and terms.get("html"):
            pages["regulamin.html"] = self._wrap_subpage(
                "Regulamin", terms["html"], project
            )

        return pages

    def _generate_thank_you_pages(self, project: Project) -> dict[str, str]:
        """Generate thank-you pages from forms config."""
        pages = {}
        config = project.config_json or {}
        forms = config.get("forms", {}) or {}

        thank_you = forms.get("thank_you_message")
        if thank_you:
            pages["dziekujemy.html"] = self._wrap_subpage(
                "Dziękujemy!", f"<div style='text-align:center;padding:4rem 1rem'><h1>Dziękujemy!</h1><p>{thank_you}</p></div>",
                project,
            )

        return pages

    def _wrap_subpage(self, title: str, body_html: str, project: Project) -> str:
        """Wrap content in a simple HTML page."""
        style = project.style_json or {}
        heading_font = style.get("heading_font", "Outfit")
        body_font = style.get("body_font", "Inter")

        return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {project.name}</title>
<link href="https://fonts.googleapis.com/css2?family={heading_font.replace(' ', '+')}:wght@400;600;700&family={body_font.replace(' ', '+')}:wght@300;400;500&display=swap" rel="stylesheet">
<style>
body {{ font-family: '{body_font}', system-ui; color: #1f2937; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.7; }}
h1, h2, h3 {{ font-family: '{heading_font}', system-ui; }}
a {{ color: var(--color-primary, #4F46E5); }}
</style>
</head>
<body>
{body_html}
<p style="margin-top:3rem;text-align:center"><a href="/">&larr; Wróć na stronę główną</a></p>
</body>
</html>"""

    @staticmethod
    def _slugify(text: str) -> str:
        """Simple slug from project name."""
        import re
        slug = text.lower().strip()
        slug = re.sub(r"[ąàáâã]", "a", slug)
        slug = re.sub(r"[ćçč]", "c", slug)
        slug = re.sub(r"[ęèéêë]", "e", slug)
        slug = re.sub(r"[łl]", "l", slug)
        slug = re.sub(r"[ńñ]", "n", slug)
        slug = re.sub(r"[óòôõö]", "o", slug)
        slug = re.sub(r"[śšş]", "s", slug)
        slug = re.sub(r"[żźž]", "z", slug)
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        return slug.strip("-")[:50]
