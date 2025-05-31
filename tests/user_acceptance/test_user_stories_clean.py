#!/usr/bin/env python3
"""
User Acceptance Tests for Basic User Stories.
Tests the system against the user stories defined in the README.
"""
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
        """Test that basic compression works"""
        test_file = generate_test_text_file("small")
        encoder = HuffmanEncoder()
        
        # Test compression
        result = encoder.compress_file(test_file)
        self.assertTrue(result)
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == '__main__':
    unittest.main()
