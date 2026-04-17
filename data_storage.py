"""
Data storage and export module for review analysis results.
"""

import json
import csv
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
from config import Config
import logging

logger = logging.getLogger(__name__)

class DataStorage:
    """Class for storing and exporting review analysis results."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def _generate_filename(self, base_name: str, extension: str) -> str:
        """Generate a timestamped filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"
    
    def save_to_json(self, reviews: List[Dict], filename: str = None) -> str:
        """
        Save reviews to JSON file.
        
        Args:
            reviews: List of review dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            filename = self._generate_filename("reviews", "json")
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Saved {len(reviews)} reviews to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            raise
    
    def save_to_csv(self, reviews: List[Dict], filename: str = None) -> str:
        """
        Save reviews to CSV file.
        
        Args:
            reviews: List of review dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            filename = self._generate_filename("reviews", "csv")
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Flatten nested dictionaries for CSV
            flattened_reviews = []
            for review in reviews:
                flat_review = {}
                
                # Basic fields
                for key in ['title', 'text', 'rating', 'date', 'author', 'verified', 'helpful_count']:
                    flat_review[key] = review.get(key, '')
                
                # Processing fields
                flat_review['token_count'] = review.get('token_count', 0)
                flat_review['processed'] = review.get('processed', False)
                
                # Sentiment analysis
                sentiment_analysis = review.get('sentiment_analysis', {})
                if isinstance(sentiment_analysis, dict):
                    flat_review['sentiment'] = sentiment_analysis.get('sentiment', '')
                    flat_review['sentiment_score'] = sentiment_analysis.get('score', 0)
                    flat_review['positive_points'] = '; '.join(sentiment_analysis.get('positive_points', []))
                    flat_review['negative_points'] = '; '.join(sentiment_analysis.get('negative_points', []))
                    flat_review['sentiment_summary'] = sentiment_analysis.get('summary', '')
                else:
                    flat_review['sentiment'] = ''
                    flat_review['sentiment_score'] = 0
                    flat_review['positive_points'] = ''
                    flat_review['negative_points'] = ''
                    flat_review['sentiment_summary'] = ''
                
                # Summary
                flat_review['llm_summary'] = review.get('summary', '')
                
                # Detailed analysis
                detailed_analysis = review.get('detailed_analysis', {})
                if isinstance(detailed_analysis, dict):
                    flat_review['themes'] = '; '.join(detailed_analysis.get('themes', []))
                    flat_review['features'] = '; '.join(detailed_analysis.get('features', []))
                    flat_review['satisfaction'] = detailed_analysis.get('satisfaction', '')
                    flat_review['recommendations'] = detailed_analysis.get('recommendations', '')
                    flat_review['impact'] = detailed_analysis.get('impact', '')
                else:
                    flat_review['themes'] = ''
                    flat_review['features'] = ''
                    flat_review['satisfaction'] = ''
                    flat_review['recommendations'] = ''
                    flat_review['impact'] = ''
                
                # Error handling
                flat_review['analysis_error'] = review.get('analysis_error', '')
                flat_review['analyzed'] = review.get('analyzed', False)
                
                flattened_reviews.append(flat_review)
            
            # Write to CSV
            if flattened_reviews:
                df = pd.DataFrame(flattened_reviews)
                df.to_csv(filepath, index=False, encoding='utf-8')
            else:
                # Create empty CSV with headers
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'title', 'text', 'rating', 'date', 'author', 'verified', 'helpful_count',
                        'token_count', 'processed', 'sentiment', 'sentiment_score', 
                        'positive_points', 'negative_points', 'sentiment_summary', 
                        'llm_summary', 'themes', 'features', 'satisfaction', 
                        'recommendations', 'impact', 'analysis_error', 'analyzed'
                    ])
            
            logger.info(f"Saved {len(reviews)} reviews to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise
    
    def save_to_excel(self, reviews: List[Dict], filename: str = None) -> str:
        """
        Save reviews to Excel file with multiple sheets.
        
        Args:
            reviews: List of review dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            filename = self._generate_filename("reviews", "xlsx")
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main reviews sheet
                flattened_reviews = []
                for review in reviews:
                    flat_review = {}
                    
                    # Basic fields
                    for key in ['title', 'text', 'rating', 'date', 'author', 'verified', 'helpful_count']:
                        flat_review[key] = review.get(key, '')
                    
                    # Processing fields
                    flat_review['token_count'] = review.get('token_count', 0)
                    flat_review['processed'] = review.get('processed', False)
                    
                    # Sentiment analysis
                    sentiment_analysis = review.get('sentiment_analysis', {})
                    if isinstance(sentiment_analysis, dict):
                        flat_review['sentiment'] = sentiment_analysis.get('sentiment', '')
                        flat_review['sentiment_score'] = sentiment_analysis.get('score', 0)
                        flat_review['positive_points'] = '; '.join(sentiment_analysis.get('positive_points', []))
                        flat_review['negative_points'] = '; '.join(sentiment_analysis.get('negative_points', []))
                        flat_review['sentiment_summary'] = sentiment_analysis.get('summary', '')
                    
                    # Summary
                    flat_review['llm_summary'] = review.get('summary', '')
                    
                    flat_review['analysis_error'] = review.get('analysis_error', '')
                    flat_review['analyzed'] = review.get('analyzed', False)
                    
                    flattened_reviews.append(flat_review)
                
                if flattened_reviews:
                    df_reviews = pd.DataFrame(flattened_reviews)
                    df_reviews.to_excel(writer, sheet_name='Reviews', index=False)
                
                # Statistics sheet
                stats = self._generate_statistics(reviews)
                df_stats = pd.DataFrame([stats])
                df_stats.to_excel(writer, sheet_name='Statistics', index=False)
            
            logger.info(f"Saved {len(reviews)} reviews to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving to Excel: {e}")
            raise
    
    def _generate_statistics(self, reviews: List[Dict]) -> Dict:
        """Generate statistics summary for the reviews."""
        stats = {
            'total_reviews': len(reviews),
            'with_text': len([r for r in reviews if r.get('text')]),
            'with_rating': len([r for r in reviews if r.get('rating')]),
            'processed': len([r for r in reviews if r.get('processed')]),
            'analyzed': len([r for r in reviews if r.get('analyzed')]),
            'analysis_errors': len([r for r in reviews if r.get('analysis_error')]),
        }
        
        # Sentiment statistics
        sentiments = [r.get('sentiment_analysis', {}).get('sentiment') for r in reviews if r.get('sentiment_analysis')]
        if sentiments:
            stats['positive_sentiment'] = sentiments.count('Positive')
            stats['negative_sentiment'] = sentiments.count('Negative')
            stats['neutral_sentiment'] = sentiments.count('Neutral')
        
        # Rating statistics
        ratings = [r.get('rating') for r in reviews if r.get('rating')]
        if ratings:
            stats['avg_rating'] = sum(ratings) / len(ratings)
            stats['min_rating'] = min(ratings)
            stats['max_rating'] = max(ratings)
        
        # Token statistics
        token_counts = [r.get('token_count', 0) for r in reviews]
        if token_counts:
            stats['total_tokens'] = sum(token_counts)
            stats['avg_tokens'] = sum(token_counts) / len(token_counts)
        
        return stats
    
    def save_summary_report(self, reviews: List[Dict], filename: str = None) -> str:
        """
        Save a comprehensive summary report.
        
        Args:
            reviews: List of review dictionaries
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            filename = self._generate_filename("summary_report", "json")
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'statistics': self._generate_statistics(reviews),
                'sample_reviews': reviews[:3] if reviews else [],  # First 3 reviews as sample
                'highlights': self._generate_highlights(reviews)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Saved summary report to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving summary report: {e}")
            raise
    
    def _generate_highlights(self, reviews: List[Dict]) -> Dict:
        """Generate highlights from the review analysis."""
        highlights = {
            'top_positive_points': [],
            'top_negative_points': [],
            'common_themes': [],
            'sample_summaries': []
        }
        
        # Collect all positive and negative points
        all_positive = []
        all_negative = []
        all_themes = []
        all_summaries = []
        
        for review in reviews:
            sentiment_analysis = review.get('sentiment_analysis', {})
            if isinstance(sentiment_analysis, dict):
                all_positive.extend(sentiment_analysis.get('positive_points', []))
                all_negative.extend(sentiment_analysis.get('negative_points', []))
            
            detailed_analysis = review.get('detailed_analysis', {})
            if isinstance(detailed_analysis, dict):
                all_themes.extend(detailed_analysis.get('themes', []))
            
            if review.get('summary'):
                all_summaries.append(review['summary'])
        
        # Get top items (simple frequency-based selection)
        from collections import Counter
        
        if all_positive:
            highlights['top_positive_points'] = [item for item, count in Counter(all_positive).most_common(5)]
        
        if all_negative:
            highlights['top_negative_points'] = [item for item, count in Counter(all_negative).most_common(5)]
        
        if all_themes:
            highlights['common_themes'] = [item for item, count in Counter(all_themes).most_common(5)]
        
        if all_summaries:
            highlights['sample_summaries'] = all_summaries[:3]
        
        return highlights
    
    def export_data(self, reviews: List[Dict], format_type: str = "json", filename: str = None) -> str:
        """
        Export reviews in the specified format.
        
        Args:
            reviews: List of review dictionaries
            format_type: Export format ("json", "csv", "excel")
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if format_type.lower() == "json":
            return self.save_to_json(reviews, filename)
        elif format_type.lower() == "csv":
            return self.save_to_csv(reviews, filename)
        elif format_type.lower() == "excel":
            return self.save_to_excel(reviews, filename)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
