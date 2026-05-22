import urllib.parse
import asyncio
from typing import List, Dict, Any
import httpx
from backend.scrapers.base import BaseScraper, logger, usage_stats
from backend.config import settings

class SearchScraper(BaseScraper):
    async def search_serper(self, query: str, num: int = 10) -> List[Dict[str, Any]]:
        """Call Serper API to get Google Search results."""
        if not settings.SERPER_API_KEY:
            logger.warning("SERPER_API_KEY not found in settings. Skipping Serper.")
            return []

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": settings.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": num
        }
        
        try:
            usage_stats["serper_calls"] += 1
            logger.info(f"Querying Serper API with: '{query}'. Total Serper calls: {usage_stats['serper_calls']}")
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("organic", [])
        except Exception as e:
            logger.error(f"Serper API search error for query '{query}': {e}")
            return []

    async def search_duckduckgo_fallback(self, query: str) -> List[Dict[str, Any]]:
        """Fallback search using DuckDuckGo HTML parsing if Serper API is unavailable."""
        logger.info(f"Using DuckDuckGo fallback search for: '{query}'")
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        try:
            # We use direct playwright or httpx to get the HTML
            headers = self.get_headers()
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html_content = response.text
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            results = []
            
            # DuckDuckGo HTML layout
            links = soup.find_all("a", class_="result__url")
            snippets = soup.find_all("a", class_="result__snippet")
            titles = soup.find_all("a", class_="result__snippet") # or result__a
            
            # Find result blocks
            blocks = soup.find_all("div", class_="result__body")
            for block in blocks:
                title_elem = block.find("a", class_="result__a")
                snippet_elem = block.find("a", class_="result__snippet")
                if title_elem and snippet_elem:
                    title = title_elem.text.strip()
                    link = title_elem.get("href", "")
                    # Extract final url from DDG redirect url
                    parsed_url = urllib.parse.urlparse(link)
                    qs = urllib.parse.parse_qs(parsed_url.query)
                    if 'uddg' in qs:
                        link = qs['uddg'][0]
                    
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet_elem.text.strip()
                    })
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo fallback search error: {e}")
            return []

    def clean_domain(self, url: str) -> str:
        """Extract main domain from URL (e.g. https://www.google.com/foo -> google.com)."""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = domain.split(":")[0]  # Remove port
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return url

    async def discover_competitors(self, company_name: str, industry: str) -> List[Dict[str, Any]]:
        """
        Discovers top 5 competitors for a target company.
        Queries Serper API or falls back to DuckDuckGo, parses domains, profiles, and names.
        """
        queries = [
            f"{company_name} competitors",
            f"companies like {company_name}",
            f"best {industry} alternatives to {company_name}"
        ]
        
        raw_results = []
        for query in queries:
            results = await self.search_serper(query)
            if not results:
                results = await self.search_duckduckgo_fallback(query)
            raw_results.extend(results)
            await asyncio.sleep(1) # short gap
            
        # Parse and filter unique competitors (exclude the company itself and major non-company directories like Wikipedia, G2, etc.)
        target_domain = self.clean_domain(company_name.lower())
        banned_domains = {
            "wikipedia.org", "g2.com", "capterra.com", "linkedin.com", "crunchbase.com", 
            "youtube.com", "facebook.com", "twitter.com", "reddit.com", "github.com",
            "glassdoor.com", "indeed.com", "quora.com", "medium.com", "pinterest.com",
            "instagram.com", "tracxn.com", "zoominfo.com", "pitchbook.com", "trustpilot.com"
        }
        
        seen_domains = set()
        seen_domains.add(target_domain)
        # also add variants of company name
        seen_domains.add(company_name.lower() + ".com")
        
        competitors = []
        
        for res in raw_results:
            link = res.get("link", "")
            title = res.get("title", "")
            snippet = res.get("snippet", "")
            
            if not link:
                continue
                
            domain = self.clean_domain(link)
            if not domain or domain in seen_domains or any(banned in domain for banned in banned_domains):
                continue
                
            # Try to infer competitor name from Title/Domain
            # e.g. "CompetitorName: The Best..." -> "CompetitorName"
            comp_name = domain.split('.')[0].capitalize()
            if "-" in comp_name:
                comp_name = " ".join([w.capitalize() for w in comp_name.split("-")])
            
            seen_domains.add(domain)
            competitors.append({
                "name": comp_name,
                "domain": domain,
                "url": f"https://{domain}",
                "description": snippet
            })
            
            if len(competitors) >= 5:
                break
                
        # If we got fewer than 5, try a general industry query
        if len(competitors) < 5:
            industry_query = f"top {industry} software companies"
            results = await self.search_serper(industry_query)
            if not results:
                results = await self.search_duckduckgo_fallback(industry_query)
            for res in results:
                link = res.get("link", "")
                snippet = res.get("snippet", "")
                domain = self.clean_domain(link)
                if not domain or domain in seen_domains or any(banned in domain for banned in banned_domains):
                    continue
                comp_name = domain.split('.')[0].capitalize()
                seen_domains.add(domain)
                competitors.append({
                    "name": comp_name,
                    "domain": domain,
                    "url": f"https://{domain}",
                    "description": snippet
                })
                if len(competitors) >= 5:
                    break
                    
        logger.info(f"Discovered {len(competitors)} competitors: {[c['name'] for c in competitors]}")
        return competitors[:5]
