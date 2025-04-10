import os
from langchain_community.chat_models import ChatOllama, ChatOpenAI

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
        # return init_chat_model(

