"""
Test Configuration for File Compression and Indexing System
Provides configuration settings and utilities for all test types
"""

import os
import tempfile
import random
import string
import logging
from pathlib import Path

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Test data directories
TEST_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = TEST_DIR / "test_data"
TEST_RESULTS_DIR = TEST_DIR / "test_results"

# Test file sizes for performance testing
TEST_FILE_SIZES = {
    "tiny": 1024,        # 1 KB
    "small": 10240,      # 10 KB
    "medium": 102400,    # 100 KB
    "large": 1048576,    # 1 MB
    "huge": 10485760     # 10 MB
}

def generate_test_text_file(size_category="small", output_path=None):
    """
    Generate a text file of specified size for testing
    
    Args:
        size_category (str): Size category ('tiny', 'small', 'medium', 'large', 'huge')
        output_path (str): Path to save the file (creates a temp file if None)
    
    Returns:
        Path: Path object to the generated file
    """
    size = TEST_FILE_SIZES.get(size_category, TEST_FILE_SIZES["small"])
    
    if not output_path:
        # Create a temporary file
        fd, output_path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        output_path = Path(output_path)
    else:
        output_path = Path(output_path)
    
    # Generate random text content
    chars = string.ascii_letters + string.digits + string.punctuation + ' \n\t'
    
    # For more realistic content with varying character frequencies
    # Use more spaces and common letters
    char_weights = {}
    for c in chars:
        if c in 'etaoinshrdlu ':
            char_weights[c] = 5  # More common
        elif c in string.ascii_lowercase:
            char_weights[c] = 2
        else:
            char_weights[c] = 1
    
    weighted_chars = []
    for c, weight in char_weights.items():
        weighted_chars.extend([c] * weight)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        remaining_size = size
        while remaining_size > 0:
            # Generate paragraph-like text for realism
            paragraph_size = min(random.randint(50, 500), remaining_size)
            paragraph = ''.join(random.choice(weighted_chars) for _ in range(paragraph_size))
            f.write(paragraph)
            f.write('\n\n')
            remaining_size -= paragraph_size + 2
    
    return output_path

def generate_test_dataset(base_dir=TEST_DATA_DIR):
    """
    Generate a complete test dataset with various file sizes
    
    Args:
        base_dir (Path): Directory to save the generated files
    
    Returns:
        dict: Dictionary mapping file size categories to file paths
    """
    base_dir = Path(base_dir)
    base_dir.mkdir(exist_ok=True)
    
    dataset = {}
    for size_name in TEST_FILE_SIZES.keys():
        file_path = base_dir / f"test_{size_name}.txt"
        generate_test_text_file(size_name, file_path)
        dataset[size_name] = file_path
    
    return dataset

def get_benchmark_results_path():
    """Get a path for storing benchmark results"""
    results_dir = TEST_RESULTS_DIR / "benchmarks"
    results_dir.mkdir(exist_ok=True)
    return results_dir

# Test configuration constants
UNIT_TEST_TIMEOUT = 5  # seconds
INTEGRATION_TEST_TIMEOUT = 30  # seconds
PERFORMANCE_TEST_TIMEOUT = 300  # seconds
