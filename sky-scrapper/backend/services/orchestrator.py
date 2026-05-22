import datetime
import uuid
import asyncio
from typing import Dict, Any, List
from sqlalchemy.future import select
from backend.database import async_session_maker
from backend.models import AnalysisJob, CompanyCache
from backend.scrapers.search import SearchScraper
from backend.scrapers.reviews import ReviewScraper
from backend.scrapers.website import WebsiteScraper
from backend.scrapers.social import SocialScraper
from backend.scrapers.ads import AdsScraper
from backend.scrapers.news import NewsScraper
from backend.scrapers.metrics import MetricsScraper
from backend.scrapers.base import logger, usage_stats
from backend.ai.analyzer import AIAnalyzer

class Orchestrator:
    def __init__(self):
        self.search_scraper = SearchScraper()
        self.review_scraper = ReviewScraper()
        self.website_scraper = WebsiteScraper()
        self.social_scraper = SocialScraper()
        self.ads_scraper = AdsScraper()
        self.news_scraper = NewsScraper()
        self.metrics_scraper = MetricsScraper()
        self.analyzer = AIAnalyzer()

    async def log_step(self, job_id: str, message: str, progress: int = None, status: str = None):
        """Helper to append a log line and update progress/status of a job in the database."""
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {"time": timestamp, "message": message}
        logger.info(f"Job {job_id} Log: {message}")
        
        async with async_session_maker() as session:
            try:
                # Find the job
                stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
                result = await session.execute(stmt)
                job = result.scalars().first()
                if job:
                    # Update fields
                    current_logs = list(job.logs or [])
                    current_logs.append(log_entry)
                    job.logs = current_logs
                    if progress is not None:
                        job.progress = progress
                    if status is not None:
                        job.status = status
                    
                    await session.commit()
            except Exception as e:
                logger.error(f"Error updating job logs in database for {job_id}: {e}")

    async def return_dummy(self, value):
        """Helper to return a resolved value inside a coroutine."""
        return value

    async def scrape_company_dataset(self, name: str, domain: str, job_id: str, is_target: bool = True, vectors: List[str] = None) -> Dict[str, Any]:
        """Scrapes requested data vectors for a single company concurrently."""
        if vectors is None:
            vectors = ["website", "reviews", "social", "ads", "news", "metrics"]

        prefix = "Target" if is_target else f"Competitor ({name})"
        await self.log_step(job_id, f"Starting scraping pipeline for {prefix}...")

        # Create tasks, using dummy returns for skipped vectors
        website_task = self.website_scraper.scrape_full_website(domain) if "website" in vectors else self.return_dummy({"domain": domain, "tagline": "N/A", "value_proposition": "N/A", "scraped_text": "", "detected_tech_stack": []})
        reviews_task = self.review_scraper.scrape_reviews(name, domain) if "reviews" in vectors else self.return_dummy({"reviews": [], "average_rating": 0.0, "review_count": 0, "available": False})
        social_task = self.social_scraper.scrape_all_social(name) if "social" in vectors else self.return_dummy({"linkedin": {}, "twitter": {}, "instagram": {}})
        ads_task = self.ads_scraper.scrape_meta_ads(name) if "ads" in vectors else self.return_dummy([])
        news_task = self.news_scraper.get_latest_news(name) if "news" in vectors else self.return_dummy([])
        metrics_task = self.metrics_scraper.scrape_growjo(name, domain) if "metrics" in vectors else self.return_dummy({"revenue": "N/A", "employees": "N/A", "growth_percentage": "N/A", "funding": "N/A", "hq_location": "N/A"})

        # Run concurrently with safety fallbacks
        results = await asyncio.gather(
            website_task, reviews_task, social_task, ads_task, news_task, metrics_task,
            return_exceptions=True
        )

        # Extract values or default placeholders
        # 1. Website
        if isinstance(results[0], Exception):
            await self.log_step(job_id, f"⚠ Error scraping website for {name}: {results[0]}")
            website_data = {"domain": domain, "tagline": "N/A", "value_proposition": "N/A", "scraped_text": "", "detected_tech_stack": []}
        else:
            website_data = results[0]
            if "website" in vectors:
                await self.log_step(job_id, f"✓ Scraped website for {name} ({len(website_data.get('scraped_text', ''))} chars)")

        # 2. Reviews
        if isinstance(results[1], Exception):
            await self.log_step(job_id, f"⚠ Error scraping reviews for {name}: {results[1]}")
            reviews_data = {"reviews": [], "average_rating": 0.0, "review_count": 0, "available": False}
        else:
            reviews_data = results[1]
            if "reviews" in vectors:
                rev_cnt = reviews_data.get("review_count", 0)
                await self.log_step(job_id, f"✓ Scraped {rev_cnt} Trustpilot reviews for {name}")

        # 3. Social
        if isinstance(results[2], Exception):
            await self.log_step(job_id, f"⚠ Error scraping social data for {name}: {results[2]}")
            social_data = {"linkedin": {}, "twitter": {}, "instagram": {}}
        else:
            social_data = results[2]
            if "social" in vectors:
                await self.log_step(job_id, f"✓ Scraped social media handles for {name}")

        # 4. Ads
        if isinstance(results[3], Exception):
            await self.log_step(job_id, f"⚠ Error scraping Meta Ads for {name}: {results[3]}")
            ads_data = []
        else:
            ads_data = results[3]
            if "ads" in vectors:
                await self.log_step(job_id, f"✓ Discovered {len(ads_data)} active ads for {name}")

        # 5. News
        if isinstance(results[4], Exception):
            await self.log_step(job_id, f"⚠ Error scraping news for {name}: {results[4]}")
            news_data = []
        else:
            news_data = results[4]
            if "news" in vectors:
                await self.log_step(job_id, f"✓ Collected {len(news_data)} news items for {name}")

        # 6. Metrics
        if isinstance(results[5], Exception):
            await self.log_step(job_id, f"⚠ Error scraping metrics for {name}: {results[5]}")
            metrics_data = {"revenue": "N/A", "employees": "N/A", "growth_percentage": "N/A", "funding": "N/A", "hq_location": "N/A"}
        else:
            metrics_data = results[5]
            if "metrics" in vectors:
                await self.log_step(job_id, f"✓ Extracted Growjo financials for {name}")

        return {
            "name": name,
            "domain": domain,
            "website": website_data,
            "reviews": reviews_data,
            "social": social_data,
            "ads": ads_data,
            "news": news_data,
            "metrics": metrics_data
        }

    async def run_analysis(self, job_id: str):
        """Asynchronous orchestration workflow for competitor intelligence gathering and AI analysis."""
        await self.log_step(job_id, "Initializing analysis job...", progress=5, status="discovering")
        
        async with async_session_maker() as session:
            stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
            result = await session.execute(stmt)
            job = result.scalars().first()
            if not job:
                logger.error(f"Job ID {job_id} not found in DB. Orchestration aborted.")
                return
            company_name = job.company_name
            industry = job.industry
            depth = job.depth
            job_type = getattr(job, "job_type", "analyze") or "analyze"

        try:
            # Determine scraper vectors based on job_type
            if job_type == "marketing":
                vectors = ["reviews", "social", "ads", "website"]
            elif job_type == "future":
                vectors = ["metrics", "news", "website"]
            else: # "analyze"
                vectors = ["website", "metrics", "news", "reviews"]

            # 1. Discover Competitors
            await self.log_step(job_id, f"Discovering competitors for '{company_name}' in '{industry}'...", progress=10)
            competitors = await self.search_scraper.discover_competitors(company_name, industry)
            
            if not competitors:
                await self.log_step(job_id, "No competitors discovered automatically. Using fallbacks.", progress=15)
                # Form default fallback competitor list
                competitors = [
                    {"name": f"{industry} Competitor 1", "domain": "competitor1.com", "url": "https://competitor1.com", "description": "Competitor fallback"},
                    {"name": f"{industry} Competitor 2", "domain": "competitor2.com", "url": "https://competitor2.com", "description": "Competitor fallback"}
                ]
            else:
                comp_names = ", ".join([c["name"] for c in competitors])
                await self.log_step(job_id, f"✓ Discovered {len(competitors)} competitors: {comp_names}", progress=20)

            # 2. Scrape Target Company Data
            await self.log_step(job_id, f"Scraping target company data vectors ({', '.join(vectors)})...", progress=25, status="scraping")
            target_domain = self.search_scraper.clean_domain(company_name.lower())
            if not "." in target_domain:
                target_domain = target_domain + ".com"
                
            target_scraped = await self.scrape_company_dataset(company_name, target_domain, job_id, is_target=True, vectors=vectors)
            await self.log_step(job_id, "✓ Completed scraping target company data.", progress=40)

            # 3. Scrape Competitors Data (Concurrently)
            await self.log_step(job_id, "Scraping competitors data vectors in parallel...", progress=45)
            comp_tasks = []
            for comp in competitors:
                comp_tasks.append(
                    self.scrape_company_dataset(comp["name"], comp["domain"], job_id, is_target=False, vectors=vectors)
                )
                
            competitor_datasets = await asyncio.gather(*comp_tasks, return_exceptions=True)
            cleaned_competitor_datasets = []
            
            for idx, c_dataset in enumerate(competitor_datasets):
                c_info = competitors[idx]
                if isinstance(c_dataset, Exception):
                    await self.log_step(job_id, f"⚠ Fatal scraping failure for competitor {c_info['name']}: {c_dataset}")
                    # Provide empty structure
                    cleaned_competitor_datasets.append({
                        "name": c_info["name"], "domain": c_info["domain"],
                        "website": {}, "reviews": {"reviews": []}, "social": {}, "ads": [], "news": [], "metrics": {}
                    })
                else:
                    cleaned_competitor_datasets.append(c_dataset)
                    
            await self.log_step(job_id, "✓ Completed scraping all competitors.", progress=60, status="analyzing")

            # 4. AI Analysis Layer
            competitor_profiles = []
            swot_report = {}
            sentiment_report = {}
            ads_report = {}
            opportunity_report = {}
            recommendations_report = {}

            if job_type == "analyze":
                # A. Competitor Profiling (in parallel for each competitor)
                await self.log_step(job_id, "Running AI Competitor Profiling...", progress=65)
                profile_tasks = []
                for c_data in cleaned_competitor_datasets:
                    profile_tasks.append(
                        self.analyzer.analyze_competitor_profile(c_data["name"], c_data)
                    )
                competitor_profiles = await asyncio.gather(*profile_tasks)
                await self.log_step(job_id, f"✓ Completed profiling {len(competitor_profiles)} competitors", progress=80)

                # B. SWOT Analysis
                await self.log_step(job_id, "Running SWOT analysis for target company...", progress=85)
                swot_report = await self.analyzer.analyze_swot(company_name, industry, target_scraped)

            elif job_type == "marketing":
                # C. Customer Sentiment Analysis
                await self.log_step(job_id, "Analyzing customer reviews and sentiment...", progress=65)
                sentiment_report = await self.analyzer.analyze_customer_sentiment(
                    company_name, target_scraped["reviews"]["reviews"]
                )

                # D. Ad Intelligence Summary
                await self.log_step(job_id, "Analyzing social and Meta Ad messaging strategies...", progress=80)
                all_ads_data = [{"company_name": target_scraped["name"], "ads": target_scraped["ads"]}]
                for c_data in cleaned_competitor_datasets:
                    all_ads_data.append({"company_name": c_data["name"], "ads": c_data["ads"]})
                ads_report = await self.analyzer.analyze_ads_intelligence(company_name, all_ads_data)

            elif job_type == "future":
                # E. Market Opportunity Report
                await self.log_step(job_id, "Generating market gap and opportunities report...", progress=65)
                metrics_comparison = [{
                    "company": target_scraped["name"],
                    "revenue": target_scraped["metrics"]["revenue"],
                    "employees": target_scraped["metrics"]["employees"],
                    "growth": target_scraped["metrics"]["growth_percentage"],
                    "funding": target_scraped["metrics"]["funding"]
                }]
                for c_data in cleaned_competitor_datasets:
                    metrics_comparison.append({
                        "company": c_data["name"],
                        "revenue": c_data["metrics"]["revenue"],
                        "employees": c_data["metrics"]["employees"],
                        "growth": c_data["metrics"]["growth_percentage"],
                        "funding": c_data["metrics"]["funding"]
                    })
                    
                opportunity_context = {
                    "competitor_profiles": [],
                    "sentiment": {},
                    "metrics_comparison": metrics_comparison,
                    "news": target_scraped["news"]
                }
                opportunity_report = await self.analyzer.analyze_market_opportunity(
                    company_name, industry, opportunity_context
                )

                # F. Strategic Recommendations
                await self.log_step(job_id, "Assembling strategic corporate recommendations...", progress=80)
                recommendations_context = {
                    "swot": {},
                    "sentiment": {},
                    "ads": {},
                    "market_opportunity": opportunity_report,
                    "competitor_profiles": []
                }
                recommendations_report = await self.analyzer.generate_strategic_recommendations(
                    company_name, industry, recommendations_context
                )

            # 5. Assemble Final Report Object
            await self.log_step(job_id, "Assembling final intelligence report package...", progress=95)
            
            final_report = {
                "metadata": {
                    "company_name": company_name,
                    "industry": industry,
                    "depth": depth,
                    "job_type": job_type,
                    "analysis_date": datetime.datetime.utcnow().isoformat(),
                    "quota_usage": {
                        "serper_calls": usage_stats["serper_calls"],
                        "scraperapi_calls": usage_stats["scraperapi_calls"],
                        "direct_scrapes": usage_stats["direct_scrapes"]
                    }
                },
                "target_company": {
                    "name": company_name,
                    "domain": target_domain,
                    "tagline": target_scraped["website"].get("tagline", "N/A"),
                    "value_proposition": target_scraped["website"].get("value_proposition", "N/A"),
                    "detected_tech_stack": target_scraped["website"].get("detected_tech_stack", []),
                    "metrics": target_scraped["metrics"],
                    "social": target_scraped["social"],
                    "news": target_scraped["news"]
                },
                "competitor_data": [
                    {
                        "name": cd["name"],
                        "domain": cd["domain"],
                        "tagline": cd["website"].get("tagline", "N/A"),
                        "value_proposition": cd["website"].get("value_proposition", "N/A"),
                        "detected_tech_stack": cd["website"].get("detected_tech_stack", []),
                        "metrics": cd["metrics"],
                        "social": cd["social"],
                        "news": cd["news"],
                        "ads": cd["ads"],
                        "average_rating": cd["reviews"].get("average_rating", 0.0),
                        "review_count": cd["reviews"].get("review_count", 0)
                    } for cd in cleaned_competitor_datasets
                ]
            }

            # Conditionally attach reports
            if job_type == "analyze":
                final_report["competitor_profiles"] = competitor_profiles
                final_report["swot"] = swot_report
            elif job_type == "marketing":
                final_report["sentiment"] = sentiment_report
                final_report["ads_analysis"] = ads_report
            elif job_type == "future":
                final_report["market_opportunity"] = opportunity_report
                final_report["recommendations"] = recommendations_report

            # Update Database status and save result
            async with async_session_maker() as session:
                stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
                res = await session.execute(stmt)
                job = res.scalars().first()
                if job:
                    job.result = final_report
                    job.status = "complete"
                    job.progress = 100
                    await session.commit()
                    
            await self.log_step(job_id, "✓ Competitor intelligence report completed successfully!", progress=100, status="complete")

        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Job {job_id} failed with error: {error_details}")
            
            async with async_session_maker() as session:
                stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
                res = await session.execute(stmt)
                job = res.scalars().first()
                if job:
                    job.status = "failed"
                    job.error_log = error_details
                    await session.commit()
                    
            await self.log_step(job_id, f"❌ Analysis job failed: {str(e)}", progress=100, status="failed")
