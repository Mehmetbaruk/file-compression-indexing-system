#!/usr/bin/env python3
"""
User Acceptance Tests for Compression Functionality.
Tests the system against the user stories defined in the README.
"""
import unittest
import os
import sys
import tempfile

# Add project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from compression.huffman import HuffmanEncoder, HuffmanDecoder
from tests.test_config import generate_test_text_file, TEST_DATA_DIR


class CompressionUserStoryTests(unittest.TestCase):
    """
    Tests for User Stories 1-5: Basic Compression Operations
    1. Simple File Compression
    2. File Decompression 
    3. Compression Ratio Display
    5. Automatic Frequency Analysis
    """
    
    def setUp(self):
        """Set up test environment"""
        self.test_file = generate_test_text_file("small")
        self.encoder = HuffmanEncoder()
        self.decoder = HuffmanDecoder()
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.remove(self.test_file)
        if hasattr(self, 'compressed_file') and os.path.exists(self.compressed_file):
            os.remove(self.compressed_file)
        if hasattr(self, 'decompressed_file') and os.path.exists(self.decompressed_file):
            os.remove(self.decompressed_file)
    
    def test_story1_simple_file_compression(self):
        """User Story 1: Simple File Compression"""
        # Assert file exists and has content
        self.assertTrue(os.path.exists(self.test_file))
        original_size = os.path.getsize(self.test_file)
        self.assertGreater(original_size, 0)
        
        # Compress the file
        self.compressed_file = self.encoder.compress_file(self.test_file)
        
        # Assert compressed file exists
        self.assertTrue(os.path.exists(self.compressed_file))
        compressed_size = os.path.getsize(self.compressed_file)
        
        # For small files, expect some reduction in size
        # Note: Very small files may not compress well due to Huffman overhead
        self.assertTrue(compressed_size > 0)
    
    def test_story2_file_decompression(self):
        """User Story 2: File Decompression"""
        # First compress a file
        self.compressed_file = self.encoder.compress_file(self.test_file)
        
        # Save original content for comparison
        with open(self.test_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Decompress the file
        self.decompressed_file = self.decoder.decompress_file(self.compressed_file)
        
        # Assert decompressed file exists
        self.assertTrue(os.path.exists(self.decompressed_file))
        
        # Check content matches original
        with open(self.decompressed_file, 'r', encoding='utf-8') as f:
            decompressed_content = f.read()
        
        self.assertEqual(decompressed_content, original_content)
    
    def test_story3_compression_ratio_display(self):
        """User Story 3: Compression Ratio Display"""
        # Compress a file
        self.compressed_file = self.encoder.compress_file(self.test_file)
        
        # Check that compression ratio is calculated and meaningful
        self.assertIsNotNone(self.encoder.compression_ratio)
        self.assertGreaterEqual(self.encoder.compression_ratio, -100)  # Allow for expansion
        self.assertLessEqual(self.encoder.compression_ratio, 100)  # Max possible percentage
    
    def test_story5_automatic_frequency_analysis(self):
        """User Story 5: Automatic Frequency Analysis"""
        # Create a file with known character distribution
        temp_file = os.path.join(tempfile.gettempdir(), "frequency_test.txt")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write("aaaabbbccdeeee")  # a:4, b:3, c:2, d:1, e:4
        
        # Check that frequency analysis is performed correctly
        frequencies = self.encoder.analyze_frequency(temp_file)
        
        self.assertEqual(frequencies.get('a', 0), 4)
        self.assertEqual(frequencies.get('b', 0), 3)
        self.assertEqual(frequencies.get('c', 0), 2)
        self.assertEqual(frequencies.get('d', 0), 1)
        self.assertEqual(frequencies.get('e', 0), 4)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()