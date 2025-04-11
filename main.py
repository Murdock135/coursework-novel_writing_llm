# from plot_generator import generate_novel_outline
from llm_config import get_llm
from load_env import load_env_vars
import argparse
from utilities.io import load_text
from config import Config
from langchain_core.prompts import ChatPromptTemplate

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
  
    # Novel metadata (genre, tone, etc)
    config = Config()
    novel_metadata: dict = config.get_novel_metadata()
    breakpoint()
    
    # Get user input
    user_input = input("Describe the novel you want to write:\n")

    # Produce novel outline
    outliner_prompt_raw_text = load_text(config.plot_generator_prompt)
    outliner_prompt = ChatPromptTemplate.from_messages([
        ("system", outliner_prompt_raw_text),
        ("user", "{user_input}")]).partial(
        genre=novel_metadata['genre'],
        tone=novel_metadata['tone'],
        main_character=novel_metadata['main_character'],
        themes=novel_metadata['themes'],
        authors_message=novel_metadata['authors_message']
    )
    
    chain = outliner_prompt | llm
    breakpoint()
    response = chain.invoke({"user_input" : user_input}).content
    print(response)
    # outline = generate_novel_outline() 
