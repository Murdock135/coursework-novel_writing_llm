# Novel Writer LLM

A modular pipeline for generating complete novels using language models.

## Overview

This project provides an automated pipeline for generating novels following a three-act structure. It uses language models to:

1. Generate a structured outline based on a story concept
2. Write individual scenes based on the outline with context awareness
3. Generate summaries for each scene
4. Compile the novel with proper organization

## Features

- Flexible configuration through `config.py`
- Support for multiple LLM providers (OpenRouter, Ollama)
- Three-act structure with modular scene generation
- Structured output formats using Pydantic models
- Vector-based retrieval system using FAISS for context-aware writing
- Progress tracking and error handling
- Scene and summary file organization
- Statistics tracking for pipeline execution

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- API keys for language model providers

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables for API keys
   - `OPENROUTER_API_KEY`
   - `OPENROUTER_BASE_URL`

## Usage

Run the full pipeline:

```bash
python main.py
```

Command-line options:
- `-p, --provider`: LLM provider (default: openrouter)
- `-m, --model`: Model name to use (default: meta-llama/llama-4-maverick:free)
- `-s, --summary-model`: Model for scene summarization
- `-o, --outline-only`: Generate only the outline without writing scenes

Test with a specified number of acts:

```bash
python test_one_act.py --acts 2
```

Test outputs are saved to separate directories for analysis.

## Configuration

Edit `config.py` to customize:
- Novel metadata (genre, tone, themes)
- File paths for prompts and outputs
- Default settings
- LLM provider configurations

## Project Structure

- `main.py`: Entry point and pipeline orchestration
- `novel_pipeline.py`: Core pipeline implementation
- `novel_outliner.py`: Manages the outlining process
- `outline_generator.py`: Generates structured novel outline
- `scene_writer.py`: Writes individual scenes
- `scene_summary_generator.py`: Creates summaries of scenes
- `retrieval.py`: Vector-based context retrieval using FAISS
- `stats_tracker.py`: Tracks performance and completion metrics
- `config.py`: Configuration settings
- `output_schemas.py`: Pydantic data models
- `utilities/`: Helper functions and tools
- `sys_messages/`: System prompts for LLMs
- `data/`: Input story descriptions and output files
  - `scenes/`: Generated scene content
  - `scene_summaries/`: Summaries for each scene
  - `test/`: Test output storage