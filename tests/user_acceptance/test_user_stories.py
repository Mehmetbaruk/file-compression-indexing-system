import unittest
import os
import sys

# Add project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from compression.huffman import HuffmanEncoder, HuffmanDecoder
from storage.red_black_tree import FileIndexManager
from tests.test_config import generate_test_text_file, TEST_DATA_DIR

class SimpleUserAcceptanceTest(unittest.TestCase):
    def test_basic_compression(self):
        """Test that compression works as expected for a user"""
        encoder = HuffmanEncoder()
        test_file = generate_test_text_file("small")
        compressed = encoder.compress_file(test_file)
        self.assertTrue(os.path.exists(compressed))
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(compressed):
            os.remove(compressed)

if __name__ == "__main__":
    unittest.main()
