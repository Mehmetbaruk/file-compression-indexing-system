#!/usr/bin/env python3
"""
Cleanup script for removing personal information before GitHub upload
"""
import os
import shutil
import glob

def cleanup_personal_data():
    """Remove files containing personal information"""
    
    # Files and directories to remove
    to_remove = [
        # Test results with personal paths
        "tests/test_results/",
        "benchmark_results/",
        
        # Generated temporary files
        "*.huff",
        "*_decompressed",
        "*.bin",
        "*_huffman_tree.txt",
        
        # Personal data directories
        "test_gui_output_data/",
        "indexes/",
        
        # Corrupted test files
        "tests/user_acceptance/test_user_stories.py",
        
        # IDE files
        ".vscode/",
        ".idea/",
        
        # OS files
        ".DS_Store",
        "Thumbs.db",
        
        # Python cache
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "*.so",
    ]
    
    print("Cleaning up personal data...")
    
    for pattern in to_remove:
        if os.path.isdir(pattern):
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"Removed directory: {pattern}")
        else:
            # Handle glob patterns
            matches = glob.glob(pattern, recursive=True)
            for match in matches:
                try:
                    if os.path.isfile(match):
                        os.remove(match)
                        print(f"Removed file: {match}")
                    elif os.path.isdir(match):
                        shutil.rmtree(match)
                        print(f"Removed directory: {match}")
                except Exception as e:
                    print(f"Warning: Could not remove {match}: {e}")
    
    print("Cleanup complete!")
    print("\nRemaining files are ready for GitHub upload.")
    print("Remember to:")
    print("1. Check the .gitignore file")
    print("2. Review all files for any remaining personal information")
    print("3. Test the application after cleanup")

if __name__ == "__main__":
    cleanup_personal_data()
