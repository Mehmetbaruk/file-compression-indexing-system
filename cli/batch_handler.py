"""
Handler for batch operations
"""
import os
from cli.handler_base import MenuHandler
from compression.huffman import Encoder
from storage.red_black_tree import FileIndexManager
from storage.btree import FileIndexBTree

class BatchHandler(MenuHandler):
    """
    Handler for batch operations
    """
    def __init__(self):
        """Initialize the batch operations handler"""
        super().__init__()
        self.title = "Batch Operations"
        self.options = [
            "Batch compress files",
            "Batch add files to Red-Black Tree index",
            "Batch add files to B-Tree index"
        ]
        
        # Initialize components used for batch operations
        self.encoder = Encoder()
        self.rbtree_manager = FileIndexManager()
        self.btree_manager = FileIndexBTree()
    
    def _handle_option_1(self):
        """Handle batch compress files option"""
        print("\nBatch Compress Files")
        print("==================================")
        
        # Get directory path
        directory = self._get_directory_path()
        if not directory:
            return
        
        # Get file filter
        file_filter = input("Enter file extension to filter by (e.g., '.txt') or leave blank for all: ").strip()
        
        # Get output directory
        output_dir = input("Enter output directory for compressed files (or leave blank to use same as input): ").strip()
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except Exception as e:
                self._display_error_message(f"Error creating output directory: {str(e)}")
                return
        
        if not output_dir:
            output_dir = directory
        
        # Get files in directory
        files = self._get_filtered_files(directory, file_filter)
        if not files:
            return
        
        # Process each file
        print(f"\nCompressing {len(files)} files...")
        results = self._batch_compress_files(files, output_dir)
        
        # Show summary
        self._display_compression_summary(results)
        
        # Ask if user wants to add files to an index
        self._prompt_for_indexing(results)
    
    def _handle_option_2(self):
        """Handle batch add files to Red-Black Tree index option"""
        print("\nBatch Add Files to Red-Black Tree Index")
        print("==================================")
        
        # Get directory and filtered files
        directory = self._get_directory_path()
        if not directory:
            return
            
        file_filter = input("Enter file extension to filter by (e.g., '.txt') or leave blank for all: ").strip()
        files = self._get_filtered_files(directory, file_filter)
        if not files:
            return
        
        # Get compressed status
        compressed = input("Are these files compressed? (y/n): ").lower() == 'y'
        
        # Process files
        print(f"\nAdding {len(files)} files to Red-Black Tree index...")
        added = 0
        
        for filename, file_path in files:
            try:
                size = os.path.getsize(file_path)
                self.rbtree_manager.add_file(filename, file_path, size, compressed)
                added += 1
                print(f"✓ Added {filename} to index")
            except Exception as e:
                print(f"✗ Error adding {filename} to index: {str(e)}")
        
        print(f"\nBatch operation complete. {added}/{len(files)} files added to Red-Black Tree index.")
    
    def _handle_option_3(self):
        """Handle batch add files to B-Tree index option"""
        print("\nBatch Add Files to B-Tree Index")
        print("==================================")
        
        # Get directory and filtered files
        directory = self._get_directory_path()
        if not directory:
            return
            
        file_filter = input("Enter file extension to filter by (e.g., '.txt') or leave blank for all: ").strip()
        files = self._get_filtered_files(directory, file_filter)
        if not files:
            return
        
        # Get compressed status
        compressed = input("Are these files compressed? (y/n): ").lower() == 'y'
        
        # Ask for common categories
        common_categories = self._get_common_categories()
        
        # Process files
        print(f"\nAdding {len(files)} files to B-Tree index...")
        added = 0
        
        for filename, file_path in files:
            try:
                size = os.path.getsize(file_path)
                self.btree_manager.add_file(filename, file_path, size, compressed, common_categories)
                added += 1
                print(f"✓ Added {filename} to index")
            except Exception as e:
                print(f"✗ Error adding {filename} to index: {str(e)}")
        
        print(f"\nBatch operation complete. {added}/{len(files)} files added to B-Tree index.")
    
    def _get_directory_path(self):
        """
        Get and validate a directory path from user input
        
        Returns:
            A valid directory path or None if invalid
        """
        directory = input("Enter directory path: ").strip()
        if not os.path.isdir(directory):
            self._display_error_message(f"Error: Directory {directory} does not exist.")
            return None
        return directory
    
    def _get_filtered_files(self, directory, file_filter=""):
        """
        Get filtered files from a directory
        
        Args:
            directory: The directory to search in
            file_filter: Optional file extension filter
            
        Returns:
            List of (filename, file_path) tuples
        """
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and (not file_filter or file.endswith(file_filter)):
                files.append((file, file_path))
        
        if not files:
            print(f"No{' ' + file_filter if file_filter else ''} files found in {directory}")
        
        return files
    
    def _batch_compress_files(self, files, output_dir):
        """
        Compress multiple files
        
        Args:
            files: List of (filename, file_path) tuples
            output_dir: Directory for output files
            
        Returns:
            List of result dictionaries
        """
        results = []
        
        for filename, file_path in files:
            try:
                # Generate output path
                output_path = os.path.join(output_dir, filename + ".bin")
                
                # Compress the file
                self.encoder.compress(file_path, output_path)
                ratio = self.encoder.get_compression_ratio()
                
                results.append({
                    'file': filename,
                    'input_path': file_path,
                    'output_path': output_path,
                    'ratio': ratio,
                    'size': self.encoder.compressed_size,
                    'success': True
                })
                
                print(f"✓ Compressed {filename} -> {os.path.basename(output_path)} ({ratio}% reduction)")
                
            except Exception as e:
                results.append({
                    'file': filename,
                    'input_path': file_path,
                    'error': str(e),
                    'success': False
                })
                print(f"✗ Error compressing {filename}: {str(e)}")
        
        return results
    
    def _display_compression_summary(self, results):
        """
        Display a summary of compression results
        
        Args:
            results: List of compression result dictionaries
        """
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\nBatch compression complete.")
        print(f"  Total files processed: {len(results)}")
        print(f"  Successfully compressed: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        
        if successful:
            avg_ratio = sum(r['ratio'] for r in successful) / len(successful)
            print(f"  Average compression ratio: {avg_ratio:.2f}%")
    
    def _prompt_for_indexing(self, results):
        """
        Prompt user to add compressed files to an index
        
        Args:
            results: List of compression result dictionaries
        """
        successful = [r for r in results if r['success']]
        if not successful:
            return
            
        add_to_index = input("\nWould you like to add all compressed files to an index? (y/n): ").lower()
        if add_to_index != 'y':
            return
            
        index_type = input("Which index? (1: Red-Black Tree, 2: B-Tree): ").strip()
        
        if index_type not in ('1', '2'):
            print("Invalid index type. Files not added to any index.")
            return
            
        # If B-Tree, get common categories
        common_categories = []
        if index_type == '2':
            common_categories = self._get_common_categories()
        
        # Add files to selected index
        added = 0
        for result in successful:
            try:
                file_path = result['output_path']
                filename = os.path.basename(file_path)
                size = result['size']
                
                if index_type == '1':
                    self.rbtree_manager.add_file(filename, file_path, size, True)
                elif index_type == '2':
                    self.btree_manager.add_file(filename, file_path, size, True, common_categories)
                
                added += 1
                print(f"✓ Added {filename} to index")
                
            except Exception as e:
                print(f"✗ Error adding {result['file']} to index: {str(e)}")
        
        index_name = "Red-Black Tree" if index_type == '1' else "B-Tree"
        print(f"\n{added}/{len(successful)} files added to {index_name} index.")
    
    def _get_common_categories(self):
        """
        Get common categories for batch file operations
        
        Returns:
            List of category strings
        """
        categories = []
        add_categories = input("Would you like to add common categories to all files? (y/n): ").lower()
        
        if add_categories == 'y':
            print("Enter categories one per line (leave blank to finish):")
            while True:
                category = input("> ").strip()
                if not category:
                    break
                categories.append(category)
                print(f"Added common category: {category}")
        
        return categories
    
    def _display_error_message(self, message):
        """
        Display an error message
        
        Args:
            message: The error message to display
        """
        print(f"\n✗ {message}")