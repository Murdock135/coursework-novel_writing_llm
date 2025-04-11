import os
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from load_env import load_env_vars

def get_llm(provider="openrouter", model="meta-llama/llama-4-maverick:free", temperature=0.7, max_retries=2):
    """
    Create and configure an LLM instance based on provider and parameters.
    
    Args:
        provider: LLM provider ("openrouter" or "ollama")
        model: Model name to use
        temperature: Temperature setting for generation (0.0-1.0)
        max_retries: Maximum number of retries on API failure
        
    Returns:
        Configured LLM instance
    """
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
            temperature=temperature,
            max_retries=max_retries,
        )
    else:
        return ChatOllama(
            model=model,
            temperature=temperature,
        )
    

if __name__ == "__main__":
    load_env_vars()
    llm = get_llm()
    response = llm.invoke("Hi there. What model are you?").content
    print(response)
