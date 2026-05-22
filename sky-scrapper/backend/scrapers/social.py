import asyncio
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from backend.scrapers.base import BaseScraper, logger
from backend.scrapers.search import SearchScraper

class SocialScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.search_scraper = SearchScraper()

    async def get_social_handles(self, company_name: str) -> Dict[str, str]:
        """Discovers company social handles/URLs using Google Search/Serper."""
        handles = {"linkedin": "", "twitter": "", "instagram": ""}
        
        # Discover LinkedIn
        results = await self.search_scraper.search_serper(f"{company_name} linkedin company page")
        if not results:
            results = await self.search_scraper.search_duckduckgo_fallback(f"{company_name} linkedin company page")
        for res in results:
            link = res.get("link", "")
            if "linkedin.com/company/" in link:
                handles["linkedin"] = link
                break

        # Discover Twitter
        results = await self.search_scraper.search_serper(f"{company_name} twitter profile")
        if not results:
            results = await self.search_scraper.search_duckduckgo_fallback(f"{company_name} twitter profile")
        for res in results:
            link = res.get("link", "")
            if "twitter.com/" in link or "x.com/" in link:
                handle = link.split("/")[-1].split("?")[0]
                if handle and handle not in ["home", "search", "explore", "i"]:
                    handles["twitter"] = handle
                    break

        # Discover Instagram
        results = await self.search_scraper.search_serper(f"{company_name} instagram profile")
        if not results:
            results = await self.search_scraper.search_duckduckgo_fallback(f"{company_name} instagram profile")
        for res in results:
            link = res.get("link", "")
            if "instagram.com/" in link:
                handle = link.split("/")[-1].split("?")[0]
                if handle and handle not in ["p", "reels", "stories", "explore"]:
                    handles["instagram"] = handle
                    break

        logger.info(f"Discovered handles for {company_name}: {handles}")
        return handles

    async def scrape_linkedin(self, url: str) -> Dict[str, Any]:
        """Scrape public LinkedIn company page."""
        if not url:
            return {"follower_count": 0, "employee_count": 0, "recent_posts": []}
            
        logger.info(f"Scraping LinkedIn company page: {url}")
        try:
            # LinkedIn is heavily protected, so use ScraperAPI
            html_content = await self.get_page_content_playwright(url, use_proxy=True)
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Look for follower count and employee count in header or description
            text = soup.get_text()
            followers = 0
            employees = 0
            
            # Simple regex search
            fol_match = re.search(r'([\d,]+)\s+followers', text, re.IGNORECASE)
            if fol_match:
                followers = int(fol_match.group(1).replace(",", ""))
                
            emp_match = re.search(r'([\d,]+)\s+employees', text, re.IGNORECASE)
            if emp_match:
                employees = int(emp_match.group(1).replace(",", ""))
                
            # Fallback parsing in head (meta description)
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                content = meta_desc.get("content", "")
                if not followers:
                    fol_match = re.search(r'([\d,]+)\s+followers', content, re.IGNORECASE)
                    if fol_match:
                        followers = int(fol_match.group(1).replace(",", ""))
                if not employees:
                    emp_match = re.search(r'([\d,]+)\s+employees', content, re.IGNORECASE)
                    if emp_match:
                        employees = int(emp_match.group(1).replace(",", ""))
            
            # Parse updates if present
            posts = []
            post_elements = soup.select('li[class*="updates"]') or soup.select('div[class*="update-v2"]')
            for el in post_elements[:5]:
                text_el = el.select_one('p[class*="text"]') or el.select_one('span[class*="break-words"]')
                if text_el:
                    posts.append(text_el.text.strip())

            return {
                "follower_count": followers,
                "employee_count": employees,
                "recent_posts": posts,
                "url": url
            }
        except Exception as e:
            logger.warning(f"Error scraping LinkedIn {url}: {e}")
            return {"follower_count": 0, "employee_count": 0, "recent_posts": [], "error": str(e)}

    async def scrape_twitter(self, handle: str) -> Dict[str, Any]:
        """Scrape public Twitter profile via Nitter instance."""
        if not handle:
            return {"follower_count": 0, "recent_tweets": []}
            
        # Try a public nitter instance
        nitter_instances = ["https://nitter.poast.org", "https://nitter.net", "https://nitter.cz"]
        
        for instance in nitter_instances:
            url = f"{instance}/{handle}"
            logger.info(f"Scraping Twitter via Nitter: {url}")
            try:
                html_content = await self.get_page_content_playwright(url, use_proxy=False)
                if not html_content or "not found" in html_content.lower():
                    continue
                    
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Extract followers
                followers = 0
                fol_el = soup.select_one('.profile-stat-num') or soup.select_one('.followers .profile-stat-num')
                if fol_el:
                    fol_text = fol_el.text.strip().replace(",", "")
                    if "k" in fol_text.lower():
                        followers = int(float(fol_text.lower().replace("k", "")) * 1000)
                    elif "m" in fol_text.lower():
                        followers = int(float(fol_text.lower().replace("m", "")) * 1000000)
                    else:
                        try:
                            followers = int(fol_text)
                        except ValueError:
                            pass
                
                # Extract tweets
                tweets = []
                tweet_elements = soup.select('.tweet-content')
                for el in tweet_elements[:5]:
                    tweets.append(el.text.strip())
                    
                return {
                    "follower_count": followers,
                    "recent_tweets": tweets,
                    "url": f"https://twitter.com/{handle}"
                }
            except Exception as e:
                logger.warning(f"Error scraping Nitter at {instance}: {e}")
                continue
                
        # Return fallback
        return {"follower_count": 0, "recent_tweets": [], "url": f"https://twitter.com/{handle}"}

    async def scrape_instagram(self, handle: str) -> Dict[str, Any]:
        """Scrape public Instagram bio and follower count."""
        if not handle:
            return {"follower_count": 0, "post_count": 0, "bio": ""}
            
        url = f"https://www.instagram.com/{handle}/"
        logger.info(f"Scraping Instagram profile: {url}")
        
        try:
            # Instagram blocks aggressively, parse meta tags from the raw page
            html_content = await self.get_page_content_playwright(url, use_proxy=True)
            soup = BeautifulSoup(html_content, "html.parser")
            
            followers = 0
            posts = 0
            bio = ""
            
            # Parse from meta description tag:
            # "<meta content="12M Followers, 250 Following, 1,234 Posts - See Instagram photos and videos from..." name="description">"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                content = meta_desc.get("content", "")
                # Extract followers
                fol_match = re.search(r'([\d,kKmM\.]+)\s+Followers', content, re.IGNORECASE)
                if fol_match:
                    fol_text = fol_match.group(1).replace(",", "")
                    if "k" in fol_text.lower():
                        followers = int(float(fol_text.lower().replace("k", "")) * 1000)
                    elif "m" in fol_text.lower():
                        followers = int(float(fol_text.lower().replace("m", "")) * 1000000)
                    else:
                        try:
                            followers = int(fol_text)
                        except ValueError:
                            pass
                            
                # Extract posts
                posts_match = re.search(r'([\d,kKmM\.]+)\s+Posts', content, re.IGNORECASE)
                if posts_match:
                    posts_text = posts_match.group(1).replace(",", "")
                    try:
                        posts = int(posts_text)
                    except ValueError:
                        pass
            
            # Extract bio from meta title or JSON-LD if available
            title_tag = soup.find("title")
            if title_tag:
                bio = title_tag.text.strip()
                
            return {
                "follower_count": followers,
                "post_count": posts,
                "bio": bio,
                "url": url
            }
        except Exception as e:
            logger.warning(f"Error scraping Instagram {handle}: {e}")
            return {"follower_count": 0, "post_count": 0, "bio": "", "error": str(e)}

    async def scrape_all_social(self, company_name: str) -> Dict[str, Any]:
        """Main entry point to discover and scrape all social platforms."""
        handles = await self.get_social_handles(company_name)
        
        # Run scraping concurrently
        linkedin_task = self.scrape_linkedin(handles["linkedin"])
        twitter_task = self.scrape_twitter(handles["twitter"])
        instagram_task = self.scrape_instagram(handles["instagram"])
        
        linkedin_res, twitter_res, instagram_res = await asyncio.gather(
            linkedin_task, twitter_task, instagram_task
        )
        
        return {
            "linkedin": linkedin_res,
            "twitter": twitter_res,
            "instagram": instagram_res
        }
