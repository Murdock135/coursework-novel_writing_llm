def get_llm(provider, model):
    model = model or "meta-llama/llama-4-maverick:free"

    if provider == openrouter:
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL")
        breakpoint()        
        return ChatOpenAI(
                openai_api_key=api_key,
                openai_api_base=base_url,
                model_name=str(model)
                )

    elif provider == ollama:
        return ChatOllama(model="gemma3:12b")  

if __name__ == "__main__":
    pass
