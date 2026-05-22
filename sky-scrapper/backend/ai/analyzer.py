import json
import re
import anthropic
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.scrapers.base import logger
from backend.ai import prompts

class AIAnalyzer:
    def __init__(self):
        # Initialize AsyncAnthropic client if key is available
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            logger.warning("ANTHROPIC_API_KEY is not set. AI analysis calls will return mock/fallback structures.")

    def clean_json_response(self, text: str) -> str:
        """Strips markdown code blocks, whitespaces, and code fences from the JSON string."""
        if not text:
            return ""
        
        # Strip ```json ... ``` or ``` ... ```
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # Remove start fence
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            # Remove end fence
            cleaned = re.sub(r"\s*```$", "", cleaned)
            
        cleaned = cleaned.strip()
        return cleaned

    async def call_claude(self, system_prompt: str, user_prompt: str, schema_template: Dict[str, Any], attempt: int = 1) -> Dict[str, Any]:
        """Performs the actual Claude API call with validation and retry logic."""
        if not self.client:
            logger.warning("Claude Client not initialized. Returning template placeholder.")
            return schema_template

        try:
            logger.info(f"Sending request to Claude Sonnet (Attempt {attempt})...")
            response = await self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            raw_text = response.content[0].text
            cleaned_text = self.clean_json_response(raw_text)
            
            try:
                data = json.loads(cleaned_text)
                return data
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse Claude JSON response on attempt {attempt}: {je}. Raw response: {raw_text[:200]}")
                if attempt == 1:
                    # Retry once with a stricter system prompt
                    retry_system = f"{system_prompt}\n\nCRITICAL: Your previous response was not valid JSON. You MUST respond with ONLY a pure valid JSON string. Absolutely NO explanations, NO markdown tags, NO backticks. If you do not follow this, the parser will fail."
                    return await self.call_claude(retry_system, user_prompt, schema_template, attempt=2)
                else:
                    # Return fallback structured error object
                    logger.error("JSON parsing failed twice. Returning structured error.")
                    error_result = schema_template.copy()
                    error_result["error"] = "Failed to parse AI response. Malformed JSON."
                    return error_result
                    
        except Exception as e:
            logger.error(f"Claude API exception: {e}")
            error_result = schema_template.copy()
            error_result["error"] = f"Claude API connection error: {str(e)}"
            return error_result

    async def analyze_competitor_profile(self, competitor_name: str, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a profile for a single competitor."""
        schema = {
            "company": competitor_name,
            "positioning": "Unknown positioning",
            "target_audience": "Unknown target audience",
            "key_strengths": ["Data scraping unavailable"],
            "key_weaknesses": ["Data scraping unavailable"],
            "pricing_model": "N/A",
            "estimated_market_share_tier": "niche"
        }
        
        # Prepare variables
        reviews_list = scraped_data.get("reviews", {}).get("reviews", [])
        reviews_text = "\n".join([f"- Rating: {r['rating']} stars, Text: {r['text']}" for r in reviews_list[:10]])
        
        metrics_data = scraped_data.get("metrics", {})
        metrics_str = f"Revenue: {metrics_data.get('revenue')}, Employees: {metrics_data.get('employees')}, Growth: {metrics_data.get('growth_percentage')}, Funding: {metrics_data.get('funding')}, HQ: {metrics_data.get('hq_location')}"
        
        user_prompt = prompts.COMPETITOR_PROFILING_USER.format(
            company_name=competitor_name,
            tagline=scraped_data.get("website", {}).get("tagline", "N/A"),
            value_prop=scraped_data.get("website", {}).get("value_proposition", "N/A"),
            pricing_clues=str(scraped_data.get("website", {}).get("pricing_clues", [])),
            about_text=scraped_data.get("website", {}).get("about_clues", "N/A"),
            metrics=metrics_str,
            reviews=reviews_text or "No customer reviews scraped",
            raw_text=scraped_data.get("website", {}).get("scraped_text", "")[:4000] # Cap raw text to keep context window small
        )
        
        return await self.call_claude(prompts.COMPETITOR_PROFILING_SYSTEM, user_prompt, schema)

    async def analyze_swot(self, company_name: str, industry: str, gathered_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates SWOT analysis for the target company."""
        schema = {
            "strengths": [{"point": "No data available", "evidence": "Scraper failed"}],
            "weaknesses": [{"point": "No data available", "evidence": "Scraper failed"}],
            "opportunities": [{"point": "No data available", "evidence": "Scraper failed"}],
            "threats": [{"point": "No data available", "evidence": "Scraper failed"}]
        }
        
        # Prepare inputs
        website = gathered_data.get("website", {})
        metrics = gathered_data.get("metrics", {})
        social = gathered_data.get("social", {})
        news = gathered_data.get("news", [])
        reviews = gathered_data.get("reviews", {}).get("reviews", [])
        
        metrics_str = f"Revenue: {metrics.get('revenue')}, Employees: {metrics.get('employees')}, Growth: {metrics.get('growth_percentage')}, Funding: {metrics.get('funding')}, HQ: {metrics.get('hq_location')}"
        news_str = "\n".join([f"- Headline: {n['headline']} (Source: {n['source']})" for n in news[:10]])
        reviews_str = "\n".join([f"- Rating: {r['rating']}, Text: {r['text']}" for r in reviews[:10]])
        social_str = str(social)
        
        user_prompt = prompts.SWOT_USER.format(
            company_name=company_name,
            industry=industry,
            tagline=website.get("tagline", "N/A"),
            value_prop=website.get("value_proposition", "N/A"),
            metrics=metrics_str,
            social=social_str,
            news=news_str or "No recent news found",
            reviews=reviews_str or "No reviews found",
            raw_text=website.get("scraped_text", "")[:4000]
        )
        
        return await self.call_claude(prompts.SWOT_SYSTEM, user_prompt, schema)

    async def analyze_customer_sentiment(self, company_name: str, reviews_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates sentiment breakdown from Trustpilot reviews."""
        schema = {
            "overall_score": 5.0,
            "sentiment_breakdown": {"positive": 33, "neutral": 33, "negative": 34},
            "top_praise_themes": ["No customer reviews found"],
            "top_complaint_themes": ["No customer reviews found"],
            "urgent_issues": ["No urgent complaints"],
            "nps_estimate": 0
        }
        
        if not reviews_list:
            return schema
            
        reviews_text = "\n".join([f"[{r['rating']}/5 stars] {r['text']}" for r in reviews_list[:50]])
        user_prompt = prompts.SENTIMENT_USER.format(company_name=company_name, reviews=reviews_text)
        
        return await self.call_claude(prompts.SENTIMENT_SYSTEM, user_prompt, schema)

    async def analyze_ads_intelligence(self, company_name: str, ads_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates marketing insights from active Meta Ads."""
        schema = {
            "dominant_messaging_themes": ["No advertising data discovered"],
            "competitor_ad_strategies": [],
            "content_gaps": ["No advertising data discovered"],
            "recommended_angles": ["Leverage generic benefits"]
        }
        
        # Prepare combined ads information
        ads_text_blocks = []
        for item in ads_data:
            c_name = item.get("company_name", "Unknown")
            c_ads = item.get("ads", [])
            ads_text_blocks.append(f"Company: {c_name}")
            if not c_ads:
                ads_text_blocks.append("  - No active Meta ads found.")
            for idx, ad in enumerate(c_ads):
                ads_text_blocks.append(f"  - Ad {idx+1}: Platform(s): {', '.join(ad.get('platforms', []))} | First Seen: {ad.get('date_seen')}")
                ads_text_blocks.append(f"    Text: {ad.get('text')}")
                ads_text_blocks.append(f"    CTA: {ad.get('cta')} | Visuals: {ad.get('image_desc')}")
                
        user_prompt = prompts.ADS_USER.format(company_name=company_name, ads_data="\n".join(ads_text_blocks))
        
        return await self.call_claude(prompts.ADS_SYSTEM, user_prompt, schema)

    async def analyze_market_opportunity(self, company_name: str, industry: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generates market gaps and emerging opportunities."""
        schema = {
            "market_gaps": ["No opportunity data available"],
            "underserved_segments": ["No opportunity data available"],
            "emerging_trends": ["No opportunity data available"],
            "threats": ["No opportunity data available"],
            "top_opportunities": [{"title": "Explore market niches", "rationale": "No scraper data found", "urgency": "medium"}]
        }
        
        comp_profiles_str = json.dumps(context.get("competitor_profiles", []), indent=2)
        sentiment_str = json.dumps(context.get("sentiment", {}), indent=2)
        metrics_str = json.dumps(context.get("metrics_comparison", []), indent=2)
        news_list = context.get("news", [])
        news_str = "\n".join([f"- {n['headline']} (Source: {n['source']})" for n in news_list[:15]])
        
        user_prompt = prompts.MARKET_OPPORTUNITY_USER.format(
            company_name=company_name,
            industry=industry,
            competitor_profiles=comp_profiles_str,
            sentiment=sentiment_str,
            metrics=metrics_str,
            news=news_str or "No recent news found"
        )
        
        return await self.call_claude(prompts.MARKET_OPPORTUNITY_SYSTEM, user_prompt, schema)

    async def generate_strategic_recommendations(self, company_name: str, industry: str, reports_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generates final strategic recommendations dashboard view."""
        schema = {
            "executive_summary": "Consultant report generation failed.",
            "weekly_priorities": ["Maintain status quo"],
            "monthly_goals": ["Refine competitive metrics"],
            "marketing_recommendations": ["Conduct localized search optimization"],
            "product_recommendations": ["Optimize backend stability"],
            "competitive_responses": [{"threat": "Competitors expanding", "response": "Monitor developments"}]
        }
        
        user_prompt = prompts.RECOMMENDATIONS_USER.format(
            company_name=company_name,
            industry=industry,
            swot=json.dumps(reports_context.get("swot", {}), indent=2),
            sentiment=json.dumps(reports_context.get("sentiment", {}), indent=2),
            ads=json.dumps(reports_context.get("ads", {}), indent=2),
            market_opportunity=json.dumps(reports_context.get("market_opportunity", {}), indent=2),
            competitor_profiles=json.dumps(reports_context.get("competitor_profiles", []), indent=2)
        )
        
        return await self.call_claude(prompts.RECOMMENDATIONS_SYSTEM, user_prompt, schema)
