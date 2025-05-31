#!/usr/bin/env python3
"""
User Acceptance Tests for Workflow Integration.
Tests the system against the user stories defined in the README.
"""
import unittest
import os
import sys

# Add project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from compression.huffman import HuffmanEncoder, HuffmanDecoder
from storage.red_black_tree import FileIndexManager
from storage.btree import FileIndexBTree
from tests.test_config import generate_test_text_file, TEST_DATA_DIR


class WorkflowIntegrationTests(unittest.TestCase):
    """
    Tests for User Stories 30-31: Workflow Integration
    30. Compress and Index
    31. Search and Decompress
    """
    
    def setUp(self):
        """Set up test environment"""
        self.test_file = generate_test_text_file("small")
        self.rbtree_manager = FileIndexManager()
        self.btree_manager = FileIndexBTree(min_degree=3)
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
    
    def test_story30_compress_and_index_rbtree(self):
        """
        User Story 30: Compress and Index (Red-Black Tree)
        As a user, I want to compress a file and immediately add it to the index in one operation.
        """
        # Read original content for later verification
        with open(self.test_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 1. Compress the file
        self.compressed_file = self.encoder.compress_file(self.test_file)
        
        # 2. Add compressed file to the index using RB-Tree
        compressed_filename = os.path.basename(self.compressed_file)
        self.rbtree_manager.add_file(
            compressed_filename,
            self.compressed_file,
            os.path.getsize(self.compressed_file),
            compression_status=True
        )
        
        # Verify file was added to index
        indexed_file = self.rbtree_manager.search_file(compressed_filename)
        self.assertIsNotNone(indexed_file)
        self.assertTrue(indexed_file["compression_status"])
        
        # Also verify the compressed file is valid by decompressing it
        self.decompressed_file = self.decoder.decompress_file(self.compressed_file)
        with open(self.decompressed_file, 'r', encoding='utf-8') as f:
            decompressed_content = f.read()
        
        self.assertEqual(decompressed_content, original_content)
    
    def test_story30_compress_and_index_btree(self):
        """
        User Story 30: Compress and Index (B-Tree)
        As a user, I want to compress a file and immediately add it to the index in one operation.
        """
        # Read original content for later verification
        with open(self.test_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 1. Compress the file
        self.compressed_file = self.encoder.compress_file(self.test_file)
        
        # 2. Add compressed file to the index using B-Tree
        compressed_filename = os.path.basename(self.compressed_file)
        self.btree_manager.add_file(
            compressed_filename,
            self.compressed_file,
            os.path.getsize(self.compressed_file),
            compression_status=True
        )
        
        # Verify file was added to index
        indexed_file = self.btree_manager.search_file(compressed_filename)
        self.assertIsNotNone(indexed_file)
        self.assertTrue(indexed_file["metadata"]["compression_status"])
        
        # Also verify the compressed file is valid by decompressing it
        self.decompressed_file = self.decoder.decompress_file(self.compressed_file)
        with open(self.decompressed_file, 'r', encoding='utf-8') as f:
            decompressed_content = f.read()
        
        self.assertEqual(decompressed_content, original_content)
    
    def test_story31_search_and_decompress_rbtree(self):
        """
        User Story 31: Search and Decompress (Red-Black Tree)
        As a user, I want to search for a file and decompress it in one operation.
        """
        # First compress and index a file
        self.compressed_file = self.encoder.compress_file(self.test_file)
        compressed_filename = os.path.basename(self.compressed_file)
        
        self.rbtree_manager.add_file(
            compressed_filename,
            self.compressed_file,
            os.path.getsize(self.compressed_file),
            compression_status=True
        )
        
        # Read original content for verification
        with open(self.test_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 1. Search for the file
        indexed_file = self.rbtree_manager.search_file(compressed_filename)
        self.assertIsNotNone(indexed_file)
        
        # 2. Decompress the file
        self.decompressed_file = self.decoder.decompress_file(indexed_file["filepath"])
        
        # Verify file was correctly decompressed
        with open(self.decompressed_file, 'r', encoding='utf-8') as f:
            decompressed_content = f.read()
        
        self.assertEqual(decompressed_content, original_content)
    
    def test_story31_search_and_decompress_btree(self):
        """
        User Story 31: Search and Decompress (B-Tree)
        As a user, I want to search for a file and decompress it in one operation.
        """
        # First compress and index a file
        self.compressed_file = self.encoder.compress_file(self.test_file)
        compressed_filename = os.path.basename(self.compressed_file)
        
        self.btree_manager.add_file(
            compressed_filename,
            self.compressed_file,
            os.path.getsize(self.compressed_file),
            compression_status=True
        )
        
        # Read original content for verification
        with open(self.test_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 1. Search for the file
        indexed_file = self.btree_manager.search_file(compressed_filename)
        self.assertIsNotNone(indexed_file)
        
        # 2. Decompress the file
        self.decompressed_file = self.decoder.decompress_file(indexed_file["metadata"]["path"])
        
        # Verify file was correctly decompressed
        with open(self.decompressed_file, 'r', encoding='utf-8') as f:
            decompressed_content = f.read()
        
        self.assertEqual(decompressed_content, original_content)


if __name__ == '__main__':
    unittest.main()