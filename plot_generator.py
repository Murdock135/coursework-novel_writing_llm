
def generate_novel_outline(llm, prompt) -> str:
    novel_outline = llm.invoke(prompt).content
    return novel_outline

if __name__ == "__main__":
    outline = generate_n;ovel_outline()
