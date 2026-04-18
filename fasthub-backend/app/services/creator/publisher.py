"""
PublishingEngine — render, package, and publish a website.
Brief 35: step 9 — publish pipeline.
"""

import html as html_mod
import io
import json
import logging
import re
import zipfile
from datetime import datetime
from typing import Optional

import httpx
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
        raw_subdomain = hosting.get("subdomain") or project.domain or self._slugify(project.name)
        # Validate subdomain format
        subdomain = self._sanitize_subdomain(raw_subdomain)

        # Check existing site for this project
        result = await self.db.execute(
            select(PublishedSite).where(PublishedSite.project_id == project.id)
        )
        site = result.scalar_one_or_none()

        # Check subdomain collision with other projects
        if not site or site.subdomain != subdomain:
            collision = await self.db.execute(
                select(PublishedSite).where(
                    PublishedSite.subdomain == subdomain,
                    PublishedSite.project_id != project.id,
                )
            )
            if collision.scalar_one_or_none():
                raise ValueError(f"Subdomena '{subdomain}' jest już zajęta. Wybierz inną.")

        # Generate AI Visibility files (Brief 41)
        from app.services.creator.llms_generator import LlmsGenerator
        from app.services.creator.openapi_generator import OpenAPIGenerator
        llms_txt = LlmsGenerator().generate(project)
        openapi_json = OpenAPIGenerator().generate(project)

        if site:
            site.html_snapshot = full_html
            site.css_snapshot = css
            site.seo_json = config.get("seo")
            site.tracking_json = (config.get("seo", {}) or {}).get("tracking")
            site.legal_json = config.get("legal")
            site.forms_json = config.get("forms")
            site.llms_txt = llms_txt
            site.openapi_json = openapi_json
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
                llms_txt=llms_txt,
                openapi_json=openapi_json,
                is_active=True,
            )
            self.db.add(site)

        project.status = "published"
        project.published_at = datetime.utcnow()
        project.domain = subdomain

        await self.db.flush()
        await self.db.refresh(site)

        # Ping IndexNow for faster indexing (fire-and-forget)
        try:
            await self.ping_indexnow(project)
        except Exception:
            pass  # Non-critical — don't block publish

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
        """Generate ZIP with index.html, style.css, sitemap.xml, robots.txt, llms.txt, legal pages."""
        html_body, css = await self.renderer.render_project_html(self.db, project)
        full_html = self._build_full_html(project, html_body, css)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("index.html", full_html)
            zf.writestr("style.css", css)
            zf.writestr("sitemap.xml", self._generate_sitemap(project))
            zf.writestr("robots.txt", self._generate_robots(project))

            # llms.txt (Brief 41)
            from app.services.creator.llms_generator import LlmsGenerator
            llms_txt = LlmsGenerator().generate(project)
            zf.writestr("llms.txt", llms_txt)

            # openapi.json (Brief 41)
            from app.services.creator.openapi_generator import OpenAPIGenerator
            openapi = OpenAPIGenerator().generate(project)
            if openapi:
                zf.writestr("openapi.json", json.dumps(openapi, ensure_ascii=False, indent=2))

            # Legal pages
            legal_pages = self._generate_legal_pages(project)
            for filename, content in legal_pages.items():
                zf.writestr(filename, content)

            # Thank-you pages
            ty_pages = self._generate_thank_you_pages(project)
            for filename, content in ty_pages.items():
                zf.writestr(filename, content)

        return buf.getvalue()

    async def ping_indexnow(self, project: Project) -> bool:
        """Ping IndexNow after publish to speed up indexing."""
        config = project.config_json or {}
        hosting = config.get("hosting", {}) or {}
        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain
        if not domain:
            return False

        base_url = f"https://{domain}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.indexnow.org/indexnow",
                    params={"url": base_url, "key": domain.replace(".", "")[:32]},
                )
                return resp.status_code < 300
        except Exception:
            logger.warning(f"IndexNow ping failed for {domain}")
            return False

    # ─── HTML Builder ───

    def _build_schema_jsonld(self, project: Project) -> str:
        """Generate rich JSON-LD structured data from brief + ai_visibility (Brief 41)."""
        from app.services.creator.schema_generator import SchemaGenerator
        schemas = SchemaGenerator().generate(project)
        return f'<script type="application/ld+json">{json.dumps(schemas, ensure_ascii=False)}</script>'

    def _optimize_images_html(self, html_body: str) -> str:
        """Post-process HTML body for CWV: lazy loading, fetchpriority, dimensions, CLS prevention."""
        img_count = 0

        def replace_img(match: re.Match) -> str:
            nonlocal img_count
            img_count += 1
            tag = match.group(0)

            # First image (hero) gets fetchpriority=high, no lazy
            if img_count == 1:
                if 'fetchpriority' not in tag:
                    tag = tag.replace('<img ', '<img fetchpriority="high" ')
                if 'loading=' in tag:
                    tag = re.sub(r'loading="[^"]*"', '', tag)
            else:
                # All other images get lazy loading
                if 'loading=' not in tag:
                    tag = tag.replace('<img ', '<img loading="lazy" ')

            # Add decoding=async for all images
            if 'decoding=' not in tag:
                tag = tag.replace('<img ', '<img decoding="async" ')

            # Add default width/height if missing (prevents CLS)
            if 'width=' not in tag and 'height=' not in tag:
                tag = tag.replace('<img ', '<img width="800" height="600" ')

            return tag

        optimized = re.sub(r'<img\s[^>]+>', replace_img, html_body, flags=re.IGNORECASE)

        # Add content-visibility: auto to sections below fold for faster rendering
        section_count = 0
        def add_content_visibility(match: re.Match) -> str:
            nonlocal section_count
            section_count += 1
            tag = match.group(0)
            if section_count > 2:  # Skip first 2 sections (above fold)
                tag = tag.replace('data-section-id=', 'style="content-visibility:auto;contain-intrinsic-size:auto 500px" data-section-id=')
            return tag

        optimized = re.sub(
            r'<div\s+data-section-id="[^"]*"',
            add_content_visibility,
            optimized,
        )

        return optimized

    def _auto_canonical(self, project: Project, manual_canonical: str) -> str:
        """Generate canonical URL if not manually set."""
        if manual_canonical:
            return manual_canonical
        config = project.config_json or {}
        hosting = config.get("hosting", {}) or {}
        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain
        if domain:
            return f"https://{domain}/"
        return ""

    def _build_full_html(self, project: Project, html_body: str, css: str) -> str:
        """Build complete <!DOCTYPE html> with tracking, cookies, OG tags."""
        config = project.config_json or {}
        seo = config.get("seo", {}) or {}
        tracking = seo.get("tracking", {}) or {}
        legal = config.get("legal", {}) or {}

        _e = html_mod.escape
        meta_title = _e(seo.get("meta_title", project.name) or "")
        meta_desc = _e(seo.get("meta_description", "") or "")
        og_title = _e(seo.get("og_title", "") or "") or meta_title
        og_desc = _e(seo.get("og_description", "") or "") or meta_desc
        og_image = _e(seo.get("og_image", "") or "")
        manual_canonical = _e(seo.get("canonical_url", "") or "")
        canonical = _e(self._auto_canonical(project, manual_canonical))

        # Schema.org JSON-LD
        schema_jsonld = self._build_schema_jsonld(project)

        # Head tracking scripts
        head_scripts = []

        def _safe_tracking_id(val: str | None) -> str | None:
            """Allow only safe tracking IDs (alphanumeric, dash, underscore)."""
            if not val:
                return None
            if not re.match(r'^[a-zA-Z0-9_-]+$', val):
                return None
            return val

        # GA4
        ga4 = _safe_tracking_id(tracking.get("ga4_id"))
        if ga4:
            head_scripts.append(
                f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga4}"></script>\n'
                f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}"
                f"gtag('js',new Date());gtag('config','{ga4}');</script>"
            )

        # GTM
        gtm = _safe_tracking_id(tracking.get("gtm_id"))
        if gtm:
            head_scripts.append(
                f"<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),"
                f"event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?"
                f"'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
                f"f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{gtm}');</script>"
            )

        # FB Pixel
        fb_pixel = _safe_tracking_id(tracking.get("fb_pixel_id"))
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
        hotjar = _safe_tracking_id(tracking.get("hotjar_id"))
        if hotjar:
            head_scripts.append(
                f"<script>(function(h,o,t,j,a,r){{h.hj=h.hj||function(){{(h.hj.q=h.hj.q||[]).push(arguments)}};"
                f"h._hjSettings={{hjid:{hotjar},hjsv:6}};a=o.getElementsByTagName('head')[0];"
                f"r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;"
                f"a.appendChild(r)}})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');</script>"
            )

        # LinkedIn Insight
        linkedin = _safe_tracking_id(tracking.get("linkedin_id"))
        if linkedin:
            head_scripts.append(
                f'<script>_linkedin_partner_id="{linkedin}";window._linkedin_data_partner_ids='
                f'window._linkedin_data_partner_ids||[];window._linkedin_data_partner_ids.push(_linkedin_partner_id);</script>'
            )

        # GSC verification
        gsc = _safe_tracking_id(tracking.get("gsc_verification"))
        if gsc:
            head_scripts.append(f'<meta name="google-site-verification" content="{_e(gsc)}">')

        # Custom head / body — strip <script> tags to prevent XSS.
        # Users should use the tracking ID fields instead.
        def _strip_scripts(val: str | None) -> str:
            if not val:
                return ""
            return re.sub(r'<script[\s\S]*?</script>', '', val, flags=re.IGNORECASE)

        custom_head = _strip_scripts(tracking.get("custom_head", ""))
        # Only allow safe meta/link tags in custom_head (no style tags — prevents CSS injection)
        custom_head = re.sub(r'<(?!meta |link |!--)([^>]+)>', '', custom_head, flags=re.IGNORECASE)

        # Body scripts
        body_scripts = []

        # GTM noscript
        if gtm:
            body_scripts.append(
                f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm}" '
                f'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
            )

        # Custom body — strip scripts
        custom_body = _strip_scripts(tracking.get("custom_body", ""))

        # Newsletter signup
        newsletter_html = ""
        forms_config = config.get("forms", {}) or {}
        if forms_config.get("newsletter_enabled"):
            newsletter_html = self._build_newsletter_form(project)

        # Cookie banner
        cookie_html = ""
        cb = legal.get("cookie_banner", {})
        if isinstance(cb, dict) and cb.get("enabled"):
            style = cb.get("style", "bar")
            text = _e(cb.get("text", "Ta strona używa cookies. Kontynuując, akceptujesz ich użycie.") or "")
            cookie_html = self._build_cookie_banner(style, text)

        # Optimize images for CWV
        optimized_body = self._optimize_images_html(html_body)

        # Language
        lang = seo.get("language", "pl") or "pl"

        # Build full document
        return f"""<!DOCTYPE html>
<html lang="{lang}">
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{schema_jsonld}
<meta name="llms" content="/llms.txt">
<style>{css}</style>
{''.join(head_scripts)}
{custom_head or ''}
</head>
<body>
{''.join(body_scripts)}
{custom_body or ''}
{optimized_body}
{newsletter_html}
{cookie_html}
{self._build_tracker_script(project)}
</body>
</html>"""

    def _build_newsletter_form(self, project: Project) -> str:
        """Build sticky newsletter signup bar at bottom of page."""
        config = project.config_json or {}
        hosting = config.get("hosting", {}) or {}
        subdomain = hosting.get("subdomain") or project.domain or "site"

        return (
            f'<div id="newsletter-bar" style="background:var(--color-primary,#4F46E5);color:#fff;'
            f'padding:1.5rem;text-align:center">'
            f'<p style="margin:0 0 0.75rem;font-size:1.1rem;font-weight:600">Zapisz się do newslettera</p>'
            f'<form onsubmit="event.preventDefault();fetch(\'/sites/{subdomain}/form-submit\','
            f'{{method:\'POST\',headers:{{\'Content-Type\':\'application/json\'}},'
            f'body:JSON.stringify({{data:{{email:this.email.value,type:\'newsletter\'}}}})}})'
            f'.then(()=>{{this.innerHTML=\'<p>Dziękujemy za zapis!</p>\'}});" '
            f'style="display:flex;gap:0.5rem;max-width:480px;margin:0 auto">'
            f'<input type="email" name="email" required placeholder="Twój adres e-mail" '
            f'style="flex:1;padding:0.5rem 1rem;border-radius:var(--radius,8px);border:none;font-size:0.875rem">'
            f'<button type="submit" style="padding:0.5rem 1.5rem;background:#fff;color:var(--color-primary,#4F46E5);'
            f'border:none;border-radius:var(--radius,8px);font-weight:600;cursor:pointer;font-size:0.875rem">'
            f'Zapisz się</button></form></div>'
        )

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

    def _build_tracker_script(self, project: Project) -> str:
        """Build native JS tracker script for published page (Brief 38)."""
        config = project.config_json or {}
        seo = config.get("seo", {}) or {}
        tracking = seo.get("tracking", {}) or {}

        # Allow disabling native tracking
        if tracking.get("native_enabled") is False:
            return ""

        # Get site ID from published site
        hosting = config.get("hosting", {}) or {}
        subdomain = hosting.get("subdomain") or project.domain or ""

        # Backend URL for tracker endpoint
        from fasthub_core.config import get_settings
        settings = get_settings()
        backend_url = getattr(settings, "BACKEND_URL", "") or "https://api.webcreator.pl"

        # Site ID will be the published_site UUID — use project.id as fallback
        site_id = str(project.id)

        return (
            f'<script>window.__wct={{sid:"{site_id}",ep:"{backend_url}/api/v1/t"}};</script>\n'
            '<script>'
            "(function(){'use strict';var c=window.__wct||{};var SID=c.sid,EP=c.ep||'/t';"
            "if(!SID)return;"
            "function gid(k,s){var v=(s?sessionStorage.getItem(k):"
            "(document.cookie.match(new RegExp('(^| )'+k+'=([^;]+)'))||[])[2])||null;"
            "if(!v){v=Date.now().toString(36)+Math.random().toString(36).substr(2,9);"
            "s?sessionStorage.setItem(k,v):(document.cookie=k+'='+v+';max-age=31536000;path=/;SameSite=Lax');}"
            "return v;}"
            "var VID=gid('_wct_vid',0),SSID=gid('_wct_sid',1);"
            "function utm(){var p=new URLSearchParams(location.search),u={};"
            "['utm_source','utm_medium','utm_campaign','utm_term','utm_content'].forEach(function(k){"
            "var v=p.get(k);if(v)u[k]=v;});return Object.keys(u).length?u:null;}"
            "function dev(){var ua=navigator.userAgent,d='desktop';"
            "if(/Mobile|Android|iPhone/i.test(ua))d='mobile';"
            "else if(/Tablet|iPad/i.test(ua))d='tablet';"
            "var b='other';"
            "if(/Chrome/i.test(ua)&&!/Edge/i.test(ua))b='chrome';"
            "else if(/Firefox/i.test(ua))b='firefox';"
            "else if(/Safari/i.test(ua)&&!/Chrome/i.test(ua))b='safari';"
            "else if(/Edge/i.test(ua))b='edge';"
            "return{device:d,browser:b,screen_w:screen.width,screen_h:screen.height,language:navigator.language};}"
            "var Q=[],S=false;"
            "function t(type,data){Q.push({site_id:SID,visitor_id:VID,session_id:SSID,"
            "event_type:type,page_url:location.pathname,page_title:document.title,"
            "referrer:document.referrer||null,timestamp:new Date().toISOString(),data:data||{}});flush();}"
            "function flush(){if(S||!Q.length)return;S=true;var b=Q.splice(0,10);"
            "if(navigator.sendBeacon){navigator.sendBeacon(EP+'/events',JSON.stringify(b));S=false;if(Q.length)setTimeout(flush,100);}"
            "else{fetch(EP+'/events',{method:'POST',headers:{'Content-Type':'application/json'},"
            "body:JSON.stringify(b),keepalive:true}).finally(function(){S=false;if(Q.length)setTimeout(flush,100);});}}"
            "t('pageview',{utm:utm(),device:dev()});"
            "var mx=0,sm=[25,50,75,90,100],st={};"
            "window.addEventListener('scroll',function(){var s=window.pageYOffset,"
            "d=Math.max(document.body.scrollHeight,document.documentElement.scrollHeight)-window.innerHeight,"
            "p=d>0?Math.round(s/d*100):0;if(p>mx){mx=p;sm.forEach(function(m){"
            "if(p>=m&&!st[m]){st[m]=1;t('scroll',{depth:m});}});}},{passive:true});"
            "var T0=Date.now(),tt={},tm=[10,30,60,120,300];"
            "setInterval(function(){var e=Math.floor((Date.now()-T0)/1000);"
            "tm.forEach(function(m){if(e>=m&&!tt[m]){tt[m]=1;t('time_on_page',{seconds:m});}});},5000);"
            "document.addEventListener('click',function(e){var el=e.target.closest('a,button,[data-track]');"
            "if(!el)return;t('click',{tag:el.tagName.toLowerCase(),text:(el.innerText||'').substring(0,100),"
            "href:el.href||null});},true);"
            "document.addEventListener('submit',function(e){if(e.target.tagName==='FORM')"
            "t('form_submit',{form_id:e.target.id||null,fields_count:e.target.querySelectorAll('input,textarea,select').length});},true);"
            "function leave(){t('page_leave',{time_on_page_seconds:Math.floor((Date.now()-T0)/1000),max_scroll_depth:mx});flush();}"
            "window.addEventListener('beforeunload',leave);"
            "window.addEventListener('pagehide',leave);"
            "})();"
            '</script>'
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
Sitemap: https://{domain}/sitemap.xml

# AI Agents
User-agent: ChatGPT-User
Allow: /
User-agent: GPTBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: PerplexityBot
Allow: /"""

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
            safe_ty = html_mod.escape(str(thank_you))
            pages["dziekujemy.html"] = self._wrap_subpage(
                "Dziękujemy!", f"<div style='text-align:center;padding:4rem 1rem'><h1>Dziękujemy!</h1><p>{safe_ty}</p></div>",
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
<title>{html_mod.escape(title)} — {html_mod.escape(project.name or '')}</title>
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
    def _sanitize_subdomain(subdomain: str) -> str:
        """Ensure subdomain contains only valid characters."""
        import re as _re
        clean = _re.sub(r'[^a-z0-9-]', '', subdomain.lower().strip())
        clean = clean.strip('-')[:63]  # DNS label max 63 chars
        return clean or "site"

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
