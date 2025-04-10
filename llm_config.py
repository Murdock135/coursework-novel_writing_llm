import os
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from load_env import load_env_vars

def get_llm(provider="openrouter", model="meta-llama/llama-4-maverick:free"):
    provider = provider.lower()

    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL")

        if not api_key or not base_url:
            raise EnvironmentError("Missing OPENROUTER_API_KEY or OPENROUTER_BASE_URL.")

        return ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base=base_url,
            model_name=model,
        )
    else:
        return ChatOllama(model=model)
    
# def get_llm_backend(args):
    # """Parse CLI args and return LLM provider and model names"""

    # provider = args.backend

    # if args.backend == 'openrouter':
    #     model= ''
    # elif args.backend == 'ollama':
    #     model = ''
    # return provider, model

if __name__ == "__main__":
    load_env_vars()
    llm = get_llm()
    response = llm.invoke("Hi there. What model are you?").content
    print(response)
