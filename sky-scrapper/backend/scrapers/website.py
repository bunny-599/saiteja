import asyncio
import urllib.parse
from typing import Dict, List, Any, Set
from bs4 import BeautifulSoup
from backend.scrapers.base import BaseScraper, logger
from backend.utils.cleaner import clean_text_for_ai

TECH_KEYWORDS = [
    "AWS", "Azure", "Google Cloud", "Kubernetes", "Docker", "React", "Vue", "Angular",
    "Node.js", "Python", "Django", "FastAPI", "Flask", "Go", "Golang", "Rust", "Java",
    "Spring Boot", "Ruby on Rails", "PHP", "Laravel", "MySQL", "PostgreSQL", "MongoDB",
    "Redis", "Elasticsearch", "Salesforce", "Stripe", "Zapier", "GraphQL", "TensorFlow",
    "PyTorch", "OpenAI", "Shopify", "Wordpress", "Webflow", "Next.js", "Tailwind"
]

class WebsiteScraper(BaseScraper):
    def get_absolute_url(self, base: str, href: str) -> str:
        """Resolve a relative URL to an absolute one."""
        return urllib.parse.urljoin(base, href)

    def extract_subpage_links(self, html: str, base_url: str) -> Dict[str, str]:
        """Scans homepage HTML for About, Pricing, and Features links."""
        soup = BeautifulSoup(html, "html.parser")
        links = {"about": "", "pricing": "", "features": ""}
        
        # Norm base URL
        parsed_base = urllib.parse.urlparse(base_url)
        base_domain = parsed_base.netloc
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            text = a_tag.text.strip().lower()
            
            # Get absolute URL
            abs_url = self.get_absolute_url(base_url, href)
            parsed_abs = urllib.parse.urlparse(abs_url)
            
            # Only follow links on same domain
            if parsed_abs.netloc != base_domain:
                continue
                
            path = parsed_abs.path.lower()
            
            # Check About page link
            if not links["about"]:
                if "about" in text or "about" in path or "company" in text or "team" in text:
                    links["about"] = abs_url
                    continue
                    
            # Check Pricing page link
            if not links["pricing"]:
                if "pricing" in text or "pricing" in path or "plans" in text or "price" in path:
                    links["pricing"] = abs_url
                    continue
                    
            # Check Features page link
            if not links["features"]:
                if "feature" in text or "product" in text or "features" in path or "platform" in text or "solution" in text or "solution" in path:
                    links["features"] = abs_url
                    
        return links

    def detect_tech_stack(self, text: str) -> List[str]:
        """Detect tech stack clues from web page copy."""
        detected = []
        text_upper = f" {text} ".replace(",", " ").replace(".", " ").replace("(", " ").replace(")", " ")
        for tech in TECH_KEYWORDS:
            # Match word boundary
            pattern = rf"\b{re.escape(tech)}\b"
            if re.search(pattern, text_upper, re.IGNORECASE):
                detected.append(tech)
        return list(set(detected))

    async def scrape_page_content(self, url: str) -> Dict[str, str]:
        """Scrapes a page and returns its cleaned text and raw HTML."""
        try:
            # We use ScraperAPI proxy for corporate homepages to avoid bot blocks
            html_content = await self.get_page_content_playwright(url, use_proxy=True)
            cleaned_text = clean_text_for_ai(html_content)
            return {"text": cleaned_text, "html": html_content, "url": url}
        except Exception as e:
            logger.warning(f"Failed to scrape webpage {url}: {e}")
            return {"text": "", "html": "", "url": url}

    async def scrape_full_website(self, domain: str) -> Dict[str, Any]:
        """Scrapes homepage, /about, /pricing, and /features pages for intelligence."""
        # Ensure url starts with https://
        base_url = f"https://{domain}"
        logger.info(f"Starting crawl of website: {base_url}")
        
        # Scrape Homepage
        homepage_data = await self.scrape_page_content(base_url)
        if not homepage_data["text"]:
            # Try http fallback
            base_url = f"http://domain"
            homepage_data = await self.scrape_page_content(f"http://{domain}")
            
        html = homepage_data["html"]
        homepage_text = homepage_data["text"]
        
        # Extract metadata taglines
        tagline = "N/A"
        val_prop = "N/A"
        if html:
            soup = BeautifulSoup(html, "html.parser")
            # Tagline / Title
            title_tag = soup.find("title")
            if title_tag:
                tagline = title_tag.text.strip()
                
            # Meta description
            meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            if meta_desc:
                val_prop = meta_desc.get("content", "").strip()
                
        # Find subpage links
        subpage_links = {}
        if html:
            subpage_links = self.extract_subpage_links(html, base_url)
            logger.info(f"Discovered subpages for {domain}: {subpage_links}")
            
        # Scrape subpages concurrently
        tasks = {}
        for key, url in subpage_links.items():
            if url:
                tasks[key] = self.scrape_page_content(url)
                
        subpage_results = {}
        if tasks:
            keys = list(tasks.keys())
            results = await asyncio.gather(*[tasks[k] for k in keys])
            for k, res in zip(keys, results):
                subpage_results[k] = res
                
        # Aggregate all text
        full_scraped_text = f"HOMEPAGE CONTENT:\n{homepage_text}\n\n"
        for key, res in subpage_results.items():
            if res["text"]:
                full_scraped_text += f"{key.upper()} PAGE CONTENT:\n{res['text']}\n\n"
                
        # Detect Tech Stack
        tech_clues = self.detect_tech_stack(full_scraped_text)
        
        # Extract features and pricing clues using text search
        pricing_clues = []
        about_clues = []
        
        pricing_text = subpage_results.get("pricing", {}).get("text", "")
        if pricing_text:
            # Extract paragraphs mentioning numbers or symbols
            lines = pricing_text.split(".")
            for line in lines:
                if any(sym in line for sym in ["$", "€", "£", "free", "pricing", "month", "year", "custom"]):
                    pricing_clues.append(line.strip())
                    
        return {
            "domain": domain,
            "url": base_url,
            "tagline": tagline,
            "value_proposition": val_prop,
            "subpage_urls": subpage_links,
            "detected_tech_stack": tech_clues,
            "scraped_text": full_scraped_text,
            "pricing_clues": pricing_clues[:10],
            "about_clues": subpage_results.get("about", {}).get("text", "")[:500]
        }
import re
