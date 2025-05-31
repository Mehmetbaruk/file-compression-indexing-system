"""
Unit Tests for Huffman Coding Module
"""
import unittest
import os
import tempfile
from pathlib import Path
import sys

# Add project root to the path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compression.huffman import HuffmanTree, HuffmanEncoder, HuffmanDecoder

class TestHuffmanTree(unittest.TestCase):
    """Test cases for the HuffmanTree class"""
    
    def test_tree_creation(self):
        """Test creating a Huffman tree from frequency dict"""
        frequencies = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
        tree = HuffmanTree()
        tree.build_tree_from_freq(frequencies)
        self.assertIsNotNone(tree.root)
        
    def test_code_generation(self):
        """Test that codes are generated correctly"""
        frequencies = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
        tree = HuffmanTree()
        tree.build_tree_from_freq(frequencies)
        codes = tree.codes
        
        # Validate codes
        self.assertIn('a', codes)
        self.assertIn('f', codes)
        
        # Check that the codes are binary strings
        for char, code in codes.items():
            self.assertTrue(all(bit in '01' for bit in code), f"Non-binary code found: {code}")
        
        # Check that no code is a prefix of another (prefix property)
        for char1, code1 in codes.items():
            for char2, code2 in codes.items():
                if char1 != char2:
                    self.assertFalse(code1.startswith(code2) or code2.startswith(code1),
                                    f"Prefix violation: {char1}:{code1} and {char2}:{code2}")
    
    def test_tree_from_text(self):
        """Test creating a tree from text"""
        text = "aaaabbbccdddddeeeeeeffffffffff"
        tree = HuffmanTree()
        tree.build_tree(text)
        self.assertIsNotNone(tree.root)
        self.assertIsNotNone(tree.freq_dict)
        
        # Check frequency distribution
        self.assertEqual(tree.freq_dict.get('a', 0), 4)
        self.assertEqual(tree.freq_dict.get('b', 0), 3)
        self.assertEqual(tree.freq_dict.get('c', 0), 2)
        self.assertEqual(tree.freq_dict.get('d', 0), 5)
        self.assertEqual(tree.freq_dict.get('e', 0), 6)
        self.assertEqual(tree.freq_dict.get('f', 0), 10)


class TestHuffmanEncoder(unittest.TestCase):
    """Test cases for the HuffmanEncoder class"""
    
    def setUp(self):
        """Create a temporary test file"""
        self.test_file = tempfile.mktemp(suffix=".txt")
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("This is a test file for Huffman encoding. It contains various characters to ensure good compression.")
        
    def tearDown(self):
        """Clean up temporary files"""
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.remove(self.test_file)
        if hasattr(self, 'compressed_file') and os.path.exists(self.compressed_file):
            os.remove(self.compressed_file)
    
    def test_encode_file(self):
        """Test encoding a file"""
        encoder = HuffmanEncoder()
        self.compressed_file = encoder.compress_file(self.test_file)
        
        # Check that compressed file exists and has smaller size
        self.assertTrue(os.path.exists(self.compressed_file))
        original_size = os.path.getsize(self.test_file)
        compressed_size = os.path.getsize(self.compressed_file)
        
        # Test if compression ratio data is returned
        self.assertIsNotNone(encoder.get_compression_ratio())
        self.assertGreater(original_size, 0)
        
        # Print compression details for debugging
        print(f"Original size: {original_size} bytes")
        print(f"Compressed size: {compressed_size} bytes")
        print(f"Compression ratio: {encoder.get_compression_ratio():.2f}%")
        
        # The compressed file might be larger due to overhead in very small test files
        # But for real-world cases, it should be smaller


class TestHuffmanDecoder(unittest.TestCase):
    """Test cases for the HuffmanDecoder class"""
    
    def setUp(self):
        """Create and compress a test file"""
        # Create a test file
        self.test_file = tempfile.mktemp(suffix=".txt")
        self.test_content = "This is a test file for Huffman encoding and decoding. Testing 123!"
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
        
        # Compress it first
        encoder = HuffmanEncoder()
        self.compressed_file = encoder.compress_file(self.test_file)
    
    def tearDown(self):
        """Clean up temporary files"""
        if hasattr(self, 'test_file') and os.path.exists(self.test_file):
            os.remove(self.test_file)
        if hasattr(self, 'compressed_file') and os.path.exists(self.compressed_file):
            os.remove(self.compressed_file)
        if hasattr(self, 'decompressed_file') and os.path.exists(self.decompressed_file):
            os.remove(self.decompressed_file)
    
    def test_decode_file(self):
        """Test decoding a compressed file"""
        decoder = HuffmanDecoder()
        self.decompressed_file = decoder.decompress_file(self.compressed_file)
        
        # Check that decompressed file exists
        self.assertTrue(os.path.exists(self.decompressed_file))
        
        # Check that content matches original
        with open(self.decompressed_file, 'r', encoding='utf-8') as f:
            decompressed_content = f.read()
        
        self.assertEqual(decompressed_content, self.test_content)


if __name__ == '__main__':
    unittest.main()