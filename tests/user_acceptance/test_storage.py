#!/usr/bin/env python3
"""
User Acceptance Tests for Storage Functionality.
Tests the system against the user stories defined in the README.
"""
import unittest
import os
import sys

# Add project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from storage.red_black_tree import FileIndexManager
from storage.btree import FileIndexBTree
from tests.test_config import generate_test_text_file, TEST_DATA_DIR


class StorageUserStoryTests(unittest.TestCase):
    """
    Tests for User Stories 6-10: Basic Storage Operations
    6. Add File to Index
    7. File Search
    8. Index Listing
    9. File Deletion
    10. File Update
    """
    
    def setUp(self):
        """Set up test environment"""
        self.rbtree_manager = FileIndexManager()
        self.btree_manager = FileIndexBTree(min_degree=3)
        self.test_files = []
        
        # Create test files
        for i in range(3):
            test_file = generate_test_text_file("tiny")
            self.test_files.append(test_file)
    
    def tearDown(self):
        """Clean up test environment"""
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_story6_add_file_to_rbtree_index(self):
        """User Story 6: Add File to Index (Red-Black Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            result = self.rbtree_manager.add_file(
                filename, 
                file_path, 
                os.path.getsize(file_path)
            )
            self.assertTrue(result)
        
        # Verify files were added
        self.assertEqual(len(self.rbtree_manager.tree), len(self.test_files))
    
    def test_story6_add_file_to_btree_index(self):
        """User Story 6: Add File to Index (B-Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            result = self.btree_manager.add_file(
                filename, 
                file_path, 
                os.path.getsize(file_path)
            )
            self.assertTrue(result)
        
        # Verify files can be found in the B-Tree
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            result = self.btree_manager.search_file(filename)
            self.assertIsNotNone(result)
    
    def test_story7_file_search_rbtree(self):
        """User Story 7: File Search (Red-Black Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            self.rbtree_manager.add_file(
                filename,
                file_path,
                os.path.getsize(file_path)
            )
        
        # Search for a specific file
        target_filename = os.path.basename(self.test_files[0])
        result = self.rbtree_manager.search_file(target_filename)
        
        # Verify search result
        self.assertIsNotNone(result)
        self.assertEqual(result["filepath"], self.test_files[0])
    
    def test_story7_file_search_btree(self):
        """User Story 7: File Search (B-Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            self.btree_manager.add_file(
                filename,
                file_path,
                os.path.getsize(file_path)
            )
        
        # Search for a specific file
        target_filename = os.path.basename(self.test_files[0])
        result = self.btree_manager.search_file(target_filename)
        
        # Verify search result
        self.assertIsNotNone(result)
        self.assertEqual(result["metadata"]["path"], self.test_files[0])
    
    def test_story8_index_listing_rbtree(self):
        """User Story 8: Index Listing (Red-Black Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            self.rbtree_manager.add_file(
                filename,
                file_path,
                os.path.getsize(file_path)
            )
        
        # List all files
        all_files = self.rbtree_manager.list_all_files()
        
        # Verify all files are listed
        self.assertEqual(len(all_files), len(self.test_files))
        
        # Check that each file in the test set is found in the listing
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            found = False
            for indexed_file in all_files:
                if indexed_file["filename"] == filename:
                    found = True
                    break
            self.assertTrue(found, f"File {filename} not found in index listing")
    
    def test_story8_index_listing_btree(self):
        """User Story 8: Index Listing (B-Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            self.btree_manager.add_file(
                filename,
                file_path,
                os.path.getsize(file_path)
            )
        
        # List all files
        all_files = self.btree_manager.list_all_files()
        
        # Verify all files are listed
        self.assertEqual(len(all_files), len(self.test_files))
        
        # Check that each file in the test set is found in the listing
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            found = False
            for indexed_file in all_files:
                if indexed_file["filename"] == filename:
                    found = True
                    break
            self.assertTrue(found, f"File {filename} not found in index listing")
    
    def test_story9_file_deletion_rbtree(self):
        """User Story 9: File Deletion (Red-Black Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            self.rbtree_manager.add_file(
                filename,
                file_path,
                os.path.getsize(file_path)
            )
        
        # Delete a specific file
        target_filename = os.path.basename(self.test_files[0])
        result = self.rbtree_manager.remove_file(target_filename)
        
        # Verify file was removed
        self.assertTrue(result)
        self.assertIsNone(self.rbtree_manager.search_file(target_filename))
        self.assertEqual(len(self.rbtree_manager.tree), len(self.test_files) - 1)
    
    def test_story9_file_deletion_btree(self):
        """User Story 9: File Deletion (B-Tree)"""
        # Add files to the index
        for file_path in self.test_files:
            filename = os.path.basename(file_path)
            self.btree_manager.add_file(
                filename,
                file_path,
                os.path.getsize(file_path)
            )
        
        # Delete a specific file
        target_filename = os.path.basename(self.test_files[0])
        result = self.btree_manager.remove_file(target_filename)
        
        # Verify file was removed
        self.assertTrue(result)
        self.assertIsNone(self.btree_manager.search_file(target_filename))
    
    def test_story10_file_update_rbtree(self):
        """User Story 10: File Update (Red-Black Tree)"""
        # Add a file to the index
        file_path = self.test_files[0]
        filename = os.path.basename(file_path)
        self.rbtree_manager.add_file(
            filename,
            file_path,
            os.path.getsize(file_path)
        )
        
        # Update the file metadata
        new_metadata = {
            "size": 9876,
            "last_modified": "2025-05-11",
            "tags": ["important", "document"]
        }
        result = self.rbtree_manager.update_file_metadata(filename, new_metadata)
        
        # Verify update was successful
        self.assertTrue(result)
        updated_file = self.rbtree_manager.search_file(filename)
        self.assertEqual(updated_file["size"], 9876)
        self.assertEqual(updated_file["last_modified"], "2025-05-11")
        self.assertEqual(updated_file["tags"], ["important", "document"])
    
    def test_story10_file_update_btree(self):
        """User Story 10: File Update (B-Tree)"""
        # Add a file to the index
        file_path = self.test_files[0]
        filename = os.path.basename(file_path)
        self.btree_manager.add_file(
            filename,
            file_path,
            os.path.getsize(file_path)
        )
        
        # Update the file metadata
        new_metadata = {
            "size": 9876,
            "last_modified": "2025-05-11",
            "categories": ["important", "document"]
        }
        result = self.btree_manager.update_file_metadata(filename, new_metadata)
        
        # Verify update was successful
        self.assertTrue(result)
        updated_file = self.btree_manager.search_file(filename)
        self.assertEqual(updated_file["metadata"]["size"], 9876)
        self.assertEqual(updated_file["metadata"]["last_modified"], "2025-05-11")
        self.assertEqual(updated_file["metadata"]["categories"], ["important", "document"])


if __name__ == '__main__':
    unittest.main()