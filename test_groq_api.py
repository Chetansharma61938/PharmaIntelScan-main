import os
from dotenv import load_dotenv
from groq import Groq
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_groq_api():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY not found in environment variables")
        return False
        
    logger.info(f"API Key found: {api_key[:10]}...")  # Only log first 10 chars for security
    
    try:
        # Initialize client
        client = Groq(api_key=api_key)
        
        # Test with a simple request
        logger.info("Testing API connection...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Using the correct Llama model
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=10
        )
        
        logger.info("API Test Successful!")
        logger.info(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        logger.error(f"API Test Failed: {str(e)}")
        logger.error("Please ensure your API key is valid and has not expired")
        return False

if __name__ == "__main__":
    test_groq_api() 