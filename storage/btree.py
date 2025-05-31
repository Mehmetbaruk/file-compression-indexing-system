"""
B-Tree implementation for advanced file indexing
"""
import os
from datetime import datetime
from storage import FileMetadata

class BTreeNode:
    """
    Node class for B-Tree
    """
    def __init__(self, leaf=True, t=3):
        """
        Initialize a B-Tree node
        
        Args:
            leaf: Boolean indicating if the node is a leaf node
            t: Minimum degree of the B-Tree (determines the number of keys)
        """
        self.leaf = leaf  # True if node is leaf
        self.t = t  # Minimum degree
        self.keys = []  # List of keys (filenames)
        self.values = []  # List of values (metadata) associated with keys
        self.children = []  # List of children nodes
    
    def is_full(self):
        """Check if the node has the maximum number of keys"""
        return len(self.keys) == 2 * self.t - 1

class BTree:
    """
    B-Tree implementation for efficient file indexing and range queries
    """
    def __init__(self, t=3):
        """
        Initialize an empty B-Tree
        
        Args:
            t: Minimum degree of the B-Tree (must be >= 2)
        """
        self.root = BTreeNode(leaf=True, t=max(2, t))
        self.t = max(2, t)  # Ensure minimum degree is at least 2
    
    def search(self, key):
        """
        Search for a key in the B-Tree
        
        Args:
            key: The key to search for (filename)
        
        Returns:
            Tuple of (node, index) if found, otherwise (None, -1)
        """
        return self._search(self.root, key)
    
    def _search(self, node, key):
        """
        Helper function for search
        
        Args:
            node: The current node to search in
            key: The key to search for
        
        Returns:
            Tuple of (node, index) if found, otherwise (None, -1)
        """
        # Find the first key greater than or equal to the target key
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        # If the key is found at index i
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        
        # If this is a leaf node, the key is not in the tree
        if node.leaf:
            return (None, -1)
        
        # Recursively search the appropriate child
        return self._search(node.children[i], key)
    
    def insert(self, key, value):
        """
        Insert a key-value pair into the B-Tree
        
        Args:
            key: The key to insert (filename)
            value: The value to associate with the key (metadata)
        """
        root = self.root
        
        # If root is full, tree grows in height
        if root.is_full():
            # Create a new root
            new_root = BTreeNode(leaf=False, t=self.t)
            new_root.children.append(root)
            self.root = new_root
            self._split_child(new_root, 0)
        
        self._insert_non_full(self.root, key, value)
    
    def _insert_non_full(self, node, key, value):
        """
        Insert a key-value pair into a non-full node
        
        Args:
            node: The node to insert into (not full)
            key: The key to insert
            value: The value associated with the key
        """
        # Initialize index as the rightmost element
        i = len(node.keys) - 1
        
        # If this is a leaf node, insert the key in the correct position
        if node.leaf:
            # Find the position to insert the key
            while i >= 0 and key < node.keys[i]:
                i -= 1
            
            # Insert the key and value at the correct position
            node.keys.insert(i + 1, key)
            node.values.insert(i + 1, value)
        else:
            # Find the child which is going to have the new key
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # If the child is full, split it
            if node.children[i].is_full():
                self._split_child(node, i)
                
                # After splitting, the middle key from children[i]
                # moves up and children[i] is split into two
                if key > node.keys[i]:
                    i += 1
            
            # Recursively insert the key into the appropriate child
            self._insert_non_full(node.children[i], key, value)
    
    def _split_child(self, parent, index):
        """
        Split a full child node
        
        Args:
            parent: Parent node
            index: Index of the child to split
        """
        # Get the child to split
        child = parent.children[index]
        t = self.t
        
        # Create a new node which will store the keys and children after splitting
        new_node = BTreeNode(leaf=child.leaf, t=t)
        
        # Check if the child has enough keys to split
        if len(child.keys) < t:
            # Child doesn't have enough keys, so we can't split it
            return
            
        # Copy the last (t-1) keys and values from child to new_node
        new_node.keys = child.keys[t:]
        new_node.values = child.values[t:]
        
        # Save the middle key and value before truncating the child
        middle_key = child.keys[t-1]
        middle_value = child.values[t-1]
        
        # Truncate the child's keys and values
        child.keys = child.keys[:t-1]
        child.values = child.values[:t-1]
        
        # If child is not a leaf, copy the last t children as well
        if not child.leaf:
            new_node.children = child.children[t:]
            child.children = child.children[:t]
        
        # Insert the new node as a child of parent
        parent.children.insert(index + 1, new_node)
        
        # Move the middle key and value from child to parent
        parent.keys.insert(index, middle_key)
        parent.values.insert(index, middle_value)
    
    def delete(self, key):
        """
        Delete a key from the B-Tree
        
        Args:
            key: The key to delete
            
        Returns:
            True if the key was deleted, False otherwise
        """
        if not self.root.keys:
            return False  # Empty tree
        
        deleted = self._delete(self.root, key)
        
        # If the root has no keys and has a child, make the child the new root
        if not self.root.keys and not self.root.leaf:
            self.root = self.root.children[0]
        
        return deleted
    
    def _delete(self, node, key):
        """
        Helper function for delete
        
        Args:
            node: The current node
            key: The key to delete
            
        Returns:
            True if the key was deleted, False otherwise
        """
        t = self.t
        
        # Find the position of the key in the node
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        # If the key is found in this node
        if i < len(node.keys) and node.keys[i] == key:
            # If this is a leaf node, simply remove the key and value
            if node.leaf:
                node.keys.pop(i)
                node.values.pop(i)
                return True
            else:
                # If this is an internal node, handle the deletion differently
                return self._delete_internal_node(node, key, i)
        else:
            # Key not found in this node
            
            # If this is a leaf node, key is not in the tree
            if node.leaf:
                return False
            
            # Check if the child where the key might exist has enough keys
            return self._ensure_child_has_enough_keys_and_delete(node, key, i)
    
    def _delete_internal_node(self, node, key, index):
        """
        Delete a key from an internal node
        
        Args:
            node: The node containing the key
            key: The key to delete
            index: The index of the key in the node
            
        Returns:
            True if the key was deleted, False otherwise
        """
        # Case 1: If the child at left has at least t keys
        if len(node.children[index].keys) >= self.t:
            # Find the predecessor
            predecessor, pred_index = self._get_predecessor(node, index)
            
            # Replace the key and value with the predecessor
            node.keys[index] = predecessor.keys[pred_index]
            node.values[index] = predecessor.values[pred_index]
            
            # Recursively delete the predecessor from the left subtree
            return self._delete(node.children[index], node.keys[index])
        
        # Case 2: If the child at right has at least t keys
        elif len(node.children[index+1].keys) >= self.t:
            # Find the successor
            successor, succ_index = self._get_successor(node, index)
            
            # Replace the key and value with the successor
            node.keys[index] = successor.keys[succ_index]
            node.values[index] = successor.values[succ_index]
            
            # Recursively delete the successor from the right subtree
            return self._delete(node.children[index+1], node.keys[index])
        
        # Case 3: Both left and right children have t-1 keys
        else:
            # Merge the key and the right child into the left child
            self._merge_nodes(node, index)
            
            # Recursively delete the key from the merged child
            return self._delete(node.children[index], key)
    
    def _ensure_child_has_enough_keys_and_delete(self, node, key, index):
        """
        Make sure the child at index has enough keys and then delete the key
        
        Args:
            node: The current node
            key: The key to delete
            index: The index of the child to check
            
        Returns:
            True if the key was deleted, False otherwise
        """
        # If the child has only t-1 keys
        if len(node.children[index].keys) == self.t - 1:
            # Try to borrow from the left sibling
            if index > 0 and len(node.children[index-1].keys) >= self.t:
                self._borrow_from_left(node, index)
            
            # Try to borrow from the right sibling
            elif index < len(node.children) - 1 and len(node.children[index+1].keys) >= self.t:
                self._borrow_from_right(node, index)
            
            # If can't borrow, merge with a sibling
            else:
                # If this is the rightmost child, merge with the left sibling
                if index == len(node.children) - 1:
                    self._merge_nodes(node, index - 1)
                    index = index - 1
                else:
                    # Otherwise, merge with the right sibling
                    self._merge_nodes(node, index)
        
        # Recursively delete from the appropriate child
        return self._delete(node.children[index], key)
    
    def _get_predecessor(self, node, index):
        """
        Find the predecessor of the key at index in node
        
        Args:
            node: The current node
            index: The index of the key
            
        Returns:
            Tuple of (node, index) of the predecessor
        """
        current = node.children[index]
        
        # Go to the rightmost node in the left subtree
        while not current.leaf:
            current = current.children[-1]
        
        # Return the rightmost key in this leaf node
        return (current, len(current.keys) - 1)
    
    def _get_successor(self, node, index):
        """
        Find the successor of the key at index in node
        
        Args:
            node: The current node
            index: The index of the key
            
        Returns:
            Tuple of (node, index) of the successor
        """
        current = node.children[index + 1]
        
        # Go to the leftmost node in the right subtree
        while not current.leaf:
            current = current.children[0]
        
        # Return the leftmost key in this leaf node
        return (current, 0)
    
    def _borrow_from_left(self, node, index):
        """
        Borrow a key from the left sibling
        
        Args:
            node: The parent node
            index: The index of the child that needs to borrow
        """
        child = node.children[index]
        left_sibling = node.children[index - 1]
        
        # Move a key from parent to child
        child.keys.insert(0, node.keys[index - 1])
        child.values.insert(0, node.values[index - 1])
        
        # Move a key from left sibling to parent
        node.keys[index - 1] = left_sibling.keys.pop()
        node.values[index - 1] = left_sibling.values.pop()
        
        # If not leaf nodes, move a child pointer from left sibling to child
        if not child.leaf:
            child.children.insert(0, left_sibling.children.pop())
    
    def _borrow_from_right(self, node, index):
        """
        Borrow a key from the right sibling
        
        Args:
            node: The parent node
            index: The index of the child that needs to borrow
        """
        child = node.children[index]
        right_sibling = node.children[index + 1]
        
        # Move a key from parent to child
        child.keys.append(node.keys[index])
        child.values.append(node.values[index])
        
        # Move a key from right sibling to parent
        node.keys[index] = right_sibling.keys.pop(0)
        node.values[index] = right_sibling.values.pop(0)
        
        # If not leaf nodes, move a child pointer from right sibling to child
        if not right_sibling.leaf:
            child.children.append(right_sibling.children.pop(0))
    
    def _merge_nodes(self, node, index):
        """
        Merge the child at index with the child at index+1
        
        Args:
            node: The parent node
            index: The index of the left child to merge
        """
        left_child = node.children[index]
        right_child = node.children[index + 1]
        
        # Move a key from parent to left child
        left_child.keys.append(node.keys[index])
        left_child.values.append(node.values[index])
        
        # Remove the key from parent
        node.keys.pop(index)
        node.values.pop(index)
        
        # Move all keys from right child to left child
        left_child.keys.extend(right_child.keys)
        left_child.values.extend(right_child.values)
        
        # If not leaf nodes, move all children from right child to left child
        if not left_child.leaf:
            left_child.children.extend(right_child.children)
        
        # Remove the right child
        node.children.pop(index + 1)
    
    def range_search(self, start_key, end_key):
        """
        Search for all keys in a given range
        
        Args:
            start_key: The start of the range (inclusive)
            end_key: The end of the range (inclusive)
            
        Returns:
            List of (key, value) pairs in the range
        """
        result = []
        self._range_search(self.root, start_key, end_key, result)
        return result
    
    def _range_search(self, node, start_key, end_key, result):
        """
        Helper function for range search
        
        Args:
            node: The current node
            start_key: The start of the range (inclusive)
            end_key: The end of the range (inclusive)
            result: List to store the results
        """
        # Find the first key that is greater than or equal to start_key
        i = 0
        while i < len(node.keys) and start_key > node.keys[i]:
            i += 1
        
        # Check keys in this node
        while i < len(node.keys) and node.keys[i] <= end_key:
            if not node.leaf:
                # Recursively search the left subtree
                self._range_search(node.children[i], start_key, end_key, result)
            
            # Add the current key-value pair to the result
            result.append((node.keys[i], node.values[i]))
            i += 1
        
        # If not a leaf node, check the last child
        if not node.leaf and i < len(node.children):
            self._range_search(node.children[i], start_key, end_key, result)
    
    def get_all(self):
        """
        Get all key-value pairs in the B-Tree
        
        Returns:
            List of (key, value) pairs
        """
        result = []
        self._inorder_traversal(self.root, result)
        return result
    
    def _inorder_traversal(self, node, result):
        """
        Helper function for inorder traversal
        
        Args:
            node: The current node
            result: List to store the results
        """
        if not node:
            return
        
        for i in range(len(node.keys)):
            # If not a leaf, visit the left child
            if not node.leaf:
                self._inorder_traversal(node.children[i], result)
            
            # Visit the current key
            result.append((node.keys[i], node.values[i]))
        
        # Visit the rightmost child if not a leaf
        if not node.leaf and node.children:
            self._inorder_traversal(node.children[-1], result)
    
    def visualize_tree(self):
        """
        Return a string representation of the B-Tree structure
        
        Returns:
            String representation of the tree
        """
        if not self.root.keys:
            return "Empty B-Tree"
        
        lines = []
        self._visualize_node(self.root, 0, lines)
        return "\n".join(lines)
    
    def _visualize_node(self, node, level, lines):
        """
        Helper function for tree visualization
        
        Args:
            node: The current node
            level: The level in the tree
            lines: List to store the string representation
        """
        # Add the keys of this node
        keys_str = ", ".join(str(key) for key in node.keys)
        lines.append(f"{' ' * (level * 4)}[{keys_str}]")
        
        # Recursively visualize children
        if not node.leaf:
            for child in node.children:
                self._visualize_node(child, level + 1, lines)

