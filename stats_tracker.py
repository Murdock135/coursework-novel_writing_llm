class StatsTracker:
    """A class to track statistics during the novel writing process."""
    
    def __init__(self):
        self.llm_call_count = 0
        self.scenes_processed = 0
        self.summaries_generated = 0
        self.errors = []
    
    def increment_llm_calls(self, count=1):
        """Increment the LLM call counter."""
        self.llm_call_count += count
        return self.llm_call_count
    
    def add_error(self, error_message):
        """Add an error message to the list of errors."""
        self.errors.append(error_message)
    
    def increment_scenes(self):
        """Increment the scenes processed counter."""
        self.scenes_processed += 1
        return self.scenes_processed
    
    def increment_summaries(self):
        """Increment the summaries generated counter."""
        self.summaries_generated += 1
        return self.summaries_generated
    
    def get_statistics(self):
        """Return a dictionary of all tracked statistics."""
        return {
            "llm_call_count": self.llm_call_count,
            "scenes_processed": self.scenes_processed,
            "summaries_generated": self.summaries_generated,
            "errors": self.errors
        }
    
    def print_statistics(self):
        """Print a summary of the tracked statistics."""
        print(f"\nStatistics:")
        print(f"- Total LLM calls: {self.llm_call_count}")
        print(f"- Scenes processed: {self.scenes_processed}")
        print(f"- Summaries generated: {self.summaries_generated}")
        
        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"- {error}")