"""
Huffman coding implementation for text file compression
"""
import heapq
import os
from collections import Counter

# We need to create a custom Node class that's comparable for the priority queue
class Node:
    """Node class for Huffman Tree"""
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
        self.huff = ''
        
    def __lt__(self, other):
        """Less than comparison for priority queue"""
        return self.freq < other.freq
    
    def __eq__(self, other):
        """Equal comparison for priority queue"""
        if other is None:
            return False
        return self.freq == other.freq

class HuffmanTree:
    """
    Huffman Tree implementation for encoding and decoding
    """
    def __init__(self):
        self.codes = {}
        self.reverse_mapping = {}
        self.root = None
        self.freq_dict = None

    def _make_frequency_dict(self, text):
        """
        Create a frequency dictionary for the input text
        """
        return dict(Counter(text))
    
    def _make_heap(self, frequency):
        """
        Create a priority queue from frequency dictionary
        """
        heap = []
        for symbol, freq in frequency.items():
            node = Node(freq, symbol)
            heapq.heappush(heap, node)
        return heap
    
    def _merge_nodes(self, heap):
        """
        Merge nodes to create Huffman tree
        """
        if len(heap) == 1:
            # Special case: Only one unique character in text
            symbol = heap[0].symbol
            new_node = Node(
                freq=heap[0].freq, 
                symbol=None, 
                left=Node(freq=0, symbol=symbol),
                right=Node(freq=0, symbol=None)
            )
            heapq.heappush(heap, new_node)
            heapq.heappop(heap)
            
        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            
            merged = Node(freq=node1.freq + node2.freq, symbol=None, left=node1, right=node2)
            heapq.heappush(heap, merged)
        
        return heap[0]
    
    def _make_codes_helper(self, root, current_code):
        """
        Helper function to create codes recursively
        """
        if root is None:
            return
        
        if root.symbol is not None:
            self.codes[root.symbol] = current_code
            self.reverse_mapping[current_code] = root.symbol
            return
        
        self._make_codes_helper(root.left, current_code + "0")
        self._make_codes_helper(root.right, current_code + "1")
    
    def _make_codes(self):
        """
        Create Huffman codes for each symbol
        """
        self._make_codes_helper(self.root, "")
    
    def _get_encoded_text(self, text):
        """
        Encode the input text using generated Huffman codes
        """
        encoded_text = ""
        for character in text:
            encoded_text += self.codes[character]
        return encoded_text
    
    def _pad_encoded_text(self, encoded_text):
        """
        Pad the encoded text to make it a multiple of 8 bits
        """
        extra_padding = 8 - len(encoded_text) % 8
        for _ in range(extra_padding):
            encoded_text += "0"
        
        # Add information about padding at the beginning
        padded_info = format(extra_padding, '08b')
        encoded_text = padded_info + encoded_text
        return encoded_text
    
    def _get_byte_array(self, padded_encoded_text):
        """
        Convert the padded encoded text to bytes
        """
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return bytes(b)
    
    def _remove_padding(self, padded_encoded_text):
        """
        Remove padding from the encoded text
        """
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-extra_padding] if extra_padding > 0 else padded_encoded_text
        
        return encoded_text
    
    def _decode_text(self, encoded_text):
        """
        Decode text using reverse mapping of codes
        """
        current_code = ""
        decoded_text = ""
        
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_text += self.reverse_mapping[current_code]
                current_code = ""
        
        return decoded_text
    
    def build_tree(self, text):
        """
        Build the Huffman tree from text
        """
        self.freq_dict = self._make_frequency_dict(text)
        heap = self._make_heap(self.freq_dict)
        self.root = self._merge_nodes(heap)
        self._make_codes()
    
    def build_tree_from_freq(self, freq_dict):
        """
        Build the Huffman tree from a frequency dictionary
        """
        self.freq_dict = freq_dict
        heap = self._make_heap(freq_dict)
        self.root = self._merge_nodes(heap)
        self._make_codes()
    
    def visualize_tree(self):
        """
        Return a simple visualization of the tree structure
        """
        if not self.root:
            return "Tree not built yet"
        
        lines = []
        
        def _print_tree(node, prefix="", is_left=True):
            if node is None:
                return
            
            if node.symbol is not None:
                lines.append(f"{prefix}{'└── ' if is_left else '┌── '}{node.symbol} ({node.freq})")
            else:
                lines.append(f"{prefix}{'└── ' if is_left else '┌── '}Internal ({node.freq})")
            
            new_prefix = prefix + ("    " if is_left else "│   ")
            _print_tree(node.left, new_prefix, True)
            _print_tree(node.right, new_prefix, False)
        
        _print_tree(self.root, "", True)
        return "\n".join(lines)

