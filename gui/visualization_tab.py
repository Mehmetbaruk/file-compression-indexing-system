import os
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QFileDialog, QGroupBox, QSplitter,
                            QTextEdit, QTabWidget, QMessageBox, QSpacerItem,
                            QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont

class TreeCanvas(FigureCanvas):
    """Canvas for rendering tree visualizations using matplotlib"""
    
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def clear_plot(self):
        """Clear the plot area"""
        self.axes.clear()
        self.draw()
        
    def plot_tree(self, G, pos=None, node_colors=None, title=None):
        """Plot a tree using networkx and matplotlib"""
        self.axes.clear()
        
        if pos is None:
            # Use a simple hierarchical layout
            pos = self.hierarchical_layout(G)
            
        if node_colors is None:
            node_colors = ['lightblue'] * len(G.nodes())
            
        nx.draw(G, pos, with_labels=True, arrows=False, 
                node_color=node_colors, node_size=800, font_size=10,
                font_weight='bold', ax=self.axes)
        
        if title:
            self.axes.set_title(title)
            
        self.fig.tight_layout()
        self.draw()
    
    def hierarchical_layout(self, G):
        """Custom hierarchical layout for trees"""
        pos = {}
        
        # Find root node (the one with no parents or lowest in-degree)
        roots = [n for n in G.nodes() if G.in_degree(n) == 0]
        if not roots:
            # Try to find a good starting point
            roots = [sorted(G.nodes(), key=lambda n: G.in_degree(n))[0]]
        
        # Build tree level by level using BFS
        visited = set(roots)
        current_level = roots
        y_offset = 0
        
        while current_level:
            # Position nodes in this level
            x_offset = -(len(current_level) - 1) / 2
            for i, node in enumerate(current_level):
                pos[node] = (x_offset + i, -y_offset)
            
            # Get the next level
            next_level = []
            for node in current_level:
                # Add unvisited children
                children = [child for child in G.successors(node) if child not in visited]
                next_level.extend(children)
                visited.update(children)
            
            current_level = next_level
            y_offset += 1
        
        return pos
        
    def plot_comparison(self, labels, values, title="Compression Ratio Comparison"):
        """Plot a bar chart comparing compression ratios"""
        self.axes.clear()
        
        self.axes.bar(labels, values, color='skyblue')
        self.axes.set_title(title)
        self.axes.set_ylabel('Compression Ratio (%)')
        self.axes.set_ylim(0, 100)
        
        # Add value labels on top of each bar
        for i, v in enumerate(values):
            self.axes.text(i, v + 1, f"{v:.2f}%", ha='center')
            
        self.fig.tight_layout()
        self.draw()

