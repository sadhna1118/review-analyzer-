"""
Example usage script for the Review Analyzer application.
"""

import os
import sys
from main import ReviewAnalyzer

def main():
    """Demonstrate different usage patterns of the Review Analyzer."""
    
    print("Review Analyzer - Example Usage")
    print("=" * 50)
    
    # Test URLs for demonstration
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",  # AirPods Pro
        "https://www.amazon.com/dp/B07XJ8C8F5",  # Echo Dot
    ]
    
    try:
        # Initialize the analyzer
        analyzer = ReviewAnalyzer()
        
        # Example 1: Basic sentiment analysis
        print("\n1. Basic Sentiment Analysis")
        print("-" * 30)
        
        url = test_urls[0]
        print(f"Analyzing: {url}")
        
        results = analyzer.analyze_product_reviews(
            url=url,
            analysis_type="sentiment",
            max_pages=2,  # Limit to 2 pages for demo
            output_format="json"
        )
        
        print(f"Results: {results['scraped_reviews']} scraped, {results['analyzed_reviews']} analyzed")
        print(f"Output files: {[f['file'] for f in results['output_files']]}")
        
        # Example 2: Summary analysis
        print("\n2. Summary Analysis")
        print("-" * 30)
        
        url = test_urls[1] if len(test_urls) > 1 else test_urls[0]
        print(f"Analyzing: {url}")
        
        results = analyzer.analyze_product_reviews(
            url=url,
            analysis_type="summary",
            max_pages=1,  # Just 1 page for demo
            output_format="csv"
        )
        
        print(f"Results: {results['scraped_reviews']} scraped, {results['analyzed_reviews']} analyzed")
        print(f"Output files: {[f['file'] for f in results['output_files']]}")
        
        # Example 3: Detailed analysis with Excel output
        print("\n3. Detailed Analysis (Excel)")
        print("-" * 30)
        
        url = test_urls[0]
        print(f"Analyzing: {url}")
        
        results = analyzer.analyze_product_reviews(
            url=url,
            analysis_type="detailed",
            max_pages=1,  # Just 1 page for demo
            output_format="excel"
        )
        
        print(f"Results: {results['scraped_reviews']} scraped, {results['analyzed_reviews']} analyzed")
        print(f"Output files: {[f['file'] for f in results['output_files']]}")
        
        # Example 4: Batch analysis
        print("\n4. Batch Analysis")
        print("-" * 30)
        
        print(f"Analyzing {len(test_urls)} URLs...")
        
        batch_results = analyzer.batch_analyze(
            urls=test_urls,
            analysis_type="sentiment",
            max_pages=1,
            output_format="json"
        )
        
        for i, result in enumerate(batch_results):
            print(f"URL {i+1}: {result['scraped_reviews']} scraped, {result['analyzed_reviews']} analyzed")
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("Check the 'output' directory for generated files.")
        
    except Exception as e:
        print(f"Error during examples: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
