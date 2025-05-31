"""
Handler for B-Tree operations
"""
import os
from cli.handler_base import MenuHandler
from storage.btree import FileIndexBTree

class BTreeHandler(MenuHandler):
    """
    Handler for B-Tree file indexing operations
    """
    def __init__(self):
        """Initialize the B-Tree handler"""
        super().__init__()
        self.title = "Advanced Storage Operations (B-Tree)"
        self.options = [
            "Add file to B-Tree index",
            "Search for a file by name",
            "Search files by name range",
            "Search files by category",
            "Add category to file",
            "List all indexed files",
            "Delete file from index",
            "View B-Tree structure"
        ]
        
        self.btree_manager = FileIndexBTree()
    
    def _handle_option_1(self):
        """Handle add file to B-Tree index option"""
        print("\nAdd File to B-Tree Index")
        print("==================================")
        
        filename = input("Enter the filename: ")
        filepath = input("Enter the file path (or leave blank if same as filename): ").strip() or filename
        
        # Validate file if it exists
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
        else:
            create_anyway = input(f"Warning: File {filepath} does not exist. Add to index anyway? (y/n): ").lower()
            if create_anyway != 'y':
                return
            size = 0
        
        compressed = input("Is this file compressed? (y/n): ").lower() == 'y'
        
        # Get categories
        categories = self._get_file_categories()
        
        try:
            self.btree_manager.add_file(filename, filepath, size, compressed, categories)
            self._display_success_message(f"File {filename} added to the B-Tree index successfully.")
        except Exception as e:
            self._display_error_message(f"Error adding file to B-Tree index: {str(e)}")
    
    def _handle_option_2(self):
        """Handle search for a file option"""
        print("\nSearch for a File (B-Tree)")
        print("==================================")
        
        filename = input("Enter the filename to search for: ")
        result = self.btree_manager.search_file(filename)
        
        if result:
            self._display_file_info(result)
        else:
            print(f"No file with name '{filename}' found in the B-Tree index.")
    
    def _handle_option_3(self):
        """Handle search files by name range option"""
        print("\nSearch by Name Range (B-Tree)")
        print("==================================")
        
        start_name = input("Enter the start of the name range: ")
        end_name = input("Enter the end of the name range: ")
        
        results = self.btree_manager.search_files_by_range(start_name, end_name)
        
        if results:
            print(f"\nFound {len(results)} files in range '{start_name}' to '{end_name}':")
            self._display_search_results(results)
        else:
            print(f"No files found in range '{start_name}' to '{end_name}'.")
    
    def _handle_option_4(self):
        """Handle search files by category option"""
        print("\nSearch by Category (B-Tree)")
        print("==================================")
        
        category = input("Enter the category to search for: ")
        results = self.btree_manager.search_files_by_category(category)
        
        if results:
            print(f"\nFound {len(results)} files with category '{category}':")
            self._display_search_results(results)
        else:
            print(f"No files found with category '{category}'.")
    
    def _handle_option_5(self):
        """Handle add category to file option"""
        print("\nAdd Category to File (B-Tree)")
        print("==================================")
        
        filename = input("Enter the filename: ")
        category = input("Enter the category to add: ")
        
        if self.btree_manager.add_file_category(filename, category):
            self._display_success_message(f"Category '{category}' added to file '{filename}'.")
        else:
            self._display_error_message(f"File '{filename}' not found in the B-Tree index.")
    
    def _handle_option_6(self):
        """Handle list all files option"""
        print("\nAll Indexed Files (B-Tree)")
        print("==================================")
        
        files = self.btree_manager.list_all_files()
        
        if files:
            print(f"Total files indexed: {len(files)}")
            self._display_search_results(files)
        else:
            print("No files in the B-Tree index.")
    
    def _handle_option_7(self):
        """Handle delete file option"""
        print("\nDelete File from B-Tree Index")
        print("==================================")
        
        filename = input("Enter the filename to delete: ")
        
        if self.btree_manager.remove_file(filename):
            self._display_success_message(f"File '{filename}' successfully deleted from the B-Tree index.")
        else:
            self._display_error_message(f"No file with name '{filename}' found in the B-Tree index.")
    
    def _handle_option_8(self):
        """Handle view B-Tree structure option"""
        print("\nB-Tree Structure")
        print("==================================")
        
        tree_visualization = self.btree_manager.get_tree_visualization()
        if tree_visualization:
            print(tree_visualization)
        else:
            print("B-Tree is empty.")
    
    def _get_file_categories(self):
        """
        Get categories from user input
        
        Returns:
            List of categories
        """
        categories = []
        add_categories = input("Would you like to add categories to this file? (y/n): ").lower()
        
        if add_categories == 'y':
            print("Enter categories one per line (leave blank to finish):")
            while True:
                category = input("> ").strip()
                if not category:
                    break
                categories.append(category)
                print(f"Added category: {category}")
        
        return categories
    
    def _display_file_info(self, file_info):
        """
        Display detailed file information
        
        Args:
            file_info: Dictionary containing file information
        """
        print(f"\nFile found: {file_info['filename']}")
        self._display_file_metadata(file_info['metadata'])
    
    def _display_file_metadata(self, metadata):
        """
        Display file metadata including categories
        
        Args:
            metadata: Dictionary containing file metadata
        """
        print(f"   Path: {metadata['path']}")
        print(f"   Size: {metadata['size']} bytes")
        print(f"   Creation date: {metadata['creation_date']}")
        print(f"   Compression status: {'Compressed' if metadata['compression_status'] else 'Not compressed'}")
        
        # Display categories
        if 'categories' in metadata and metadata['categories']:
            print(f"   Categories: {', '.join(metadata['categories'])}")
        else:
            print("   Categories: None")
    
    def _display_search_results(self, results):
        """
        Display search results
        
        Args:
            results: List of file information dictionaries
        """
        for i, result in enumerate(results):
            print(f"\n{i+1}. {result['filename']}")
            self._display_file_metadata(result['metadata'])
    
    def _display_success_message(self, message):
        """
        Display a success message
        
        Args:
            message: The success message to display
        """
        print(f"\n✓ {message}")
    
    def _display_error_message(self, message):
        """
        Display an error message
        
        Args:
            message: The error message to display
        """
        print(f"\n✗ {message}")