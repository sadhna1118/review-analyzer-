"""
Web scraping module for extracting product reviews from e-commerce sites.
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReviewScraper:
    """Main class for scraping product reviews."""
    
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def _make_request(self, url: str, retries: int = None) -> Optional[BeautifulSoup]:
        """Make HTTP request with retry logic."""
        if retries is None:
            retries = Config.MAX_RETRIES
            
        for attempt in range(retries):
            try:
                logger.info(f"Making request to {url} (attempt {attempt + 1})")
                
                # Rotate user agent for each attempt
                self.session.headers['User-Agent'] = self.ua.random
                
                response = self.session.get(
                    url, 
                    timeout=Config.TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # Add delay between requests
                time.sleep(Config.REQUEST_DELAY)
                
                return BeautifulSoup(response.content, 'lxml')
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
                
        return None
    
    def _extract_amazon_reviews(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract reviews from Amazon product page."""
        reviews = []
        
        # Look for review containers
        review_containers = soup.find_all('div', {'data-hook': 'review'})
        
        if not review_containers:
            # Try alternative selectors
            review_containers = soup.find_all('div', class_='review')
        
        for container in review_containers:
            try:
                review = {}
                
                # Rating
                rating_elem = container.find('i', {'data-hook': 'review-star-rating'})
                if rating_elem:
                    rating_text = rating_elem.get_text().strip()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    review['rating'] = float(rating_match.group(1)) if rating_match else None
                
                # Title
                title_elem = container.find('a', {'data-hook': 'review-title'})
                if title_elem:
                    review['title'] = title_elem.get_text().strip()
                else:
                    title_elem = container.find('span', {'data-hook': 'review-title'})
                    if title_elem:
                        review['title'] = title_elem.get_text().strip()
                
                # Date
                date_elem = container.find('span', {'data-hook': 'review-date'})
                if date_elem:
                    review['date'] = date_elem.get_text().strip()
                
                # Author
                author_elem = container.find('div', class_='a-profile-name')
                if author_elem:
                    review['author'] = author_elem.get_text().strip()
                
                # Review text
                body_elem = container.find('span', {'data-hook': 'review-body'})
                if body_elem:
                    review['text'] = body_elem.get_text().strip()
                
                # Verified purchase
                verified_elem = container.find('span', {'data-hook': 'avp-badge'})
                review['verified'] = bool(verified_elem) if verified_elem else False
                
                # Helpful count
                helpful_elem = container.find('span', {'data-hook': 'helpful-vote-statement'})
                if helpful_elem:
                    helpful_text = helpful_elem.get_text().strip()
                    helpful_match = re.search(r'(\d+)', helpful_text)
                    review['helpful_count'] = int(helpful_match.group(1)) if helpful_match else 0
                
                if review.get('text'):  # Only include reviews with text
                    reviews.append(review)
                    
            except Exception as e:
                logger.warning(f"Error extracting review: {e}")
                continue
        
        return reviews
    
    def _extract_bestbuy_reviews(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract reviews from Best Buy product page."""
        reviews = []
        
        # Look for review containers
        review_containers = soup.find_all('div', class_='review-item')
        
        for container in review_containers:
            try:
                review = {}
                
                # Rating
                rating_elem = container.find('div', class_='c-review-rating')
                if rating_elem:
                    rating_text = rating_elem.get_text().strip()
                    rating_match = re.search(r'(\d+)', rating_text)
                    review['rating'] = int(rating_match.group(1)) if rating_match else None
                
                # Title
                title_elem = container.find('h4', class_='c-review-title')
                if title_elem:
                    review['title'] = title_elem.get_text().strip()
                
                # Date
                date_elem = container.find('div', class_='c-review-date')
                if date_elem:
                    review['date'] = date_elem.get_text().strip()
                
                # Author
                author_elem = container.find('div', class_='c-review-author')
                if author_elem:
                    review['author'] = author_elem.get_text().strip()
                
                # Review text
                body_elem = container.find('div', class_='c-review-body')
                if body_elem:
                    review['text'] = body_elem.get_text().strip()
                
                if review.get('text'):
                    reviews.append(review)
                    
            except Exception as e:
                logger.warning(f"Error extracting Best Buy review: {e}")
                continue
        
        return reviews
    
    def _get_pagination_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract pagination links for review pages."""
        links = []
        
        # Look for pagination elements
        pagination = soup.find('ul', class_='a-pagination')
        if pagination:
            page_links = pagination.find_all('a', href=True)
            for link in page_links:
                href = link['href']
                if 'pageNumber=' in href or 'page=' in href:
                    full_url = urljoin(base_url, href)
                    if full_url not in links:
                        links.append(full_url)
        
        return links
    
    def scrape_reviews(self, url: str, max_pages: int = 5) -> List[Dict]:
        """
        Scrape reviews from a product URL.
        
        Args:
            url: Product page URL
            max_pages: Maximum number of review pages to scrape
            
        Returns:
            List of review dictionaries
        """
        logger.info(f"Starting to scrape reviews from {url}")
        
        # Parse the URL to determine the site
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        soup = self._make_request(url)
        if not soup:
            logger.error("Failed to fetch the main page")
            return []
        
        all_reviews = []
        
        # Extract reviews based on the site
        if 'amazon.com' in domain:
            all_reviews.extend(self._extract_amazon_reviews(soup, url))
            
            # Get pagination links
            pagination_links = self._get_pagination_links(soup, url)
            
            # Scrape additional pages
            for i, link in enumerate(pagination_links[:max_pages-1]):
                logger.info(f"Scraping page {i+2}")
                page_soup = self._make_request(link)
                if page_soup:
                    page_reviews = self._extract_amazon_reviews(page_soup, url)
                    all_reviews.extend(page_reviews)
                    
        elif 'bestbuy.com' in domain:
            all_reviews.extend(self._extract_bestbuy_reviews(soup, url))
            
        else:
            logger.warning(f"Unsupported site: {domain}")
            # Try generic extraction
            all_reviews.extend(self._extract_generic_reviews(soup, url))
        
        logger.info(f"Extracted {len(all_reviews)} reviews")
        return all_reviews
    
    def _extract_generic_reviews(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Generic review extraction for unknown sites."""
        reviews = []
        
        # Common selectors for reviews
        selectors = [
            {'container': '[class*="review"]', 'text': '[class*="text"]', 'rating': '[class*="rating"]'},
            {'container': '[class*="Review"]', 'text': '[class*="content"]', 'rating': '[class*="stars"]'},
            {'container': '[data-review]', 'text': '[data-text]', 'rating': '[data-rating]'},
        ]
        
        for selector_set in selectors:
            containers = soup.select(selector_set['container'])
            
            for container in containers:
                try:
                    review = {}
                    
                    # Extract text
                    text_elem = container.select_one(selector_set['text'])
                    if text_elem:
                        review['text'] = text_elem.get_text().strip()
                    
                    # Extract rating
                    rating_elem = container.select_one(selector_set['rating'])
                    if rating_elem:
                        rating_text = rating_elem.get_text().strip()
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        review['rating'] = float(rating_match.group(1)) if rating_match else None
                    
                    if review.get('text'):
                        reviews.append(review)
                        
                except Exception as e:
                    logger.warning(f"Error in generic extraction: {e}")
                    continue
        
        return reviews
