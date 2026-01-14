import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable is required")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are required")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is required")
