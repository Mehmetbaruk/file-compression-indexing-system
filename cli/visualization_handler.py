"""
Handler for visualization operations
"""
import os
from cli.handler_base import MenuHandler
from compression.huffman import Encoder
from storage.red_black_tree import FileIndexManager
from storage.btree import FileIndexBTree

class VisualizationHandler(MenuHandler):
    """
    Handler for visualization operations
    """
    def __init__(self):
        """Initialize the visualization handler"""
        super().__init__()
        self.title = "Visualization Tools"
        self.options = [
            "View Huffman tree structure",
            "View Red-Black tree structure",
            "View B-Tree structure",
            "Compare compression ratios"
        ]
        
        # Initialize components used for visualization
        self.encoder = Encoder()
        self.rb_manager = FileIndexManager()
        self.btree_manager = FileIndexBTree()
    
    def _handle_option_1(self):
        """Handle view Huffman tree option"""
        print("\nView Huffman Tree")
        print("==================================")
        
        file_path = input("Enter the path to the file: ")
        if not self._validate_file_exists(file_path):
            return
            
        try:
            # Try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            except UnicodeDecodeError:
                # If text reading fails, try binary mode
                with open(file_path, 'rb') as file:
                    binary_data = file.read()
                    text = str(binary_data)  # Convert binary data to string representation
                print("Note: File appears to be binary. Using binary representation for visualization.")
            
            huffman_tree = self.encoder.huffman_tree
            huffman_tree.build_tree(text)
            
            tree_visualization = huffman_tree.visualize_tree()
            print("\nHuffman Tree Structure:")
            print(tree_visualization)
            
            # Ask if the user wants to export the visualization
            export = input("\nWould you like to export this visualization to a file? (y/n): ").lower()
            if export == 'y':
                output_path = input("Enter the output file path (or leave blank for default): ").strip()
                if not output_path:
                    output_path = file_path + "_huffman_tree.txt"
                
                # Check if output_path is a directory
                if os.path.isdir(output_path):
                    # If it's a directory, append a default filename
                    output_path = os.path.join(output_path, os.path.basename(file_path) + "_huffman_tree.txt")
                
                with open(output_path, 'w', encoding='utf-8') as viz_file:
                    viz_file.write(f"Huffman Tree Visualization for {file_path}\n")
                    viz_file.write("=" * 50 + "\n")
                    viz_file.write(tree_visualization)
                
                print(f"\nTree visualization exported to {output_path}")
            
        except Exception as e:
            self._display_error_message(f"Error visualizing Huffman tree: {str(e)}")
    
    def _handle_option_2(self):
        """Handle view Red-Black tree option"""
        print("\nRed-Black Tree Structure")
        print("==================================")
        
        tree_visualization = self.rb_manager.get_tree_visualization()
        if not tree_visualization:
            print("Red-Black Tree is empty.")
            return
        
        print(tree_visualization)
        
        # Ask if the user wants to export the visualization
        export = input("\nWould you like to export this visualization to a file? (y/n): ").lower()
        if export == 'y':
            output_path = input("Enter the output file path: ").strip()
            if not output_path:
                output_path = "rbtree_visualization.txt"
            
            try:
                # Check if output_path is a directory
                if os.path.isdir(output_path):
                    # If it's a directory, append a default filename
                    output_path = os.path.join(output_path, "rbtree_visualization.txt")
                
                with open(output_path, 'w', encoding='utf-8') as viz_file:
                    viz_file.write("Red-Black Tree Visualization\n")
                    viz_file.write("=" * 50 + "\n")
                    viz_file.write(tree_visualization)
                
                print(f"\nTree visualization exported to {output_path}")
            except Exception as e:
                self._display_error_message(f"Error exporting visualization: {str(e)}")
    
    def _handle_option_3(self):
        """Handle view B-Tree structure option"""
        print("\nB-Tree Structure")
        print("==================================")
        
        # Check if there are any files in the B-Tree
        files = self.btree_manager.list_all_files()
        if not files:
            print("The B-Tree is currently empty. Add some files first.")
            
            # Offer to add a test file for demonstration
            add_test = input("\nWould you like to add a test file to the B-Tree for visualization? (y/n): ").lower()
            if add_test == 'y':
                test_filename = "test_file.txt"
                test_filepath = os.path.join(os.getcwd(), test_filename)
                self.btree_manager.add_file(
                    test_filename, 
                    test_filepath, 
                    1024,  # Example size
                    False,  # Not compressed
                    ["test", "example"]  # Example categories
                )
                print(f"\nAdded test file '{test_filename}' to B-Tree.")
        
        # Get and display the visualization
        tree_visualization = self.btree_manager.get_tree_visualization()
        if not tree_visualization or tree_visualization == "Empty B-Tree":
            # This shouldn't happen after adding files, but just in case
            if files:
                print("Warning: Tree visualization returned empty despite having files.")
                print("Here are the files that should be in the tree:")
                print("-" * 50)
                for file in files:
                    print(f"- {file['filename']}")
                return
            else:
                print("B-Tree is empty.")
                return
        
        print(tree_visualization)
        
        # Ask if the user wants to export the visualization
        export = input("\nWould you like to export this visualization to a file? (y/n): ").lower()
        if export == 'y':
            output_path = input("Enter the output file path: ").strip()
            if not output_path:
                output_path = "btree_visualization.txt"
            
            try:
                # Check if output_path is a directory
                if os.path.isdir(output_path):
                    # If it's a directory, append a default filename
                    output_path = os.path.join(output_path, "btree_visualization.txt")
                
                with open(output_path, 'w', encoding='utf-8') as viz_file:
                    viz_file.write("B-Tree Visualization\n")
                    viz_file.write("=" * 50 + "\n")
                    viz_file.write(tree_visualization)
                
                print(f"\nTree visualization exported to {output_path}")
            except Exception as e:
                self._display_error_message(f"Error exporting visualization: {str(e)}")
    
    def _handle_option_4(self):
        """Handle compare compression ratios option"""
        print("\nCompare Compression Ratios")
        print("==================================")
        
        # Get list of files to compare
        file_paths = self._get_multiple_file_paths()
        if not file_paths:
            return
        
        # Analyze each file
        results = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                
                original_size = len(text) * 8  # Assuming 8 bits per character
                
                temp_encoder = Encoder()
                temp_encoder.huffman_tree.build_tree(text)
                encoded_text = temp_encoder.huffman_tree._get_encoded_text(text)
                compressed_size = len(encoded_text)
                
                ratio = round((1 - compressed_size / original_size) * 100, 2)
                results.append({
                    'file': os.path.basename(file_path),
                    'path': file_path,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'ratio': ratio
                })
            
            except Exception as e:
                print(f"Error analyzing {file_path}: {str(e)}")
        
        # Display results
        if not results:
            print("No valid results to display.")
            return
        
        # Sort by compression ratio (descending)
        sorted_results = sorted(results, key=lambda x: x['ratio'], reverse=True)
        
        # Display the comparison table
        self._display_comparison_table(sorted_results)
        
        # Ask if the user wants to export the comparison
        export = input("\nWould you like to export this comparison to a file? (y/n): ").lower()
        if export == 'y':
            output_path = input("Enter the output file path: ").strip()
            if not output_path:
                output_path = "compression_comparison.txt"
            
            try:
                with open(output_path, 'w', encoding='utf-8') as comp_file:
                    comp_file.write("Compression Ratio Comparison\n")
                    comp_file.write("=" * 70 + "\n")
                    comp_file.write(f"{'Filename':<30} {'Original Size':<15} {'Compressed Size':<15} {'Ratio':<10}\n")
                    comp_file.write("-" * 70 + "\n")
                    
                    for result in sorted_results:
                        comp_file.write(f"{result['file']:<30} {result['original_size']:<15} {result['compressed_size']:<15} {result['ratio']}%\n")
                
                print(f"\nComparison exported to {output_path}")
            except Exception as e:
                self._display_error_message(f"Error exporting comparison: {str(e)}")
    
    def _get_multiple_file_paths(self):
        """
        Get multiple file paths from user input
        
        Returns:
            List of valid file paths
        """
        file_paths = []
        print("Enter file paths to analyze (leave blank to finish):")
        
        while True:
            file_path = input("> ").strip()
            if not file_path:
                break
            
            if os.path.exists(file_path):
                file_paths.append(file_path)
            else:
                print(f"Error: File {file_path} does not exist. Skipping.")
        
        if not file_paths:
            print("No valid files entered.")
        
        return file_paths
    
    def _display_comparison_table(self, results):
        """
        Display a comparison table of compression results
        
        Args:
            results: List of compression results
        """
        print("\nCompression Ratio Comparison:")
        print("----------------------------------")
        print(f"{'Filename':<30} {'Original Size':<15} {'Compressed Size':<15} {'Ratio':<10}")
        print("-" * 70)
        
        for result in results:
            print(f"{result['file']:<30} {result['original_size']:<15} {result['compressed_size']:<15} {result['ratio']}%")
    
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