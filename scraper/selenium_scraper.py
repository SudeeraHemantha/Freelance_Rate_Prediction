import sys
import os
import time
import random
import re
from typing import List, Dict, Any
from decimal import Decimal

# Configure logging
import logging
logger = logging.getLogger("scraper.selenium_scraper")

# Try to import selenium. It will be installed in the venv.
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Ensure backend folder is in path for relative imports if run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))


class SeleniumScraper:
    """Handles Chrome browser automation, page fetching, and heuristic parsing of freelance gigs."""

    def __init__(self, headless: bool = True, delay_range: tuple = (3, 8)):
        self.headless = headless
        self.delay_range = delay_range
        self.driver = None

        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium or BeautifulSoup4 is not installed. Scraper will not run in real mode.")

    def _init_driver(self):
        """Initializes the headless/non-headless Chrome driver with security and anti-bot arguments."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium/BS4 not installed. Cannot initialize webdriver.")

        if self.driver is not None:
            return

        logger.info("Initializing Selenium Chrome WebDriver...")
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        # Security and bypass configurations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Polite/Standard User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Exclude automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Script to override navigator.webdriver properties to bypass bot detection
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                }
            )
            logger.info("Chrome WebDriver initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            self.driver = None
            raise

    def close(self):
        """Safely tears down the webdriver instance."""
        if self.driver:
            try:
                logger.info("Closing Chrome WebDriver...")
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing webdriver: {e}")
            finally:
                self.driver = None

    def fetch_page_source(self, url: str) -> str:
        """Navigates to a URL with a random polite delay and returns page source HTML."""
        self._init_driver()
        
        # Polite delay before requesting page
        delay = random.uniform(*self.delay_range)
        logger.info(f"Polite delay: sleeping for {delay:.2f} seconds before requesting {url}...")
        time.sleep(delay)

        try:
            logger.info(f"Navigating browser to: {url}")
            self.driver.get(url)
            # Give dynamic Javascript a few seconds to load
            time.sleep(random.uniform(3, 5))
            
            # Anti-bot detection verification
            if "captcha" in self.driver.title.lower() or "cloudflare" in self.driver.title.lower():
                logger.warning(f"Bot detection challenge encountered on page: {self.driver.title}")
                raise PermissionError("Access denied by Cloudflare / Captcha shield.")
                
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Error fetching page source from {url}: {e}")
            raise

    def scrape_upwork_gigs(self, tech_stack: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Scrapes Upwork job search results for a given technology term."""
        url = f"https://www.upwork.com/nx/search/jobs/?q={tech_stack.replace(' ', '+')}&sort=recency"
        try:
            html = self.fetch_page_source(url)
            soup = BeautifulSoup(html, "html.parser")
            return self._parse_upwork_html(soup, tech_stack, max_results)
        except Exception as e:
            logger.error(f"Upwork scraping failed: {e}. Falling back or bubbling up.")
            raise

    def scrape_fiverr_gigs(self, tech_stack: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Scrapes Fiverr search results for a given technology service."""
        url = f"https://www.fiverr.com/search/gigs?query={tech_stack.replace(' ', '%20')}"
        try:
            html = self.fetch_page_source(url)
            soup = BeautifulSoup(html, "html.parser")
            return self._parse_fiverr_html(soup, tech_stack, max_results)
        except Exception as e:
            logger.error(f"Fiverr scraping failed: {e}. Falling back or bubbling up.")
            raise

    def _parse_upwork_html(self, soup: BeautifulSoup, tech_stack: str, max_results: int) -> List[Dict[str, Any]]:
        """Heuristically extracts gig metrics from Upwork job cards search HTML."""
        gigs = []
        # Find job tiles (class names or data attributes frequently change, but job-tile/job-tile-title are standard)
        job_cards = soup.find_all(attrs={"data-test": re.compile(r"JobTile|job-tile")}) or \
                    soup.find_all("article", class_=re.compile(r"job-tile|up-card"))
        
        logger.info(f"Found {len(job_cards)} potential Upwork job listings.")

        for card in job_cards[:max_results]:
            try:
                # Title
                title_elem = card.find(attrs={"data-test": re.compile(r"job-tile-title|UpLink")}) or \
                             card.find("h3") or card.find("h2")
                title = title_elem.text.strip() if title_elem else "Freelance Software Developer"

                # Description / Description snippet
                desc_elem = card.find(attrs={"data-test": re.compile(r"job-description|JobDescription")}) or \
                            card.find(class_=re.compile(r"description|job-description"))
                description = desc_elem.text.strip() if desc_elem else ""

                parsed_gig = self._extract_heuristics_from_text(
                    title=title,
                    description=description,
                    platform="Upwork",
                    tech_stack=tech_stack
                )
                gigs.append(parsed_gig)
            except Exception as ex:
                logger.error(f"Error parsing individual Upwork card: {ex}")
                continue
        
        # If no cards found, fail so simulation fallback handles it
        if not gigs:
            raise ValueError("No Upwork job cards parsed from HTML source.")

        return gigs

    def _parse_fiverr_html(self, soup: BeautifulSoup, tech_stack: str, max_results: int) -> List[Dict[str, Any]]:
        """Heuristically extracts gig metrics from Fiverr gig cards search HTML."""
        gigs = []
        # Fiverr structures gigs under .gig-card-layout or articles
        gig_cards = soup.find_all(class_=re.compile(r"gig-card-layout|gig-wrapper|gig_card")) or \
                    soup.find_all("div", attrs={"data-gig-id": True})
        
        logger.info(f"Found {len(gig_cards)} potential Fiverr gig listings.")

        for card in gig_cards[:max_results]:
            try:
                # Title / Gig description
                title_elem = card.find(class_=re.compile(r"title|gig-title")) or \
                             card.find("h3") or card.find("a")
                title = title_elem.text.strip() if title_elem else "Build Freelance Project"

                # Fiverr usually doesn't show descriptions on search, but we can look for text snippets
                desc_elem = card.find(class_=re.compile(r"description|seller-name"))
                description = desc_elem.text.strip() if desc_elem else title

                # Price / Payout
                price_elem = card.find(class_=re.compile(r"price|payout|starting-at")) or \
                             card.find(text=re.compile(r"\$\d+"))
                price_str = price_elem.text if price_elem else "$50"
                payout_val = self._parse_price(price_str)

                parsed_gig = self._extract_heuristics_from_text(
                    title=title,
                    description=description,
                    platform="Fiverr",
                    tech_stack=tech_stack,
                    extracted_payout=payout_val
                )
                gigs.append(parsed_gig)
            except Exception as ex:
                logger.error(f"Error parsing individual Fiverr card: {ex}")
                continue
                
        if not gigs:
            raise ValueError("No Fiverr gig cards parsed from HTML source.")

        return gigs

    def _parse_price(self, text: str) -> Decimal:
        """Helper to extract price digits from string to Decimal."""
        digits = re.findall(r"\d[\d,]*", text)
        if digits:
            clean_digits = digits[0].replace(",", "")
            return Decimal(clean_digits)
        return Decimal("50.00")

    def _extract_heuristics_from_text(
        self, 
        title: str, 
        description: str, 
        platform: str, 
        tech_stack: str,
        extracted_payout: Decimal = None
    ) -> Dict[str, Any]:
        """Analyzes textual listings to extract complexity, estimated hours, auth, APIs, payout, and urgency."""
        full_text = f"{title} {description}".lower()

        # 1. Platform & Tech
        tech = tech_stack.strip().capitalize()

        # 2. Project Type
        project_type = title.strip()
        if len(project_type) > 100:
            project_type = project_type[:97] + "..."

        # 3. Complexity Level (Low, Medium, High)
        complexity = "Medium"
        high_indicators = ["expert", "senior", "lead", "advanced", "complex", "architecture", "scale", "performance"]
        low_indicators = ["entry", "junior", "simple", "easy", "fix", "basic", "beginner", "quick"]
        
        if any(ind in full_text for ind in high_indicators):
            complexity = "High"
        elif any(ind in full_text for ind in low_indicators):
            complexity = "Low"

        # 4. Authentication and Third Party APIs
        has_auth = any(
            auth in full_text 
            for auth in ["auth", "login", "signup", "cognito", "jwt", "oauth", "firebase auth", "okta", "auth0"]
        )
        has_apis = any(
            api in full_text 
            for api in ["api", "stripe", "paypal", "third-party", "webhook", "twilio", "sendgrid", "integration"]
        )

        # 5. Urgency
        urgency = "Medium"
        urgency_indicators = ["urgent", "asap", "immediate", "fast", "quick turnaround", "rush", "today"]
        low_urgency = ["flexible", "whenever", "ongoing", "long term", "no rush"]
        
        if any(ind in full_text for ind in urgency_indicators):
            urgency = "Urgent"
        elif any(ind in full_text for ind in low_urgency):
            urgency = "Low"
        elif "high" in full_text:
            urgency = "High"

        # 6. Estimated Hours (Heuristics based on complexity)
        hours_match = re.search(r"(\d+)\s*(?:hrs|hours|hour)", full_text)
        if hours_match:
            hours = Decimal(hours_match.group(1))
        else:
            if complexity == "Low":
                hours = Decimal(random.randint(5, 15))
            elif complexity == "Medium":
                hours = Decimal(random.randint(20, 60))
            else:
                hours = Decimal(random.randint(80, 200))

        # 7. Actual Payout
        if extracted_payout:
            payout = extracted_payout
        else:
            # Let's derive payout based on standard rates of tech stack and hours
            base_hourly_rate = {
                "Python": 85, "Django": 90, "Tensorflow": 120,
                "React": 75, "Node.js": 80, "Go": 110, "Rust": 130,
                "Kubernetes": 125, "Flutter": 70, "Wordpress": 40
            }.get(tech, 65)

            # Modify rate slightly based on complexity
            if complexity == "Low":
                rate_multiplier = 0.8
            elif complexity == "High":
                rate_multiplier = 1.3
            else:
                rate_multiplier = 1.0

            hourly_rate = Decimal(base_hourly_rate) * Decimal(rate_multiplier)
            payout = (hours * hourly_rate).quantize(Decimal("0.01"))
            
            # Premium calculations
            if has_auth:
                payout += Decimal("150.00")
            if has_apis:
                payout += Decimal("100.00")
            if urgency == "Urgent":
                payout *= Decimal("1.15") # 15% rush fee
                
            payout = payout.quantize(Decimal("0.01"))

        # Final bounds validation
        if payout < Decimal("10.00"):
            payout = Decimal("50.00")

        return {
            "platform": platform,
            "primary_tech": tech,
            "project_type": project_type,
            "complexity_level": complexity,
            "estimated_hours": hours.quantize(Decimal("0.01")),
            "urgency": urgency,
            "has_auth": has_auth,
            "has_third_party_apis": has_apis,
            "actual_payout": payout
        }
