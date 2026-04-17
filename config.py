"""
Configuration management for the review analyzer application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    
    # LLM Model Configuration
    DEFAULT_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.3
    
    # Scraping Configuration
    REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', 1))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    TIMEOUT = int(os.getenv('TIMEOUT', 30))
    
    # Text Processing
    MAX_REVIEW_LENGTH = 8000  # Maximum characters for a single review
    CHUNK_SIZE = 4000  # Size of chunks for long reviews
    
    # Output Configuration
    OUTPUT_DIR = "output"
    DEFAULT_OUTPUT_FORMAT = "json"
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        
        return True
