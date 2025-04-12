import requests
import os
import sys
import pathlib

# Add parent directory to path to allow importing load_env
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from load_env import load_env_vars

# Load environment variables
load_env_vars()

# Get API key from environment
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("Error: OPENROUTER_API_KEY not found in environment variables")
    exit(1)

response = requests.get(
    url="https://openrouter.ai/api/v1/auth/key",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)

print(json.dumps(response.json(), indent=2))