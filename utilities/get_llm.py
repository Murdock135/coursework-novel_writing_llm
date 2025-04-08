def get_llm(args):
    model = args.model or "meta-llama/llama-4-maverick:free"

    if args.openrouter and args.ollama:
        raise ValueError("Please specify only one backend: --openrouter or --ollama. Not both.")

    if args.openrouter:
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL")
        breakpoint()        
        return ChatOpenAI(
                openai_api_key=api_key,
                openai_api_base=base_url,
                model_name=str(model)
                )

    elif args.ollama:
        return ChatOllama(model="gemma3:12b")  
