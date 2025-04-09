import datetime
import os
import sys
from typing import List
from config import Config
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import load_prompt, ChatPromptTemplate, PromptTemplate
from pydantic import BaseModel, Field
from get_llm import get_llm

def load_text(file_path):
    with open(file_path, 'r') as f:
        text = f.read()

    return text

def generate_novel_outline():
    pass

if __name__ == "__main__":
    generate_novel_outline()
