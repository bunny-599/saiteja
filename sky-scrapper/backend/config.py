import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from root of the project
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Sky-Scrapper Competitor Intelligence Platform"
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    SCRAPERAPI_KEY: str = os.getenv("SCRAPERAPI_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sky_scrapper.db")
    
    # AI Model
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022") # fallback from claude-sonnet-4-20250514 to ensure compatibility, but user requested model will be used if set.
    
    # Scraper Settings
    PLAYWRIGHT_HEADLESS: bool = True
    SCRAPING_DEPTH_DEFAULT: str = "standard"
    
    # Path for saved reports
    REPORTS_DIR: Path = Path(__file__).resolve().parent.parent / "reports"
    
    def validate(self):
        missing = []
        if not self.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if not self.SERPER_API_KEY:
            missing.append("SERPER_API_KEY")
        # ScraperAPI is highly recommended but not strictly required if fallback to playwright direct scrapers works
        return missing

settings = Settings()
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
