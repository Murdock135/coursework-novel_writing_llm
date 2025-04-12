from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Scene(BaseModel):
    """Represents a single scene in an act of the novel."""
    description: str = Field(description="Description of what happens in the scene")


class Act(BaseModel):
    """Represents one act of the three-act structure."""
    scenes: List[Scene] = Field(description="List of scenes in the act")


class NovelOutline(BaseModel):
    """Complete outline of a novel following a three-act structure."""
    acts: List[Act] = Field(description="The three acts of the novel")
    
    def format_readable(self) -> str:
        """Returns a human-readable string representation of the outline."""
        result = []
        for i, act in enumerate(self.acts, 1):
            result.append(f"Act {i}:")
            for j, scene in enumerate(act.scenes, 1):
                result.append(f"  Scene {j}: {scene.description}")
            result.append("")
        return "\n".join(result)


class DiversityAssessment(BaseModel):
    """Result of a scene diversity assessment."""
    is_diverse_enough: bool = Field(description="Whether the scene is diverse enough")
    analysis: str = Field(description="Analysis of the scene's diversity compared to existing scenes")
    guidance: Optional[str] = Field(None, description="Specific guidance for improving diversity if needed")