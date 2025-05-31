"""
Handler for compression operations
"""
import os
import time
import sys
import threading
from cli.handler_base import MenuHandler
from compression.huffman import Encoder, Decoder

class CompressionHandler(MenuHandler):
    """
    Handler for file compression operations
    """
    def __init__(self):
        """Initialize the compression handler"""
        super().__init__()
        self.title = "Compression Operations"
        self.options = [
            "Compress a file",
            "Decompress a file",
            "Analyze file compression potential",
            "Batch compress multiple files",
            "View file character frequencies"
        ]
        
        self.encoder = Encoder()
        self.decoder = Decoder()
        
        # Configuration settings
        self.max_file_size = 100 * 1024 * 1024  # 100MB default limit
        self.max_file_size_warning = 10 * 1024 * 1024  # 10MB warning threshold
        self.chunk_size = 1024 * 1024  # 1MB for reading chunks
        
        # Progress tracking
        self.operation_in_progress = False
        self.progress_thread = None
        self.progress = 0
        self.total_size = 0
    
    def _handle_option_1(self):
        """Handle compress file option"""
        print("\nCompress a File")
        print("==================================")
        
        input_file = input("Enter the path to the file to compress: ")
        if not self._validate_file_exists(input_file):
            return
        
        # Check file size before proceeding
        file_size = os.path.getsize(input_file)
        if file_size > self.max_file_size:
            print(f"\n⚠️ Warning: File size ({self._format_size(file_size)}) exceeds the maximum recommended size "
                  f"({self._format_size(self.max_file_size)}).")
            print("Compressing files this large may cause memory issues.")
            confirm = input("Do you want to proceed anyway? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled.")
                return
        elif file_size > self.max_file_size_warning:
            print(f"\n⚠️ Note: File size ({self._format_size(file_size)}) is large. "
                  f"Compression may take some time.")
            
        output_file = input("Enter the path for the compressed file (leave blank for default): ").strip()
        if not output_file:
            output_file = input_file + ".bin"
        
        print(f"\nCompressing {input_file}...")
        start_time = time.time()
        
        try:
            # Set progress tracking variables
            self.operation_in_progress = True
            self.progress = 0
            self.total_size = file_size
            
            # Start progress indicator in a separate thread
            self.progress_thread = threading.Thread(target=self._show_progress_indicator, 
                                                   args=("Compressing", ))
            self.progress_thread.daemon = True
            self.progress_thread.start()
            
            # Compress the file
            self.encoder.compress(input_file, output_file, 
                                 progress_callback=self._update_progress)
            
            # Stop progress indicator
            self.operation_in_progress = False
            if self.progress_thread:
                self.progress_thread.join()
            
            # Clear progress line and move to next line
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.flush()
            
            # Get compression stats
            end_time = time.time()
            elapsed_time = end_time - start_time
            compression_ratio = self.encoder.get_compression_ratio()
            original_size = self.encoder.original_size
            compressed_size = self.encoder.compressed_size
            
            # Print results
            print(f"\n✓ File compressed successfully!")
            print(f"  Original size: {self._format_size(original_size)}")
            print(f"  Compressed size: {self._format_size(compressed_size)}")
            print(f"  Compression ratio: {compression_ratio:.2f}%")
            print(f"  Elapsed time: {elapsed_time:.4f} seconds")
            print(f"  Output file: {output_file}")
            
            # Save Huffman tree for future reference
            tree_file = output_file + "_huffman_tree.txt"
            with open(tree_file, 'w') as f:
                f.write(self.encoder.huffman_tree.visualize_tree())
            print(f"  Huffman tree saved to: {tree_file}")
            
            # Ask if user wants to view the Huffman tree
            view_tree = input("\nWould you like to view the Huffman tree? (y/n): ").lower()
            if view_tree == 'y':
                tree_visualization = self.encoder.huffman_tree.visualize_tree()
                print("\nHuffman Tree Structure:")
                print(tree_visualization)
                
        except MemoryError as e:
            self._display_error_message(f"Memory error during compression: {str(e)}")
            print("Try compressing a smaller file or increase your system's memory.")
        except Exception as e:
            self._display_error_message(f"Error compressing file: {str(e)}")
            
        # Ensure progress indicator is stopped
        self.operation_in_progress = False
    
    def _handle_option_2(self):
        """Handle decompress file option"""
        print("\nDecompress a File")
        print("==================================")
        
        input_file = input("Enter the path to the compressed file: ")
        if not self._validate_file_exists(input_file):
            return
            
        # Check file size before proceeding
        file_size = os.path.getsize(input_file)
        if file_size > self.max_file_size:
            print(f"\n⚠️ Warning: Compressed file size ({self._format_size(file_size)}) is very large.")
            print("Decompressing may result in an extremely large file and could cause memory issues.")
            confirm = input("Do you want to proceed anyway? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled.")
                return
            
        output_file = input("Enter the path for the decompressed file (leave blank for default): ").strip()
        if not output_file:
            # Remove .bin extension if present
            if input_file.endswith(".bin"):
                output_file = input_file[:-4] + "_decompressed"
            else:
                output_file = input_file + "_decompressed"
        
        print(f"\nDecompressing {input_file}...")
        start_time = time.time()
        
        try:
            # Set progress tracking variables
            self.operation_in_progress = True
            self.progress = 0
            self.total_size = file_size
            
            # Start progress indicator in a separate thread
            self.progress_thread = threading.Thread(target=self._show_progress_indicator, 
                                                   args=("Decompressing", ))
            self.progress_thread.daemon = True
            self.progress_thread.start()
            
            # Decompress the file
            self.decoder.decompress(input_file, output_file, 
                                   progress_callback=self._update_progress)
            
            # Stop progress indicator
            self.operation_in_progress = False
            if self.progress_thread:
                self.progress_thread.join()
            
            # Clear progress line and move to next line
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.flush()
            
            # Get decompression stats
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Print results
            compressed_size = os.path.getsize(input_file)
            decompressed_size = os.path.getsize(output_file)
            expansion_ratio = (decompressed_size / compressed_size) * 100
            
            print(f"\n✓ File decompressed successfully!")
            print(f"  Compressed size: {self._format_size(compressed_size)}")
            print(f"  Decompressed size: {self._format_size(decompressed_size)}")
            print(f"  Expansion ratio: {expansion_ratio:.2f}%")
            print(f"  Elapsed time: {elapsed_time:.4f} seconds")
            print(f"  Output file: {output_file}")
            
        except MemoryError as e:
            self._display_error_message(f"Memory error during decompression: {str(e)}")
            print("The compressed file may expand to a size that exceeds available memory.")
        except Exception as e:
            self._display_error_message(f"Error decompressing file: {str(e)}")
            
        # Ensure progress indicator is stopped
        self.operation_in_progress = False
    
    def _handle_option_3(self):
        """Handle analyze file compression potential option"""
        print("\nAnalyze File Compression Potential")
        print("==================================")
        
        input_file = input("Enter the path to the file to analyze: ")
        if not self._validate_file_exists(input_file):
            return
        
        # Check file size before proceeding
        file_size = os.path.getsize(input_file)
        if file_size > self.max_file_size:
            print(f"\n⚠️ Warning: File size ({self._format_size(file_size)}) exceeds the maximum recommended size "
                  f"({self._format_size(self.max_file_size)}).")
            print("Analysis may be slow or cause memory issues.")
            print("Consider analyzing a smaller file or a sample of this file.")
            confirm = input("Do you want to proceed anyway? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled.")
                return
        
        try:
            # For large files, we'll use a chunked approach
            is_large_file = file_size > self.max_file_size_warning
            
            if is_large_file:
                print(f"\nAnalyzing large file ({self._format_size(file_size)}), this may take some time...")
                # Set progress tracking variables
                self.operation_in_progress = True
                self.progress = 0
                self.total_size = file_size
                
                # Start progress indicator
                self.progress_thread = threading.Thread(target=self._show_progress_indicator, 
                                                       args=("Analyzing", ))
                self.progress_thread.daemon = True
                self.progress_thread.start()
                
                # Process in chunks
                frequencies = {}
                bytes_processed = 0
                total_chars = 0
                
                with open(input_file, 'rb') as file:
                    while chunk := file.read(self.chunk_size):
                        # Try to decode as text, fallback to binary if needed
                        try:
                            text_chunk = chunk.decode('utf-8')
                            for char in text_chunk:
                                frequencies[char] = frequencies.get(char, 0) + 1
                                total_chars += 1
                        except UnicodeDecodeError:
                            for byte in chunk:
                                char_key = f"BYTE_{byte}"
                                frequencies[char_key] = frequencies.get(char_key, 0) + 1
                                total_chars += 1
                        
                        bytes_processed += len(chunk)
                        self._update_progress(bytes_processed)
                
                # Stop progress indicator
                self.operation_in_progress = False
                if self.progress_thread:
                    self.progress_thread.join()
                
            else:
                # For smaller files, process the entire file at once
                print(f"\nAnalyzing file...")
                
                # Always start with binary mode, then try to interpret as text if possible
                with open(input_file, 'rb') as file:
                    binary_data = file.read()
                    
                # Try to decode as text
                try:
                    text = binary_data.decode('utf-8')
                    
                    # Calculate character frequencies
                    frequencies = {}
                    for char in text:
                        frequencies[char] = frequencies.get(char, 0) + 1
                    total_chars = len(text)
                    
                except UnicodeDecodeError:
                    # If text reading fails, use binary data
                    frequencies = {}
                    for byte in binary_data:
                        char_key = f"BYTE_{byte}"
                        frequencies[char_key] = frequencies.get(char_key, 0) + 1
                    total_chars = len(binary_data)
            
            # Calculate entropy and potential compression
            entropy = self._calculate_entropy(frequencies, total_chars)
            potential_ratio = (1 - (entropy / 8)) * 100
            
            # Clear progress line if needed
            if is_large_file:
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()
            
            # Print analysis results
            print(f"\nAnalysis Results:")
            print(f"  File size: {self._format_size(file_size)}")
            print(f"  Total characters/bytes analyzed: {total_chars}")
            print(f"  Unique characters/bytes: {len(frequencies)}")
            print(f"  Entropy: {entropy:.4f} bits per character/byte")
            print(f"  Theoretical maximum compression ratio: {potential_ratio:.2f}%")
            print(f"  Estimated compressed size: {self._format_size(int(total_chars * entropy / 8))}")
            
            # Compression suitability assessment
            if potential_ratio < 10:
                print(f"\nCompression Assessment: ⚠️ Poor candidate for compression")
                print(f"  This file has high entropy and may not compress well.")
            elif potential_ratio < 30:
                print(f"\nCompression Assessment: ⚠️ Moderate compression potential")
                print(f"  Some space savings possible, but may not be significant.")
            else:
                print(f"\nCompression Assessment: ✓ Good candidate for compression")
                print(f"  This file should compress well with Huffman coding.")
            
            # Show most frequent characters
            print("\nMost frequent characters:")
            most_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:5]
            for char, count in most_freq:
                if isinstance(char, str) and char.startswith("BYTE_"):
                    byte_val = int(char.split("_")[1])
                    char_display = f"Byte {byte_val}"
                    if 32 <= byte_val <= 126:
                        char_display += f" ('{chr(byte_val)}')"
                elif isinstance(char, str) and char.isspace():
                    char_display = f"Space (ASCII {ord(char)})"
                elif isinstance(char, str) and (ord(char) < 32 or ord(char) > 126):
                    char_display = f"ASCII {ord(char)}"
                else:
                    char_display = f"'{char}'"
                print(f"  {char_display}: {count} occurrences ({count/total_chars*100:.2f}%)")
            
            input("\nPress Enter to continue...")
                
        except MemoryError as e:
            self._display_error_message(f"Memory error during analysis: {str(e)}")
            print("Try analyzing a smaller file or increase your system's memory.")
        except Exception as e:
            self._display_error_message(f"Error analyzing file: {str(e)}")
            
        # Ensure progress indicator is stopped
        self.operation_in_progress = False
    
    def _handle_option_4(self):
        """Handle batch compress multiple files option"""
        print("\nBatch Compress Multiple Files")
        print("==================================")
        
        # Get directory path
        dir_path = input("Enter the directory path containing files to compress: ")
        if not os.path.isdir(dir_path):
            self._display_error_message(f"Error: Directory {dir_path} does not exist.")
            return
            
        # Get file pattern to match
        file_pattern = input("Enter file pattern to match (e.g., *.txt) or leave blank for all files: ").strip()
        
        # Find matching files
        import glob
        if file_pattern:
            file_paths = glob.glob(os.path.join(dir_path, file_pattern))
        else:
            file_paths = [os.path.join(dir_path, f) for f in os.listdir(dir_path) 
                         if os.path.isfile(os.path.join(dir_path, f))]
            
        if not file_paths:
            print(f"No matching files found in {dir_path}")
            return
            
        # Output directory
        output_dir = input("Enter output directory for compressed files (leave blank for same as input): ").strip()
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")
            except Exception as e:
                self._display_error_message(f"Error creating directory: {str(e)}")
                return
        elif not output_dir:
            output_dir = dir_path
            
        # Confirm the operation
        print(f"\nFound {len(file_paths)} files to compress.")
        print(f"Files will be saved to: {output_dir}")
        confirm = input("Proceed with batch compression? (y/n): ").lower()
        if confirm != 'y':
            print("Batch operation cancelled.")
            return
            
        # Process files
        print(f"\nStarting batch compression of {len(file_paths)} files...")
        successful = 0
        failed = 0
        total_original_size = 0
        total_compressed_size = 0
        
        # Batch progress tracking
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths, 1):
            file_name = os.path.basename(file_path)
            output_path = os.path.join(output_dir, file_name + ".bin")
            
            progress_percent = (i / total_files) * 100
            print(f"\rProcessing file {i}/{total_files} ({progress_percent:.1f}%): {file_name}", end="")
            sys.stdout.flush()
            
            try:
                # Check file size before proceeding
                file_size = os.path.getsize(file_path)
                if file_size > self.max_file_size:
                    print(f"\n⚠️ Skipping {file_name}: File size ({self._format_size(file_size)}) exceeds the maximum limit.")
                    failed += 1
                    continue
                
                # Compress the file
                self.encoder.compress(file_path, output_path)
                
                # Update statistics
                original_size = self.encoder.original_size
                compressed_size = self.encoder.compressed_size
                total_original_size += original_size
                total_compressed_size += compressed_size
                successful += 1
                
            except Exception as e:
                print(f"\nError compressing {file_name}: {str(e)}")
                failed += 1
                
        # Clear progress line
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()
                
        # Print summary
        total_compression_ratio = 0
        if total_original_size > 0:
            total_compression_ratio = (1 - (total_compressed_size / total_original_size)) * 100
            
        print("\nBatch Compression Summary:")
        print(f"  Total files processed: {total_files}")
        print(f"  Successfully compressed: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total original size: {self._format_size(total_original_size)}")
        print(f"  Total compressed size: {self._format_size(total_compressed_size)}")
        print(f"  Overall compression ratio: {total_compression_ratio:.2f}%")
        
        if successful > 0:
            print(f"✓ Batch compression completed with {successful} files compressed successfully.")
        else:
            print("⚠️ Batch compression completed but no files were successfully compressed.")
            
        input("\nPress Enter to continue...")
    
    def _handle_option_5(self):
        """Handle view file character frequencies option"""
        print("\nView File Character Frequencies")
        print("==================================")
        
        input_file = input("Enter the path to the file: ")
        if not self._validate_file_exists(input_file):
            return
        
        # Check file size before proceeding
        file_size = os.path.getsize(input_file)
        if file_size > self.max_file_size:
            print(f"\n⚠️ Warning: File size ({self._format_size(file_size)}) exceeds the maximum recommended size.")
            print("Analysis may be slow or cause memory issues.")
            print("Consider analyzing a smaller file or a sample of this file.")
            confirm = input("Do you want to proceed anyway? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled.")
                return
        
        try:
            # For large files, we'll use a chunked approach
            is_large_file = file_size > self.max_file_size_warning
            
            if is_large_file:
                print(f"\nAnalyzing large file ({self._format_size(file_size)}), this may take some time...")
                # Set progress tracking variables
                self.operation_in_progress = True
                self.progress = 0
                self.total_size = file_size
                
                # Start progress indicator
                self.progress_thread = threading.Thread(target=self._show_progress_indicator, 
                                                       args=("Analyzing", ))
                self.progress_thread.daemon = True
                self.progress_thread.start()
                
                # Process in chunks
                frequencies = {}
                bytes_processed = 0
                total_chars = 0
                
                with open(input_file, 'rb') as file:
                    while chunk := file.read(self.chunk_size):
                        # Try to decode as text, fallback to binary if needed
                        try:
                            text_chunk = chunk.decode('utf-8')
                            for char in text_chunk:
                                frequencies[char] = frequencies.get(char, 0) + 1
                                total_chars += 1
                        except UnicodeDecodeError:
                            for byte in chunk:
                                char_key = f"BYTE_{byte}"
                                frequencies[char_key] = frequencies.get(char_key, 0) + 1
                                total_chars += 1
                        
                        bytes_processed += len(chunk)
                        self._update_progress(bytes_processed)
                
                # Stop progress indicator
                self.operation_in_progress = False
                if self.progress_thread:
                    self.progress_thread.join()
                
                # Clear progress line
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()
                
            else:
                # For smaller files, process the entire file at once
                print(f"\nAnalyzing file...")
                
                # Always start with binary mode, then try to interpret as text if possible
                with open(input_file, 'rb') as file:
                    binary_data = file.read()
                    
                # Try to decode as text
                try:
                    text = binary_data.decode('utf-8')
                    
                    # Calculate character frequencies
                    frequencies = {}
                    for char in text:
                        frequencies[char] = frequencies.get(char, 0) + 1
                    total_chars = len(text)
                    
                except UnicodeDecodeError:
                    # If text reading fails, use binary data
                    frequencies = {}
                    for byte in binary_data:
                        char_key = f"BYTE_{byte}"
                        frequencies[char_key] = frequencies.get(char_key, 0) + 1
                    total_chars = len(binary_data)
            
            # Sort by frequency
            sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
            
            # Display character distribution
            print(f"\nCharacter frequency distribution for {input_file}:")
            print(f"Total characters/bytes: {total_chars}")
            print(f"Unique characters/bytes: {len(frequencies)}")
            print(f"{'Character':<15} {'Frequency':<10} {'Percentage':<12} {'Visual'}")
            print("-" * 70)
            
            # Limit display to top 50 characters to avoid overwhelming output
            display_limit = min(50, len(sorted_freq))
            for char, count in sorted_freq[:display_limit]:
                percentage = (count / total_chars) * 100
                bar_length = int((count / total_chars) * 40)
                bar = '#' * bar_length
                
                if isinstance(char, str) and char.startswith("BYTE_"):
                    byte_val = int(char.split("_")[1])
                    char_display = f"Byte {byte_val}"
                    if 32 <= byte_val <= 126:
                        char_display += f" ('{chr(byte_val)}')"
                elif isinstance(char, str) and char.isspace():
                    char_display = f"Space (ASCII {ord(char)})"
                elif isinstance(char, str) and (ord(char) < 32 or ord(char) > 126):
                    char_display = f"ASCII {ord(char)}"
                else:
                    char_display = f"'{char}'"
                
                print(f"{char_display:<15} {count:<10} {percentage:6.2f}%     {bar}")
            
            if len(sorted_freq) > display_limit:
                print(f"... and {len(sorted_freq) - display_limit} more unique characters/bytes")
            
            # Ask if user wants to export frequencies
            export = input("\nWould you like to export these frequencies to a file? (y/n): ").lower()
            if export == 'y':
                output_file = input("Enter the output file path (leave blank for default): ").strip()
                if not output_file:
                    output_file = input_file + "_frequencies.txt"
                
                with open(output_file, 'w', encoding='utf-8') as out:
                    out.write(f"Character frequency distribution for {input_file}\n")
                    out.write(f"Total characters/bytes: {total_chars}\n")
                    out.write(f"Unique characters/bytes: {len(frequencies)}\n")
                    out.write(f"{'Character':<15} {'Frequency':<10} {'Percentage':<12}\n")
                    out.write("-" * 40 + "\n")
                    
                    for char, count in sorted_freq:
                        percentage = (count / total_chars) * 100
                        
                        if isinstance(char, str) and char.startswith("BYTE_"):
                            byte_val = int(char.split("_")[1])
                            char_display = f"Byte {byte_val}"
                            if 32 <= byte_val <= 126:
                                char_display += f" ('{chr(byte_val)}')"
                        elif isinstance(char, str) and char.isspace():
                            char_display = f"Space (ASCII {ord(char)})"
                        elif isinstance(char, str) and (ord(char) < 32 or ord(char) > 126):
                            char_display = f"ASCII {ord(char)}"
                        else:
                            char_display = f"'{char}'"
                        
                        out.write(f"{char_display:<15} {count:<10} {percentage:6.2f}%\n")
                
                print(f"\nFrequencies exported to {output_file}")
                
        except MemoryError as e:
            self._display_error_message(f"Memory error during analysis: {str(e)}")
            print("Try analyzing a smaller file or increase your system's memory.")
        except Exception as e:
            self._display_error_message(f"Error processing file: {str(e)}")
            
        # Ensure progress indicator is stopped
        self.operation_in_progress = False
    
    def _calculate_entropy(self, frequencies, total):
        """
        Calculate Shannon entropy of character frequencies
        
        Args:
            frequencies: Dictionary of character frequencies
            total: Total number of characters
            
        Returns:
            Entropy value in bits per character
        """
        import math
        
        entropy = 0
        for count in frequencies.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        
        return entropy
    
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
        
        if not os.path.isfile(file_path):
            self._display_error_message(f"Error: {file_path} is not a file.")
            return False
            
        return True
    
    def _display_error_message(self, message):
        """
        Display an error message
        
        Args:
            message: The error message to display
        """
        print(f"\n✗ {message}")
        print("Press Enter to continue...")
        input()
    
    def _format_size(self, size_bytes):
        """Format the file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    def _show_progress_indicator(self, operation_name):
        """
        Show a progress indicator for ongoing operations
        
        Args:
            operation_name: The name of the operation (e.g., "Compressing")
        """
        spinner = ['-', '\\', '|', '/']
        i = 0
        
        while self.operation_in_progress:
            if self.total_size > 0:
                progress_percent = (self.progress / self.total_size) * 100
                bar_width = 30
                filled_width = int(bar_width * self.progress / self.total_size)
                bar = '█' * filled_width + '░' * (bar_width - filled_width)
                
                sys.stdout.write(f'\r{operation_name}: [{bar}] {progress_percent:.1f}% {self._format_size(self.progress)}/{self._format_size(self.total_size)} {spinner[i]} ')
            else:
                sys.stdout.write(f'\r{operation_name}... {spinner[i]} ')
                
            sys.stdout.flush()
            i = (i + 1) % len(spinner)
            time.sleep(0.1)
    
    def _update_progress(self, current_progress):
        """
        Update the progress of the current operation
        
        Args:
            current_progress: The current progress value
        """
        self.progress = current_progress