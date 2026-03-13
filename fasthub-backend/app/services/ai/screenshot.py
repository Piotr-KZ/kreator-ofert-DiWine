"""
Screenshot Service — renders HTML in Playwright browser and takes screenshots.
Used by AIVisionService for feedback loop and visual review.
"""

import logging

logger = logging.getLogger(__name__)


class ScreenshotService:
    """Renders HTML in a headless Playwright browser and captures PNG screenshots.

    Uses singleton browser pattern — one browser instance for all screenshots.
    """

    VIEWPORTS = {
        "desktop": {"width": 1920, "height": 1080},
        "tablet": {"width": 768, "height": 1024},
        "mobile": {"width": 375, "height": 812},
    }

    _browser = None
    _playwright = None

    @classmethod
    async def get_browser(cls):
        if cls._browser is None:
            from playwright.async_api import async_playwright

            cls._playwright = await async_playwright().start()
            cls._browser = await cls._playwright.chromium.launch(headless=True)
        return cls._browser

    @classmethod
    async def shutdown(cls):
        if cls._browser:
            await cls._browser.close()
            cls._browser = None
        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None

    async def capture(self, project, viewport: str = "desktop") -> bytes:
        """Screenshot of project page from blocks.

        1. Render HTML from blocks + styles
        2. Playwright opens page → screenshot
        """
        from app.services.creator.renderer import render_project_html

        html, css = await render_project_html(project)
        return await self.capture_from_html(html, css, viewport)

    async def capture_from_html(
        self,
        html: str,
        css: str,
        viewport: str = "desktop",
    ) -> bytes:
        """Screenshot from raw HTML + CSS.

        Returns:
            PNG bytes
        """
        vp = self.VIEWPORTS[viewport]

        full_html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{css}</style>
</head>
<body>{html}</body>
</html>"""

        browser = await self.get_browser()
        page = await browser.new_page(viewport=vp)

        try:
            await page.set_content(full_html, wait_until="networkidle")
            screenshot = await page.screenshot(full_page=True, type="png")
        finally:
            await page.close()

        return screenshot
