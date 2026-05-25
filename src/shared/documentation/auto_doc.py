import json
import os
from src.shared.llm_router import LLMCascadeRouter

class SemanticModelDocumenter:
    """
    Provides automated documentation and semantic mapping for the AI assistant.
    Integrates with LLM Cascade to help users understand data and create analysis.
    """

    _cache = {}

    def __init__(self, mapping_path="src/shared/models/semantic_map.json"):
        self.mapping_path = mapping_path
        self.mapping = self._load_mapping()
        self.ai = LLMCascadeRouter()

    def _load_mapping(self):
        if self.mapping_path not in self.__class__._cache:
            if os.path.exists(self.mapping_path):
                with open(self.mapping_path, "r") as f:
                    self.__class__._cache[self.mapping_path] = json.load(f)
            else:
                self.__class__._cache[self.mapping_path] = {}

        return self.__class__._cache[self.mapping_path]

    def get_column_description(self, col_name):
        return self.mapping.get(col_name, "No description available.")

    def generate_ai_context(self):
        ctx = "Semantic Model Context for Alile CRE Analytics:\n"
        for col, desc in self.mapping.items():
            ctx += f"- {col}: {desc}\n"
        return ctx

    def assist_user(self, query):
        context = self.generate_ai_context()
        prompt = f"Context: {context}\n\nUser Question: {query}\n\nHelp the user understand the data or create analysis based on the semantic model."
        return self.ai.route_request(prompt)
