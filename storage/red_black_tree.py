"""
Red-Black Tree implementation for efficient filename searching
"""
import os
from datetime import datetime
from storage import FileMetadata

# Colors for Red-Black Tree nodes
RED = 0
BLACK = 1

class Node:
    """
    Node class for the Red-Black Tree
    """
    def __init__(self, filename, metadata=None):
        self.filename = filename  # Key for sorting
        self.metadata = metadata or {}  # File information
        self.color = RED  # New nodes are red by default
        self.left = None
        self.right = None
        self.parent = None
    
    def __repr__(self):
        return f"Node({self.filename}, {self.color})"

class RedBlackTree:
    """
    Red-Black Tree implementation for efficient filename searching
    """
    def __init__(self):
        self.NIL = Node(None)  # Sentinel node
        self.NIL.color = BLACK
        self.NIL.left = None
        self.NIL.right = None
        self.root = self.NIL
    
    def insert(self, filename, filepath=None, size=None, compression_status=False, categories=None, additional_metadata=None):
        """
        Insert a file into the tree with its metadata
        
        Args:
            filename: Name of the file (used as key)
            filepath: Path to the file
            size: Size of the file in bytes
            compression_status: Whether the file is compressed
            categories: List of categories the file belongs to
            additional_metadata: Any additional metadata to include
            
        Returns:
            The newly created node
        """
        # Create standardized metadata
        metadata = FileMetadata.create(
            filepath=filepath,
            size=size,
            compression_status=compression_status,
            categories=categories,
            additional_metadata=additional_metadata
        )
        
        # Create new node
        new_node = Node(filename, metadata)
        new_node.left = self.NIL
        new_node.right = self.NIL
        
        # Standard BST insert
        y = self.NIL
        x = self.root
        
        while x != self.NIL:
            y = x
            if new_node.filename < x.filename:
                x = x.left
            else:
                x = x.right
        
        new_node.parent = y
        if y == self.NIL:
            self.root = new_node  # Tree was empty
        elif new_node.filename < y.filename:
            y.left = new_node
        else:
            y.right = new_node
            
        # Fix Red-Black properties
        self._fix_insert(new_node)
        
        return new_node
    
    def _fix_insert(self, k):
        """
        Fix the Red-Black Tree properties after insertion
        """
        while k != self.root and k.parent.color == RED:
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left  # uncle
                if u.color == RED:
                    u.color = BLACK
                    k.parent.color = BLACK
                    k.parent.parent.color = RED
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self._right_rotate(k)
                    k.parent.color = BLACK
                    k.parent.parent.color = RED
                    self._left_rotate(k.parent.parent)
            else:
                u = k.parent.parent.right  # uncle
                if u.color == RED:
                    u.color = BLACK
                    k.parent.color = BLACK
                    k.parent.parent.color = RED
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self._left_rotate(k)
                    k.parent.color = BLACK
                    k.parent.parent.color = RED
                    self._right_rotate(k.parent.parent)
            
        self.root.color = BLACK
    
    def _left_rotate(self, x):
        """
        Rotate the subtree to the left with x as the root
        """
        y = x.right
        x.right = y.left
        
        if y.left != self.NIL:
            y.left.parent = x
        
        y.parent = x.parent
        
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        
        y.left = x
        x.parent = y
    
    def _right_rotate(self, x):
        """
        Rotate the subtree to the right with x as the root
        """
        y = x.left
        x.left = y.right
        
        if y.right != self.NIL:
            y.right.parent = x
        
        y.parent = x.parent
        
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        
        y.right = x
        x.parent = y
    
    def search(self, filename):
        """
        Search for a file by its filename
        """
        return self._search_helper(self.root, filename)
    
    def _search_helper(self, node, filename):
        """
        Helper function for search
        """
        if node == self.NIL:
            return None
        
        if filename == node.filename:
            return node
        
        if filename < node.filename:
            return self._search_helper(node.left, filename)
        
        return self._search_helper(node.right, filename)
    
    def partial_search(self, partial_name):
        """
        Search for files with names that partially match the given string
        """
        results = []
        self._partial_search_helper(self.root, partial_name.lower(), results)
        return results
    
    def _partial_search_helper(self, node, partial_name, results):
        """
        Helper function for partial search
        """
        if node == self.NIL:
            return
        
        # Check if current node matches
        if partial_name in node.filename.lower():
            results.append(node)
        
        # Check both subtrees since partial matches could be anywhere
        self._partial_search_helper(node.left, partial_name, results)
        self._partial_search_helper(node.right, partial_name, results)
    
    def delete(self, filename):
        """
        Delete a file from the tree
        """
        node = self.search(filename)
        if node:
            self._delete_node(node)
            return True
        return False
    
    def _delete_node(self, z):
        """
        Delete the given node and fix the tree
        """
        y = z
        y_original_color = y.color
        
        if z.left == self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right == self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right
            
            if y.parent == z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        
        if y_original_color == BLACK:
            self._fix_delete(x)
    
    def _transplant(self, u, v):
        """
        Replace subtree u with subtree v
        """
        if u.parent == self.NIL:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent
    
    def _minimum(self, x):
        """
        Find the node with the minimum key in the subtree rooted at x
        """
        while x.left != self.NIL:
            x = x.left
        return x
    
    def _fix_delete(self, x):
        """
        Fix the Red-Black Tree properties after deletion
        """
        while x != self.root and x.color == BLACK:
            if x == x.parent.left:
                w = x.parent.right
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._left_rotate(x.parent)
                    w = x.parent.right
                
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self._right_rotate(w)
                        w = x.parent.right
                    
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._right_rotate(x.parent)
                    w = x.parent.left
                
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self._left_rotate(w)
                        w = x.parent.left
                    
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self._right_rotate(x.parent)
                    x = self.root
        
        x.color = BLACK
    
    def update_metadata(self, filename, metadata):
        """
        Update the metadata of a file
        """
        node = self.search(filename)
        if node:
            node.metadata.update(metadata)
            return True
        return False
    
    def get_all_files(self):
        """
        Get a list of all files in the tree
        """
        files = []
        self._inorder_traversal(self.root, files)
        return files
    
    def _inorder_traversal(self, node, files):
        """
        Helper function for inorder traversal
        """
        if node != self.NIL:
            self._inorder_traversal(node.left, files)
            files.append({
                'filename': node.filename,
                'metadata': node.metadata
            })
            self._inorder_traversal(node.right, files)
    
    def visualize_tree(self):
        """
        Return a simple visualization of the tree structure
        """
        lines = []
        
        def _print_tree(node, prefix="", is_left=True):
            if node == self.NIL:
                return
            
            color_text = "BLACK" if node.color == BLACK else "RED"
            lines.append(f"{prefix}{'└── ' if is_left else '┌── '}{node.filename} ({color_text})")
            
            new_prefix = prefix + ("    " if is_left else "│   ")
            _print_tree(node.left, new_prefix, True)
            _print_tree(node.right, new_prefix, False)
        
        _print_tree(self.root, "", True)
        return "\n".join(lines)

    def __len__(self):
        """
        Return the number of nodes in the tree
        """
        count = [0]
        
        def _count_nodes(node):
            if node != self.NIL:
                count[0] += 1
                _count_nodes(node.left)
                _count_nodes(node.right)
        
        _count_nodes(self.root)
        return count[0]

