from typing import List, Dict, Any, Optional, Tuple
import os
import random
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from utilities.io import load_summaries

def create_embeddings(provider: str = "ollama", model_name: str = None):
    """
    Create an embeddings model for vectorizing scene content.
    
    Args:
        provider: The provider to use for embeddings
        model_name: Specific model name to use
        
    Returns:
        Embeddings model
    """
    # Use llama3.2:latest as the default model for embeddings
    return OllamaEmbeddings(model=model_name or "llama3.2:latest")

def create_vector_store(summaries_dict: Dict[str, Document], embeddings):
    """
    Create a FAISS vector store from a dictionary of summaries.
    
    Args:
        summaries_dict: Dictionary mapping keys to Document objects
        embeddings: Embedding model to use for vectorization
        
    Returns:
        FAISS vector store or None if summaries_dict is empty
    """
    if not summaries_dict:
        print("No summaries provided to create vector store")
        return None
        
    summaries_list = list(summaries_dict.values())
    print(f"Creating vector store with {len(summaries_list)} summaries")
    return FAISS.from_documents(summaries_list, embeddings)

def get_relevant_scenes(vector_store, scene_content: str, relevant_count: int) -> List[Document]:
    """
    Retrieve the most relevant scenes based on semantic similarity.
    
    Args:
        vector_store: FAISS vector store containing scene embeddings
        scene_content: The content to find similar scenes for
        relevant_count: Number of relevant scenes to retrieve
        
    Returns:
        List of Document objects representing the most relevant scenes
    """
    if not vector_store:
        return []
        
    return vector_store.similarity_search(scene_content, k=relevant_count)

def diversify_context(relevant_docs: List[Document], all_summaries: Dict[str, Document], 
                    total_count: int, diversity_factor: float) -> List[Document]:
    """
    Add diversity to the selected context by including some random non-similar documents.
    
    Args:
        relevant_docs: List of already selected relevant documents
        all_summaries: Dictionary of all available summaries
        total_count: Total number of documents to return
        diversity_factor: Proportion of scenes that should be diverse (0.0-1.0)
        
    Returns:
        List of documents with both relevant and diverse selections
    """
    if not relevant_docs or not all_summaries:
        return relevant_docs
    
    # If we don't have enough summaries for meaningful diversity
    if len(all_summaries) <= len(relevant_docs):
        return list(all_summaries.values())[:total_count]
    
    # Calculate how many diverse documents we need
    diverse_count = total_count - len(relevant_docs)
    
    if diverse_count <= 0:
        return relevant_docs[:total_count]
    
    # Get IDs of scenes we already selected
    selected_ids = [doc.metadata.get("file") for doc in relevant_docs]
    
    # Select potential diverse scenes (not already selected)
    potential_diverse_docs = [doc for key, doc in all_summaries.items() 
                            if doc.metadata.get("file") not in selected_ids]
    
    if not potential_diverse_docs:
        return relevant_docs
    
    # Randomly select diverse scenes
    diverse_docs = random.sample(potential_diverse_docs, 
                              min(diverse_count, len(potential_diverse_docs)))
    
    # Combine relevant and diverse scenes
    result = relevant_docs + diverse_docs
    
    # Shuffle to prevent the model from identifying which are relevant vs diverse
    random.shuffle(result)
    
    return result

def format_context(docs: List[Document]) -> str:
    """
    Format a list of Document objects into a context string.
    
    Args:
        docs: List of Document objects to format
        
    Returns:
        Formatted context string
    """
    if not docs:
        return ""
        
    context_parts = []
    for doc in docs:
        act = doc.metadata.get("act", "Unknown Act")
        scene = doc.metadata.get("scene", "Unknown Scene")
        context_parts.append(f"Previous Scene ({act}, {scene}):\n{doc.page_content}")
    
    return "\n\n".join(context_parts)

def get_relevant_context(scene_content: str, summaries_dir: str, 
                     embeddings=None, k: int = 3, diversity_factor: float = 0.5) -> str:
    """
    Retrieve scene context with a mix of relevant and diverse contexts.
    
    Args:
        scene_content: The content of the current scene 
        summaries_dir: Directory to load summaries from
        embeddings: Optional embedding model (created if not provided)
        k: Total number of context scenes to return
        diversity_factor: Proportion of scenes that should be diverse (0.0-1.0)
    
    Returns:
        Formatted context string with a mix of relevant and diverse scenes
    """
    # Create embedding model if not provided
    if embeddings is None:
        embeddings = create_embeddings()
        
    # Load summaries from the directory
    summaries = load_summaries(summaries_dir)
    if not summaries:
        return ""
    
    # Create vector store from summaries
    vector_store = create_vector_store(summaries, embeddings)
    if not vector_store:
        return ""
    
    # Calculate how many should be relevant vs diverse
    relevant_count = max(1, int(k * (1 - diversity_factor)))
    
    # Get most relevant scenes based on similarity
    relevant_docs = get_relevant_scenes(vector_store, scene_content, relevant_count)
    
    # Add diversity to the context
    final_docs = diversify_context(relevant_docs, summaries, k, diversity_factor)
    
    # Format and return the context
    return format_context(final_docs)