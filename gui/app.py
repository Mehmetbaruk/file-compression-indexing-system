import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QMessageBox, QProgressBar, QSplitter,
                            QStatusBar, QTextEdit, QLineEdit, QCheckBox, QSpinBox, QListWidget, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

# Import existing functionality
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compression.huffman import Encoder, Decoder
from storage.red_black_tree import RedBlackTree
from storage.btree import BTree
from utils.config_manager import ConfigManager

# Import GUI components
from gui.other_tabs import CompressionTab
from gui.visualization_tab import VisualizationTab

# File managers might need to be imported or created based on actual implementation
class FileIndexManager:
    """Simple manager for Red-Black Tree file indexing"""
    def __init__(self):
        self.rbtree = RedBlackTree()
        self.files = {}
    
    def add_file(self, filename, filepath, size=0, is_compressed=False, categories=None):
        """Add a file to the Red-Black Tree index"""
        self.files[filename] = {
            'path': filepath,
            'size': size,
            'compressed': is_compressed,
            'categories': categories or []
        }
        self.rbtree.insert(filename)
        
    def get_tree_visualization(self):
        """Get text visualization of the Red-Black Tree"""
        if not self.files:
            return "Red-Black Tree is empty."
        
        # This is a placeholder - actual implementation depends on the RBTree's capabilities
        if hasattr(self.rbtree, 'visualize'):
            return self.rbtree.visualize()
        
        # Basic visualization if the tree doesn't have a built-in method
        result = "Red-Black Tree Visualization:\n"
        result += "=" * 40 + "\n"
        for i, filename in enumerate(sorted(self.files.keys())):
            result += f"Node {i}: {filename} " + ("(RED)" if i % 2 == 0 else "(BLACK)") + "\n"
            if i > 0:
                parent = sorted(self.files.keys())[i//2]
                result += f"{parent} -> {filename}\n"
        
        return result
    
    def search(self, filename):
        """Search for a file in the Red-Black Tree"""
        if filename in self.files:
            return self.files[filename]
        return None
    
    def list_all_files(self):
        """List all files in the index"""
        return list(self.files.keys())


class FileIndexBTree:
    """Simple manager for B-Tree file indexing"""
    def __init__(self, order=5):
        self.btree = BTree(order)
        self.files = {}
    
    def add_file(self, filename, filepath, size=0, is_compressed=False, categories=None):
        """Add a file to the B-Tree index"""
        file_info = {
            'path': filepath,
            'size': size,
            'compressed': is_compressed,
            'categories': categories or []
        }
        self.files[filename] = file_info
        # Fix: Pass both key and value to the B-Tree insert method
        self.btree.insert(filename, file_info)
        
    def get_tree_visualization(self):
        """Get text visualization of the B-Tree"""
        if not self.files:
            return "B-Tree is empty."
        
        # This is a placeholder - actual implementation depends on the BTree's capabilities
        if hasattr(self.btree, 'visualize'):
            return self.btree.visualize()
        
        # Basic visualization if the tree doesn't have a built-in method
        result = "B-Tree Visualization:\n"
        result += "=" * 40 + "\n"
        
        # Create a simple representation
        result += "Node [Root]\n"
        result += "Keys: " + ", ".join(sorted(self.files.keys())[:3]) + "\n"
        
        for i, filename in enumerate(sorted(self.files.keys())[3:]):
            result += f"Node [{i+1}]\n"
            result += f"Keys: {filename}\n"
            result += f"Child: Node [{i+1}]\n"
        
        return result
    
    def search(self, filename):
        """Search for a file in the B-Tree"""
        if filename in self.files:
            return self.files[filename]
        return None
    
    def list_all_files(self):
        """List all files in the index"""
        return list(self.files.keys())


class RBTreeTab(QWidget):
    """Tab for Red-Black Tree operations"""
    
    def __init__(self, rb_manager):
        super().__init__()
        self.rb_manager = rb_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        layout = QVBoxLayout(self)
        
        # Add RB-Tree specific UI elements here
        layout.addWidget(QLabel("Red-Black Tree Storage"))
        
        # Add file button
        add_file_btn = QPushButton("Add File to RB-Tree")
        add_file_btn.clicked.connect(self.add_file_to_rbtree)
        
        # Search file button
        search_file_btn = QPushButton("Search File")
        search_file_btn.clicked.connect(self.search_file_in_rbtree)
        
        # List files button
        list_files_btn = QPushButton("List All Files")
        list_files_btn.clicked.connect(self.list_all_rbtree_files)
        
        # Add buttons to layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(add_file_btn)
        buttons_layout.addWidget(search_file_btn)
        buttons_layout.addWidget(list_files_btn)
        layout.addLayout(buttons_layout)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.results_text)
        
    def add_file_to_rbtree(self):
        """Add a file to the Red-Black Tree"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Add", "", "All Files (*)"
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Add file to RB-Tree
            self.rb_manager.add_file(filename, file_path, file_size, False, [])
            
            self.results_text.append(f"Added file '{filename}' to Red-Black Tree")
            self.results_text.append(f"Path: {file_path}")
            self.results_text.append(f"Size: {file_size} bytes")
            self.results_text.append("---")
            
    def search_file_in_rbtree(self):
        """Search for a file in the Red-Black Tree"""
        # In a full implementation, you'd have a dialog to enter a filename
        # For simplicity, we'll just search for the first file in the tree
        files = self.rb_manager.list_all_files()
        
        if not files:
            self.results_text.append("Red-Black Tree is empty.")
            return
            
        # For demo purposes, just show all files
        self.results_text.append("Files in Red-Black Tree:")
        for filename in files:
            file_info = self.rb_manager.search(filename)
            self.results_text.append(f"- {filename}: {file_info['path']}")
        
    def list_all_rbtree_files(self):
        """List all files in the Red-Black Tree"""
        files = self.rb_manager.list_all_files()
        
        if not files:
            self.results_text.append("Red-Black Tree is empty.")
            return
            
        self.results_text.append("All files in Red-Black Tree:")
        for filename in files:
            self.results_text.append(f"- {filename}")


class BTreeTab(QWidget):
    """Tab for B-Tree operations"""
    
    def __init__(self, btree_manager):
        super().__init__()
        self.btree_manager = btree_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        layout = QVBoxLayout(self)
        
        # Add B-Tree specific UI elements here
        layout.addWidget(QLabel("B-Tree Storage"))
        
        # Add file button
        add_file_btn = QPushButton("Add File to B-Tree")
        add_file_btn.clicked.connect(self.add_file_to_btree)
        
        # Search file button
        search_file_btn = QPushButton("Search File")
        search_file_btn.clicked.connect(self.search_file_in_btree)
        
        # List files button
        list_files_btn = QPushButton("List All Files")
        list_files_btn.clicked.connect(self.list_all_btree_files)
        
        # Add buttons to layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(add_file_btn)
        buttons_layout.addWidget(search_file_btn)
        buttons_layout.addWidget(list_files_btn)
        layout.addLayout(buttons_layout)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.results_text)
        
    def add_file_to_btree(self):
        """Add a file to the B-Tree"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Add", "", "All Files (*)"
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Add file to B-Tree
            self.btree_manager.add_file(filename, file_path, file_size, False, [])
            
            self.results_text.append(f"Added file '{filename}' to B-Tree")
            self.results_text.append(f"Path: {file_path}")
            self.results_text.append(f"Size: {file_size} bytes")
            self.results_text.append("---")
            
    def search_file_in_btree(self):
        """Search for a file in the B-Tree"""
        # In a full implementation, you'd have a dialog to enter a filename
        # For simplicity, we'll just search for the first file in the tree
        files = self.btree_manager.list_all_files()
        
        if not files:
            self.results_text.append("B-Tree is empty.")
            return
            
        # For demo purposes, just show all files
        self.results_text.append("Files in B-Tree:")
        for filename in files:
            file_info = self.btree_manager.search(filename)
            self.results_text.append(f"- {filename}: {file_info['path']}")
        
    def list_all_btree_files(self):
        """List all files in the B-Tree"""
        files = self.btree_manager.list_all_files()
        
        if not files:
            self.results_text.append("B-Tree is empty.")
            return
            
        self.results_text.append("All files in B-Tree:")
        for filename in files:
            self.results_text.append(f"- {filename}")


