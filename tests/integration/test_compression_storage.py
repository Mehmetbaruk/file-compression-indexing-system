"""
Integration Tests for Compression and Storage Integration
Tests the interaction between compression and storage modules
"""
import unittest
import os
import sys
import tempfile
from pathlib import Path

# Add project root to the path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compression.huffman import HuffmanEncoder, HuffmanDecoder
from storage.red_black_tree import FileIndexManager
from storage.btree import BTree

# Create our own test file generator since import is causing issues
def generate_test_text_file(size_category="small"):
    """Generate a test text file for testing purposes"""
    # Create a temporary text file
    fd, temp_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    
    # Write some content
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(f"This is a test file for {size_category} size testing.\n")
        f.write("It contains some text to analyze and process.\n")
        
        # Add more content based on size
        if size_category == "small":
            f.write("Adding more text to increase the file size.\n" * 10)
        elif size_category == "medium":
            f.write("Adding more text to increase the file size.\n" * 100)
            
    return temp_path

class TestCompressionStorageIntegration(unittest.TestCase):
    """Test cases for integration between compression and storage modules"""
    
    def setUp(self):
        """Set up test environment"""
        # Create file index manager
        self.file_manager = FileIndexManager()
        
        # Create compression components
        self.encoder = HuffmanEncoder()
        self.decoder = HuffmanDecoder()
        
        # Generate test files
        self.test_files = [generate_test_text_file() for _ in range(3)]
        
        # To store compressed files
        self.compressed_files = []
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Remove compressed files
        for file_path in self.compressed_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                
        # Remove any decompressed files
        for file_path in self.test_files:
            decompressed_path = file_path + "_decompressed.txt"
            if os.path.exists(decompressed_path):
                os.remove(decompressed_path)
    
    def test_compress_and_index(self):
        """Test compressing files and adding them to the index"""
        for file_path in self.test_files:
            # Compress file
            compressed_file = self.encoder.compress_file(file_path)
            self.compressed_files.append(compressed_file)
            
            # Add to index
            file_name = os.path.basename(compressed_file)
            file_size = os.path.getsize(compressed_file)
            
            self.file_manager.add_file(
                file_name,
                compressed_file,
                file_size,
                compression_status=True
            )
        
        # Verify all files were added to index
        for compressed_file in self.compressed_files:
            file_name = os.path.basename(compressed_file)
            result = self.file_manager.search_file(file_name)
            
            # Check file was found in index
            self.assertIsNotNone(result)
            self.assertEqual(result["filepath"], compressed_file)
            self.assertTrue(result["compression_status"])
    
    def test_search_and_decompress(self):
        """Test searching for files and decompressing them"""
        # First compress files and add to index
        for file_path in self.test_files:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            # Compress file
            compressed_file = self.encoder.compress_file(file_path)
            self.compressed_files.append(compressed_file)
            
            # Add to index with metadata
            file_name = os.path.basename(compressed_file)
            file_size = os.path.getsize(compressed_file)
            
            self.file_manager.add_file(
                file_name,
                compressed_file,
                file_size,
                compression_status=True
            )
            
            # Store original content for verification
            self.file_manager.update_file_metadata(
                file_name, 
                {"original_path": file_path, "original_content": original_content}
            )
        
        # Now search and decompress
        for compressed_file in self.compressed_files:
            file_name = os.path.basename(compressed_file)
            
            # Find in index
            search_result = self.file_manager.search_file(file_name)
            self.assertIsNotNone(search_result)
            
            # Decompress
            decompressed_file = self.decoder.decompress_file(search_result["filepath"])
            
            # Verify content
            with open(decompressed_file, 'r', encoding='utf-8') as f:
                decompressed_content = f.read()
            
            original_content = search_result.get("original_content", "")
            self.assertEqual(decompressed_content, original_content)
    
    def test_compression_metadata(self):
        """Test that compression metadata is properly stored"""
        # Compress a file
        test_file = self.test_files[0]
        original_size = os.path.getsize(test_file)
        
        # Compress file
        compressed_file = self.encoder.compress_file(test_file)
        self.compressed_files.append(compressed_file)
        compressed_size = os.path.getsize(compressed_file)
        compression_ratio = self.encoder.get_compression_ratio()
        
        # Add to index with compression metadata
        file_name = os.path.basename(compressed_file)
        self.file_manager.add_file(
            file_name,
            compressed_file,
            compressed_size,
            compression_status=True
        )
        
        # Update with compression metrics
        self.file_manager.update_file_metadata(
            file_name,
            {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio
            }
        )
        
        # Retrieve and verify metrics
        file_info = self.file_manager.search_file(file_name)
        self.assertEqual(file_info["original_size"], original_size)
        self.assertEqual(file_info["compressed_size"], compressed_size)
        self.assertEqual(file_info["compression_ratio"], compression_ratio)
    
    def test_btree_compression_integration(self):
        """Test integration between B-Tree and compression"""
        # Create a B-Tree with t parameter (minimum degree) instead of order
        btree = BTree(t=5)
        
        # Compress files and add to B-Tree
        for file_path in self.test_files:
            # Compress file
            compressed_file = self.encoder.compress_file(file_path)
            self.compressed_files.append(compressed_file)
            
            # Add to B-Tree
            file_name = os.path.basename(compressed_file)
            btree.insert(file_name, {
                "path": compressed_file,
                "size": os.path.getsize(compressed_file),
                "compression_status": True
            })
        
        # Verify all files are in the B-Tree
        for compressed_file in self.compressed_files:
            file_name = os.path.basename(compressed_file)
            result = btree.search(file_name)
            
            # Check file was found - BTree.search returns a tuple (node, index)
            self.assertIsNotNone(result[0])
            # Get the actual value from the node at the found index
            value = result[0].values[result[1]]
            self.assertEqual(value["path"], compressed_file)
            self.assertTrue(value["compression_status"])

if __name__ == '__main__':
    unittest.main()