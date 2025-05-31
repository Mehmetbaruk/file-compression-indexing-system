"""
Handler for performance benchmarking operations
"""
import os
import time
import json
import datetime
from cli.handler_base import MenuHandler
from compression.huffman import Encoder
from storage.btree import BTree
from storage.red_black_tree import RedBlackTree

class BenchmarkHandler(MenuHandler):
    """
    Handler for performance benchmarking operations
    """
    def __init__(self):
        """Initialize the benchmark handler"""
        super().__init__()
        self.title = "Performance Benchmarking"
        self.options = [
            "Benchmark compression performance",
            "Benchmark storage performance",
            "Compare B-Tree vs Red-Black Tree",
            "Run comprehensive benchmark suite",
            "View previous benchmark results"
        ]
        
        # Create benchmark results directory if it doesn't exist
        self.results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark_results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Initialize components needed for benchmarking
        self.encoder = Encoder()
    
    def _handle_option_1(self):
        """Benchmark compression performance"""
        print("\nCompression Performance Benchmark")
        print("=" * 50)
        
        # Get file for benchmarking
        file_path = input("Enter path to text file for benchmarking: ").strip()
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return
            
        # Check if file is too large
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        if file_size > 100:  # 100 MB limit
            confirm = input(f"Warning: File is {file_size:.2f} MB. Benchmarking large files may take time. Continue? (y/n): ").lower()
            if confirm != 'y':
                return
                
        print(f"\nRunning compression benchmarks on {file_path} ({file_size:.2f} MB)...")
        
        # Prepare results
        results = {
            "file_path": file_path,
            "file_size_bytes": os.path.getsize(file_path),
            "timestamp": datetime.datetime.now().isoformat(),
            "compression": {}
        }
        
        # Test Huffman compression
        print("\n1. Testing Huffman Compression...")
        start_time = time.time()
        output_file = os.path.join(self.results_dir, "benchmark_temp.bin")
        
        try:
            # Compress the file
            self.encoder.compress(file_path, output_file)
            
            # Calculate metrics
            compression_time = time.time() - start_time
            original_size = self.encoder.original_size
            compressed_size = self.encoder.compressed_size
            compression_ratio = self.encoder.get_compression_ratio()
            
            # Store results
            results["compression"]["huffman"] = {
                "compression_time_seconds": compression_time,
                "original_size_bytes": original_size,
                "compressed_size_bytes": compressed_size,
                "compression_ratio_percent": compression_ratio,
                "throughput_mb_per_second": (original_size / 1024 / 1024) / compression_time
            }
            
            # Display results
            print(f"  • Time taken: {compression_time:.4f} seconds")
            print(f"  • Compression ratio: {compression_ratio:.2f}%")
            print(f"  • Throughput: {results['compression']['huffman']['throughput_mb_per_second']:.2f} MB/s")
            
            # Clean up temp file
            if os.path.exists(output_file):
                os.remove(output_file)
                
        except Exception as e:
            print(f"Error during compression benchmark: {str(e)}")
        
        # Save benchmark results
        self._save_benchmark_results(results, "compression_benchmark")
        
        # Ask if user wants to compare with other files
        add_file = input("\nWould you like to benchmark another file for comparison? (y/n): ").lower()
        if add_file == 'y':
            self._handle_option_1()  # Recursive call to benchmark another file
        else:
            print("\nBenchmark completed. Press Enter to continue...")
            input()
    
    def _handle_option_2(self):
        """Benchmark storage performance"""
        print("\nStorage Performance Benchmark")
        print("=" * 50)
        
        # Ask which tree type to benchmark
        print("Select tree type to benchmark:")
        print("1. Red-Black Tree")
        print("2. B-Tree")
        print("3. Both (for comparison)")
        
        tree_choice = input("Enter your choice (1-3): ").strip()
        
        # Get number of items to insert
        try:
            n_items = int(input("Enter number of items to insert (recommended 1000-100000): "))
            if n_items <= 0:
                print("Number of items must be positive.")
                return
        except ValueError:
            print("Please enter a valid number.")
            return
        
        # Prepare benchmark results
        results = {
            "n_items": n_items,
            "timestamp": datetime.datetime.now().isoformat(),
            "storage": {}
        }
        
        # Benchmark Red-Black Tree if selected
        if tree_choice in ['1', '3']:
            print(f"\nBenchmarking Red-Black Tree with {n_items} items...")
            rb_tree = RedBlackTree()
            
            # Measure insertion time
            start_time = time.time()
            for i in range(n_items):
                key = f"key_{i}"
                value = f"value_{i}"
                rb_tree.insert(key, value)
            insertion_time = time.time() - start_time
            
            # Measure search time (for 100 random items)
            start_time = time.time()
            for _ in range(100):
                i = int(n_items * 0.9 * ((_ % 10) / 10))  # Distribute searches across the tree
                key = f"key_{i}"
                rb_tree.search(key)
            search_time = time.time() - start_time
            
            # Store results
            results["storage"]["rbtree"] = {
                "insertion_time_seconds": insertion_time,
                "search_time_seconds": search_time,
                "insertions_per_second": n_items / insertion_time,
                "searches_per_second": 100 / search_time
            }
            
            # Display results
            print(f"  • Insertion time: {insertion_time:.4f} seconds ({results['storage']['rbtree']['insertions_per_second']:.2f} items/second)")
            print(f"  • Search time (100 lookups): {search_time:.4f} seconds ({results['storage']['rbtree']['searches_per_second']:.2f} lookups/second)")
        
        # Benchmark B-Tree if selected
        if tree_choice in ['2', '3']:
            print(f"\nBenchmarking B-Tree with {n_items} items...")
            # Instantiate B-Tree using its correct parameter name
            b_tree = BTree(t=5)
            
            # Measure insertion time
            start_time = time.time()
            for i in range(n_items):
                key = f"key_{i}"
                value = f"value_{i}"
                b_tree.insert(key, value)
            insertion_time = time.time() - start_time
            
            # Measure search time (for 100 random items)
            start_time = time.time()
            for _ in range(100):
                i = int(n_items * 0.9 * ((_ % 10) / 10))
                key = f"key_{i}"
                b_tree.search(key)
            search_time = time.time() - start_time
            
            # Store results
            # Safely calculate rates to avoid division by zero
            insert_rate = n_items / insertion_time if insertion_time > 0 else 0
            search_rate = 100 / search_time if search_time > 0 else 0
            results["storage"]["btree"] = {
                "insertion_time_seconds": insertion_time,
                "search_time_seconds": search_time,
                "insertions_per_second": insert_rate,
                "searches_per_second": search_rate
            }
            
            # Display results
            print(f"  • Insertion time: {insertion_time:.4f} seconds ({results['storage']['btree']['insertions_per_second']:.2f} items/second)")
            print(f"  • Search time (100 lookups): {search_time:.4f} seconds ({results['storage']['btree']['searches_per_second']:.2f} lookups/second)")
        
        # If both were benchmarked, show comparison
        if tree_choice == '3':
            print("\nComparison:")
            
            rb_insert = results["storage"]["rbtree"]["insertions_per_second"]
            b_insert = results["storage"]["btree"]["insertions_per_second"]
            
            rb_search = results["storage"]["rbtree"]["searches_per_second"]
            b_search = results["storage"]["btree"]["searches_per_second"]
            
            insert_winner = "Red-Black Tree" if rb_insert > b_insert else "B-Tree"
            search_winner = "Red-Black Tree" if rb_search > b_search else "B-Tree"
            
            insert_factor = rb_insert / b_insert if rb_insert > b_insert else b_insert / rb_insert
            search_factor = rb_search / b_search if rb_search > b_search else b_search / rb_search
            
            print(f"  • Insertion performance: {insert_winner} is {insert_factor:.2f}x faster")
            print(f"  • Search performance: {search_winner} is {search_factor:.2f}x faster")
        
        # Save benchmark results
        self._save_benchmark_results(results, "storage_benchmark")
        
        print("\nBenchmark completed. Press Enter to continue...")
        input()
    
    def _handle_option_3(self):
        """Compare B-Tree vs Red-Black Tree with varying data sizes"""
        print("\nB-Tree vs Red-Black Tree Comparison")
        print("=" * 50)
        
        # Define sizes for comparison
        sizes = [100, 1000, 10000]
        
        try:
            # Ask for custom sizes
            custom_sizes = input("Enter custom data sizes to compare (comma-separated numbers, e.g. 500,5000,50000) or press Enter for defaults: ")
            if custom_sizes.strip():
                sizes = [int(s.strip()) for s in custom_sizes.split(",")]
        except ValueError:
            print("Invalid input for sizes, using defaults.")
        
        # Prepare results
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "comparison": {}
        }
        
        # For each size, benchmark both tree types
        for size in sizes:
            print(f"\nTesting with {size} items...")
            results["comparison"][size] = {"rbtree": {}, "btree": {}}
            
            # Test Red-Black Tree
            print("  Testing Red-Black Tree...")
            rb_tree = RedBlackTree()
            
            # Insertion test
            start_time = time.time()
            for i in range(size):
                rb_tree.insert(f"key_{i}", f"value_{i}")
            rb_insert_time = time.time() - start_time
            
            # Search test
            start_time = time.time()
            for i in range(0, size, max(1, size // 100)):  # Test ~100 searches distributed across tree
                rb_tree.search(f"key_{i}")
            rb_search_time = time.time() - start_time
            
            # Range search test (if size is big enough)
            if size >= 1000:
                start_key = f"key_{size//4}"
                end_key = f"key_{3*size//4}"
                start_time = time.time()
                if hasattr(rb_tree, 'range_search'):
                    rb_tree.range_search(start_key, end_key)
                rb_range_time = time.time() - start_time
            else:
                rb_range_time = 0
            
            # Store RB-Tree results
            results["comparison"][size]["rbtree"] = {
                "insertion_time": rb_insert_time,
                "search_time": rb_search_time,
                "range_search_time": rb_range_time,
                "insertions_per_second": size / rb_insert_time
            }
            
            # Test B-Tree
            print("  Testing B-Tree...")
            b_tree = BTree(t=5)
            
            # Insertion test
            start_time = time.time()
            for i in range(size):
                b_tree.insert(f"key_{i}", f"value_{i}")
            b_insert_time = time.time() - start_time
            
            # Search test
            start_time = time.time()
            for i in range(0, size, max(1, size // 100)):
                b_tree.search(f"key_{i}")
            b_search_time = time.time() - start_time
            
            # Range search test (if size is big enough)
            if size >= 1000:
                start_key = f"key_{size//4}"
                end_key = f"key_{3*size//4}"
                start_time = time.time()
                if hasattr(b_tree, 'range_search'):
                    b_tree.range_search(start_key, end_key)
                b_range_time = time.time() - start_time
            else:
                b_range_time = 0
            
            # Store B-Tree results
            # Safely calculate rates to avoid division by zero
            b_insert_rate = 10000 / b_insert_time if b_insert_time > 0 else 0
            b_search_rate = 1000 / b_search_time if b_search_time > 0 else 0
            results["comparison"][size]["btree"] = {
                "insertion_time": b_insert_time,
                "search_time": b_search_time,
                "range_search_time": b_range_time,
                "insertions_per_second": b_insert_rate
            }
            
            # Show comparison for this size
            print(f"  Results for {size} items:")
            print(f"    • Insertion: RB-Tree {rb_insert_time:.4f}s vs B-Tree {b_insert_time:.4f}s")
            print(f"    • Search: RB-Tree {rb_search_time:.4f}s vs B-Tree {b_search_time:.4f}s")
            if size >= 1000:
                print(f"    • Range Search: RB-Tree {rb_range_time:.4f}s vs B-Tree {b_range_time:.4f}s")
            
            # Show winner
            rb_insert_rate = results["comparison"][size]["rbtree"]["insertions_per_second"]
            b_insert_rate = results["comparison"][size]["btree"]["insertions_per_second"]
            insert_winner = "Red-Black Tree" if rb_insert_rate > b_insert_rate else "B-Tree"
            
            print(f"    • Best for insertion at size {size}: {insert_winner}")
        
        # Save benchmark results
        self._save_benchmark_results(results, "tree_comparison")
        
        # Show overall recommendation
        print("\nOverall recommendation based on benchmarks:")
        
        # Calculate average performance difference across all sizes
        rb_advantage = 0
        b_advantage = 0
        
        for size in sizes:
            rb_insert = results["comparison"][size]["rbtree"]["insertions_per_second"]
            b_insert = results["comparison"][size]["btree"]["insertions_per_second"]
            
            if rb_insert > b_insert:
                rb_advantage += 1
            else:
                b_advantage += 1
        
        if rb_advantage > b_advantage:
            print("• Red-Black Tree performed better overall for your test cases.")
            print("• Best for: Frequent insertions and single-item lookups.")
        elif b_advantage > rb_advantage:
            print("• B-Tree performed better overall for your test cases.")
            print("• Best for: Large datasets and range queries.")
        else:
            print("• Both tree structures performed similarly in your tests.")
            print("• Red-Black Trees are generally better for frequent updates.")
            print("• B-Trees are generally better for large datasets and range queries.")
        
        print("\nBenchmark completed. Press Enter to continue...")
        input()
    
    def _handle_option_4(self):
        """Run comprehensive benchmark suite"""
        print("\nComprehensive Benchmark Suite")
        print("=" * 50)
        print("This will run a series of benchmarks across all system components.")
        print("Note: This may take several minutes to complete.")
        
        confirm = input("Do you want to proceed? (y/n): ").lower()
        if confirm != 'y':
            return
        
        # Prepare results container
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "comprehensive": {
                "compression": {},
                "storage": {}
            }
        }
        
        # 1. Test file operations with sample data (create a temporary test file)
        print("\n1. Creating sample data for testing...")
        test_file = os.path.join(self.results_dir, "benchmark_sample.txt")
        
        try:
            with open(test_file, 'w') as f:
                # Write ~100KB of test data
                for i in range(1000):
                    f.write(f"This is test line {i} with some random data: {''.join(['x' for _ in range(100)])}\n")
            
            file_size = os.path.getsize(test_file)
            print(f"  • Created {file_size / 1024:.2f} KB sample file")
            
            # 2. Benchmark compression
            print("\n2. Benchmarking compression...")
            output_file = os.path.join(self.results_dir, "benchmark_sample.bin")
            
            # Time compression
            start_time = time.time()
            self.encoder.compress(test_file, output_file)
            compression_time = time.time() - start_time
            
            # Get metrics
            original_size = self.encoder.original_size
            compressed_size = self.encoder.compressed_size
            compression_ratio = self.encoder.get_compression_ratio()
            
            # Store results
            results["comprehensive"]["compression"] = {
                "file_size_bytes": original_size,
                "compressed_size_bytes": compressed_size,
                "compression_ratio": compression_ratio,
                "compression_time_seconds": compression_time,
                "throughput_mb_per_second": (original_size / 1024 / 1024) / compression_time
            }
            
            print(f"  • Compression time: {compression_time:.4f} seconds")
            print(f"  • Compression ratio: {compression_ratio:.2f}%")
            
            # 3. Benchmark Red-Black Tree operations
            print("\n3. Benchmarking Red-Black Tree operations...")
            rb_tree = RedBlackTree()
            
            # Insertion benchmark (10,000 items)
            start_time = time.time()
            for i in range(10000):
                rb_tree.insert(f"key_{i}", f"value_{i}")
            rb_insert_time = time.time() - start_time
            
            # Search benchmark (1,000 lookups)
            start_time = time.time()
            for i in range(0, 10000, 10):
                rb_tree.search(f"key_{i}")
            rb_search_time = time.time() - start_time
            
            # Store results
            results["comprehensive"]["storage"]["rbtree"] = {
                "insertion_time_seconds": rb_insert_time,
                "search_time_seconds": rb_search_time,
                "insertions_per_second": 10000 / rb_insert_time,
                "searches_per_second": 1000 / rb_search_time
            }
            
            print(f"  • RB-Tree insertion time (10,000 items): {rb_insert_time:.4f} seconds")
            print(f"  • RB-Tree search time (1,000 lookups): {rb_search_time:.4f} seconds")
            
            # 4. Benchmark B-Tree operations
            print("\n4. Benchmarking B-Tree operations...")
            b_tree = BTree(t=5)
            
            # Insertion benchmark (10,000 items)
            start_time = time.time()
            for i in range(10000):
                b_tree.insert(f"key_{i}", f"value_{i}")
            b_insert_time = time.time() - start_time
            
            # Search benchmark (1,000 lookups)
            start_time = time.time()
            for i in range(0, 10000, 10):
                b_tree.search(f"key_{i}")
            b_search_time = time.time() - start_time
            
            # Store results
            # Safely calculate rates to avoid division by zero
            b_insert_rate = 10000 / b_insert_time if b_insert_time > 0 else 0
            b_search_rate = 1000 / b_search_time if b_search_time > 0 else 0
            results["comprehensive"]["storage"]["btree"] = {
                "insertion_time_seconds": b_insert_time,
                "search_time_seconds": b_search_time,
                "insertions_per_second": b_insert_rate,
                "searches_per_second": b_search_rate
            }
            
            print(f"  • B-Tree insertion time (10,000 items): {b_insert_time:.4f} seconds")
            print(f"  • B-Tree search time (1,000 lookups): {b_search_time:.4f} seconds")
            
            # Clean up temporary files
            if os.path.exists(test_file):
                os.remove(test_file)
            if os.path.exists(output_file):
                os.remove(output_file)
                
        except Exception as e:
            print(f"Error during comprehensive benchmarks: {str(e)}")
        
        # Save benchmark results
        self._save_benchmark_results(results, "comprehensive_benchmark")
        
        # Show summary
        print("\nBenchmark Summary:")
        print("-" * 30)
        print(f"• Compression throughput: {results['comprehensive']['compression']['throughput_mb_per_second']:.2f} MB/s")
        print(f"• RB-Tree insertions: {results['comprehensive']['storage']['rbtree']['insertions_per_second']:.2f} items/s")
        print(f"• B-Tree insertions: {results['comprehensive']['storage']['btree']['insertions_per_second']:.2f} items/s")
        
        rb_search_speed = results["comprehensive"]["storage"]["rbtree"]["searches_per_second"]
        b_search_speed = results["comprehensive"]["storage"]["btree"]["searches_per_second"]
        search_winner = "Red-Black Tree" if rb_search_speed > b_search_speed else "B-Tree"
        
        print(f"• Fastest search performance: {search_winner}")
        
        print("\nBenchmark completed. Press Enter to continue...")
        input()
    
    def _handle_option_5(self):
        """View previous benchmark results"""
        print("\nPrevious Benchmark Results")
        print("=" * 50)
        
        # List available benchmark files
        benchmark_files = []
        for file in os.listdir(self.results_dir):
            if file.endswith('.json'):
                benchmark_files.append(file)
        
        if not benchmark_files:
            print("No benchmark results found.")
            print("\nPress Enter to continue...")
            input()
            return
        
        print("Available benchmark results:")
        for i, file in enumerate(benchmark_files, start=1):
            # Get file creation time
            file_path = os.path.join(self.results_dir, file)
            created = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            
            print(f"{i}. {file} (Created: {created.strftime('%Y-%m-%d %H:%M:%S')})")
        
        print("0. Back")
        
        try:
            choice = int(input(f"Enter your choice (0-{len(benchmark_files)}): "))
            
            if 1 <= choice <= len(benchmark_files):
                file_path = os.path.join(self.results_dir, benchmark_files[choice - 1])
                self._display_benchmark_file(file_path)
            elif choice != 0:
                print(f"Invalid choice. Please select 0-{len(benchmark_files)}")
        except ValueError:
            print("Please enter a number.")
        
        print("\nPress Enter to continue...")
        input()
    
    def _display_benchmark_file(self, file_path):
        """
        Display the contents of a benchmark file
        
        Args:
            file_path: Path to the benchmark file
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"\nBenchmark Results from {os.path.basename(file_path)}")
            print("=" * 50)
            
            # Check what type of benchmark this is
            if "compression" in data and isinstance(data["compression"], dict):
                print("Compression Benchmark Results:")
                print(f"• File: {data.get('file_path', 'Unknown')}")
                print(f"• Size: {data.get('file_size_bytes', 0) / 1024:.2f} KB")
                print(f"• Date: {data.get('timestamp', 'Unknown')}")
                
                huffman = data["compression"].get("huffman", {})
                if huffman:
                    print("\nHuffman Compression:")
                    print(f"• Time: {huffman.get('compression_time_seconds', 0):.4f} seconds")
                    print(f"• Ratio: {huffman.get('compression_ratio_percent', 0):.2f}%")
                    print(f"• Throughput: {huffman.get('throughput_mb_per_second', 0):.2f} MB/s")
            
            elif "storage" in data and isinstance(data["storage"], dict):
                print("Storage Benchmark Results:")
                print(f"• Items: {data.get('n_items', 0)}")
                print(f"• Date: {data.get('timestamp', 'Unknown')}")
                
                rbtree = data["storage"].get("rbtree", {})
                btree = data["storage"].get("btree", {})
                
                if rbtree:
                    print("\nRed-Black Tree Performance:")
                    print(f"• Insertion time: {rbtree.get('insertion_time_seconds', 0):.4f} seconds")
                    print(f"• Insertions per second: {rbtree.get('insertions_per_second', 0):.2f}")
                    print(f"• Search time: {rbtree.get('search_time_seconds', 0):.4f} seconds")
                    print(f"• Searches per second: {rbtree.get('searches_per_second', 0):.2f}")
                
                if btree:
                    print("\nB-Tree Performance:")
                    print(f"• Insertion time: {btree.get('insertion_time_seconds', 0):.4f} seconds")
                    print(f"• Insertions per second: {btree.get('insertions_per_second', 0):.2f}")
                    print(f"• Search time: {btree.get('search_time_seconds', 0):.4f} seconds")
                    print(f"• Searches per second: {btree.get('searches_per_second', 0):.2f}")
            
            elif "comparison" in data and isinstance(data["comparison"], dict):
                print("Tree Comparison Results:")
                print(f"• Date: {data.get('timestamp', 'Unknown')}")
                
                for size, results in data["comparison"].items():
                    print(f"\nResults for {size} items:")
                    
                    rbtree = results.get("rbtree", {})
                    btree = results.get("btree", {})
                    
                    if rbtree and btree:
                        rb_insert = rbtree.get("insertion_time", 0)
                        b_insert = btree.get("insertion_time", 0)
                        
                        rb_search = rbtree.get("search_time", 0)
                        b_search = btree.get("search_time", 0)
                        
                        print(f"• Insertion: RB-Tree {rb_insert:.4f}s vs B-Tree {b_insert:.4f}s")
                        print(f"• Search: RB-Tree {rb_search:.4f}s vs B-Tree {b_search:.4f}s")
                        
                        if "range_search_time" in rbtree and "range_search_time" in btree:
                            rb_range = rbtree["range_search_time"]
                            b_range = btree["range_search_time"]
                            print(f"• Range Search: RB-Tree {rb_range:.4f}s vs B-Tree {b_range:.4f}s")
            
            elif "comprehensive" in data and isinstance(data["comprehensive"], dict):
                print("Comprehensive Benchmark Results:")
                print(f"• Date: {data.get('timestamp', 'Unknown')}")
                
                comp = data["comprehensive"].get("compression", {})
                if comp:
                    print("\nCompression Performance:")
                    print(f"• Ratio: {comp.get('compression_ratio', 0):.2f}%")
                    print(f"• Throughput: {comp.get('throughput_mb_per_second', 0):.2f} MB/s")
                
                rbtree = data["comprehensive"].get("storage", {}).get("rbtree", {})
                btree = data["comprehensive"].get("storage", {}).get("btree", {})
                
                if rbtree:
                    print("\nRed-Black Tree Performance:")
                    print(f"• Insertions per second: {rbtree.get('insertions_per_second', 0):.2f}")
                    print(f"• Searches per second: {rbtree.get('searches_per_second', 0):.2f}")
                
                if btree:
                    print("\nB-Tree Performance:")
                    print(f"• Insertions per second: {btree.get('insertions_per_second', 0):.2f}")
                    print(f"• Searches per second: {btree.get('searches_per_second', 0):.2f}")
            
            else:
                # Just dump the JSON in a readable format
                print(json.dumps(data, indent=2))
            
        except Exception as e:
            print(f"Error loading benchmark file: {str(e)}")
    
    def _save_benchmark_results(self, results, prefix):
        """
        Save benchmark results to a JSON file
        
        Args:
            results: Dictionary containing benchmark results
            prefix: Prefix for the filename
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        file_path = os.path.join(self.results_dir, filename)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n✓ Benchmark results saved to {file_path}")
        except Exception as e:
            print(f"\nError saving benchmark results: {str(e)}")