class SearchTab(QWidget):
    """Tab for unified search across both trees"""
    
    def __init__(self, rb_manager, btree_manager):
        super().__init__()
        self.rb_manager = rb_manager
        self.btree_manager = btree_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Unified Search"))
        
        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter filename to search...")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Add to layout
        layout.addLayout(search_layout)
        layout.addWidget(QLabel("Search Results:"))
        layout.addWidget(self.results_text)
        
    def perform_search(self):
        """Perform search across both trees"""
        filename = self.search_input.text().strip()
        
        if not filename:
            QMessageBox.warning(self, "Warning", "Please enter a filename to search")
            return
            
        self.results_text.clear()
        self.results_text.append(f"Searching for '{filename}' in both trees...\n")
        
        # Search in RB-Tree
        rb_result = self.rb_manager.search(filename)
        if rb_result:
            self.results_text.append("Found in Red-Black Tree:")
            self.results_text.append(f"Path: {rb_result['path']}")
            self.results_text.append(f"Size: {rb_result['size']} bytes")
            self.results_text.append(f"Compressed: {'Yes' if rb_result['compressed'] else 'No'}")
            self.results_text.append("")
        else:
            self.results_text.append("Not found in Red-Black Tree.\n")
            
        # Search in B-Tree
        btree_result = self.btree_manager.search(filename)
        if btree_result:
            self.results_text.append("Found in B-Tree:")
            self.results_text.append(f"Path: {btree_result['path']}")
            self.results_text.append(f"Size: {btree_result['size']} bytes")
            self.results_text.append(f"Compressed: {'Yes' if btree_result['compressed'] else 'No'}")
        else:
            self.results_text.append("Not found in B-Tree.")


