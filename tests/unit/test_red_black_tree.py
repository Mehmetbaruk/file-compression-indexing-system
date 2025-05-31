"""
Unit Tests for Red-Black Tree Implementation
"""
import unittest
import os
import sys
import random
import tempfile
from pathlib import Path

# Add project root to the path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from storage.red_black_tree import RedBlackTree, Node, FileIndexManager, RED, BLACK

# Create our own generate_test_text_file function since import is causing issues
def generate_test_text_file(size_category="tiny"):
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

class TestRedBlackTreeNode(unittest.TestCase):
    """Test cases for the Red-Black Tree Node class"""
    
    def test_node_creation(self):
        """Test creating nodes with correct properties"""
        node = Node("test_key")
        self.assertEqual(node.filename, "test_key")  # Updated to use filename instead of key
        self.assertIsNone(node.parent)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertEqual(node.color, RED)  # Compare to RED constant
        
    def test_node_with_data(self):
        """Test creating nodes with associated data"""
        data = {"filepath": "/path/to/file", "size": 1024}
        node = Node("test_key", data)
        self.assertEqual(node.metadata, data)  # Updated to use metadata

class TestRedBlackTree(unittest.TestCase):
    """Test cases for the Red-Black Tree implementation"""
    
    def setUp(self):
        """Set up a new tree for each test"""
        self.tree = RedBlackTree()
    
    def test_empty_tree(self):
        """Test properties of an empty tree"""
        self.assertEqual(self.tree.root, self.tree.NIL)  # Root should be NIL node
        self.assertEqual(len(self.tree), 0)
        
    def test_insert_single_node(self):
        """Test inserting a single node"""
        # Insert with filename and filepath
        self.tree.insert("test_key", "/path/to/file")
        self.assertNotEqual(self.tree.root, self.tree.NIL)
        self.assertEqual(self.tree.root.filename, "test_key")  # Use filename
        self.assertEqual(len(self.tree), 1)
        self.assertEqual(self.tree.root.color, BLACK)  # Root should be black
        
    def test_insert_multiple_nodes(self):
        """Test inserting multiple nodes maintains RB tree properties"""
        keys = ["apple", "banana", "cherry", "date", "elderberry"]
        for i, key in enumerate(keys):
            self.tree.insert(key, f"/path/to/{key}")  # Use proper insert signature
            
        # Check tree size
        self.assertEqual(len(self.tree), len(keys))
        
        # Verify all keys are in the tree
        for key in keys:
            self.assertIsNotNone(self.tree.search(key))
            
    def test_search(self):
        """Test searching for nodes"""
        # Insert some data with proper method signature
        self.tree.insert("apple", "/path/to/apple", 100)
        self.tree.insert("banana", "/path/to/banana", 200)
        self.tree.insert("carrot", "/path/to/carrot", 300)
        
        # Find existing nodes
        apple_node = self.tree.search("apple")
        self.assertIsNotNone(apple_node)
        self.assertEqual(apple_node.metadata['path'], "/path/to/apple")
        
        # Search for non-existent node
        self.assertIsNone(self.tree.search("dragonfruit"))
        
    def test_delete(self):
        """Test deleting nodes"""
        # Insert nodes
        keys = ["apple", "banana", "cherry", "date", "elderberry"]
        for key in keys:
            self.tree.insert(key)
            
        # Delete a node
        self.tree.delete("cherry")
        
        # Verify deletion
        self.assertEqual(len(self.tree), len(keys) - 1)
        self.assertIsNone(self.tree.search("cherry"))
        
        # Verify other nodes still exist
        self.assertIsNotNone(self.tree.search("apple"))
        self.assertIsNotNone(self.tree.search("banana"))
        
    def test_tree_properties(self):
        """Test that Red-Black tree properties are maintained"""
        # Insert many random nodes to test tree balancing
        random.seed(42)  # For reproducibility
        keys = [str(random.randint(1, 1000)) for _ in range(100)]
        
        # Remove duplicates
        keys = list(set(keys))
        
        for key in keys:
            self.tree.insert(key)
            
        # Property 1: Root is black
        self.assertEqual(self.tree.root.color, BLACK)
        
        # Check tree height (should be roughly 2*log2(n) for a balanced tree)
        height = self.get_tree_height(self.tree.root)
        max_height = 2 * (len(keys)).bit_length()  # 2 * log2(n) approximation
        self.assertLessEqual(height, max_height)
    
    def get_tree_height(self, node):
        """Helper method to get tree height"""
        if node == self.tree.NIL:  # Check against NIL node
            return 0
        return 1 + max(self.get_tree_height(node.left), self.get_tree_height(node.right))
        
class TestFileIndexManager(unittest.TestCase):
    """Test cases for the FileIndexManager class"""
    
    def setUp(self):
        """Set up a new FileIndexManager for each test"""
        self.manager = FileIndexManager()
        self.test_files = []
        
        # Create some test files
        for i in range(5):
            test_file = generate_test_text_file("tiny")
            self.test_files.append(test_file)
    
    def tearDown(self):
        """Clean up test files"""
        for file in self.test_files:
            if os.path.exists(file):
                os.remove(file)
    
    def test_add_file(self):
        """Test adding files to the index"""
        # Add files with different metadata
        for i, file_path in enumerate(self.test_files):
            file_name = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            self.manager.add_file(file_name, file_path, size, i % 2 == 0)
            
        # Check that files were added
        self.assertEqual(len(self.manager.tree), len(self.test_files))
        
    def test_search_file(self):
        """Test searching for files in the index"""
        # Add files
        for file_path in self.test_files:
            file_name = os.path.basename(file_path)
            self.manager.add_file(file_name, file_path)
            
        # Search for a file that should exist
        test_name = os.path.basename(self.test_files[0])
        found = self.manager.search_file(test_name)
        self.assertIsNotNone(found)
        self.assertEqual(found["filepath"], self.test_files[0])
        
    def test_remove_file(self):
        """Test removing files from the index"""
        # Add files
        for file_path in self.test_files:
            file_name = os.path.basename(file_path)
            self.manager.add_file(file_name, file_path)
            
        # Remove one file
        remove_name = os.path.basename(self.test_files[0])
        self.manager.remove_file(remove_name)
        
        # Check that it was removed
        self.assertIsNone(self.manager.search_file(remove_name))
        self.assertEqual(len(self.manager.tree), len(self.test_files) - 1)
        
    def test_update_file_metadata(self):
        """Test updating file metadata"""
        # Add a file
        file_path = self.test_files[0]
        file_name = os.path.basename(file_path)
        self.manager.add_file(file_name, file_path, 1000, False)
        
        # Update metadata
        new_metadata = {
            "size": 2000,
            "compression_status": True,
            "modified_date": "2025-05-11"
        }
        self.manager.update_file_metadata(file_name, new_metadata)
        
        # Check that metadata was updated
        found = self.manager.search_file(file_name)
        self.assertEqual(found["size"], 2000)
        self.assertTrue(found["compression_status"])
        self.assertEqual(found["modified_date"], "2025-05-11")
        
    def test_search_partial_name(self):
        """Test searching for files by partial name"""
        # Add files with specific names
        test_names = ["project_report.txt", "project_data.csv", "notes.txt", "project_plan.doc"]
        
        for i, name in enumerate(test_names):
            self.manager.add_file(name, f"/path/to/{name}")
            
        # Search by partial name
        results = self.manager.search_files_by_partial_name("project")
        self.assertEqual(len(results), 3)  # Should find 3 files with "project" in name

if __name__ == '__main__':
    unittest.main()