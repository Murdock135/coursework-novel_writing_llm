from pathlib import Path
from dotenv import load_dotenv
import os

# load ~/.secrets/.llm_apis
load_dotenv(dotenv_path=Path.home() / ".secrets/.llm_apis")

# load project .env
load_dotenv()
print(os.getenv("OPENROUTER_API"))