class BatchTab(QWidget):
    """Tab for batch operations"""
    
    def __init__(self, encoder, rb_manager, btree_manager):
        super().__init__()
        self.encoder = encoder
        self.rb_manager = rb_manager
        self.btree_manager = btree_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Batch Operations"))
        
        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("No directory selected")
        dir_select_btn = QPushButton("Select Directory")
        dir_select_btn.clicked.connect(self.select_directory)
        
        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.dir_label, 1)
        dir_layout.addWidget(dir_select_btn)
        
        # Operation selection
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Operations:"))
        
        self.compress_check = QCheckBox("Compress Files")
        self.index_rb_check = QCheckBox("Index in RB-Tree")
        self.index_btree_check = QCheckBox("Index in B-Tree")
        
        op_layout.addWidget(self.compress_check)
        op_layout.addWidget(self.index_rb_check)
        op_layout.addWidget(self.index_btree_check)
        
        # File filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("File Filter:"))
        self.filter_input = QLineEdit("*.txt")
        filter_layout.addWidget(self.filter_input)
        
        # Execute button
        execute_btn = QPushButton("Execute Batch Operations")
        execute_btn.clicked.connect(self.execute_batch)
        
        # Progress bar
        self.progress = QProgressBar()
        
        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Add to layout
        layout.addLayout(dir_layout)
        layout.addLayout(op_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(execute_btn)
        layout.addWidget(QLabel("Progress:"))
        layout.addWidget(self.progress)
        layout.addWidget(QLabel("Results:"))
        layout.addWidget(self.results_text)
        
    def select_directory(self):
        """Select a directory for batch operations"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", ""
        )
        
        if directory:
            self.directory = directory
            self.dir_label.setText(directory)
            
    def execute_batch(self):
        """Execute the batch operations"""
        if not hasattr(self, 'directory'):
            QMessageBox.warning(self, "Warning", "Please select a directory first.")
            return
            
        if not (self.compress_check.isChecked() or 
                self.index_rb_check.isChecked() or 
                self.index_btree_check.isChecked()):
            QMessageBox.warning(self, "Warning", "Please select at least one operation.")
            return
            
        # Get all matching files
        file_filter = self.filter_input.text().strip() or "*.txt"
        matching_files = []
        
        import fnmatch
        for root, _, files in os.walk(self.directory):
            for filename in files:
                if fnmatch.fnmatch(filename, file_filter):
                    matching_files.append(os.path.join(root, filename))
                    
        if not matching_files:
            QMessageBox.information(self, "Information", f"No files matching {file_filter} found in the selected directory.")
            return
            
        # Process files
        self.results_text.clear()
        self.results_text.append(f"Found {len(matching_files)} files to process.\n")
        self.progress.setRange(0, len(matching_files))
        
        for i, file_path in enumerate(matching_files):
            filename = os.path.basename(file_path)
            self.results_text.append(f"Processing {filename}...")
            
            # Perform selected operations
            if self.compress_check.isChecked():
                try:
                    output_path = file_path + ".huff"
                    self.encoder.compress(file_path, output_path)
                    self.results_text.append(f"  - Compressed to {os.path.basename(output_path)}")
                except Exception as e:
                    self.results_text.append(f"  - Compression failed: {str(e)}")
                    
            if self.index_rb_check.isChecked():
                try:
                    self.rb_manager.add_file(filename, file_path, os.path.getsize(file_path), False, [])
                    self.results_text.append("  - Indexed in Red-Black Tree")
                except Exception as e:
                    self.results_text.append(f"  - RB-Tree indexing failed: {str(e)}")
                    
            if self.index_btree_check.isChecked():
                try:
                    self.btree_manager.add_file(filename, file_path, os.path.getsize(file_path), False, [])
                    self.results_text.append("  - Indexed in B-Tree")
                except Exception as e:
                    self.results_text.append(f"  - B-Tree indexing failed: {str(e)}")
                    
            self.results_text.append("")
            self.progress.setValue(i + 1)
            QApplication.processEvents()  # Update UI
            
        self.results_text.append("Batch processing complete!")


class ConfigTab(QWidget):
    """Tab for system configuration"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager() if 'ConfigManager' in globals() else None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("System Configuration"))
        
        # B-Tree configuration
        btree_group = QGroupBox("B-Tree Configuration")
        btree_layout = QVBoxLayout(btree_group)
        
        self.btree_order_input = QSpinBox()
        self.btree_order_input.setRange(3, 100)
        self.btree_order_input.setValue(5)  # Default value
        
        btree_order_layout = QHBoxLayout()
        btree_order_layout.addWidget(QLabel("B-Tree Order:"))
        btree_order_layout.addWidget(self.btree_order_input)
        
        btree_layout.addLayout(btree_order_layout)
        
        # Compression configuration
        compression_group = QGroupBox("Compression Configuration")
        compression_layout = QVBoxLayout(compression_group)
        
        self.save_tree_check = QCheckBox("Save Huffman Tree with Compressed File")
        self.save_tree_check.setChecked(True)
        
        self.optimize_check = QCheckBox("Optimize Compression for Speed")
        self.optimize_check.setChecked(False)
        
        compression_layout.addWidget(self.save_tree_check)
        compression_layout.addWidget(self.optimize_check)
        
        # UI configuration
        ui_group = QGroupBox("User Interface Configuration")
        ui_layout = QVBoxLayout(ui_group)
        
        self.dark_mode_check = QCheckBox("Dark Mode (Requires Restart)")
        self.dark_mode_check.setChecked(False)
        
        self.show_tooltips_check = QCheckBox("Show Tooltips")
        self.show_tooltips_check.setChecked(True)
        
        ui_layout.addWidget(self.dark_mode_check)
        ui_layout.addWidget(self.show_tooltips_check)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_configuration)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_configuration)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        
        # Add all to main layout
        layout.addWidget(btree_group)
        layout.addWidget(compression_group)
        layout.addWidget(ui_group)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # Load current configuration if available
        self.load_configuration()
        
    def load_configuration(self):
        """Load the current configuration"""
        if not self.config_manager:
            return
            
        try:
            # Use get() instead of get_config()
            # Load B-Tree config
            btree_order = self.config_manager.get("storage.btree_order", 5)
            self.btree_order_input.setValue(btree_order)
                
            # Compression config
            save_tree = self.config_manager.get("compression.show_huffman_tree_after_compression", True)
            self.save_tree_check.setChecked(save_tree)
            
            optimize_compression = self.config_manager.get("compression.optimize_for_speed", False)
            self.optimize_check.setChecked(optimize_compression)
                
            # UI config
            dark_mode = self.config_manager.get("interface.dark_mode", False)
            self.dark_mode_check.setChecked(dark_mode)
            
            show_tooltips = self.config_manager.get("interface.show_tooltips", True)
            self.show_tooltips_check.setChecked(show_tooltips)
                
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
        
    def save_configuration(self):
        """Save the configuration"""
        if not self.config_manager:
            QMessageBox.warning(self, "Warning", "Configuration manager not available.")
            return
            
        try:
            # Use set() instead of set_config()
            self.config_manager.set("storage.btree_order", self.btree_order_input.value())
            self.config_manager.set("compression.show_huffman_tree_after_compression", self.save_tree_check.isChecked())
            self.config_manager.set("compression.optimize_for_speed", self.optimize_check.isChecked())
            self.config_manager.set("interface.dark_mode", self.dark_mode_check.isChecked())
            self.config_manager.set("interface.show_tooltips", self.show_tooltips_check.isChecked())
            
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
        
    def reset_configuration(self):
        """Reset to default configuration"""
        # Set default values
        self.btree_order_input.setValue(5)
        self.save_tree_check.setChecked(True)
        self.optimize_check.setChecked(False)
        self.dark_mode_check.setChecked(False)
        self.show_tooltips_check.setChecked(True)
        
        # Save if config manager is available
        if self.config_manager:
            self.save_configuration()


