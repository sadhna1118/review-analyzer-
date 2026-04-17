"""
Test demo with mock data to demonstrate the application functionality.
"""

import json
from main import ReviewAnalyzer
from text_processor import TextProcessor
from llm_analyzer import LLMAnalyzer
from data_storage import DataStorage

def create_mock_reviews():
    """Create mock review data for testing."""
    return [
        {
            "title": "Amazing Product!",
            "text": "I absolutely love this product! The quality is outstanding and it exceeded all my expectations. The build quality is premium and it works exactly as described. Customer service was also excellent when I had questions.",
            "rating": 5,
            "date": "October 15, 2023",
            "author": "John Smith",
            "verified": True,
            "helpful_count": 42
        },
        {
            "title": "Good but not perfect",
            "text": "The product is generally good and works well for basic tasks. However, I found the setup process to be a bit confusing and the instructions could be clearer. Once set up, it performs adequately but doesn't quite live up to the premium price point.",
            "rating": 3,
            "date": "October 10, 2023",
            "author": "Sarah Johnson",
            "verified": True,
            "helpful_count": 15
        },
        {
            "title": "Terrible experience",
            "text": "This product stopped working after just two weeks of use. The quality feels cheap and it broke during normal use. Customer service was unhelpful and refused to provide a refund. I would not recommend this to anyone.",
            "rating": 1,
            "date": "October 5, 2023",
            "author": "Mike Wilson",
            "verified": False,
            "helpful_count": 8
        },
        {
            "title": "Great value for money",
            "text": "For the price, this product offers excellent value. It may not have all the premium features of more expensive models, but it gets the job done reliably. The design is clean and modern, and it's very easy to use right out of the box.",
            "rating": 4,
            "date": "September 28, 2023",
            "author": "Emily Brown",
            "verified": True,
            "helpful_count": 23
        },
        {
            "title": "Average product",
            "text": "It's an okay product. Nothing special but it works. The quality is decent for the price. I've had it for a month now and no major issues. Would probably buy again if I needed another one.",
            "rating": 3,
            "date": "September 20, 2023",
            "author": "David Lee",
            "verified": True,
            "helpful_count": 5
        }
    ]

def main():
    """Run demo with mock data."""
    print("Review Analyzer - Demo with Mock Data")
    print("=" * 50)
    
    try:
        # Initialize components
        print("Initializing components...")
        text_processor = TextProcessor()
        llm_analyzer = LLMAnalyzer()
        data_storage = DataStorage()
        
        # Create mock reviews
        print("\n1. Creating mock review data...")
        mock_reviews = create_mock_reviews()
        print(f"Created {len(mock_reviews)} mock reviews")
        
        # Process text
        print("\n2. Processing review text...")
        processed_reviews = text_processor.preprocess_reviews(mock_reviews)
        print(f"Processed {len(processed_reviews)} reviews")
        
        # Show text statistics
        stats = text_processor.get_text_statistics(processed_reviews)
        print(f"Text stats: {stats}")
        
        # Analyze with LLM (only do first 2 to save API calls)
        print("\n3. Analyzing reviews with LLM...")
        demo_reviews = processed_reviews[:2]  # Just first 2 for demo
        
        analyzed_reviews = []
        for i, review in enumerate(demo_reviews):
            print(f"Analyzing review {i+1}/{len(demo_reviews)}...")
            analyzed_review = llm_analyzer.analyze_review(review, "sentiment")
            analyzed_reviews.append(analyzed_review)
        
        print(f"Analyzed {len(analyzed_reviews)} reviews")
        
        # Save results
        print("\n4. Saving results...")
        
        # Save to JSON
        json_file = data_storage.save_to_json(analyzed_reviews)
        print(f"Saved JSON: {json_file}")
        
        # Save to CSV
        csv_file = data_storage.save_to_csv(analyzed_reviews)
        print(f"Saved CSV: {csv_file}")
        
        # Save summary report
        summary_file = data_storage.save_summary_report(analyzed_reviews)
        print(f"Saved summary: {summary_file}")
        
        # Show sample results
        print("\n5. Sample Results:")
        print("-" * 30)
        
        for i, review in enumerate(analyzed_reviews):
            print(f"\nReview {i+1}:")
            print(f"Title: {review.get('title', 'N/A')}")
            print(f"Rating: {review.get('rating', 'N/A')}")
            print(f"Text: {review.get('text', 'N/A')[:100]}...")
            
            sentiment = review.get('sentiment_analysis', {})
            if sentiment:
                print(f"Sentiment: {sentiment.get('sentiment', 'N/A')}")
                print(f"Score: {sentiment.get('score', 'N/A')}")
                print(f"Summary: {sentiment.get('summary', 'N/A')}")
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("Check the 'output' directory for generated files.")
        
        # Show analysis statistics
        analysis_stats = llm_analyzer.get_analysis_statistics(analyzed_reviews)
        print(f"\nAnalysis Statistics:")
        for key, value in analysis_stats.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
