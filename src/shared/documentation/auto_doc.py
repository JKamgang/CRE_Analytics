class SemanticModelDocumenter:
    """
    Self-Documenting feature where any change to the Semantic Model automatically
    updates the user-facing 'Learning Hub'.
    """

    def generate_hub_docs(self, schema_changes: dict) -> str:
        docs = "# Alile CRE Analytics - Learning Hub\n\n"
        docs += "This documentation is auto-generated based on the current semantic model.\n\n"

        for field, description in schema_changes.items():
            docs += f"## {field}\n"
            docs += f"**Description**: {description}\n\n"

        # In a real app, this would use a local LLM or Jules to rewrite/explain
        # the changes to students.
        docs += "## Auto-Generated AI Insight\n"
        docs += "The changes above reflect the transmission vector of capital across metro regions.\n\n"

        docs += "## Understanding the Data & Transformation\n"
        docs += "**Z-Score Normalization**: Because a $500M project in DC is different than a $5M permit in Atlanta, we compute a `Z-Score` to standardize 'Growth Pressure'. It compares the size of a project relative to its own regional average rather than absolute value.\n\n"

        docs += "## Guide to Local Open-Source LLMs (Llama 3 / Gemma 4)\n"
        docs += "Use offline tools like LM Studio to connect this solution to your local LLM.\n"
        docs += "### Example Prompts for Power BI DAX\n"
        docs += "- *\"Given a column 'growth_pressure', write a DAX measure to calculate a 5-year rolling average.\"* \n"
        docs += "- *\"I have 'EntryDate'. Help me write a DAX string for Year-Over-Year 'flood' calculation.\"* \n"
        docs += "### Example Prompts for Excel VBA / Macros\n"
        docs += "- *\"Write an Excel VBA macro that automatically generates a Pivot Table mapping 'City' to 'Growth Pressure'.\"*\n"

        return docs
