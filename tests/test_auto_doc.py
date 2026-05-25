import unittest
import os
import json
import sys
import unittest.mock

sys.modules['google'] = unittest.mock.MagicMock()
sys.modules['google.generativeai'] = unittest.mock.MagicMock()
sys.modules['google.genai'] = unittest.mock.MagicMock()
sys.modules['dotenv'] = unittest.mock.MagicMock()
sys.modules['streamlit'] = unittest.mock.MagicMock()

from src.shared.documentation.auto_doc import SemanticModelDocumenter

class TestSemanticModelDocumenter(unittest.TestCase):
    def setUp(self):
        self.mapping_path = "test_semantic_map.json"
        with open(self.mapping_path, "w") as f:
            json.dump({"col1": "desc1"}, f)

    def tearDown(self):
        if os.path.exists(self.mapping_path):
            os.remove(self.mapping_path)

    def test_load_mapping_and_cache(self):
        doc1 = SemanticModelDocumenter(mapping_path=self.mapping_path)
        self.assertEqual(doc1.get_column_description("col1"), "desc1")

        # Modify the file, but cache should prevent loading new values for the same path
        with open(self.mapping_path, "w") as f:
            json.dump({"col1": "new_desc"}, f)

        doc2 = SemanticModelDocumenter(mapping_path=self.mapping_path)
        self.assertEqual(doc2.get_column_description("col1"), "desc1")

        # Clear cache to see the new value
        SemanticModelDocumenter._load_mapping.cache_clear()
        doc3 = SemanticModelDocumenter(mapping_path=self.mapping_path)
        self.assertEqual(doc3.get_column_description("col1"), "new_desc")

if __name__ == '__main__':
    unittest.main()
