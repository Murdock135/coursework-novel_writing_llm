from pathlib import Path
from dotenv import load_dotenv
import os

def load_env_vars():
    # load ~/.secrets/.llm_apis
    load_dotenv(dotenv_path=Path.home() / ".secrets/.llm_apis")

    # load project .env
    load_dotenv()

if __name__=="__main__":
    load_env_vars()
    print(os.getenv("OPENROUTER_API"))
