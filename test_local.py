"""
Test with local HTML file to demonstrate scraping functionality.
"""

import os
from bs4 import BeautifulSoup
from scraper import ReviewScraper
from text_processor import TextProcessor
from data_storage import DataStorage

def test_local_scraping():
    """Test scraping with local HTML file."""
    
    print("Testing Local HTML Scraping")
    print("=" * 40)
    
    # Read local HTML file
    html_file = "test_reviews.html"
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Extract reviews using generic method
    scraper = ReviewScraper()
    reviews = scraper._extract_generic_reviews(soup, "file:///" + os.path.abspath(html_file))
    
    print(f"Found {len(reviews)} reviews")
    
    # Process the reviews
    processor = TextProcessor()
    processed_reviews = processor.preprocess_reviews(reviews)
    
    print(f"Processed {len(processed_reviews)} reviews")
    
    # Show results
    for i, review in enumerate(processed_reviews):
        print(f"\nReview {i+1}:")
        print(f"  Title: {review.get('title', 'N/A')}")
        print(f"  Rating: {review.get('rating', 'N/A')}")
        print(f"  Text: {review.get('text', 'N/A')[:100]}...")
        print(f"  Tokens: {review.get('token_count', 0)}")
    
    # Save results
    storage = DataStorage()
    output_file = storage.save_to_json(processed_reviews, "local_test_reviews.json")
    print(f"\nSaved to: {output_file}")
    
    return processed_reviews

if __name__ == "__main__":
    test_local_scraping()
