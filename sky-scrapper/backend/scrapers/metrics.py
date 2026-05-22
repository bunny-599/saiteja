import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from backend.scrapers.base import BaseScraper, logger
from backend.scrapers.search import SearchScraper

class MetricsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.search_scraper = SearchScraper()

    async def find_growjo_url(self, company_name: str) -> Optional[str]:
        """Find the Growjo profile URL for a company via Google search."""
        query = f"site:growjo.com {company_name}"
        results = await self.search_scraper.search_serper(query, num=3)
        if not results:
            results = await self.search_scraper.search_duckduckgo_fallback(query)
            
        for res in results:
            link = res.get("link", "")
            if "growjo.com/company/" in link:
                logger.info(f"Found Growjo page for {company_name} via search: {link}")
                return link
        return None

    def clean_metric_string(self, text: str) -> str:
        """Helper to extract and clean metric strings."""
        if not text:
            return "N/A"
        return text.strip().replace("\n", " ").replace("\r", "")

    async def scrape_growjo(self, company_name: str, domain: str) -> Dict[str, Any]:
        """Scrape company financial and growth metrics from Growjo."""
        logger.info(f"Attempting to scrape Growjo metrics for {company_name}")
        
        # 1. Resolve Growjo URL
        url = await self.find_growjo_url(company_name)
        if not url:
            # Try forming a default URL
            slug = company_name.lower().replace(" ", "-").replace(".", "").replace(",", "")
            url = f"https://growjo.com/company/{slug}"
            
        try:
            # Fetch Growjo page
            html_content = await self.get_page_content_playwright(url, use_proxy=False)
            if not html_content or "not found" in html_content.lower() or "404" in html_content:
                logger.warning(f"Growjo page not found or empty for {company_name}. Using fallback.")
                return await self.fallback_metrics_search(company_name, domain)
                
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Initialize metrics dict
            metrics = {
                "company_name": company_name,
                "domain": domain,
                "revenue": "N/A",
                "employees": "N/A",
                "growth_percentage": "N/A",
                "funding": "N/A",
                "hq_location": "N/A",
                "source": "Growjo"
            }
            
            # Extract metrics from page content
            text_content = soup.get_text(" ")
            
            # Revenue (e.g. "Estimated Revenue is $54.2 M")
            rev_match = re.search(r'(?:Estimated Revenue|Revenue|Est\. Revenue)\s*(?:is)?\s*(\$[\d\.]+\s*[MBBillionMillion]*)', text_content, re.IGNORECASE)
            if rev_match:
                metrics["revenue"] = rev_match.group(1).strip()
            
            # Employees (e.g. "Employee Count: 120" or "Growjo has 120 employees")
            emp_match = re.search(r'(?:Employee Count|Total Employees|Employees|Number of employees)\s*(?:is)?\s*([\d,]+)', text_content, re.IGNORECASE)
            if emp_match:
                metrics["employees"] = emp_match.group(1).strip()
            
            # Growth percentage
            growth_match = re.search(r'(?:Growth|Growth Rate|Employee Growth)\s*(?:is)?\s*([\d\.-]+%)', text_content, re.IGNORECASE)
            if growth_match:
                metrics["growth_percentage"] = growth_match.group(1).strip()
                
            # HQ Location
            hq_match = re.search(r'(?:HQ|Headquarters|Location|HQ Location|based in)\s*(?:is)?\s*([A-Za-z\s,\.]+)(?:\.|\n|\r|and)', text_content, re.IGNORECASE)
            if hq_match:
                loc = hq_match.group(1).strip()
                # filter out unrelated descriptions
                if len(loc) < 50:
                    metrics["hq_location"] = loc
                    
            # Funding
            funding_match = re.search(r'(?:Total Funding|Funding|Raised|Funding Amount)\s*(?:is)?\s*(\$[\d\.]+\s*[MBBillionMillion]*)', text_content, re.IGNORECASE)
            if funding_match:
                metrics["funding"] = funding_match.group(1).strip()
            
            # Double check table elements if regex was not fully successful
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = [c.text.strip() for c in row.find_all(["td", "th"])]
                    if len(cells) >= 2:
                        label = cells[0].lower()
                        val = cells[1]
                        if "revenue" in label and metrics["revenue"] == "N/A":
                            metrics["revenue"] = val
                        elif "employees" in label and metrics["employees"] == "N/A":
                            metrics["employees"] = val
                        elif "growth" in label and metrics["growth_percentage"] == "N/A":
                            metrics["growth_percentage"] = val
                        elif "location" in label or "hq" in label and metrics["hq_location"] == "N/A":
                            metrics["hq_location"] = val
                        elif "funding" in label and metrics["funding"] == "N/A":
                            metrics["funding"] = val
                            
            logger.info(f"Extracted Growjo metrics for {company_name}: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error scraping Growjo for {company_name}: {e}")
            return await self.fallback_metrics_search(company_name, domain)

    async def fallback_metrics_search(self, company_name: str, domain: str) -> Dict[str, Any]:
        """Fallback to Google/Serper search snippets to extract company stats."""
        logger.info(f"Falling back to Serper metrics search for {company_name}")
        query = f'"{company_name}" funding revenue employees site:crunchbase.com OR site:linkedin.com'
        results = await self.search_scraper.search_serper(query, num=5)
        if not results:
            results = await self.search_scraper.search_duckduckgo_fallback(query)
            
        combined_snippets = " ".join([res.get("snippet", "") for res in results])
        
        metrics = {
            "company_name": company_name,
            "domain": domain,
            "revenue": "N/A",
            "employees": "N/A",
            "growth_percentage": "N/A",
            "funding": "N/A",
            "hq_location": "N/A",
            "source": "Search Fallback (LinkedIn/Crunchbase)"
        }
        
        # Regex search on combined snippets
        rev_match = re.search(r'(?:revenue|valuation|worth|sales)\s*(?:of|is|around|estimated)?\s*(\$[\d\.]+\s*[MBBillionMillion]*)', combined_snippets, re.IGNORECASE)
        if rev_match:
            metrics["revenue"] = rev_match.group(1).strip()
            
        emp_match = re.search(r'([\d,]+)\s*(?:employees|people|staff|workers)', combined_snippets, re.IGNORECASE)
        if emp_match:
            metrics["employees"] = emp_match.group(1).strip()
            
        fund_match = re.search(r'(?:raised|funding|total funding|funding of)\s*(\$[\d\.]+\s*[MBBillionMillion]*)', combined_snippets, re.IGNORECASE)
        if fund_match:
            metrics["funding"] = fund_match.group(1).strip()
            
        loc_match = re.search(r'(?:headquartered in|based in|hq in)\s*([A-Za-z\s,\.]+)', combined_snippets, re.IGNORECASE)
        if loc_match:
            loc = loc_match.group(1).strip()
            if len(loc) < 40:
                metrics["hq_location"] = loc
                
        logger.info(f"Fallback metrics extracted for {company_name}: {metrics}")
        return metrics
