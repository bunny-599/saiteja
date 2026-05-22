import asyncio
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from backend.scrapers.base import BaseScraper, logger
from backend.scrapers.search import SearchScraper
from backend.utils.cleaner import clean_review

class ReviewScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.search_scraper = SearchScraper()

    async def find_trustpilot_url(self, company_name: str, domain: str) -> str:
        """Search Google/Serper to find the correct Trustpilot page URL."""
        query = f"{company_name} reviews site:trustpilot.com"
        results = await self.search_scraper.search_serper(query, num=3)
        if not results:
            results = await self.search_scraper.search_duckduckgo_fallback(query)
            
        for res in results:
            link = res.get("link", "")
            if "trustpilot.com/review/" in link:
                logger.info(f"Found Trustpilot page via search: {link}")
                return link
        return f"https://www.trustpilot.com/review/{domain}"

    async def scrape_reviews(self, company_name: str, domain: str) -> Dict[str, Any]:
        """
        Scrapes Trustpilot for reviews of a given company.
        Fallback to search if default URL returns 404/not found.
        """
        url = f"https://www.trustpilot.com/review/{domain}"
        logger.info(f"Attempting to scrape Trustpilot for {company_name} at {url}")
        
        # Scrape with proxy enabled for Trustpilot to bypass bot checks
        try:
            html_content = await self.get_page_content_playwright(url, use_proxy=True)
            reviews = self.parse_trustpilot_html(html_content)
        except Exception as e:
            logger.warning(f"Direct Trustpilot scrape for {domain} failed: {e}. Trying search fallback...")
            reviews = []

        # If no reviews found, try finding URL via search
        if not reviews:
            search_url = await self.find_trustpilot_url(company_name, domain)
            if search_url and search_url != url:
                try:
                    html_content = await self.get_page_content_playwright(search_url, use_proxy=True)
                    reviews = self.parse_trustpilot_html(html_content)
                except Exception as e:
                    logger.error(f"Search-fallback Trustpilot scrape failed for {search_url}: {e}")
        
        # Calculate summary metrics if we found reviews
        if reviews:
            ratings = [r["rating"] for r in reviews if r["rating"] is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
            logger.info(f"Scraped {len(reviews)} reviews for {company_name}. Avg Rating: {avg_rating:.2f}")
            return {
                "company_name": company_name,
                "domain": domain,
                "reviews": reviews[:50],
                "average_rating": avg_rating,
                "review_count": len(reviews),
                "available": True
            }
        else:
            logger.warning(f"No Trustpilot reviews available for {company_name} ({domain})")
            return {
                "company_name": company_name,
                "domain": domain,
                "reviews": [],
                "average_rating": 0.0,
                "review_count": 0,
                "available": False,
                "note": "No Trustpilot data available"
            }

    def parse_trustpilot_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Parses Trustpilot HTML content and extracts reviews details."""
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, "html.parser")
        reviews = []
        
        # Search for article tags which usually represent individual reviews
        articles = soup.find_all("article")
        if not articles:
            # Fallback to search classes containing review card pattern
            articles = soup.select('div[class*="styles_reviewCard"]')
            
        for article in articles:
            try:
                # 1. Rating
                rating = None
                # Check for image alt text or star attributes
                star_div = article.select_one('div[data-consumer-review-rating]')
                if star_div and star_div.has_attr('data-consumer-review-rating'):
                    rating = int(star_div['data-consumer-review-rating'])
                else:
                    # Look inside imgs or svg attributes
                    imgs = article.find_all("img")
                    for img in imgs:
                        alt = img.get("alt", "")
                        if "Rated" in alt and "stars" in alt:
                            rating = int(alt.split("out of")[0].replace("Rated", "").strip())
                            break
                            
                # 2. Review Text & Title
                # The review text: typically has an attribute or specific class
                text_elem = article.select_one('p[data-consumer-review-text-attributes="true"]')
                if not text_elem:
                    text_elem = article.select_one('div[class*="styles_reviewContent"] p')
                if not text_elem:
                    # Generic lookup
                    text_elem = article.find("p", class_=lambda x: x and "reviewText" in x)
                
                review_text = text_elem.text.strip() if text_elem else ""
                
                # If there's a title, let's prepend it to the text for context
                title_elem = article.select_one('h2[data-consumer-review-title-attributes="true"]')
                if title_elem:
                    review_title = title_elem.text.strip()
                    if review_title:
                        review_text = f"{review_title}: {review_text}"
                
                if not review_text:
                    continue # Skip empty review contents
                    
                cleaned_text = clean_review(review_text)
                
                # 3. Date of review
                date_elem = article.find("time")
                date_str = ""
                if date_elem:
                    date_str = date_elem.get("datetime", date_elem.text.strip())
                
                # 4. Reviewer Location
                loc_elem = article.select_one('div[data-consumer-profile-location]')
                if not loc_elem:
                    loc_elem = article.find("span", class_=lambda x: x and "location" in x)
                location = loc_elem.text.strip() if loc_elem else "Unknown"
                
                reviews.append({
                    "rating": rating if rating else 5, # default fallback
                    "text": cleaned_text,
                    "date": date_str,
                    "location": location
                })
            except Exception as e:
                logger.debug(f"Error parsing single review item: {e}")
                continue
                
        return reviews