class FileIndexBTree:
    """
    File indexing manager using B-Tree for storage and retrieval
    """
    def __init__(self, min_degree=3):
        """
        Initialize the file index
        
        Args:
            min_degree: Minimum degree of the B-Tree
        """
        self.btree = BTree(t=min_degree)
    
    def add_file(self, filename, filepath=None, size=None, compression_status=False, categories=None, additional_metadata=None):
        """
        Add a file to the index
        
        Args:
            filename: The name of the file
            filepath: The path to the file
            size: The size of the file in bytes
            compression_status: Whether the file is compressed
            categories: List of categories the file belongs to
            additional_metadata: Any additional metadata to include
            
        Returns:
            True if the file was added successfully
        """
        # Create standardized metadata
        metadata = FileMetadata.create(
            filepath=filepath,
            size=size,
            compression_status=compression_status,
            categories=categories,
            additional_metadata=additional_metadata
        )
        
        # Add to the B-Tree
        self.btree.insert(filename, metadata)
        return True
    
    def remove_file(self, filename):
        """
        Remove a file from the index
        
        Args:
            filename: The name of the file
            
        Returns:
            True if the file was removed, False if it wasn't found
        """
        return self.btree.delete(filename)
    
    def search_file(self, filename):
        """
        Search for a file by its exact name
        
        Args:
            filename: The name of the file
            
        Returns:
            Dictionary with file information or None if not found
        """
        result = self.btree.search(filename)
        if result[0]:  # If a node was found
            metadata = result[0].values[result[1]]
            # Ensure metadata has all required fields
            normalized_metadata = FileMetadata.normalize(metadata)
            return {
                'filename': filename,
                'metadata': normalized_metadata
            }
        return None
    
    def search_files_by_range(self, start_name, end_name):
        """
        Search for files within a range of names
        
        Args:
            start_name: The start of the filename range
            end_name: The end of the filename range
            
        Returns:
            List of file information dictionaries
        """
        results = self.btree.range_search(start_name, end_name)
        return [{
            'filename': key, 
            'metadata': FileMetadata.normalize(value)
        } for key, value in results]
    
    def search_files_by_category(self, category):
        """
        Search for files by category
        
        Args:
            category: The category to search for
            
        Returns:
            List of file information dictionaries
        """
        all_files = self.btree.get_all()
        return [
            {'filename': key, 'metadata': FileMetadata.normalize(value)}
            for key, value in all_files
            if 'categories' in value and category in value['categories']
        ]
    
    def update_file_metadata(self, filename, new_metadata):
        """
        Update a file's metadata
        
        Args:
            filename: The name of the file
            new_metadata: The new metadata (will be merged with existing)
            
        Returns:
            True if the file was updated, False if it wasn't found
        """
        node_result = self.btree.search(filename)
        if node_result[0]:  # If a node was found
            node, index = node_result
            # Use the FileMetadata utility to update metadata
            node.values[index] = FileMetadata.update(node.values[index], new_metadata)
            return True
        return False
    
    def add_file_category(self, filename, category):
        """
        Add a category to a file
        
        Args:
            filename: The name of the file
            category: The category to add
            
        Returns:
            True if the category was added, False if the file wasn't found
        """
        node_result = self.btree.search(filename)
        if node_result[0]:  # If a node was found
            node, index = node_result
            if 'categories' not in node.values[index]:
                node.values[index]['categories'] = []
            
            if category not in node.values[index]['categories']:
                node.values[index]['categories'].append(category)
            return True
        return False
    
    def list_all_files(self):
        """
        List all files in the index
        
        Returns:
            List of file information dictionaries
        """
        all_files = self.btree.get_all()
        return [{
            'filename': key, 
            'metadata': FileMetadata.normalize(value)
        } for key, value in all_files]
    
    def get_tree_visualization(self):
        """
        Get a visualization of the B-Tree structure
        
        Returns:
            String representation of the B-Tree
        """
        return self.btree.visualize_tree()