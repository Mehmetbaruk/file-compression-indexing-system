"""
Handler for Red-Black Tree operations
"""
import os
from cli.handler_base import MenuHandler
from storage.red_black_tree import FileIndexManager

class RBTreeHandler(MenuHandler):
    """
    Handler for Red-Black Tree file indexing operations
    """
    def __init__(self):
        """Initialize the Red-Black Tree handler"""
        super().__init__()
        self.title = "Red-Black Tree Operations"
        self.options = [
            "Add file to index",
            "Search for file by name",
            "Delete file from index",
            "List all indexed files",
            "View tree structure",
            "Export index to file"
        ]
        
        # Initialize the file index manager
        self.file_manager = FileIndexManager()
    
    def _handle_option_1(self):
        """Handle add file to index option"""
        print("\nAdd File to Red-Black Tree Index")
        print("==================================")
        
        # Get file information
        file_path = input("Enter the path to the file: ")
        if not self._validate_file_exists(file_path):
            return
        
        filename = input("Enter a name for this file in the index (leave blank to use filename): ").strip()
        if not filename:
            filename = os.path.basename(file_path)
        
        # Get file attributes
        file_size = os.path.getsize(file_path)
        compressed = input("Is this file compressed? (y/n): ").lower() == 'y'
        
        # Add file to index
        try:
            self.file_manager.add_file(filename, file_path, file_size, compressed)
            print(f"\n✓ File '{filename}' added to index successfully!")
            
            # Ask if user wants to view the updated tree
            view_tree = input("\nWould you like to view the updated tree? (y/n): ").lower()
            if view_tree == 'y':
                tree_visualization = self.file_manager.visualize_tree()
                if tree_visualization:
                    print("\nRed-Black Tree Structure:")
                    print(tree_visualization)
                else:
                    print("\nTree visualization not available.")
            
        except Exception as e:
            self._display_error_message(f"Error adding file to index: {str(e)}")
    
    def _handle_option_2(self):
        """Handle search for file by name option"""
        print("\nSearch for File by Name")
        print("==================================")
        
        search_term = input("Enter filename to search for: ")
        if not search_term:
            print("Search term cannot be empty.")
            return
        
        try:
            # First try exact match
            file_result = self.file_manager.search_file(search_term)
            
            if file_result:
                # Found an exact match
                print(f"\nFound file matching '{search_term}':")
                print(f"{'Filename':<30} {'Path':<40} {'Size':<10} {'Compressed'}")
                print("-" * 90)
                
                compressed_status = "Yes" if file_result.get('compression_status', False) else "No"
                size_display = self._format_file_size(file_result.get('size', 0))
                print(f"{file_result.get('filename'):<30} {file_result.get('filepath', ''):<40} {size_display:<10} {compressed_status}")
                
                # Display detailed information
                self._display_file_details(file_result)
            else:
                # Try partial match
                print(f"\nNo exact match found for '{search_term}'. Searching for partial matches...")
                partial_results = self.file_manager.search_files_by_partial_name(search_term)
                
                if not partial_results:
                    print(f"\nNo files found matching '{search_term}'.")
                    return
                    
                result_count = len(partial_results)
                print(f"\nFound {result_count} file(s) partially matching '{search_term}':")
                print(f"{'Filename':<30} {'Path':<40} {'Size':<10} {'Compressed'}")
                print("-" * 90)
                
                for result in partial_results:
                    metadata = result['metadata']
                    compressed_status = "Yes" if metadata.get('compression_status', False) else "No"
                    size_display = self._format_file_size(metadata.get('size', 0))
                    print(f"{result['filename']:<30} {metadata.get('path', ''):<40} {size_display:<10} {compressed_status}")
                
                # Ask if user wants detailed information about a specific result
                if result_count > 1:
                    detail_file = input("\nEnter the exact filename to show detailed information (or leave blank): ").strip()
                    if detail_file:
                        for result in partial_results:
                            if result['filename'] == detail_file:
                                self._display_file_details({
                                    'filename': result['filename'],
                                    'filepath': result['metadata'].get('path', ''),
                                    'size': result['metadata'].get('size', 0),
                                    'compression_status': result['metadata'].get('compression_status', False)
                                })
                                break
                
        except Exception as e:
            self._display_error_message(f"Error searching for file: {str(e)}")
    
    def _handle_option_3(self):
        """Handle delete file from index option"""
        print("\nDelete File from Index")
        print("==================================")
        
        filename = input("Enter the exact filename to delete: ")
        if not filename:
            print("Filename cannot be empty.")
            return
        
        try:
            # Confirm deletion
            file_exists = self.file_manager.contains_file(filename)
            if not file_exists:
                print(f"\nNo file named '{filename}' found in the index.")
                return
                
            confirm = input(f"\nAre you sure you want to delete '{filename}' from the index? (y/n): ").lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return
            
            # Delete the file
            self.file_manager.remove_file(filename)
            print(f"\n✓ File '{filename}' deleted from index successfully!")
            
        except Exception as e:
            self._display_error_message(f"Error deleting file: {str(e)}")
    
    def _handle_option_4(self):
        """Handle list all indexed files option"""
        print("\nList All Indexed Files")
        print("==================================")
        
        try:
            all_files = self.file_manager.get_all_files()
            file_count = len(all_files)
            
            if file_count == 0:
                print("No files in the index.")
                return
            
            # Print the header for the file table
            print(f"\nTotal files: {file_count}")
            print(f"\n{'Filename':<30} {'Size':<10} {'Compressed'}")
            print("-" * 50)
            
            # Calculate total size
            total_size = 0
            compressed_files = 0
            
            # Print each file
            for file_info in all_files:
                filename = file_info['filename']
                metadata = file_info['metadata']
                
                file_size = metadata.get('size', 0)
                total_size += file_size
                
                compressed_status = "Yes" if metadata.get('compression_status', False) else "No"
                if metadata.get('compression_status', False):
                    compressed_files += 1
                    
                size_display = self._format_file_size(file_size)
                print(f"{filename:<30} {size_display:<10} {compressed_status}")
            
            # Print summary
            print(f"\nTotal size: {self._format_file_size(total_size)}")
            print(f"Compressed files: {compressed_files}")
            
        except Exception as e:
            self._display_error_message(f"Error listing files: {str(e)}")
    
    def _display_file_details(self, file_info):
        """
        Display detailed information about a file
        
        Args:
            file_info: Dictionary with file information
        """
        filename = file_info.get('filename', '')
        filepath = file_info.get('filepath', '')
        size = file_info.get('size', 0)
        compressed = file_info.get('compression_status', False)
        
        print(f"\nDetailed information for '{filename}':")
        print("-" * 40)
        print(f"Path: {filepath}")
        print(f"Size: {self._format_file_size(size)}")
        print(f"Compressed: {'Yes' if compressed else 'No'}")
        
        # Check if file exists
        if filepath:
            file_exists = os.path.exists(filepath)
            print(f"File exists on disk: {'Yes' if file_exists else 'No'}")
            
            if file_exists:
                # Get file modification time
                mod_time = os.path.getmtime(filepath)
                print(f"Last modified: {self._format_datetime(mod_time)}")
        else:
            print("File exists on disk: No (no path information)")
    
    def _export_text_format(self, output_file, files):
        """
        Export files in plain text format
        
        Args:
            output_file: Path to output file
            files: List of file information dictionaries
        """
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write("Red-Black Tree Index Export\n")
            out.write("=" * 30 + "\n\n")
            
            out.write(f"Total files: {len(files)}\n")
            out.write(f"Date exported: {self._get_current_datetime()}\n\n")
            
            out.write(f"{'Filename':<30} {'Path':<40} {'Size':<10} {'Compressed'}\n")
            out.write("-" * 90 + "\n")
            
            for file in files:
                filename = file['filename']
                metadata = file['metadata']
                path = metadata.get('path', '')
                size = metadata.get('size', 0)
                compressed = metadata.get('compression_status', False)
                
                compressed_status = "Yes" if compressed else "No"
                size_display = self._format_file_size(size)
                out.write(f"{filename:<30} {path:<40} {size_display:<10} {compressed_status}\n")
    
    def _export_csv_format(self, output_file, files):
        """
        Export files in CSV format
        
        Args:
            output_file: Path to output file
            files: List of file information dictionaries
        """
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as out:
            writer = csv.writer(out)
            
            # Write header
            writer.writerow(["Filename", "Path", "Size", "Compressed"])
            
            # Write data
            for file in files:
                filename = file['filename']
                metadata = file['metadata']
                path = metadata.get('path', '')
                size = metadata.get('size', 0)
                compressed = metadata.get('compression_status', False)
                
                writer.writerow([
                    filename,
                    path,
                    size,
                    "Yes" if compressed else "No"
                ])
    
    def _export_json_format(self, output_file, files):
        """
        Export files in JSON format
        
        Args:
            output_file: Path to output file
            files: List of file information dictionaries
        """
        import json
        
        # Convert to dictionaries
        files_data = []
        for file in files:
            filename = file['filename']
            metadata = file['metadata']
            
            files_data.append({
                "filename": filename,
                "path": metadata.get('path', ''),
                "size": metadata.get('size', 0),
                "compressed": metadata.get('compression_status', False),
                "metadata": {
                    "export_date": self._get_current_datetime(),
                    "creation_date": metadata.get('creation_date', ''),
                    "modified_date": metadata.get('modified_date', '')
                }
            })
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as out:
            json.dump({
                "total_files": len(files),
                "export_date": self._get_current_datetime(),
                "files": files_data
            }, out, indent=2)
    
    def _format_file_size(self, size_in_bytes):
        """
        Format file size in human readable format
        
        Args:
            size_in_bytes: File size in bytes
            
        Returns:
            Formatted file size string
        """
        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        elif size_in_bytes < 1024 * 1024:
            return f"{size_in_bytes / 1024:.2f} KB"
        else:
            return f"{size_in_bytes / (1024 * 1024):.2f} MB"
    
    def _format_datetime(self, timestamp):
        """
        Format a timestamp as a readable date/time
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted date/time string
        """
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_current_datetime(self):
        """
        Get the current date and time
        
        Returns:
            Current date/time string
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _validate_file_exists(self, file_path):
        """
        Validate that a file exists
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            Boolean indicating if the file exists
        """
        if not os.path.exists(file_path):
            self._display_error_message(f"Error: File {file_path} does not exist.")
            return False
        return True
    
    def _display_error_message(self, message):
        """
        Display an error message
        
        Args:
            message: The error message to display
        """
        print(f"\n✗ {message}")