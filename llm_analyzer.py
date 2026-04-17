"""
LLM integration module for sentiment analysis and review summarization.
"""

import openai
import time
from typing import Dict, List, Optional
from config import Config
import logging

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """Class for analyzing reviews using LLM APIs."""
    
    def __init__(self):
        # Configure OpenAI client
        self.client = openai.OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )
        
        # System prompts for different analysis tasks
        self.sentiment_prompt = """You are an expert sentiment analyzer. Analyze the sentiment of the following product review and provide:
1. Overall sentiment (Positive, Negative, or Neutral)
2. Sentiment score (1-10, where 1 is very negative and 10 is very positive)
3. Key positive points (if any)
4. Key negative points (if any)
5. Brief summary (1-2 sentences)

Format your response as JSON with keys: sentiment, score, positive_points, negative_points, summary."""

        self.summary_prompt = """You are an expert at summarizing product reviews. Provide a concise summary of the following review that captures the main points, key insights, and overall customer experience. Keep the summary to 2-3 sentences maximum."""

        self.detailed_analysis_prompt = """You are an expert product review analyst. Analyze the following review and provide:
1. Main themes/topics discussed
2. Specific product features mentioned
3. Customer satisfaction level
4. Recommendations or complaints
5. Overall impact assessment

Format your response as JSON with keys: themes, features, satisfaction, recommendations, impact."""
    
    def _make_api_call(self, messages: List[Dict], max_retries: int = 3) -> Optional[str]:
        """
        Make API call with retry logic and rate limiting.
        
        Args:
            messages: List of message dictionaries for the API
            max_retries: Maximum number of retry attempts
            
        Returns:
            API response content or None if failed
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Making LLM API call (attempt {attempt + 1})")
                
                response = self.client.chat.completions.create(
                    model=Config.DEFAULT_MODEL,
                    messages=messages,
                    max_tokens=Config.MAX_TOKENS,
                    temperature=Config.TEMPERATURE,
                    timeout=30
                )
                
                return response.choices[0].message.content
                
            except openai.RateLimitError as e:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Rate limit hit, waiting {wait_time} seconds: {e}")
                time.sleep(wait_time)
                
            except openai.APIError as e:
                logger.warning(f"API error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"API call failed after {max_retries} attempts")
                    return None
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error in API call: {e}")
                return None
        
        return None
    
    def analyze_sentiment(self, text: str) -> Optional[Dict]:
        """
        Analyze sentiment of review text.
        
        Args:
            text: Review text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text or not text.strip():
            return None
        
        messages = [
            {"role": "system", "content": self.sentiment_prompt},
            {"role": "user", "content": f"Review to analyze:\n\n{text}"}
        ]
        
        response = self._make_api_call(messages)
        
        if response:
            try:
                import json
                # Try to parse as JSON
                if response.strip().startswith('{'):
                    return json.loads(response)
                else:
                    # If not JSON, create a simple response
                    return {
                        "sentiment": "Neutral",
                        "score": 5,
                        "positive_points": [],
                        "negative_points": [],
                        "summary": response.strip()
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning raw text")
                return {
                    "sentiment": "Neutral",
                    "score": 5,
                    "positive_points": [],
                    "negative_points": [],
                    "summary": response.strip()
                }
        
        return None
    
    def summarize_review(self, text: str) -> Optional[str]:
        """
        Generate a summary of review text.
        
        Args:
            text: Review text to summarize
            
        Returns:
            Summary string or None if failed
        """
        if not text or not text.strip():
            return None
        
        messages = [
            {"role": "system", "content": self.summary_prompt},
            {"role": "user", "content": f"Review to summarize:\n\n{text}"}
        ]
        
        return self._make_api_call(messages)
    
    def detailed_analysis(self, text: str) -> Optional[Dict]:
        """
        Perform detailed analysis of review text.
        
        Args:
            text: Review text to analyze
            
        Returns:
            Dictionary with detailed analysis results
        """
        if not text or not text.strip():
            return None
        
        messages = [
            {"role": "system", "content": self.detailed_analysis_prompt},
            {"role": "user", "content": f"Review to analyze:\n\n{text}"}
        ]
        
        response = self._make_api_call(messages)
        
        if response:
            try:
                import json
                # Try to parse as JSON
                if response.strip().startswith('{'):
                    return json.loads(response)
                else:
                    # If not JSON, create a simple response
                    return {
                        "themes": [],
                        "features": [],
                        "satisfaction": "Unknown",
                        "recommendations": response.strip(),
                        "impact": "Not assessed"
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning raw text")
                return {
                    "themes": [],
                    "features": [],
                    "satisfaction": "Unknown",
                    "recommendations": response.strip(),
                    "impact": "Not assessed"
                }
        
        return None
    
    def analyze_review(self, review: Dict, analysis_type: str = "sentiment") -> Dict:
        """
        Analyze a single review.
        
        Args:
            review: Review dictionary
            analysis_type: Type of analysis ("sentiment", "summary", or "detailed")
            
        Returns:
            Review dictionary with analysis results
        """
        analyzed_review = review.copy()
        text = review.get('text', '')
        
        if not text:
            logger.warning("No text found in review")
            analyzed_review['analysis_error'] = "No text to analyze"
            return analyzed_review
        
        try:
            if analysis_type == "sentiment":
                result = self.analyze_sentiment(text)
                analyzed_review['sentiment_analysis'] = result
                
            elif analysis_type == "summary":
                result = self.summarize_review(text)
                analyzed_review['summary'] = result
                
            elif analysis_type == "detailed":
                result = self.detailed_analysis(text)
                analyzed_review['detailed_analysis'] = result
                
            else:
                logger.warning(f"Unknown analysis type: {analysis_type}")
                analyzed_review['analysis_error'] = f"Unknown analysis type: {analysis_type}"
                
        except Exception as e:
            logger.error(f"Error analyzing review: {e}")
            analyzed_review['analysis_error'] = str(e)
        
        analyzed_review['analyzed'] = True
        return analyzed_review
    
    def analyze_reviews(self, reviews: List[Dict], analysis_type: str = "sentiment") -> List[Dict]:
        """
        Analyze a list of reviews.
        
        Args:
            reviews: List of review dictionaries
            analysis_type: Type of analysis to perform
            
        Returns:
            List of analyzed review dictionaries
        """
        analyzed_reviews = []
        
        logger.info(f"Starting {analysis_type} analysis for {len(reviews)} reviews")
        
        for i, review in enumerate(reviews):
            logger.info(f"Analyzing review {i+1}/{len(reviews)}")
            
            analyzed_review = self.analyze_review(review, analysis_type)
            analyzed_reviews.append(analyzed_review)
            
            # Add small delay between requests to avoid rate limiting
            time.sleep(0.5)
        
        logger.info(f"Completed analysis of {len(analyzed_reviews)} reviews")
        return analyzed_reviews
    
    def get_analysis_statistics(self, reviews: List[Dict]) -> Dict:
        """
        Get statistics about the analysis results.
        
        Args:
            reviews: List of analyzed review dictionaries
            
        Returns:
            Dictionary with analysis statistics
        """
        if not reviews:
            return {}
        
        stats = {
            'total_reviews': len(reviews),
            'successfully_analyzed': 0,
            'analysis_errors': 0,
            'sentiment_distribution': {'Positive': 0, 'Negative': 0, 'Neutral': 0},
            'average_sentiment_score': 0,
        }
        
        sentiment_scores = []
        
        for review in reviews:
            if 'analysis_error' in review:
                stats['analysis_errors'] += 1
            elif review.get('analyzed'):
                stats['successfully_analyzed'] += 1
                
                # Collect sentiment data
                sentiment_analysis = review.get('sentiment_analysis')
                if sentiment_analysis:
                    sentiment = sentiment_analysis.get('sentiment', 'Neutral')
                    score = sentiment_analysis.get('score', 5)
                    
                    if sentiment in stats['sentiment_distribution']:
                        stats['sentiment_distribution'][sentiment] += 1
                    
                    sentiment_scores.append(score)
        
        # Calculate average sentiment score
        if sentiment_scores:
            stats['average_sentiment_score'] = sum(sentiment_scores) / len(sentiment_scores)
        
        return stats