class FileIndexManager:
    """
    Manager for file indexing operations using Red-Black Tree
    """
    def __init__(self):
        self.tree = RedBlackTree()
    
    def add_file(self, filename, filepath=None, size=None, compression_status=False, categories=None, additional_metadata=None):
        """
        Add a file to the index
        """
        return self.tree.insert(filename, filepath, size, compression_status, categories, additional_metadata)
    
    def remove_file(self, filename):
        """
        Remove a file from the index
        """
        return self.tree.delete(filename)
    
    def search_file(self, filename):
        """
        Search for a file by its exact name
        """
        node = self.tree.search(filename)
        if node:
            result = {
                'filename': node.filename,
                'filepath': node.metadata.get('path', ''),
                'size': node.metadata.get('size', 0),
                'creation_date': node.metadata.get('creation_date', ''),
                'compression_status': node.metadata.get('compression_status', False)
            }
            # Include any other metadata
            for key, value in node.metadata.items():
                if key not in ['path', 'size', 'creation_date', 'compression_status']:
                    result[key] = value
            return result
        return None
    
    def search_files_by_partial_name(self, partial_name):
        """
        Search for files by partial name match
        """
        nodes = self.tree.partial_search(partial_name)
        return [{
            'filename': node.filename,
            'metadata': node.metadata
        } for node in nodes]
    
    def update_file_metadata(self, filename, metadata):
        """
        Update a file's metadata
        """
        return self.tree.update_metadata(filename, metadata)
    
    def list_all_files(self):
        """
        List all files in the index
        """
        return self.tree.get_all_files()
    
    def get_tree_visualization(self):
        """
        Get a visualization of the tree structure
        """
        return self.tree.visualize_tree()

    def get_all_files(self):
        """
        Get all files in the index - alias for list_all_files
        """
        return self.tree.get_all_files()
        
    def visualize_tree(self):
        """
        Get a visualization of the tree structure - alias for get_tree_visualization
        """
        return self.tree.visualize_tree()
        
    def contains_file(self, filename):
        """
        Check if a file exists in the index
        
        Args:
            filename: The filename to check
            
        Returns:
            Boolean indicating if the file exists
        """
        return self.tree.search(filename) is not None