class VisualizationTab(QWidget):
    """Tab for visualizing tree structures and compression ratios"""
    
    def __init__(self, encoder, rb_manager, btree_manager):
        super().__init__()
        
        self.encoder = encoder
        self.rb_manager = rb_manager
        self.btree_manager = btree_manager
        self.huffman_file_path = None
        self.files_to_compare = []
        
        # Initialize the UI components
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create visualization type selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Visualization Type:"))
        
        self.vis_type_combo = QComboBox()
        self.vis_type_combo.addItems([
            "Huffman Tree Visualization",
            "Red-Black Tree Visualization",
            "B-Tree Visualization",
            "Compression Ratio Comparison"
        ])
        self.vis_type_combo.currentIndexChanged.connect(self.on_visualization_changed)
        selector_layout.addWidget(self.vis_type_combo)
        selector_layout.addStretch()
        
        # Create control panel for each visualization type
        self.control_stack = QTabWidget()
        self.control_stack.setTabPosition(QTabWidget.South)
        self.control_stack.setTabBarAutoHide(True)
        
        # Create the visualization canvas
        self.tree_canvas = TreeCanvas(self, width=10, height=8)
        
        # Create text output area for raw text representation
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setFixedHeight(200)
        self.text_output.setFont(QFont("Courier New", 10))
        
        # Create control panels for each visualization type
        self.huffman_panel = self.create_huffman_panel()
        self.rbtree_panel = self.create_rbtree_panel()
        self.btree_panel = self.create_btree_panel()
        self.comparison_panel = self.create_comparison_panel()
        
        # Add panels to the control stack
        self.control_stack.addTab(self.huffman_panel, "Huffman Controls")
        self.control_stack.addTab(self.rbtree_panel, "RB-Tree Controls")
        self.control_stack.addTab(self.btree_panel, "B-Tree Controls")
        self.control_stack.addTab(self.comparison_panel, "Comparison Controls")
        
        # Create buttons panel
        buttons_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Visualization")
        self.export_btn.clicked.connect(self.export_visualization)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_visualization)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.export_btn)
        buttons_layout.addWidget(self.clear_btn)
        
        # Add all components to the main layout
        layout.addLayout(selector_layout)
        layout.addWidget(self.tree_canvas)
        layout.addWidget(QLabel("Text Representation:"))
        layout.addWidget(self.text_output)
        layout.addWidget(self.control_stack)
        layout.addLayout(buttons_layout)
        
        # Show initial visualization type
        self.control_stack.setCurrentIndex(0)
        
    def create_huffman_panel(self):
        """Create control panel for Huffman tree visualization"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        file_select_btn = QPushButton("Select File")
        file_select_btn.clicked.connect(self.select_file_for_huffman)
        
        visualize_btn = QPushButton("Visualize Huffman Tree")
        visualize_btn.clicked.connect(self.visualize_huffman_tree)
        
        layout.addWidget(file_select_btn)
        layout.addWidget(visualize_btn)
        layout.addStretch()
        
        return panel
        
    def create_rbtree_panel(self):
        """Create control panel for Red-Black tree visualization"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        visualize_btn = QPushButton("Visualize Red-Black Tree")
        visualize_btn.clicked.connect(self.visualize_rb_tree)
        
        layout.addWidget(visualize_btn)
        layout.addStretch()
        
        return panel
    
    def create_btree_panel(self):
        """Create control panel for B-Tree visualization"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        visualize_btn = QPushButton("Visualize B-Tree")
        visualize_btn.clicked.connect(self.visualize_btree)
        
        add_test_btn = QPushButton("Add Test File")
        add_test_btn.clicked.connect(self.add_test_file_to_btree)
        
        layout.addWidget(visualize_btn)
        layout.addWidget(add_test_btn)
        layout.addStretch()
        
        return panel
    
    def create_comparison_panel(self):
        """Create control panel for compression ratio comparison"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        add_file_btn = QPushButton("Add File")
        add_file_btn.clicked.connect(self.add_file_for_comparison)
        
        compare_btn = QPushButton("Compare")
        compare_btn.clicked.connect(self.compare_compression_ratios)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_comparison)
        
        self.comparison_status = QLabel("No files added for comparison")
        
        layout.addWidget(add_file_btn)
        layout.addWidget(compare_btn)
        layout.addWidget(reset_btn)
        layout.addStretch()
        layout.addWidget(self.comparison_status)
        
        return panel
    
    def on_visualization_changed(self, index):
        """Handle visualization type change"""
        self.control_stack.setCurrentIndex(index)
        self.clear_visualization()
    
    def select_file_for_huffman(self):
        """Select a file for Huffman tree visualization"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Text File", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.huffman_file_path = file_path
            self.visualize_huffman_tree()
    
    def visualize_huffman_tree(self):
        """Generate and display Huffman tree visualization"""
        if not hasattr(self, 'huffman_file_path') or not self.huffman_file_path:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return
            
        try:
            # Check if the file exists
            if not os.path.exists(self.huffman_file_path):
                QMessageBox.warning(self, "Warning", f"File not found: {self.huffman_file_path}")
                return
                
            # Check if this is a binary file that shouldn't be visualized
            _, file_extension = os.path.splitext(self.huffman_file_path)
            if file_extension.lower() in ['.huff', '.bin'] and not self.is_huffman_file(self.huffman_file_path):
                QMessageBox.warning(self, "Warning", 
                    "This appears to be a binary file but not a valid Huffman compressed file.\n"
                    "Visualization may not be meaningful.")
                    
            # Get the Huffman tree from the encoder
            self.encoder.analyze_file(self.huffman_file_path)
            huffman_tree = self.encoder.get_tree()
            
            if huffman_tree is None:
                QMessageBox.warning(self, "Warning", "No Huffman tree available. Please select a valid file.")
                return
            
            # Convert Huffman tree to networkx graph for visualization
            G = nx.DiGraph()
            node_colors = []
            
            # Helper function to build the graph
            def build_graph(node, node_id=0, parent_id=None):
                if node is None:
                    return node_id
                
                # Add the current node
                if hasattr(node, 'symbol') and node.symbol is not None:
                    # Handle special characters for display
                    symbol_display = str(node.symbol)
                    if len(symbol_display) > 10:  # Truncate very long symbols
                        symbol_display = symbol_display[:10] + "..."
                    elif symbol_display in ['\n', '\r', '\t']:
                        symbol_display = {'\\n': 'LF', '\\r': 'CR', '\\t': 'TAB'}[repr(node.symbol)[1:-1]]
                    
                    # Leaf node
                    label = f"{symbol_display}:{node.freq}"
                    G.add_node(node_id, label=label)
                    node_colors.append("lightgreen")  # Different color for leaf nodes
                else:
                    # Internal node
                    label = f"{node.freq}"
                    G.add_node(node_id, label=label)
                    node_colors.append("lightblue")
                
                # Connect to parent if it exists
                if parent_id is not None:
                    G.add_edge(parent_id, node_id)
                
                # Process left child
                next_id = node_id + 1
                if hasattr(node, 'left') and node.left:
                    next_id = build_graph(node.left, next_id, node_id)
                
                # Process right child
                if hasattr(node, 'right') and node.right:
                    next_id = build_graph(node.right, next_id, node_id)
                
                return next_id
            
            try:
                build_graph(huffman_tree)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error building graph visualization: {str(e)}\n"
                                  "Showing text representation only.")
                # Continue to show text representation even if graph fails
            
            if G.number_of_nodes() > 0:
                # Draw the tree
                try:
                    self.tree_canvas.plot_tree(G, None, node_colors, 
                                             f"Huffman Tree for {os.path.basename(self.huffman_file_path)}")
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Error drawing tree: {str(e)}")
            
            # Show text representation
            try:
                if hasattr(self.encoder, 'get_tree_visualization'):
                    tree_text = self.encoder.get_tree_visualization()
                    if tree_text:
                        self.text_output.setText(tree_text)
                    else:
                        self.text_output.setText("Tree visualization not available.")
                else:
                    self.text_output.setText("Tree text visualization not available.")
            except Exception as e:
                self.text_output.setText(f"Error getting text visualization: {str(e)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error visualizing Huffman tree: {str(e)}")
            
    def is_huffman_file(self, file_path):
        """Check if a file is a valid Huffman compressed file"""
        try:
            with open(file_path, 'rb') as file:
                import pickle
                # Try to read the frequency dictionary that should be at the beginning
                pickle.load(file)
                return True
        except:
            return False
    
    def visualize_rb_tree(self):
        """Generate and display Red-Black tree visualization"""
        try:
            # Check if the rb_manager has visualization method
            if not hasattr(self.rb_manager, 'get_tree_visualization'):
                QMessageBox.warning(self, "Warning", "Red-Black Tree visualization not supported by the manager.")
                return
                
            # Get the Red-Black Tree visualization
            tree_text = self.rb_manager.get_tree_visualization()
            if not tree_text or tree_text == "Red-Black Tree is empty.":
                QMessageBox.information(self, "Information", "Red-Black Tree is currently empty. Please add some files first.")
                return
            
            # Show text representation
            self.text_output.setText(tree_text)
            
            # Parse tree structure from the text and create a graph
            G = nx.DiGraph()
            node_colors = []
            
            # Simple parser for RB tree text format
            # This is a simplified approach and might need adaptation based on actual format
            lines = tree_text.strip().split('\n')
            nodes = {}
            node_id_counter = 0
            
            for line in lines:
                if "->" in line:  # Edge definition line
                    parts = line.split("->")
                    if len(parts) == 2:
                        parent = parts[0].strip()
                        child = parts[1].strip()
                        
                        # Add nodes if they don't exist
                        if parent not in nodes:
                            nodes[parent] = node_id_counter
                            node_id_counter += 1
                            G.add_node(nodes[parent], label=parent)
                            # Color RED nodes red, others black
                            if "RED" in parent:
                                node_colors.append("red")
                            else:
                                node_colors.append("black")
                                
                        if child not in nodes:
                            nodes[child] = node_id_counter
                            node_id_counter += 1
                            G.add_node(nodes[child], label=child)
                            if "RED" in child:
                                node_colors.append("red")
                            else:
                                node_colors.append("black")
                                
                        G.add_edge(nodes[parent], nodes[child])
            
            if G.number_of_nodes() > 0:
                # Draw the tree
                self.tree_canvas.plot_tree(G, None, node_colors, "Red-Black Tree Structure")
            else:
                # If parsing failed, show a message
                self.tree_canvas.clear_plot()
                QMessageBox.warning(self, "Warning", "Could not parse tree structure from text representation.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error visualizing Red-Black tree: {str(e)}")
    
    def visualize_btree(self):
        """Generate and display B-Tree visualization"""
        try:
            # Check if the btree_manager has necessary methods
            if not hasattr(self.btree_manager, 'list_all_files'):
                QMessageBox.warning(self, "Warning", "B-Tree visualization not fully supported by the manager.")
                return
                
            # Check if there are any files in the B-Tree
            files = self.btree_manager.list_all_files() if hasattr(self.btree_manager, 'list_all_files') else []
            if not files:
                result = QMessageBox.question(self, "Empty B-Tree", 
                                            "The B-Tree is currently empty. Would you like to add a test file for visualization?",
                                            QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.Yes:
                    self.add_test_file_to_btree()
                return
            
            # Get the B-Tree visualization
            if hasattr(self.btree_manager, 'get_tree_visualization'):
                tree_text = self.btree_manager.get_tree_visualization()
            else:
                tree_text = "B-Tree visualization not available in text format."
            
            # Show text representation
            self.text_output.setText(tree_text)
            
            # Parse tree structure and create a graph
            G = nx.DiGraph()
            node_colors = []
            
            # Simple parsing logic for B-Tree text representation
            # Adapt this based on your actual B-Tree text format
            try:
                lines = tree_text.strip().split('\n')
                node_dict = {}
                node_id_counter = 0
                
                current_node_id = None
                
                for line in lines:
                    line = line.strip()
                    
                    # Parse node
                    if line.startswith("Node ["):
                        node_name = line
                        if node_name not in node_dict:
                            node_dict[node_name] = node_id_counter
                            node_id_counter += 1
                            G.add_node(node_dict[node_name], label=node_name)
                            node_colors.append("lightblue")
                            
                        current_node_id = node_dict[node_name]
                    
                    # Parse child reference
                    elif line.startswith("Child:") and current_node_id is not None:
                        child_ref = line.replace("Child:", "").strip()
                        if child_ref not in node_dict:
                            node_dict[child_ref] = node_id_counter
                            node_id_counter += 1
                            G.add_node(node_dict[child_ref], label=child_ref)
                            node_colors.append("lightgreen")
                            
                        G.add_edge(current_node_id, node_dict[child_ref])
                
                if G.number_of_nodes() > 0:
                    # Draw the tree
                    self.tree_canvas.plot_tree(G, None, node_colors, "B-Tree Structure")
                else:
                    # If parsing failed, create a sample visualization
                    self.create_sample_btree_visualization(files)
            except:
                # If parsing fails, create a sample visualization
                self.create_sample_btree_visualization(files)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error visualizing B-Tree: {str(e)}")
    
    def create_sample_btree_visualization(self, files):
        """Create a sample B-Tree visualization when parsing fails"""
        G = nx.DiGraph()
        node_colors = []
        
        # Create root
        root_id = 0
        G.add_node(root_id, label="Root")
        node_colors.append("orange")
        
        # Add file nodes
        for i, file_info in enumerate(files[:10]):  # Limit to 10 files
            file_id = i + 1
            
            if isinstance(file_info, dict) and 'name' in file_info:
                filename = file_info['name']
            elif isinstance(file_info, str):
                filename = file_info
            else:
                filename = f"File {i}"
                
            G.add_node(file_id, label=filename)
            G.add_edge(root_id, file_id)
            node_colors.append("lightgreen")
        
        self.tree_canvas.plot_tree(G, None, node_colors, "B-Tree Sample Visualization")
        self.text_output.append("\n\nNote: This is a simplified representation as the actual tree structure could not be parsed.")
    
    def add_test_file_to_btree(self):
        """Add a test file to B-Tree for visualization purposes"""
        try:
            test_filename = "test_file.txt"
            test_filepath = os.path.join(os.getcwd(), test_filename)
            
            # Create a test file if it doesn't exist
            if not os.path.exists(test_filepath):
                with open(test_filepath, 'w') as f:
                    f.write("This is a test file for B-Tree visualization.")
            
            # Get file size for metadata
            file_size = os.path.getsize(test_filepath)
            
            # Add the file to B-Tree
            if hasattr(self.btree_manager, 'add_file'):
                # Use the add_file method of the manager if available
                self.btree_manager.add_file(test_filename, test_filepath, file_size, False, ["test"])
            elif hasattr(self.btree_manager, 'btree') and hasattr(self.btree_manager.btree, 'insert'):
                # For direct access to the btree - BTree requires both key and value
                metadata = {
                    'filepath': test_filepath,
                    'size': file_size,
                    'compression_status': False,
                    'categories': ["test"],
                    'created_at': str(datetime.now())
                }
                self.btree_manager.btree.insert(test_filename, metadata)
            else:
                QMessageBox.warning(self, "Warning", "The B-Tree manager does not support adding files.")
                return
                
            QMessageBox.information(self, "Success", "Test file added to B-Tree. You can now visualize the tree.")
            
            # Visualize the tree
            self.visualize_btree()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding test file: {str(e)}")
            # Print detailed error for debugging
            import traceback
            print(f"Detailed error: {traceback.format_exc()}")
    
    def add_file_for_comparison(self):
        """Add a file for compression ratio comparison"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Text File", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.files_to_compare.append(file_path)
            self.comparison_status.setText(f"{len(self.files_to_compare)} files added for comparison")
    
    def compare_compression_ratios(self):
        """Compare compression ratios of selected files"""
        if not self.files_to_compare:
            QMessageBox.warning(self, "Warning", "No files added for comparison. Please add at least one file.")
            return
        
        try:
            labels = []
            ratios = []
            error_files = []
            
            for file_path in self.files_to_compare:
                filename = os.path.basename(file_path)
                
                try:
                    # Check if file exists
                    if not os.path.exists(file_path):
                        error_files.append(f"{filename} (file not found)")
                        continue
                        
                    # Skip files that are likely binary and not suitable for compression analysis
                    _, file_extension = os.path.splitext(file_path)
                    if file_extension.lower() in ['.huff', '.bin', '.zip', '.rar', '.7z', '.gz', '.jpg', '.png', '.mp3', '.mp4']:
                        # Ask if user wants to include this file despite being likely already compressed
                        result = QMessageBox.question(
                            self, "Compressed File", 
                            f"{filename} appears to be a binary or already compressed file. Include it anyway?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if result == QMessageBox.No:
                            continue
                    
                    # Analyze the file
                    self.encoder.analyze_file(file_path)
                    
                    # For visualization purposes, estimate compression potential
                    # This is not the same as the actual compression ratio after compression
                    if hasattr(self.encoder, 'get_compression_potential'):
                        ratio = self.encoder.get_compression_potential()
                    else:
                        # We need to estimate compression potential
                        # A simple heuristic based on character frequency distribution
                        freq_data = self.encoder.huffman_tree.freq_dict
                        if freq_data:
                            # More uniform distribution = less compressible
                            unique_chars = len(freq_data)
                            total_chars = sum(freq_data.values())
                            
                            # Shannon entropy calculation (simplified)
                            import math
                            entropy = 0
                            for freq in freq_data.values():
                                probability = freq / total_chars
                                entropy -= probability * math.log2(probability)
                                
                            # Estimate compression ratio based on entropy
                            # 8 bits is the typical size of a byte without compression
                            theoretical_bits_per_char = entropy
                            estimated_ratio = (1 - theoretical_bits_per_char / 8) * 100
                            ratio = max(0, min(100, estimated_ratio))  # Clamp between 0-100%
                        else:
                            # Default fallback
                            ratio = 30  # Arbitrary default
                    
                    labels.append(filename)
                    ratios.append(ratio)
                    
                except Exception as e:
                    error_files.append(f"{filename} ({str(e)})")
            
            if not labels:
                if error_files:
                    QMessageBox.warning(self, "Error", f"Could not analyze any files. Errors:\n" + "\n".join(error_files))
                else:
                    QMessageBox.warning(self, "Warning", "No files available for comparison.")
                return
                
            # Plot the comparison
            self.tree_canvas.plot_comparison(labels, ratios)
            
            # Show text representation
            text_output = "Compression Ratio Comparison:\n"
            text_output += "=" * 40 + "\n"
            
            for i, filename in enumerate(labels):
                text_output += f"{filename}: {ratios[i]:.2f}%\n"
                
            if error_files:
                text_output += "\nFiles with errors:\n"
                text_output += "\n".join(error_files)
                
            self.text_output.setText(text_output)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error comparing compression ratios: {str(e)}")
            import traceback
            print(f"Detailed error: {traceback.format_exc()}")
    
    def reset_comparison(self):
        """Reset the comparison data"""
        self.files_to_compare = []
        self.comparison_status.setText("No files added for comparison")
        self.clear_visualization()
    
    def export_visualization(self):
        """Export the current visualization to a file"""
        # Get the current visualization type
        vis_type = self.vis_type_combo.currentText()
        
        # Determine default filename based on visualization type
        default_filename = "visualization.png"
        if "Huffman" in vis_type:
            default_filename = "huffman_tree.png"
        elif "Red-Black" in vis_type:
            default_filename = "rbtree_visualization.png"
        elif "B-Tree" in vis_type:
            default_filename = "btree_visualization.png"
        elif "Compression" in vis_type:
            default_filename = "compression_comparison.png"
        
        # Get file path for saving
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Visualization", default_filename,
            "PNG Images (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Save the figure to file
            self.tree_canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            
            # Also export text representation if available
            text_content = self.text_output.toPlainText()
            if text_content:
                text_file_path = os.path.splitext(file_path)[0] + ".txt"
                with open(text_file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
            
            QMessageBox.information(self, "Success", f"Visualization exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting visualization: {str(e)}")
    
    def clear_visualization(self):
        """Clear the current visualization"""
        self.tree_canvas.clear_plot()
        self.text_output.clear()