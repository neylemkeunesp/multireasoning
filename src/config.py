from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Dict
import os

# Load environment variables and print status
load_dotenv()
if not os.getenv("OPENROUTER_API_KEY"):
    print("Warning: OPENROUTER_API_KEY not found in environment variables")
    print("Checking .env file...")
    try:
        with open(".env") as f:
            if "OPENROUTER_API_KEY" not in f.read():
                print("OPENROUTER_API_KEY not found in .env file")
    except FileNotFoundError:
        print(".env file not found")

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str = ""  # Make it optional to avoid immediate error
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Model configurations
    MODELS: Dict[str, str] = {
        "o1": "openai/gpt-4",  # Primary model (using GPT-4)
        "gemini": "google/gemini-pro",    # Secondary model
        "deepseek": "deepseek/deepseek-r1"  # Tertiary model (using Deepseek)
    }
    
    class Config:
        env_file = ".env"

# Create settings instance and validate API key
settings = Settings()
if not settings.OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is not set. Please set it in your environment "
        "variables or .env file. Get your API key from https://openrouter.ai/"
    )
