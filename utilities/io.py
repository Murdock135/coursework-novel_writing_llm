import os
import glob
from typing import Dict, Any
from langchain_core.documents import Document

def clear_directory(directory_path: str):
    """
    Delete all files in a directory without removing the directory itself.
    
    Args:
        directory_path: Path to the directory to clear
    """
    if os.path.exists(directory_path):
        files = glob.glob(os.path.join(directory_path, '*'))
        for f in files:
            if os.path.isfile(f):
                os.remove(f)

def load_text(file_path):
    """Loads text from a file."""
    with open(file_path, 'r') as f:
        text = f.read()

    return text

def pretty_print_scene(act_num: int, scene_num: int, content: str):
    """
    Prints a scene with nice formatting.
    
    Args:
        act_num: Act number
        scene_num: Scene number
        content: The scene content to print
    """
    width = 80
    border = "=" * width
    title = f" ACT {act_num}, SCENE {scene_num} "
    padding = "=" * ((width - len(title)) // 2)
    header = padding + title + padding
    # Adjust header if width is odd
    if len(header) < width:
        header += "="
    
    print("\n" + border)
    print(header)
    print(border + "\n")
    print(content)
    print("\n" + border)
    print(border + "\n")

def get_scene_filename(act_num: int, scene_num: int, is_summary: bool = False) -> str:
    """
    Constructs a filename for a scene or summary file.
    
    Args:
        act_num: Act number
        scene_num: Scene number
        is_summary: Whether this is a scene summary
        
    Returns:
        The constructed filename
    """
    prefix = "summary_" if is_summary else ""
    return f"{prefix}act{act_num}_scene{scene_num}.txt"

def get_scene_path(act_num: int, scene_num: int, output_dir: str, is_summary: bool = False) -> str:
    """
    Constructs a full file path for a scene or summary file.
    
    Args:
        act_num: Act number
        scene_num: Scene number
        output_dir: Output directory path
        is_summary: Whether this is a scene summary path
        
    Returns:
        The constructed file path
    """
    filename = get_scene_filename(act_num, scene_num, is_summary)
    return os.path.join(output_dir, filename)

def save_content_to_file(content: str, act_num: int, scene_num: int, output_dir: str, is_summary: bool = False) -> str:
    """
    Saves content to a file and returns the file path.
    
    Args:
        content: The text content to save
        act_num: Act number
        scene_num: Scene number
        output_dir: Directory path to save the file (must already exist)
        is_summary: Whether this is a scene summary
    
    Returns:
        The path to the saved file
    """
    file_path = get_scene_path(act_num, scene_num, output_dir, is_summary)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return file_path


def load_summaries(summaries_dir: str) -> Dict[str, Document]:
    """
    Load all scene summaries from a directory into a dictionary.
    
    Args:
        summaries_dir: Directory containing summary files
        
    Returns:
        Dictionary mapping scene keys (act_scene) to Document objects containing summaries
    """
    summaries = {}
    
    # Check if directory exists
    if not os.path.exists(summaries_dir):
        print(f"Warning: Directory {summaries_dir} does not exist.")
        return summaries
        
    # Get all summary files
    summary_files = [f for f in os.listdir(summaries_dir) if f.startswith("summary_")]
    if not summary_files:
        print(f"Warning: No summary files found in {summaries_dir}")
        return summaries
        
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
                    
                    # Create key for the dictionary
                    key = f"{act}_{scene}"
                    
                    # Add to summaries with metadata
                    summaries[key] = Document(
                        page_content=content,
                        metadata={"file": filename, "act": act, "scene": scene}
                    )
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
    
    print(f"Loaded {len(summaries)} summaries from {summaries_dir}")
    return summaries
