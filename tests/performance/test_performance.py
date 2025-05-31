"""
Performance Tests for File Compression and Indexing System
Tests system performance with various file sizes and operations
"""
import unittest
import os
import sys
import time
import tempfile
import random
import json
import string
from datetime import datetime
from pathlib import Path

# Add project root to the path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from compression.huffman import HuffmanEncoder, HuffmanDecoder
from storage.red_black_tree import FileIndexManager
from storage.btree import BTree, FileIndexBTree

# Test configuration constants
TEST_FILE_SIZES = {
    'tiny': 1024,           # 1 KB
    'small': 10 * 1024,     # 10 KB
    'medium': 100 * 1024,   # 100 KB
    'large': 1024 * 1024    # 1 MB
}

def get_benchmark_results_path():
    """Get a path for storing benchmark results"""
    results_dir = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'test_results' / 'benchmarks'
    results_dir.mkdir(exist_ok=True)
    return results_dir

def generate_test_dataset(file_count=5, size_category='small'):
    """Generate a test dataset of files with specified size

    Args:
        file_count: Number of files to generate
        size_category: Size category ('tiny', 'small', 'medium', 'large')
    
    Returns:
        List of file paths
    """
    file_paths = []
    file_size = TEST_FILE_SIZES.get(size_category, 1024)
    
    for i in range(file_count):
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=f"_{size_category}_{i}.txt")
        os.close(fd)
        
        # Generate random content
        chars = string.ascii_letters + string.digits + string.punctuation + ' ' * 10
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            # For larger files, write in chunks
            chunk_size = min(10 * 1024, file_size)  # 10KB chunks or smaller
            remaining = file_size
            
            while remaining > 0:
                write_size = min(chunk_size, remaining)
                content = ''.join(random.choice(chars) for _ in range(write_size))
                f.write(content)
                remaining -= write_size
        
        file_paths.append(temp_path)
        
    return file_paths

