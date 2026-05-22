import asyncio
import urllib.parse
import xml.etree.ElementTree as ET
import datetime
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from backend.scrapers.base import BaseScraper, logger

class NewsScraper(BaseScraper):
    async def fetch_google_news_rss(self, company_name: str) -> List[Dict[str, Any]]:
        """Fetch news articles from Google News RSS feed."""
        encoded_query = urllib.parse.quote_plus(company_name)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"
        
        logger.info(f"Fetching Google News RSS for: {company_name}")
        articles = []
        try:
            headers = self.get_headers()
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                xml_content = response.text
                
            # Parse XML
            root = ET.fromstring(xml_content)
            items = root.findall(".//item")
            
            for item in items[:30]: # Get top 30 to sort and filter
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date_str = item.find("pubDate").text if item.find("pubDate") is not None else ""
                source_el = item.find("source")
                source = source_el.text if source_el is not None else "Google News"
                
                # Parse date
                pub_date = None
                if pub_date_str:
                    try:
                        # RFC 822 date format: "Tue, 19 May 2026 12:00:00 GMT"
                        pub_date = datetime.datetime.strptime(pub_date_str[:25].strip(), "%a, %d %b %Y %H:%M:%S")
                    except Exception:
                        pass
                
                # Extract clean title and source
                # Google News titles are usually: "Headline - Source Name"
                headline = title
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    headline = parts[0]
                    if source == "Google News" and len(parts) > 1:
                        source = parts[1]
                
                # Extract summary from HTML description
                description = ""
                desc_el = item.find("description")
                if desc_el is not None and desc_el.text:
                    desc_soup = BeautifulSoup(desc_el.text, "html.parser")
                    # Grab text from list links or description
                    description = desc_soup.get_text().strip()
                    # Truncate summary if too long
                    if len(description) > 200:
                        description = description[:200] + "..."
                        
                articles.append({
                    "headline": headline,
                    "url": link,
                    "date": pub_date_str,
                    "parsed_date": pub_date or datetime.datetime.utcnow(),
                    "source": source,
                    "summary": description or f"Latest news coverage about {company_name} from {source}."
                })
        except Exception as e:
            logger.error(f"Error fetching Google News RSS: {e}")
            
        return articles

    async def scrape_techcrunch_search(self, company_name: str) -> List[Dict[str, Any]]:
        """Scrape TechCrunch search for articles about the company."""
        encoded_query = urllib.parse.quote_plus(company_name)
        url = f"https://techcrunch.com/?s={encoded_query}"
        
        logger.info(f"Scraping TechCrunch search for: {company_name}")
        articles = []
        try:
            # TechCrunch search is loaded dynamically or standard Wordpress loop
            html_content = await self.get_page_content_playwright(url, use_proxy=False)
            if not html_content:
                return []
                
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Find TechCrunch post blocks
            # TechCrunch uses classes like 'post-block' or 'wp-block-post'
            posts = soup.select('.post-block') or soup.select('article')
            
            for post in posts[:10]:
                title_el = post.select_one('.post-block__title__link') or post.find('h2') or post.find('a')
                if not title_el:
                    continue
                    
                headline = title_el.text.strip()
                link = title_el.get('href', '') if hasattr(title_el, 'get') else ''
                if not link and title_el.find('a'):
                    link = title_el.find('a').get('href', '')
                    
                if not headline or not link:
                    continue
                    
                # Extract meta details
                date_el = post.select_one('time')
                date_str = ""
                pub_date = None
                if date_el:
                    date_str = date_el.text.strip()
                    datetime_attr = date_el.get('datetime', '')
                    if datetime_attr:
                        try:
                            # Parse "2026-05-19T10:00:00-07:00"
                            pub_date = datetime.datetime.fromisoformat(datetime_attr)
                        except Exception:
                            pass
                
                # Extract summary/excerpt
                excerpt_el = post.select_one('.post-block__content') or post.select_one('p')
                summary = excerpt_el.text.strip() if excerpt_el else f"TechCrunch article covering {company_name}."
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                    
                articles.append({
                    "headline": headline,
                    "url": link,
                    "date": date_str or str(pub_date or datetime.datetime.utcnow().date()),
                    "parsed_date": pub_date or datetime.datetime.utcnow(),
                    "source": "TechCrunch",
                    "summary": summary
                })
        except Exception as e:
            logger.warning(f"Error scraping TechCrunch for {company_name}: {e}")
            
        return articles

    async def get_latest_news(self, company_name: str) -> List[Dict[str, Any]]:
        """Collects and aggregates news from Google News RSS and TechCrunch, returning sorted items."""
        google_news_task = self.fetch_google_news_rss(company_name)
        tc_news_task = self.scrape_techcrunch_search(company_name)
        
        google_news, tc_news = await asyncio.gather(google_news_task, tc_news_task)
        
        all_news = google_news + tc_news
        
        # Deduplicate by URL or Headline similarity
        seen_urls = set()
        seen_headlines = set()
        deduped_news = []
        
        for item in all_news:
            url = item["url"]
            headline_lower = item["headline"].lower().strip()
            
            # Simple clean up of URL (remove query parameters)
            clean_url = url.split("?")[0]
            
            if clean_url in seen_urls or headline_lower in seen_headlines:
                continue
                
            seen_urls.add(clean_url)
            seen_headlines.add(headline_lower)
            deduped_news.append(item)
            
        # Sort by parsed_date desc
        deduped_news.sort(key=lambda x: x["parsed_date"], reverse=True)
        
        # Convert parsed_date to string for JSON serialization
        final_news = []
        for item in deduped_news[:20]:
            item_copy = item.copy()
            if "parsed_date" in item_copy:
                del item_copy["parsed_date"]
            final_news.append(item_copy)
            
        logger.info(f"Aggregated {len(final_news)} unique news items for {company_name}")
        return final_news
