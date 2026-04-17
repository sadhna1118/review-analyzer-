"""
Main application module for review analysis.
"""

import argparse
import sys
import logging
from typing import List, Dict
from tqdm import tqdm

# Import our modules
from config import Config
from scraper import ReviewScraper
from text_processor import TextProcessor
from llm_analyzer import LLMAnalyzer
from data_storage import DataStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('review_analyzer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ReviewAnalyzer:
    """Main application class for review analysis."""
    
    def __init__(self):
        """Initialize the analyzer with all components."""
        try:
            Config.validate_config()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        self.scraper = ReviewScraper()
        self.text_processor = TextProcessor()
        self.llm_analyzer = LLMAnalyzer()
        self.data_storage = DataStorage()
        
        logger.info("Review analyzer initialized successfully")
    
    def analyze_product_reviews(
        self, 
        url: str, 
        analysis_type: str = "sentiment",
        max_pages: int = 5,
        output_format: str = "json"
    ) -> Dict:
        """
        Complete pipeline for analyzing product reviews.
        
        Args:
            url: Product URL to analyze
            analysis_type: Type of analysis ("sentiment", "summary", "detailed")
            max_pages: Maximum number of pages to scrape
            output_format: Output format ("json", "csv", "excel")
            
        Returns:
            Dictionary with results and file paths
        """
        logger.info(f"Starting review analysis for: {url}")
        
        results = {
            'url': url,
            'analysis_type': analysis_type,
            'scraped_reviews': 0,
            'processed_reviews': 0,
            'analyzed_reviews': 0,
            'output_files': [],
            'errors': []
        }
        
        try:
            # Step 1: Scrape reviews
            logger.info("Step 1: Scraping reviews...")
            raw_reviews = self.scraper.scrape_reviews(url, max_pages)
            results['scraped_reviews'] = len(raw_reviews)
            
            if not raw_reviews:
                logger.warning("No reviews found")
                results['errors'].append("No reviews found on the page")
                return results
            
            logger.info(f"Scraped {len(raw_reviews)} reviews")
            
            # Step 2: Process text
            logger.info("Step 2: Processing review text...")
            processed_reviews = self.text_processor.preprocess_reviews(raw_reviews)
            results['processed_reviews'] = len(processed_reviews)
            
            # Get text statistics
            text_stats = self.text_processor.get_text_statistics(processed_reviews)
            logger.info(f"Text processing stats: {text_stats}")
            
            # Step 3: Analyze with LLM
            logger.info(f"Step 3: Analyzing reviews with LLM ({analysis_type})...")
            analyzed_reviews = []
            
            # Use tqdm for progress bar
            for i, review in enumerate(tqdm(processed_reviews, desc="Analyzing reviews")):
                try:
                    analyzed_review = self.llm_analyzer.analyze_review(review, analysis_type)
                    analyzed_reviews.append(analyzed_review)
                except Exception as e:
                    logger.warning(f"Error analyzing review {i+1}: {e}")
                    # Add the review with error information
                    review_with_error = review.copy()
                    review_with_error['analysis_error'] = str(e)
                    analyzed_reviews.append(review_with_error)
            
            results['analyzed_reviews'] = len(analyzed_reviews)
            
            # Get analysis statistics
            analysis_stats = self.llm_analyzer.get_analysis_statistics(analyzed_reviews)
            logger.info(f"Analysis stats: {analysis_stats}")
            
            # Step 4: Save results
            logger.info("Step 4: Saving results...")
            
            # Save main data
            main_file = self.data_storage.export_data(analyzed_reviews, output_format)
            results['output_files'].append({'type': 'main', 'file': main_file})
            
            # Save summary report
            summary_file = self.data_storage.save_summary_report(analyzed_reviews)
            results['output_files'].append({'type': 'summary', 'file': summary_file})
            
            # Also save in JSON format for backup
            if output_format != "json":
                json_file = self.data_storage.save_to_json(analyzed_reviews)
                results['output_files'].append({'type': 'backup', 'file': json_file})
            
            logger.info("Analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error in analysis pipeline: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def batch_analyze(self, urls: List[str], **kwargs) -> List[Dict]:
        """
        Analyze multiple product URLs.
        
        Args:
            urls: List of product URLs
            **kwargs: Additional arguments for analyze_product_reviews
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"Analyzing URL {i+1}/{len(urls)}: {url}")
            result = self.analyze_product_reviews(url, **kwargs)
            results.append(result)
        
        return results

def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Analyze product reviews using web scraping and LLM analysis"
    )
    
    parser.add_argument(
        'url',
        help='Product page URL to analyze'
    )
    
    parser.add_argument(
        '--analysis-type',
        choices=['sentiment', 'summary', 'detailed'],
        default='sentiment',
        help='Type of analysis to perform (default: sentiment)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=5,
        help='Maximum number of pages to scrape (default: 5)'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['json', 'csv', 'excel'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory (default: output)'
    )
    
    args = parser.parse_args()
    
    # Update output directory if provided
    if args.output_dir:
        Config.OUTPUT_DIR = args.output_dir
    
    try:
        # Initialize analyzer
        analyzer = ReviewAnalyzer()
        
        # Run analysis
        results = analyzer.analyze_product_reviews(
            url=args.url,
            analysis_type=args.analysis_type,
            max_pages=args.max_pages,
            output_format=args.output_format
        )
        
        # Print results summary
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY")
        print("="*50)
        print(f"URL: {results['url']}")
        print(f"Analysis Type: {results['analysis_type']}")
        print(f"Reviews Scraped: {results['scraped_reviews']}")
        print(f"Reviews Processed: {results['processed_reviews']}")
        print(f"Reviews Analyzed: {results['analyzed_reviews']}")
        
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\nOutput Files:")
        for output in results['output_files']:
            print(f"  {output['type']}: {output['file']}")
        
        print("\nAnalysis completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
