from typing import List, Dict, Any
import os
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings  # Updated import
from langchain_core.documents import Document

class SceneRetriever:
    """Retrieves relevant previous scene summaries for context."""
    
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
    
    def get_relevant_context(self, scene_description: str, k: int = 3) -> str:
        """Retrieve the k most relevant previous scene summaries."""
        if not self.vector_store or not self.summaries:
            return ""
            
        # Perform similarity search
        relevant_docs = self.vector_store.similarity_search(scene_description, k=k)
        
        # Format the context
        context_parts = []
        for i, doc in enumerate(relevant_docs):
            act = doc.metadata.get("act", "Unknown Act")
            scene = doc.metadata.get("scene", "Unknown Scene")
            context_parts.append(f"Previous Scene ({act}, {scene}):\n{doc.page_content}")
        
        return "\n\n".join(context_parts)