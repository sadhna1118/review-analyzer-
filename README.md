# Review Analyzer

A comprehensive Python application for scraping product reviews from e-commerce websites and analyzing them using Large Language Models (LLMs). This tool extracts review data, processes it, and generates sentiment analysis, summaries, and detailed insights.

## Features

- **Multi-site Support**: Works with Amazon, Best Buy, and other e-commerce sites
- **Robust Web Scraping**: Handles pagination, rate limiting, and common anti-scraping measures
- **Text Processing**: Advanced text cleaning, tokenization, and chunking for long reviews
- **LLM Integration**: Uses OpenAI-compatible APIs for sentiment analysis and summarization
- **Multiple Export Formats**: JSON, CSV, and Excel output options
- **Error Handling**: Comprehensive error handling for network issues and API failures
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Configurable**: Easy configuration through environment variables

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd review-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

## Usage

### Command Line Interface

Basic usage:
```bash
python main.py "https://www.amazon.com/product-url"
```

Advanced options:
```bash
python main.py "https://www.amazon.com/product-url" \
    --analysis-type sentiment \
    --max-pages 10 \
    --output-format excel \
    --output-dir results
```

### Options

- `url`: Product page URL to analyze (required)
- `--analysis-type`: Type of analysis (`sentiment`, `summary`, `detailed`)
- `--max-pages`: Maximum number of pages to scrape (default: 5)
- `--output-format`: Output format (`json`, `csv`, `excel`)
- `--output-dir`: Output directory (default: `output`)

### Python API

```python
from main import ReviewAnalyzer

# Initialize the analyzer
analyzer = ReviewAnalyzer()

# Analyze a single product
results = analyzer.analyze_product_reviews(
    url="https://www.amazon.com/dp/B08N5WRWNW",
    analysis_type="sentiment",
    max_pages=5,
    output_format="json"
)

# Analyze multiple products
urls = [
    "https://www.amazon.com/dp/B08N5WRWNW",
    "https://www.amazon.com/dp/B08N5M7S6K"
]
results = analyzer.batch_analyze(urls, analysis_type="sentiment")
```

## Test URL

For testing purposes, we recommend using this Amazon product:
```
https://www.amazon.com/dp/B08N5WRWNW
```
(AirPods Pro - has plenty of reviews for testing)

## Architecture

The application is organized into several modules:

### Core Components

- **`main.py`**: Main application entry point and CLI interface
- **`config.py`**: Configuration management and environment variables
- **`scraper.py`**: Web scraping functionality with support for multiple sites
- **`text_processor.py`**: Text cleaning, tokenization, and preprocessing
- **`llm_analyzer.py`**: LLM integration for sentiment analysis and summarization
- **`data_storage.py`**: Data export and storage functionality

### Key Features

#### Web Scraping (`scraper.py`)
- User agent rotation
- Exponential backoff retry logic
- Support for Amazon and Best Buy
- Generic extraction for unknown sites
- Pagination handling

#### Text Processing (`text_processor.py`)
- HTML entity removal
- URL and email cleaning
- Token counting with tiktoken
- Text chunking for long reviews
- Comprehensive statistics

#### LLM Analysis (`llm_analyzer.py`)
- Rate limiting and retry logic
- Multiple analysis types
- Structured JSON responses
- Error handling for API failures

#### Data Storage (`data_storage.py`)
- Multiple export formats
- Comprehensive statistics
- Summary reports
- Backup files

## Output Formats

### JSON
```json
[
  {
    "title": "Great product!",
    "text": "I really love this product...",
    "rating": 5,
    "date": "October 15, 2023",
    "author": "John Doe",
    "sentiment_analysis": {
      "sentiment": "Positive",
      "score": 9,
      "positive_points": ["Easy to use", "Great value"],
      "negative_points": [],
      "summary": "Customer loves the product for its ease of use and value."
    }
  }
]
```

### CSV
Flattened structure with all fields including sentiment analysis results.

### Excel
Multiple sheets:
- **Reviews**: Main review data
- **Statistics**: Comprehensive analysis statistics

## Configuration

### Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Scraping Configuration
REQUEST_DELAY=1
MAX_RETRIES=3
TIMEOUT=30
```

### Supported LLM Providers

The application supports any OpenAI-compatible API:

- **OpenAI**: Default configuration
- **Anthropic**: Set `OPENAI_BASE_URL=https://api.anthropic.com/v1`
- **Local LLMs**: Set `OPENAI_BASE_URL=http://localhost:8000/v1`
- **Other providers**: Configure base URL and API key accordingly

## Error Handling

The application includes comprehensive error handling:

- **Network Issues**: Automatic retry with exponential backoff
- **API Failures**: Rate limiting and graceful degradation
- **Scraping Errors**: Fallback to generic extraction
- **Data Validation**: Input sanitization and validation

## Logging

The application logs to both file (`review_analyzer.log`) and console:
- INFO level for normal operations
- WARNING for recoverable issues
- ERROR for serious problems

## Limitations

1. **Site Compatibility**: While we support major sites, some e-commerce platforms may require custom selectors
2. **Rate Limits**: API providers may have rate limits; the app includes delays but may still hit limits
3. **Review Availability**: Some products may have limited reviews
4. **Dynamic Content**: Sites with heavy JavaScript may not work properly
5. **API Costs**: LLM API calls incur costs based on usage

## Troubleshooting

### Common Issues

1. **No Reviews Found**
   - Check if the URL is correct
   - Verify the site is supported
   - Try increasing `--max-pages`

2. **API Errors**
   - Verify API key is correct
   - Check API quota and rate limits
   - Try a different model

3. **Scraping Failures**
   - Check internet connection
   - Verify site is accessible
   - Try with different user agent

4. **Export Issues**
   - Check output directory permissions
   - Verify disk space
   - Try different output format

### Debug Mode

Enable debug logging:
```bash
python main.py --debug "https://example.com/product"
```

## Development

### Adding New Sites

To add support for a new e-commerce site:

1. Add extraction method in `scraper.py`
2. Update site detection logic
3. Test with sample URLs
4. Add documentation

### Adding New Analysis Types

1. Add prompt in `llm_analyzer.py`
2. Update analysis methods
3. Add export logic if needed
4. Update CLI options

## Performance

### Optimization Tips

- Use appropriate `--max-pages` to balance depth vs. time
- Choose analysis type based on needs (sentiment is fastest)
- Monitor API usage and costs
- Use batch processing for multiple URLs

### Resource Usage

- Memory: ~100MB for 1000 reviews
- API Calls: 1 call per review
- Time: ~1-2 seconds per review (including API)

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Create an issue with details

---

**Note**: This tool is for educational and research purposes. Always respect website terms of service and robots.txt files.
