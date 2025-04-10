# from plot_generator import generate_novel_outline
from llm_config import get_llm
from load_env import load_env_vars
import argparse
from utilities.io import load_text
from config import Config

if __name__ == "__main__":
    # load environment variables
    load_env_vars()

    # Get LLM
    parser = argparse.ArgumentParser(
            prog='Novel Writer',
            description='Writes a novel using LLMs'
            )
    parser.add_argument('-p', '--provider', default='openrouter')
    parser.add_argument('-m', '--model', default="meta-llama/llama-4-maverick:free")
    args = parser.parse_args()
    provider, model = args.provider, args.model 
    llm = get_llm(provider, model)
   
    # Produce novel outline
    prompt = load_text(Config.plot_generator_prompt)
    breakpoint()
    response = llm.invoke(prompt).content
    print(response)
    # outline = generate_novel_outline() 