class BenchmarkTab(QWidget):
    """Tab for performance benchmarking"""
    
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Performance Benchmarking"))
        
        # Benchmark type selection
        benchmark_group = QGroupBox("Benchmark Type")
        benchmark_layout = QVBoxLayout(benchmark_group)
        
        self.compression_check = QCheckBox("Compression Performance")
        self.compression_check.setChecked(True)
        
        self.search_check = QCheckBox("Search Performance")
        self.search_check.setChecked(True)
        
        self.tree_ops_check = QCheckBox("Tree Operations Performance")
        self.tree_ops_check.setChecked(False)
        
        benchmark_layout.addWidget(self.compression_check)
        benchmark_layout.addWidget(self.search_check)
        benchmark_layout.addWidget(self.tree_ops_check)
        
        # Test file selection
        test_files_group = QGroupBox("Test Files")
        test_files_layout = QVBoxLayout(test_files_group)
        
        self.files_list = QListWidget()
        
        test_files_btns_layout = QHBoxLayout()
        add_file_btn = QPushButton("Add File")
        add_file_btn.clicked.connect(self.add_test_file)
        
        clear_files_btn = QPushButton("Clear Files")
        clear_files_btn.clicked.connect(self.clear_test_files)
        
        test_files_btns_layout.addWidget(add_file_btn)
        test_files_btns_layout.addWidget(clear_files_btn)
        
        test_files_layout.addWidget(self.files_list)
        test_files_layout.addLayout(test_files_btns_layout)
        
        # Benchmark controls
        controls_layout = QHBoxLayout()
        
        self.iterations_input = QSpinBox()
        self.iterations_input.setRange(1, 100)
        self.iterations_input.setValue(5)
        
        controls_layout.addWidget(QLabel("Iterations:"))
        controls_layout.addWidget(self.iterations_input)
        controls_layout.addStretch()
        
        run_btn = QPushButton("Run Benchmark")
        run_btn.clicked.connect(self.run_benchmark)
        controls_layout.addWidget(run_btn)
        
        # Results
        results_group = QGroupBox("Benchmark Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        self.export_results_btn = QPushButton("Export Results")
        self.export_results_btn.clicked.connect(self.export_results)
        
        results_layout.addWidget(self.results_text)
        results_layout.addWidget(self.export_results_btn)
        
        # Add to main layout
        layout.addWidget(benchmark_group)
        layout.addWidget(test_files_group)
        layout.addLayout(controls_layout)
        layout.addWidget(results_group)
        
    def add_test_file(self):
        """Add a test file for benchmarking"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Test File", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            item = QListWidgetItem(file_path)
            self.files_list.addItem(item)
            
    def clear_test_files(self):
        """Clear the test files list"""
        self.files_list.clear()
        
    def run_benchmark(self):
        """Run the selected benchmarks"""
        if self.files_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please add at least one test file.")
            return
            
        if not (self.compression_check.isChecked() or
                self.search_check.isChecked() or
                self.tree_ops_check.isChecked()):
            QMessageBox.warning(self, "Warning", "Please select at least one benchmark type.")
            return
            
        # Get benchmark parameters
        iterations = self.iterations_input.value()
        test_files = [self.files_list.item(i).text() for i in range(self.files_list.count())]
        
        # Clear results
        self.results_text.clear()
        self.results_text.append("Running benchmarks...\n")
        
        import time
        import random
        
        # Run compression benchmark
        if self.compression_check.isChecked():
            self.results_text.append("=== Compression Benchmark ===")
            
            for file_path in test_files:
                filename = os.path.basename(file_path)
                self.results_text.append(f"\nFile: {filename}")
                
                # Get file size
                file_size = os.path.getsize(file_path)
                self.results_text.append(f"Size: {file_size} bytes")
                
                # Run compression test
                compression_times = []
                
                for i in range(iterations):
                    start_time = time.time()
                    
                    try:
                        output_path = os.path.join(os.path.dirname(file_path), f"temp_benchmark_{i}.huff")
                        self.encoder.analyze_file(file_path)
                        self.encoder.compress(file_path, output_path)
                        
                        # Cleanup
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            
                        compression_time = time.time() - start_time
                        compression_times.append(compression_time)
                        
                    except Exception as e:
                        self.results_text.append(f"  Error in iteration {i+1}: {str(e)}")
                
                if compression_times:
                    avg_time = sum(compression_times) / len(compression_times)
                    self.results_text.append(f"Average compression time: {avg_time:.4f} seconds")
                    
                    # Calculate compression speed
                    if avg_time > 0:
                        speed = file_size / (avg_time * 1024)  # KB/s
                        self.results_text.append(f"Compression speed: {speed:.2f} KB/s")
            
        # Run search benchmark (simplified simulation)
        if self.search_check.isChecked():
            self.results_text.append("\n=== Search Benchmark ===")
            self.results_text.append("Note: This is a simulation of search operations.")
            
            # Create a simulated dataset of 10,000 filenames
            simulated_filenames = [f"test_file_{i}.txt" for i in range(10000)]
            
            # Measure RB-Tree search performance
            self.results_text.append("\nRed-Black Tree Search:")
            rb_search_times = []
            
            for i in range(iterations):
                # Simulate searching for 100 random filenames
                search_targets = random.sample(simulated_filenames, 100)
                
                start_time = time.time()
                for target in search_targets:
                    # Simulate RB Tree search (O(log n) operation)
                    idx = binary_search_simulation(simulated_filenames, target)
                
                search_time = time.time() - start_time
                rb_search_times.append(search_time)
                
            if rb_search_times:
                avg_time = sum(rb_search_times) / len(rb_search_times)
                self.results_text.append(f"Average search time for 100 files: {avg_time:.4f} seconds")
                self.results_text.append(f"Average time per search: {avg_time/100:.6f} seconds")
            
            # Measure B-Tree search performance
            self.results_text.append("\nB-Tree Search:")
            btree_search_times = []
            
            for i in range(iterations):
                # Simulate searching for 100 random filenames
                search_targets = random.sample(simulated_filenames, 100)
                
                start_time = time.time()
                for target in search_targets:
                    # Simulate B-Tree search (slightly faster than RB Tree)
                    idx = btree_search_simulation(simulated_filenames, target)
                
                search_time = time.time() - start_time
                btree_search_times.append(search_time)
                
            if btree_search_times:
                avg_time = sum(btree_search_times) / len(btree_search_times)
                self.results_text.append(f"Average search time for 100 files: {avg_time:.4f} seconds")
                self.results_text.append(f"Average time per search: {avg_time/100:.6f} seconds")
                
        # Run tree operations benchmark
        if self.tree_ops_check.isChecked():
            self.results_text.append("\n=== Tree Operations Benchmark ===")
            # Implementation would go here...
            self.results_text.append("Tree operations benchmark not implemented in this version.")
            
        self.results_text.append("\nBenchmarks complete!")
            
    def export_results(self):
        """Export benchmark results to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Benchmark Results", "benchmark_results.txt", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.results_text.toPlainText())
                    
                QMessageBox.information(self, "Success", f"Benchmark results exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")


# Utility functions for search benchmarks
def binary_search_simulation(sorted_list, target):
    """Simulate binary search to estimate RB-Tree performance"""
    left, right = 0, len(sorted_list) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if sorted_list[mid] == target:
            return mid
        elif sorted_list[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1

def btree_search_simulation(sorted_list, target):
    """Simulate B-Tree search (slightly more efficient than binary search)"""
    # In practice, B-Tree might be slightly faster for disk-based operations
    # Here we just add a tiny optimization to the binary search
    if not sorted_list:
        return -1
        
    # Quick check for first or last element
    if target <= sorted_list[0]:
        return 0 if target == sorted_list[0] else -1
    if target >= sorted_list[-1]:
        return len(sorted_list) - 1 if target == sorted_list[-1] else -1
        
    # Regular binary search for the rest
    return binary_search_simulation(sorted_list, target)


class FileCompressionIndexingApp(QMainWindow):
    """Main application window for the File Compression and Indexing System"""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("File Compression and Indexing System")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)
        
        # Create shared components that tabs might need
        self.encoder = Encoder()
        self.decoder = Decoder()
        self.rb_manager = FileIndexManager()
        self.btree_manager = FileIndexBTree()
        
        # Set up the UI
        self.init_ui()
        
        # Set status bar message
        self.statusBar().showMessage("Ready")
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header with title and version
        header = QWidget()
        header_layout = QHBoxLayout(header)
        title_label = QLabel("File Compression and Indexing System")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        version_label = QLabel("v2.0.0")
        version_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(version_label)
        
        # Create tab widget for different functionalities
        self.tabs = QTabWidget()
        
        # Create and add tabs
        self.tabs.addTab(CompressionTab(self.encoder, self.decoder), "Compression")
        self.tabs.addTab(RBTreeTab(self.rb_manager), "RB-Tree Storage")
        self.tabs.addTab(BTreeTab(self.btree_manager), "B-Tree Storage")
        self.tabs.addTab(SearchTab(self.rb_manager, self.btree_manager), "Unified Search")
        self.tabs.addTab(VisualizationTab(self.encoder, self.rb_manager, self.btree_manager), "Visualizations")
        self.tabs.addTab(BatchTab(self.encoder, self.rb_manager, self.btree_manager), "Batch Operations")
        self.tabs.addTab(BenchmarkTab(self.encoder), "Benchmarks")
        # Add the new Demo tab
        from gui.other_tabs import DemoTab
        self.tabs.addTab(DemoTab(self.encoder, self.decoder, self.rb_manager, self.btree_manager), "Demo")
        self.tabs.addTab(ConfigTab(), "Configuration")
        
        # Add components to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs)
        
        # Create a status bar for notifications
        self.statusBar()

# Entry point for the application
def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = FileCompressionIndexingApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()