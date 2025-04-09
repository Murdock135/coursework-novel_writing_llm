from plot_generator import generate_novel_outline
from get_llm import get_llm

def get_llm_backend(args):
    provider = args.backend

    if args.backend == 'openrouter':
        model= ''
    elif args.backend == 'ollama':
        model = ''
    return provider, model

if __name__ == "__main__":
    # Get LLM
    parser = argparse.ArgumentParser(
            prog='Novel Writer',
            description='Writes a novel using LLMs'
            )
    parser.add_argument('-b', '--backend')
    args = parser.parse_args()
    provider, model = get_llm_backend(args) 
    llm = get_llm(provider, model)

    outline = generate_novel_outline() 
