from typing import List, Dict, Any
import os
import random
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings  # Updated import
from langchain_core.documents import Document

class SceneRetriever:
    """Retrieves relevant previous scene summaries for context with added diversity."""
    
    def __init__(self, provider: str = "ollama", model_name: str = None):
        """Initialize the retriever with the appropriate embedding model."""
        # Use llama3.2:latest as the default model for embeddings
        self.embeddings = OllamaEmbeddings(model=model_name or "llama3.2:latest")
        
        self.vector_store = None
        self.summaries = []
    
    def load_summaries(self, summaries_dir: str) -> None:
        """Load scene summaries from files and create a vector store."""
        self.summaries = []
        
        # Check if directory exists
        if not os.path.exists(summaries_dir):
            print(f"Warning: Directory {summaries_dir} does not exist.")
            return
            
        # Get all summary files
        summary_files = [f for f in os.listdir(summaries_dir) if f.startswith("summary_")]
        if not summary_files:
            print(f"Warning: No summary files found in {summaries_dir}")
            return
            
        # Process each summary file
        for filename in summary_files:
            file_path = os.path.join(summaries_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Extract metadata from filename
                    parts = filename.replace("summary_", "").replace(".txt", "").split("_")
                    if len(parts) >= 2:
                        act = parts[0]
                        scene = parts[1]
                        
                        # Add to summaries with metadata
                        self.summaries.append(
                            Document(
                                page_content=content,
                                metadata={"file": filename, "act": act, "scene": scene}
                            )
                        )
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
        
        # Create vector store if we have any summaries
        if self.summaries:
            print(f"Creating vector store with {len(self.summaries)} summaries")
            self.vector_store = FAISS.from_documents(self.summaries, self.embeddings)
        else:
            print("No valid summaries found to create vector store")
    
    def get_relevant_context(self, scene_description: str, k: int = 3, diversity_factor: float = 0.5) -> str:
        """Retrieve scene context with a mix of relevant and diverse (older/disjoint) contexts.
        
        Args:
            scene_description: The description of the current scene to find relevant context for
            k: Total number of context scenes to return
            diversity_factor: Proportion of scenes that should be diverse rather than relevant
                             (0.0 = all relevant, 1.0 = all diverse)
        
        Returns:
            Formatted context string with a mix of relevant and diverse scenes
        """
        if not self.vector_store or not self.summaries:
            return ""
        
        if len(self.summaries) <= k:
            # Not enough summaries for diversity, just return all we have
            relevant_docs = self.summaries
        else:
            # Calculate how many should be relevant vs diverse
            relevant_count = max(1, int(k * (1 - diversity_factor)))
            diverse_count = k - relevant_count
            
            # Get most relevant scenes based on similarity
            relevant_docs = self.vector_store.similarity_search(scene_description, k=relevant_count)
            
            # Get IDs of scenes we already selected
            selected_ids = [doc.metadata.get("file") for doc in relevant_docs]
            
            # Select diverse scenes (older or disjoint from current context)
            potential_diverse_docs = [doc for doc in self.summaries 
                                    if doc.metadata.get("file") not in selected_ids]
            
            if potential_diverse_docs and diverse_count > 0:
                # Randomly select diverse scenes
                diverse_docs = random.sample(potential_diverse_docs, 
                                           min(diverse_count, len(potential_diverse_docs)))
                
                # Combine relevant and diverse scenes
                relevant_docs.extend(diverse_docs)
                
                # Shuffle to prevent the model from identifying which are relevant vs diverse
                random.shuffle(relevant_docs)
        
        # Format the context
        context_parts = []
        for i, doc in enumerate(relevant_docs):
            act = doc.metadata.get("act", "Unknown Act")
            scene = doc.metadata.get("scene", "Unknown Scene")
            context_parts.append(f"Previous Scene ({act}, {scene}):\n{doc.page_content}")
        
        return "\n\n".join(context_parts)