class PerformanceTest(unittest.TestCase):
    """Performance test cases for the system"""
    
    def setUp(self):
        """Set up test environment"""
        self.encoder = HuffmanEncoder()
        self.decoder = HuffmanDecoder()
        self.rb_tree_manager = FileIndexManager()
        self.btree_manager = FileIndexBTree(min_degree=5)
        
        # Store test files for cleanup
        self.test_files = []
        self.compressed_files = []
        
        # For benchmark results
        self.benchmark_results = {
            'timestamp': datetime.now().isoformat(),
            'compression': {},
            'indexing': {},
            'search': {},
            'summary': {}
        }
        
    def tearDown(self):
        """Clean up test environment"""
        # Remove test files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
                    
        # Remove compressed files
        for file_path in self.compressed_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # Save benchmark results
        results_dir = get_benchmark_results_path()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = results_dir / f"benchmark_{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.benchmark_results, f, indent=2)
            
    def _benchmark_compression(self, size_category, file_count=3):
        """Benchmark compression performance for a given file size category"""
        # Generate test files
        print(f"\nGenerating {file_count} {size_category} files for compression benchmark...")
        files = generate_test_dataset(file_count, size_category)
        self.test_files.extend(files)
        
        results = {
            'file_size': TEST_FILE_SIZES[size_category],
            'file_count': file_count,
            'compression': {
                'total_time': 0,
                'avg_time': 0,
                'total_original_size': 0,
                'total_compressed_size': 0,
                'avg_compression_ratio': 0,
                'compression_ratios': []
            },
            'decompression': {
                'total_time': 0,
                'avg_time': 0
            }
        }
        
        # Test compression
        print(f"Benchmarking compression for {size_category} files...")
        
        for file_path in files:
            # Measure compression time
            start_time = time.time()
            compressed_file = self.encoder.compress_file(file_path)
            compression_time = time.time() - start_time
            
            self.compressed_files.append(compressed_file)
            
            # Collect statistics
            original_size = os.path.getsize(file_path)
            compressed_size = os.path.getsize(compressed_file)
            compression_ratio = self.encoder.get_compression_ratio()
            
            results['compression']['total_time'] += compression_time
            results['compression']['total_original_size'] += original_size
            results['compression']['total_compressed_size'] += compressed_size
            results['compression']['compression_ratios'].append(compression_ratio)
            
            print(f"  - {os.path.basename(file_path)}: {compression_time:.4f}s, {compression_ratio:.2f}% compression ratio")
            
            # Measure decompression time
            start_time = time.time()
            decompressed_file = self.decoder.decompress_file(compressed_file)
            decompression_time = time.time() - start_time
            
            results['decompression']['total_time'] += decompression_time
            
            # Skip content verification for performance tests
            print(f"  - Decompression time: {decompression_time:.4f}s")
            
            # Clean up decompressed file
            if os.path.exists(decompressed_file):
                try:
                    os.remove(decompressed_file)
                except:
                    pass  # Ignore errors during cleanup
        
        # Calculate averages
        results['compression']['avg_time'] = results['compression']['total_time'] / file_count
        results['compression']['avg_compression_ratio'] = sum(results['compression']['compression_ratios']) / file_count
        results['decompression']['avg_time'] = results['decompression']['total_time'] / file_count
        
        print(f"Compression benchmark for {size_category} files completed:")
        print(f"  - Avg compression time: {results['compression']['avg_time']:.4f}s")
        print(f"  - Avg compression ratio: {results['compression']['avg_compression_ratio']:.2f}%")
        print(f"  - Avg decompression time: {results['decompression']['avg_time']:.4f}s")
        
        return results
    
    def _benchmark_indexing(self, size_category, file_count=50):
        """Benchmark indexing performance for a given file size category"""
        # Generate file names and metadata
        print(f"\nBenchmarking indexing with {file_count} {size_category} files...")
        
        files = []
        for i in range(file_count):
            filename = f"test_file_{size_category}_{i}.txt"
            filepath = f"/path/to/{filename}"
            size = random.randint(1000, TEST_FILE_SIZES[size_category])
            compressed = random.choice([True, False])
            
            files.append({
                'filename': filename,
                'filepath': filepath,
                'size': size,
                'compressed': compressed
            })
        
        results = {
            'file_count': file_count,
            'red_black_tree': {
                'insertion_time': 0,
                'search_time': 0,
                'deletion_time': 0
            },
            'btree': {
                'insertion_time': 0,
                'search_time': 0,
                'deletion_time': 0
            }
        }
        
        # Benchmark Red-Black Tree
        print("Benchmarking Red-Black Tree indexing...")
        
        # Insertion
        start_time = time.time()
        for file_info in files:
            self.rb_tree_manager.add_file(
                file_info['filename'],
                file_info['filepath'],
                file_info['size'],
                file_info['compressed']
            )
        results['red_black_tree']['insertion_time'] = time.time() - start_time
        
        # Search
        start_time = time.time()
        for file_info in files:
            result = self.rb_tree_manager.search_file(file_info['filename'])
            assert result is not None, f"File {file_info['filename']} not found in Red-Black Tree"
        results['red_black_tree']['search_time'] = time.time() - start_time
        
        # Deletion
        start_time = time.time()
        for file_info in files:
            self.rb_tree_manager.remove_file(file_info['filename'])
        results['red_black_tree']['deletion_time'] = time.time() - start_time
        
        # Benchmark B-Tree
        print("Benchmarking B-Tree indexing...")
        
        # Insertion
        start_time = time.time()
        for file_info in files:
            self.btree_manager.add_file(
                file_info['filename'],
                file_info['filepath'],
                file_info['size'],
                file_info['compressed']
            )
        results['btree']['insertion_time'] = time.time() - start_time
        
        # Search
        start_time = time.time()
        for file_info in files:
            result = self.btree_manager.search_file(file_info['filename'])
            assert result is not None, f"File {file_info['filename']} not found in B-Tree"
        results['btree']['search_time'] = time.time() - start_time
        
        # Deletion
        start_time = time.time()
        for file_info in files:
            self.btree_manager.remove_file(file_info['filename'])
        results['btree']['deletion_time'] = time.time() - start_time
        
        print("Indexing benchmark completed:")
        print(f"  - RB-Tree insertion: {results['red_black_tree']['insertion_time']:.4f}s")
        print(f"  - RB-Tree search: {results['red_black_tree']['search_time']:.4f}s")
        print(f"  - RB-Tree deletion: {results['red_black_tree']['deletion_time']:.4f}s")
        print(f"  - B-Tree insertion: {results['btree']['insertion_time']:.4f}s")
        print(f"  - B-Tree search: {results['btree']['search_time']:.4f}s")
        print(f"  - B-Tree deletion: {results['btree']['deletion_time']:.4f}s")
        
        return results
    
    def test_performance_benchmarks(self):
        """Run comprehensive performance benchmarks"""
        # Compression benchmarks for different file sizes
        for size in ['tiny', 'small', 'medium']:
            self.benchmark_results['compression'][size] = self._benchmark_compression(size)
        
        # Only run large file test if specifically enabled
        if os.environ.get('ENABLE_LARGE_FILE_TEST') == '1':
            self.benchmark_results['compression']['large'] = self._benchmark_compression('large', file_count=1)
        
        # Indexing benchmarks with different file counts
        self.benchmark_results['indexing']['small'] = self._benchmark_indexing('small', file_count=50)
        self.benchmark_results['indexing']['medium'] = self._benchmark_indexing('medium', file_count=100)
        
        # Calculate summary statistics
        self.benchmark_results['summary'] = {
            'total_compression_time': sum(
                results['compression']['total_time'] 
                for results in self.benchmark_results['compression'].values()
            ),
            'avg_compression_ratio': sum(
                results['compression']['avg_compression_ratio'] 
                for results in self.benchmark_results['compression'].values()
            ) / len(self.benchmark_results['compression']),
            'rbtree_vs_btree': {
                'insertion_ratio': self._calculate_tree_ratio('insertion_time'),
                'search_ratio': self._calculate_tree_ratio('search_time'),
                'deletion_ratio': self._calculate_tree_ratio('deletion_time')
            }
        }
        
        print("\nPerformance benchmarks summary:")
        print(f"Average compression ratio: {self.benchmark_results['summary']['avg_compression_ratio']:.2f}%")
        print("Red-Black Tree vs B-Tree performance ratios:")
        for operation, ratio in self.benchmark_results['summary']['rbtree_vs_btree'].items():
            faster = "RB-Tree" if ratio < 1 else "B-Tree"
            print(f"  - {operation}: {abs(1-ratio):.2f}x faster with {faster}")
    
    def _calculate_tree_ratio(self, operation):
        """Calculate performance ratio between Red-Black Tree and B-Tree for an operation"""
        rbtree_total = sum(
            result['red_black_tree'][operation] for result in self.benchmark_results['indexing'].values()
        )
        btree_total = sum(
            result['btree'][operation] for result in self.benchmark_results['indexing'].values()
        )
        
        if btree_total == 0:
            return 0  # Avoid division by zero
            
        return rbtree_total / btree_total

if __name__ == '__main__':
    unittest.main()