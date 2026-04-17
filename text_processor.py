"""
Text preprocessing and tokenization module for review analysis.
"""

import re
import tiktoken
from typing import List, Dict, Tuple
from config import Config
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """Class for processing and tokenizing review text."""
    
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize review text.
        
        Args:
            text: Raw review text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z]+;', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!?]{3,}', '!', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', '', text)
        
        # Strip and return
        return text.strip()
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text using tiktoken.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
            
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error counting tokens: {e}")
            # Fallback to rough estimation (1 token ~ 4 characters)
            return len(text) // 4
    
    def chunk_text(self, text: str, max_tokens: int = None) -> List[str]:
        """
        Split long text into chunks that fit within token limits.
        
        Args:
            text: Text to chunk
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        if max_tokens is None:
            max_tokens = Config.MAX_TOKENS
        
        # If text is short enough, return as single chunk
        if self.count_tokens(text) <= max_tokens:
            return [text]
        
        # Split into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed token limit
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if self.count_tokens(test_chunk) <= max_tokens:
                current_chunk = test_chunk
            else:
                # Add current chunk if it exists
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with current sentence
                current_chunk = sentence.strip()
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def preprocess_review(self, review: Dict) -> Dict:
        """
        Preprocess a single review dictionary.
        
        Args:
            review: Raw review dictionary
            
        Returns:
            Processed review dictionary
        """
        processed_review = review.copy()
        
        # Clean the review text
        if 'text' in review:
            processed_review['text'] = self.clean_text(review['text'])
            processed_review['token_count'] = self.count_tokens(processed_review['text'])
        
        # Clean the title if it exists
        if 'title' in review and review['title']:
            processed_review['title'] = self.clean_text(review['title'])
        
        # Add metadata about processing
        processed_review['processed'] = True
        
        return processed_review
    
    def preprocess_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """
        Preprocess a list of reviews.
        
        Args:
            reviews: List of raw review dictionaries
            
        Returns:
            List of processed review dictionaries
        """
        processed_reviews = []
        
        for review in reviews:
            try:
                processed_review = self.preprocess_review(review)
                
                # Only include reviews that have text after processing
                if processed_review.get('text') and processed_review['text'].strip():
                    processed_reviews.append(processed_review)
                else:
                    logger.warning("Review excluded due to empty text after processing")
                    
            except Exception as e:
                logger.warning(f"Error processing review: {e}")
                continue
        
        logger.info(f"Processed {len(processed_reviews)} out of {len(reviews)} reviews")
        return processed_reviews
    
    def get_text_statistics(self, reviews: List[Dict]) -> Dict:
        """
        Get statistics about the processed reviews.
        
        Args:
            reviews: List of processed review dictionaries
            
        Returns:
            Dictionary with text statistics
        """
        if not reviews:
            return {}
        
        token_counts = [r.get('token_count', 0) for r in reviews]
        text_lengths = [len(r.get('text', '')) for r in reviews]
        
        stats = {
            'total_reviews': len(reviews),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_review': sum(token_counts) / len(token_counts) if token_counts else 0,
            'max_tokens': max(token_counts) if token_counts else 0,
            'min_tokens': min(token_counts) if token_counts else 0,
            'avg_text_length': sum(text_lengths) / len(text_lengths) if text_lengths else 0,
            'max_text_length': max(text_lengths) if text_lengths else 0,
            'min_text_length': min(text_lengths) if text_lengths else 0,
        }
        
        return stats
