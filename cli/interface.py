"""
Main CLI interface for the File Compression and Indexing System
"""
from cli.handler_base import MenuHandler
from cli.compression_handler import CompressionHandler
from cli.rbtree_handler import RBTreeHandler
from cli.btree_handler import BTreeHandler
from cli.visualization_handler import VisualizationHandler
from cli.batch_handler import BatchHandler
from cli.config_handler import ConfigurationHandler
from cli.benchmark_handler import BenchmarkHandler
from cli.search_handler import SearchHandler

class UserInterface(MenuHandler):
    """
    Main user interface for the File Compression and Indexing System
    """
    def __init__(self):
        """Initialize the user interface"""
        super().__init__()
        self.title = "File Compression and Indexing System"
        self.options = [
            "Compression Operations",
            "Storage Operations (Red-Black Tree)",
            "Advanced Storage Operations (B-Tree)",
            "Unified Search",
            "Visualization Tools",
            "Help",
            "Batch Operations", 
            "Configuration Settings",
            "Performance Benchmarking"
        ]
        
        # Initialize specialized handlers
        self.compression_handler = CompressionHandler()
        self.rbtree_handler = RBTreeHandler()
        self.btree_handler = BTreeHandler()
        self.search_handler = SearchHandler()
        self.visualization_handler = VisualizationHandler()
        self.batch_handler = BatchHandler()
        self.config_handler = ConfigurationHandler()
        self.benchmark_handler = BenchmarkHandler()
        
        # Flag to track if the application is running
        self.running = True
    
    def _handle_option_1(self):
        """Handle compression operations"""
        self.compression_handler.run()
    
    def _handle_option_2(self):
        """Handle Red-Black Tree operations"""
        self.rbtree_handler.run()
    
    def _handle_option_3(self):
        """Handle B-Tree operations"""
        self.btree_handler.run()
    
    def _handle_option_4(self):
        """Handle unified search operations"""
        self.search_handler.run()
    
    def _handle_option_5(self):
        """Handle visualization operations"""
        self.visualization_handler.run()
    
    def _handle_option_6(self):
        """Display help information"""
        self._print_help()
    
    def _handle_option_7(self):
        """Handle batch operations"""
        self.batch_handler.run()
    
    def _handle_option_8(self):
        """Handle configuration settings"""
        self.config_handler.run()
    
    def _handle_option_9(self):
        """Handle performance benchmarking"""
        self.benchmark_handler.run()
    
    def _print_help(self):
        """Print help information"""
        print("\nHelp Information")
        print("=" * 50)
        print("\nFile Compression and Indexing System")
        print("-" * 35)
        print("This application allows you to compress text files using Huffman coding")
        print("and organize them using Red-Black Tree and B-Tree for efficient searching.")
        
        print("\nMain Components:")
        print("-" * 16)
        
        print("\n1. Compression Operations:")
        print("   - Compress files using Huffman coding")
        print("   - Decompress previously compressed files")
        print("   - Analyze files for compression potential")
        print("   - View and export file character frequencies")
        
        print("\n2. Storage Operations (Red-Black Tree):")
        print("   - Basic file indexing for quick search")
        print("   - Search for files by name or partial name")
        print("   - Manage file metadata")
        
        print("\n3. Advanced Storage Operations (B-Tree):")
        print("   - Enhanced file indexing with better performance for large datasets")
        print("   - Range-based file searching")
        print("   - File categorization and category-based searching")
        
        print("\n4. Unified Search:")
        print("   - Search across both Red-Black Tree and B-Tree storage structures")
        print("   - Search by filename, content or advanced filters")
        print("   - Export search results and view detailed file information")
        
        print("\n5. Visualization Tools:")
        print("   - View tree structures (Huffman, Red-Black, B-Tree)")
        print("   - Compare compression performance across files")
        print("   - Generate and export visualizations")
        
        print("\n6. Batch Operations:")
        print("   - Process multiple files with a single command")
        print("   - Batch compression of directory contents")
        print("   - Batch indexing with optional categorization")
        
        print("\n7. Configuration Settings:")
        print("   - Manage application configuration and settings")
        print("   - View and edit configuration files")
        print("   - Reset settings to default values")
        
        print("\n8. Performance Benchmarking:")
        print("   - Evaluate compression and indexing performance")
        print("   - Generate performance reports")
        print("   - Compare different algorithms and settings")
        
        print("\nPress Enter to continue...")
        input()
    
    def start(self):
        """Start the user interface"""
        print("\nWelcome to the File Compression and Indexing System")
        print("Version 2.0.0 - Enhanced Modular Architecture")
        
        while self.running:
            self.display_menu()
            choice = input(f"Enter your choice (0-{len(self.options)}): ")
            
            if choice == '0':
                self.running = False
                print("\nThank you for using the File Compression and Indexing System. Goodbye!")
            else:
                self.handle_choice(choice)
    
    def handle_choice(self, choice):
        """Handle user choice"""
        handler_method = None
        
        try:
            # Convert choice to integer
            choice_index = int(choice)
            
            # Check if choice is valid
            if choice_index >= 1 and choice_index <= len(self.options):
                # Get the handler method
                handler_method = getattr(self, f"_handle_option_{choice_index}")
            else:
                print("\nInvalid choice. Please try again.")
                
            # Call the handler method if it exists
            if handler_method:
                try:
                    handler_method()
                except Exception as e:
                    print(f"\nAn error occurred while processing your request: {str(e)}")
                    print("Please try again or contact support if the issue persists.")
        except ValueError:
            print("\nInvalid input. Please enter a number.")