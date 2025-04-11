import os

def load_text(file_path):
    """Loads text from a file."""
    with open(file_path, 'r') as f:
        text = f.read()

    return text

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