class Encoder:
    """
    Encoder for compressing files using Huffman coding
    """
    def __init__(self):
        self.huffman_tree = HuffmanTree()
        self.original_size = 0
        self.compressed_size = 0
    
    def compress(self, input_path, output_path=None):
        """
        Compress a text file using Huffman coding
        """
        if not output_path:
            output_path = input_path + ".bin"
        
        # Read file as binary to handle all file types
        with open(input_path, 'rb') as file:
            content = file.read()
            
        # Convert bytes to string for processing
        text = ''.join(chr(b) for b in content)
        
        self.original_size = len(content)
        
        # Build Huffman tree
        self.huffman_tree.build_tree(text)
        
        # Get encoded text
        encoded_text = self.huffman_tree._get_encoded_text(text)
        
        # Pad encoded text
        padded_text = self.huffman_tree._pad_encoded_text(encoded_text)
        
        # Convert to bytes
        bytes_array = self.huffman_tree._get_byte_array(padded_text)
        
        # Write to output file
        with open(output_path, 'wb') as output_file:
            # Store frequency dictionary for decompression
            import pickle
            pickle.dump(self.huffman_tree.freq_dict, output_file)
            
            # Write the bytes
            output_file.write(bytes_array)
        
        self.compressed_size = os.path.getsize(output_path)
        return output_path
    
    def get_compression_ratio(self):
        """
        Return the compression ratio achieved
        """
        if self.original_size == 0:
            return 0
        return round((1 - self.compressed_size / self.original_size) * 100, 2)
    
    def get_compression_potential(self):
        """
        Calculate potential compression ratio based on character frequency distribution.
        This is an estimation useful for visualization before actual compression.
        Uses Shannon entropy to predict theoretical compression ratio.
        """
        if not hasattr(self.huffman_tree, 'freq_dict') or not self.huffman_tree.freq_dict:
            return 30  # Default fallback if no frequency data available
            
        freq_dict = self.huffman_tree.freq_dict
        total_chars = sum(freq_dict.values())
        
        # Calculate Shannon entropy - theoretical minimum bits needed
        import math
        entropy = 0
        for freq in freq_dict.values():
            probability = freq / total_chars
            entropy -= probability * math.log2(probability)
            
        # Estimate compression ratio based on entropy
        # 8 bits is the typical size of a byte without compression
        theoretical_bits_per_char = entropy
        estimated_ratio = (1 - theoretical_bits_per_char / 8) * 100
        
        # Clamp between 0-100%
        return max(0, min(100, estimated_ratio))
    
    def analyze_file(self, file_path):
        """
        Analyze a file to generate frequency data and build a Huffman tree.
        This method is required for visualization.
        """
        try:
            # Read the file and determine character frequencies
            analyzer = Analyzer()
            analysis = analyzer.analyze_file(file_path)
            frequencies = {char: data['count'] for char, data in analysis['frequencies'].items()}
            
            # Build Huffman tree based on frequencies
            self.huffman_tree.build_tree_from_freq(frequencies)
            
            return analysis
        except Exception as e:
            import traceback
            print(f"Error analyzing file: {str(e)}")
            print(traceback.format_exc())
            raise Exception(f"Error analyzing file: {str(e)}")
    
    def get_tree(self):
        """
        Return the Huffman tree root for visualization
        """
        return self.huffman_tree.root
    
    def get_tree_visualization(self):
        """
        Return a text visualization of the Huffman tree
        """
        return self.huffman_tree.visualize_tree()

class Decoder:
    """
    Decoder for decompressing files compressed using Huffman coding
    """
    def __init__(self):
        self.huffman_tree = HuffmanTree()
    
    def decompress(self, input_path, output_path=None):
        """
        Decompress a file compressed using Huffman coding
        """
        if not output_path:
            filename, extension = os.path.splitext(input_path)
            output_path = filename + "_decompressed.txt"
        
        with open(input_path, 'rb') as file:
            # Read the frequency dictionary
            import pickle
            freq_dict = pickle.load(file)
            
            # Read the rest as bytes
            bit_string = ""
            byte = file.read(1)
            while byte:
                byte_val = ord(byte)
                bits = bin(byte_val)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
        
        # Rebuild the Huffman tree
        self.huffman_tree.build_tree_from_freq(freq_dict)
        
        # Remove padding
        encoded_text = self.huffman_tree._remove_padding(bit_string)
        
        # Decode text
        decompressed_text = self.huffman_tree._decode_text(encoded_text)
        
        # Write to output file - convert characters back to bytes
        with open(output_path, 'wb') as file:
            bytes_content = bytes([ord(c) for c in decompressed_text])
            file.write(bytes_content)
        
        return output_path

class Analyzer:
    """
    Analyzer for analyzing text files for compression
    """
    def analyze_file(self, file_path):
        """
        Analyze a file and return character frequencies
        Works with both text and binary files
        """
        try:
            # First try to read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
        except UnicodeDecodeError:
            # If that fails, read as binary
            with open(file_path, 'rb') as file:
                content = file.read()
                # Convert bytes to a representation suitable for visualization
                text = ''.join(chr(b) if b < 128 else f'\\x{b:02x}' for b in content)
        
        frequencies = Counter(text)
        total_chars = len(text)
        
        analysis = {
            'total_characters': total_chars,
            'unique_characters': len(frequencies),
            'frequencies': {char: {'count': count, 'percentage': round(count / total_chars * 100, 2)} 
                         for char, count in frequencies.items()}
        }
        
        return analysis

# Alias classes for test compatibility
class HuffmanEncoder(Encoder):
    """Alias for Encoder class for test compatibility"""
    def compress_file(self, input_path, output_path=None):
        """Wrapper method for compress to match test expectations"""
        return self.compress(input_path, output_path)
        
    def analyze_frequency(self, file_path):
        """Analyze frequencies from a file"""
        analyzer = Analyzer()
        analysis = analyzer.analyze_file(file_path)
        return analysis['frequencies']

class HuffmanDecoder(Decoder):
    """Alias for Decoder class for test compatibility"""
    def decompress_file(self, input_path, output_path=None):
        """Wrapper method for decompress to match test expectations"""
        return self.decompress(input_path, output_path)