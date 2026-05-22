import asyncio
import random
import logging
from typing import Dict, Any, Optional
import httpx
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from backend.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapers.base")

# Global usage counters for paid services
usage_stats = {
    "serper_calls": 0,
    "scraperapi_calls": 0,
    "direct_scrapes": 0
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
]

class BaseScraper:
    def __init__(self):
        self.user_agents = USER_AGENTS

    def get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)

    def get_random_viewport(self) -> Dict[str, int]:
        return {
            "width": random.randint(1280, 1920),
            "height": random.randint(720, 1080)
        }

    def get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "User-Agent": self.get_random_user_agent(),
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8,en;q=0.5"]),
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive"
        }
        if referer:
            headers["Referer"] = referer
        else:
            headers["Referer"] = random.choice([
                "https://www.google.com/",
                "https://www.bing.com/",
                "https://duckduckgo.com/"
            ])
        return headers

    async def random_delay(self):
        delay = random.uniform(1.5, 4.5)
        logger.info(f"Adding random delay of {delay:.2f} seconds...")
        await asyncio.sleep(delay)

    def wrap_scraperapi_url(self, target_url: str) -> str:
        if settings.SCRAPERAPI_KEY:
            usage_stats["scraperapi_calls"] += 1
            logger.info(f"Wrapping URL in ScraperAPI proxy. Total ScraperAPI calls: {usage_stats['scraperapi_calls']}")
            return f"http://api.scraperapi.com?api_key={settings.SCRAPERAPI_KEY}&url={target_url}"
        else:
            usage_stats["direct_scrapes"] += 1
            logger.warning("ScraperAPI key missing, falling back to direct request.")
            return target_url

    async def get_page_content_playwright(self, url: str, use_proxy: bool = False, wait_selector: Optional[str] = None) -> str:
        """Launches Playwright, navigates to the url, applies stealth, and returns HTML content."""
        await self.random_delay()
        
        target_url = self.wrap_scraperapi_url(url) if use_proxy else url
        if not use_proxy:
            usage_stats["direct_scrapes"] += 1

        logger.info(f"Navigating to {url} using Playwright (proxy={use_proxy})...")
        
        async with async_playwright() as p:
            # Configure launch arguments
            browser = await p.chromium.launch(
                headless=settings.PLAYWRIGHT_HEADLESS,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            
            ua = self.get_random_user_agent()
            viewport = self.get_random_viewport()
            
            context = await browser.new_context(
                user_agent=ua,
                viewport=viewport,
                extra_http_headers=self.get_headers()
            )
            
            page = await context.new_page()
            
            # Apply stealth mode if playwright-stealth is available
            try:
                from playwright_stealth import stealth_async
                await stealth_async(page)
            except Exception as e:
                logger.warning(f"Could not load playwright-stealth: {e}")

            try:
                # Add a timeout of 30 seconds
                await page.goto(target_url, timeout=40000, wait_until="domcontentloaded")
                
                # If there's a selector we need to wait for (e.g. for dynamic pages)
                if wait_selector:
                    try:
                        await page.wait_for_selector(wait_selector, timeout=10000)
                    except Exception as e:
                        logger.warning(f"Timeout waiting for selector '{wait_selector}': {e}")
                
                # Scroll down a bit to trigger lazy loads
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
                await asyncio.sleep(1)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2 / 3)")
                await asyncio.sleep(1)
                
                content = await page.content()
                return content
            except Exception as e:
                logger.error(f"Error during Playwright scrape of {url}: {e}")
                # Fallback if ScraperAPI fails
                if use_proxy:
                    logger.info("Retrying with direct scraping (no proxy) after error...")
                    return await self.get_page_content_playwright(url, use_proxy=False, wait_selector=wait_selector)
                raise e
            finally:
                await context.close()
                await browser.close()

    async def fetch_json_with_retry(self, url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Dict[str, Any]:
        """Fetch JSON data from an API with a retry mechanism and backoff."""
        async with httpx.AsyncClient(timeout=20.0) as client:
            for attempt in range(retries):
                try:
                    response = await client.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt == retries - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt + random.uniform(0.5, 1.5))
        return {}
