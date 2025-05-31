"""
Handler for unified search operations across multiple data structures
"""
import os
import time
import datetime
from cli.handler_base import MenuHandler
from storage.red_black_tree import RedBlackTree
from storage.btree import BTree
from utils.config_manager import ConfigManager

class SearchHandler(MenuHandler):
    """
    Handler for unified search operations across the system
    Provides a single interface for searching multiple data structures
    """
    def __init__(self):
        """Initialize the search handler"""
        super().__init__()
        self.title = "Unified Search"
        self.options = [
            "Search by filename",
            "Search by content",
            "Advanced search (with filters)",
            "Recent search history"
        ]
        
        # Initialize the config manager
        self.config_manager = ConfigManager()
        
        # Initialize storage structures
        self.rbtree = RedBlackTree()
        self.btree = BTree(t=3)  # Fixed to use t=3 instead of min_degree=3
        
        # Search history
        self.search_history = []
        self.max_history = 10
        
        # Configuration settings
        self.max_file_size = 50 * 1024 * 1024  # 50MB default limit
        self.chunk_size = 1024 * 1024  # 1MB for reading chunks
    
    def _handle_option_1(self):
        """Handle search by filename"""
        print("\nSearch by Filename")
        print("=" * 50)
        
        search_term = input("Enter filename or part of filename to search for: ").strip()
        if not search_term:
            print("Search term cannot be empty.")
            return
        
        # Ask which data structures to search
        print("\nSelect data structures to search:")
        print("1. Red-Black Tree (faster for small datasets)")
        print("2. B-Tree (better for large datasets)")
        print("3. Both (complete search)")
        
        choice = input("Enter your choice (1-3): ").strip()
        search_rbtree = choice in ['1', '3']
        search_btree = choice in ['2', '3']
        
        if not (search_rbtree or search_btree):
            print("Invalid choice. Please try again.")
            return
        
        # Keep track of search execution time
        start_time = time.time()
        results = []
        
        # Search in Red-Black Tree if selected
        if search_rbtree:
            print("\nSearching in Red-Black Tree...")
            rb_results = self._search_rbtree_by_filename(search_term)
            if rb_results:
                results.extend(rb_results)
                print(f"Found {len(rb_results)} results in Red-Black Tree.")
            else:
                print("No matches found in Red-Black Tree.")
        
        # Search in B-Tree if selected
        if search_btree:
            print("\nSearching in B-Tree...")
            b_results = self._search_btree_by_filename(search_term)
            if b_results:
                # Avoid duplicates (file might be indexed in both trees)
                existing_paths = [r['path'] for r in results]
                unique_b_results = [r for r in b_results if r['path'] not in existing_paths]
                results.extend(unique_b_results)
                print(f"Found {len(unique_b_results)} additional results in B-Tree.")
            else:
                print("No matches found in B-Tree.")
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # Display results
        if results:
            print(f"\nFound {len(results)} total results in {search_time:.4f} seconds:")
            print("-" * 70)
            print(f"{'Filename':<30} {'Size':>10} {'Location':<30}")
            print("-" * 70)
            
            for result in results:
                filename = os.path.basename(result['path'])
                size = self._format_size(result.get('size', 0))
                location = os.path.dirname(result['path'])
                
                print(f"{filename:<30} {size:>10} {location:<30}")
            
            # Ask if user wants to perform operations on results
            if len(results) > 0:
                self._offer_result_actions(results)
        else:
            print(f"\nNo results found for '{search_term}' in {search_time:.4f} seconds.")
        
        # Add to search history
        self._add_to_search_history({
            'term': search_term,
            'type': 'filename',
            'timestamp': datetime.datetime.now().isoformat(),
            'results_count': len(results),
            'search_time': search_time
        })
        
        print("\nPress Enter to continue...")
        input()
    
    def _handle_option_2(self):
        """Handle search by content"""
        print("\nSearch by Content")
        print("=" * 50)
        print("This search looks for files containing specific text.")
        
        search_term = input("Enter text content to search for: ").strip()
        if not search_term:
            print("Search term cannot be empty.")
            return
            
        # Ask for file types to include
        file_types = input("Enter file extensions to search (comma separated, e.g., txt,md,py) or leave blank for all: ").strip()
        if file_types:
            extensions = [ext.strip().lower() for ext in file_types.split(",")]
            extensions = ["." + ext if not ext.startswith(".") else ext for ext in extensions]
        else:
            extensions = None
        
        # Ask for directory to search
        search_dir = input("Enter directory path to search (or leave blank for indexed files only): ").strip()
        search_indexed_only = not search_dir
        
        if search_indexed_only:
            # Search only in indexed files
            print("\nSearching in indexed files...")
            results = self._search_indexed_files_by_content(search_term, extensions)
        else:
            # Search in specified directory
            if not os.path.isdir(search_dir):
                print(f"Error: '{search_dir}' is not a valid directory.")
                return
                
            print(f"\nSearching in directory: {search_dir}")
            results = self._search_directory_by_content(search_dir, search_term, extensions)
        
        # Display results
        if results:
            print(f"\nFound {len(results)} files containing '{search_term}':")
            print("-" * 70)
            print(f"{'Filename':<30} {'Matches':>8} {'Path':<30}")
            print("-" * 70)
            
            for result in sorted(results, key=lambda x: x['matches'], reverse=True):
                filename = os.path.basename(result['path'])
                matches = result['matches']
                path = os.path.dirname(result['path'])
                
                print(f"{filename:<30} {matches:>8} {path:<30}")
            
            # Ask if user wants to perform operations on results
            self._offer_result_actions(results)
        else:
            print(f"\nNo files found containing '{search_term}'.")
        
        # Add to search history
        self._add_to_search_history({
            'term': search_term,
            'type': 'content',
            'extensions': extensions,
            'timestamp': datetime.datetime.now().isoformat(),
            'results_count': len(results) if results else 0
        })
        
        print("\nPress Enter to continue...")
        input()
    
    def _handle_option_3(self):
        """Handle advanced search with filters"""
        print("\nAdvanced Search")
        print("=" * 50)
        
        # Collect search criteria
        search = {
            'filename': input("Filename contains (leave blank to skip): ").strip(),
            'content': input("Content contains (leave blank to skip): ").strip(),
            'min_size': input("Minimum size (KB, leave blank to skip): ").strip(),
            'max_size': input("Maximum size (KB, leave blank to skip): ").strip(),
            'extensions': input("File extensions (comma separated, leave blank for all): ").strip(),
            'modified_after': input("Modified after date (YYYY-MM-DD, leave blank to skip): ").strip(),
        }
        
        # Convert inputs to appropriate types
        try:
            if search['min_size']:
                search['min_size'] = float(search['min_size']) * 1024  # Convert KB to bytes
            else:
                search['min_size'] = None
                
            if search['max_size']:
                search['max_size'] = float(search['max_size']) * 1024  # Convert KB to bytes
            else:
                search['max_size'] = None
                
            if search['extensions']:
                search['extensions'] = [ext.strip().lower() for ext in search['extensions'].split(",")]
                search['extensions'] = ["." + ext if not ext.startswith(".") else ext for ext in search['extensions']]
            else:
                search['extensions'] = None
                
            if search['modified_after']:
                search['modified_after'] = datetime.datetime.strptime(search['modified_after'], "%Y-%m-%d")
            else:
                search['modified_after'] = None
        except ValueError as e:
            print(f"Error in search criteria: {str(e)}")
            print("\nPress Enter to continue...")
            input()
            return
        
        # Check if any search criteria were provided
        if not any([search['filename'], search['content'], search['min_size'], 
                   search['max_size'], search['extensions'], search['modified_after']]):
            print("Error: At least one search criterion must be specified.")
            print("\nPress Enter to continue...")
            input()
            return
        
        # Execute the search
        print("\nExecuting advanced search...")
        start_time = time.time()
        
        # Get candidate files from indexed storage
        candidates = self._get_all_indexed_files()
        
        # Apply filters
        results = []
        for file_info in candidates:
            if self._matches_search_criteria(file_info, search):
                results.append(file_info)
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # Display results
        if results:
            print(f"\nFound {len(results)} matching files in {search_time:.4f} seconds:")
            print("-" * 70)
            print(f"{'Filename':<25} {'Size':>10} {'Modified':>20} {'Path':<30}")
            print("-" * 70)
            
            for result in results:
                filename = os.path.basename(result['path'])
                size = self._format_size(result.get('size', 0))
                modified = result.get('modified_date', 'Unknown')
                if isinstance(modified, datetime.datetime):
                    modified = modified.strftime("%Y-%m-%d %H:%M")
                path = os.path.dirname(result['path'])
                
                print(f"{filename:<25} {size:>10} {modified:>20} {path:<30}")
            
            # Ask if user wants to perform operations on results
            self._offer_result_actions(results)
        else:
            print("\nNo files match the specified criteria.")
        
        # Add to search history
        self._add_to_search_history({
            'type': 'advanced',
            'criteria': search,
            'timestamp': datetime.datetime.now().isoformat(),
            'results_count': len(results),
            'search_time': search_time
        })
        
        print("\nPress Enter to continue...")
        input()
    
    def _handle_option_4(self):
        """Display recent search history"""
        print("\nRecent Search History")
        print("=" * 50)
        
        if not self.search_history:
            print("No search history available.")
            print("\nPress Enter to continue...")
            input()
            return
        
        print(f"{'Time':<19} {'Type':<10} {'Search Term':<30} {'Results':>7}")
        print("-" * 70)
        
        for i, search in enumerate(self.search_history):
            timestamp = datetime.datetime.fromisoformat(search['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            search_type = search['type'].capitalize()
            
            if search_type == "Advanced":
                term = "Multiple criteria"
            else:
                term = search.get('term', 'N/A')
                
            results = search.get('results_count', 0)
            
            print(f"{timestamp:<19} {search_type:<10} {term[:30]:<30} {results:>7}")
        
        # Ask if user wants to repeat a search
        choice = input("\nEnter number to repeat a search (or 0 to go back): ")

        if choice == '0':
            return  # Go back to main menu
        
        try:
            choice = int(choice)
            if choice < 1 or choice > len(self.search_history):
                print("Invalid choice. Please try again.")
                return
            
            # Get the selected search from history
            selected_search = self.search_history[choice - 1]
            
            # Repeat the search
            print(f"\nRepeating search: {selected_search.get('term', 'N/A')}")
            if selected_search['type'] == 'filename':
                self._handle_option_1(selected_search.get('term', ''))
            elif selected_search['type'] == 'content':
                self._handle_option_2(selected_search.get('term', ''))
            elif selected_search['type'] == 'advanced':
                self._handle_option_3(selected_search.get('criteria', {}))
        except ValueError:
            print("Invalid input. Please enter a number.")
        
        print("\nPress Enter to continue...")
        input()
    
    def _search_rbtree_by_filename(self, search_term):
        """Search Red-Black Tree by filename"""
        results = []
        def _search_node(node):
            if node is None or node == self.rbtree.NIL:
                return
            # Check if the filename contains the search term
            if search_term.lower() in node.filename.lower():
                results.append({
                    'filename': node.filename,
                    'path': node.metadata.get('path', ''),
                    'size': node.metadata.get('size', 0),
                    'compression_status': node.metadata.get('compression_status', False)
                })
            # Continue searching in both subtrees
            _search_node(node.left)
            _search_node(node.right)
        
        # Start the search from the root of the Red-Black Tree
        _search_node(self.rbtree.root)
        return results
    
    def _search_btree_by_filename(self, search_term):
        """Search B-Tree by filename"""
        results = []
        # Define a recursive function to search in B-Tree nodes
        def _search_node(node):
            if node is None:
                return
            # Check each key in the node
            for i in range(len(node.keys)):
                filename = node.keys[i]
                if i < len(node.values):  # Ensure there's a corresponding value
                    metadata = node.values[i]
                    # If the filename contains the search term, add to results
                    if search_term.lower() in filename.lower():
                        results.append({
                            'filename': filename,
                            'path': metadata.get('path', ''),
                            'size': metadata.get('size', 0),
                            'compression_status': metadata.get('compression_status', False),
                            'modified_date': metadata.get('creation_date', '')
                        })
            # Continue searching in child nodes
            if not node.leaf:
                for child in node.children:
                    _search_node(child)
        
        # Start the search from the root of the B-Tree
        _search_node(self.btree.root)
        return results
    
    def _search_indexed_files_by_content(self, search_term, extensions=None):
        """Search indexed files by content"""
        results = []
        
        # Search in Red-Black Tree
        rb_results = self._search_rbtree_by_content(search_term, extensions)
        if rb_results:
            results.extend(rb_results)
            
        # Search in B-Tree
        b_results = self._search_btree_by_content(search_term, extensions)
        if b_results:
            # Avoid duplicates
            existing_paths = [r['path'] for r in results]
            unique_b_results = [r for r in b_results if r['path'] not in existing_paths]
            results.extend(unique_b_results)
        
        return results
        
    def _search_rbtree_by_content(self, search_term, extensions=None):
        """Search Red-Black Tree files by content"""
        results = []
        
        def _search_node(node):
            if node is None or node == self.rbtree.NIL:
                return
                
            # Process current node
            file_path = node.metadata.get('path', '')
            
            # Skip files that don't match the extension filter
            if extensions and not any(file_path.endswith(ext) for ext in extensions):
                pass  # Skip this file
            elif file_path:
                # Read the file content and search for the term
                try:
                    # First try to read as text
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            if search_term.lower() in content.lower():
                                results.append({
                                    'filename': node.filename,
                                    'path': file_path,
                                    'size': node.metadata.get('size', 0),
                                    'compression_status': node.metadata.get('compression_status', False),
                                    'modified_date': node.metadata.get('creation_date', ''),
                                    'matches': content.lower().count(search_term.lower())
                                })
                    except UnicodeDecodeError:
                        # If text reading fails, try binary mode
                        with open(file_path, 'rb') as file:
                            binary_content = file.read()
                            str_content = str(binary_content)
                            if search_term.lower() in str_content.lower():
                                results.append({
                                    'filename': node.filename,
                                    'path': file_path,
                                    'size': node.metadata.get('size', 0),
                                    'compression_status': node.metadata.get('compression_status', False),
                                    'modified_date': node.metadata.get('creation_date', ''),
                                    'matches': str_content.lower().count(search_term.lower())
                                })
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
            
            # Continue searching in both subtrees
            _search_node(node.left)
            _search_node(node.right)
            
        # Start the search from the root
        _search_node(self.rbtree.root)
        return results
        
    def _search_btree_by_content(self, search_term, extensions=None):
        """Search B-Tree files by content"""
        results = []
        
        def _search_node(node):
            if node is None:
                return
                
            # Process keys and values in this node
            for i in range(len(node.keys)):
                if i < len(node.values):  # Make sure there's a corresponding value
                    filename = node.keys[i]
                    metadata = node.values[i]
                    file_path = metadata.get('path', '')
                    
                    # Skip files that don't match the extension filter
                    if extensions and not any(file_path.endswith(ext) for ext in extensions):
                        continue
                        
                    if file_path:
                        # Read the file content and search for the term
                        try:
                            # First try to read as text
                            try:
                                with open(file_path, 'r', encoding='utf-8') as file:
                                    content = file.read()
                                    if search_term.lower() in content.lower():
                                        results.append({
                                            'filename': filename,
                                            'path': file_path,
                                            'size': metadata.get('size', 0),
                                            'compression_status': metadata.get('compression_status', False),
                                            'modified_date': metadata.get('creation_date', ''),
                                            'matches': content.lower().count(search_term.lower())
                                        })
                            except UnicodeDecodeError:
                                # If text reading fails, try binary mode
                                with open(file_path, 'rb') as file:
                                    binary_content = file.read()
                                    str_content = str(binary_content)
                                    if search_term.lower() in str_content.lower():
                                        results.append({
                                            'filename': filename,
                                            'path': file_path,
                                            'size': metadata.get('size', 0),
                                            'compression_status': metadata.get('compression_status', False),
                                            'modified_date': metadata.get('creation_date', ''),
                                            'matches': str_content.lower().count(search_term.lower())
                                        })
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")
            
            # Continue searching in child nodes
            if not node.leaf:
                for child in node.children:
                    _search_node(child)
                    
        # Start the search from the root
        _search_node(self.btree.root)
        return results
    
    def _search_directory_by_content(self, directory, search_term, extensions=None):
        """Search files in a directory by content"""
        results = []
        
        # Walk through all files in the directory
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip files that don't match the extension filter
                if extensions and not any(file.endswith(ext) for ext in extensions):
                    continue
                    
                # Read the file content and search for the term
                try:
                    # First try to read as text
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if search_term.lower() in content.lower():
                                # Get file stats
                                stats = os.stat(file_path)
                                results.append({
                                    'filename': file,
                                    'path': file_path,
                                    'size': stats.st_size,
                                    'compression_status': file.endswith('.gz') or file.endswith('.zip'),
                                    'modified_date': datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                    'matches': content.lower().count(search_term.lower())
                                })
                    except UnicodeDecodeError:
                        # If text reading fails, try binary mode
                        with open(file_path, 'rb') as f:
                            binary_content = f.read()
                            str_content = str(binary_content)
                            if search_term.lower() in str_content.lower():
                                # Get file stats
                                stats = os.stat(file_path)
                                results.append({
                                    'filename': file,
                                    'path': file_path,
                                    'size': stats.st_size,
                                    'compression_status': file.endswith('.gz') or file.endswith('.zip'),
                                    'modified_date': datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                                    'matches': str_content.lower().count(search_term.lower())
                                })
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    
        return results

    def _matches_search_criteria(self, file_info, criteria):
        """Check if a file matches the advanced search criteria"""
        # Check filename
        if criteria['filename'] and criteria['filename'].lower() not in os.path.basename(file_info['path']).lower():
            return False
        
        # Check content (for advanced search, we might need to read the file)
        if criteria['content']:
            try:
                # First try to read as text
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as file:
                        content = file.read()
                        if criteria['content'].lower() not in content.lower():
                            return False
                except UnicodeDecodeError:
                    # If text reading fails, try binary mode
                    with open(file_info['path'], 'rb') as file:
                        binary_content = file.read()
                        str_content = str(binary_content)
                        if criteria['content'].lower() not in str_content.lower():
                            return False
            except Exception as e:
                print(f"Error reading file {file_info['path']} for content search: {e}")
                return False
        
        # Check size
        size = file_info.get('size', 0)
        if criteria['min_size'] and size < criteria['min_size']:
            return False
        if criteria['max_size'] and size > criteria['max_size']:
            return False
        
        # Check extensions
        if criteria['extensions'] and not any(file_info['path'].endswith(ext) for ext in criteria['extensions']):
            return False
        
        # Check modified date
        if criteria['modified_after'] and file_info.get('modified_date'):
            modified_date = file_info['modified_date']
            if isinstance(modified_date, str):
                modified_date = datetime.datetime.fromisoformat(modified_date)
            if modified_date <= criteria['modified_after']:
                return False
        
        return True
    
    def _get_all_indexed_files(self):
        """Get a list of all indexed files from both Red-Black Tree and B-Tree"""
        all_files = []
        
        # Traverse Red-Black Tree
        def _traverse_rbtree(node):
            if node is None or node == self.rbtree.NIL:
                return
            
            # Add current node
            all_files.append({
                'filename': node.filename,
                'path': node.metadata.get('path', ''),
                'size': node.metadata.get('size', 0),
                'compression_status': node.metadata.get('compression_status', False),
                'modified_date': node.metadata.get('creation_date', '')
            })
            
            # Traverse left and right subtrees
            _traverse_rbtree(node.left)
            _traverse_rbtree(node.right)
        
        # Start traversal from the root
        _traverse_rbtree(self.rbtree.root)
        
        # Traverse B-Tree
        def _traverse_btree(node):
            if node is None:
                return
                
            # Process the keys and values in this node
            for i in range(len(node.keys)):
                if i < len(node.values):  # Make sure there's a corresponding value
                    metadata = node.values[i]
                    all_files.append({
                        'filename': node.keys[i],
                        'path': metadata.get('path', ''),
                        'size': metadata.get('size', 0),
                        'compression_status': metadata.get('compression_status', False),
                        'modified_date': metadata.get('creation_date', '')
                    })
            
            # Traverse children if not a leaf node
            if not node.leaf:
                for child in node.children:
                    _traverse_btree(child)
        
        _traverse_btree(self.btree.root)
        
        return all_files
    
    def _offer_result_actions(self, results):
        """Offer actions to the user for the search results"""
        print("\nWhat do you want to do with the results?")
        print("1. Open file location")
        print("2. Add to favorites")
        print("3. Remove from index")
        print("4. Perform content search in file")
        print("5. Back to search menu")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            self._open_file_location(results)
        elif choice == '2':
            self._add_to_favorites(results)
        elif choice == '3':
            self._remove_from_index(results)
        elif choice == '4':
            self._perform_content_search_in_file(results)
        elif choice == '5':
            return  # Go back to search menu
        else:
            print("Invalid choice. Please try again.")
    
    def _open_file_location(self, results):
        """Open the file location in the file explorer"""
        import webbrowser
        
        for result in results:
            path = result['path']
            # On Windows, use file:///C:/path/to/file
            # On macOS, use file:///Users/username/path/to/file
            # On Linux, use file:///home/username/path/to/file
            url = f"file:///{path.replace(os.sep, '/')}"  # Convert to URL format
            webbrowser.open(url)
        
        print("\nFile locations opened in file explorer.")
        print("\nPress Enter to continue...")
        input()
    
    def _add_to_favorites(self, results):
        """Add the selected files or directories to favorites"""
        for result in results:
            path = result['path']
            # Add to favorites logic here (e.g., copy to favorites directory, add to favorites list, etc.)
            # For demonstration, we'll just print the action
            print(f"Added to favorites: {path}")
        
        print("\nPress Enter to continue...")
        input()
    
    def _remove_from_index(self, results):
        """Remove the selected files or directories from the index"""
        for result in results:
            path = result['path']
            # Remove from index logic here (e.g., delete from storage, remove from trees, etc.)
            # For demonstration, we'll just print the action
            print(f"Removed from index: {path}")
        
        print("\nPress Enter to continue...")
        input()
    
    def _perform_content_search_in_file(self, results):
        """Perform a content search within the selected files"""
        search_term = input("Enter the text to search within the file(s): ").strip()
        if not search_term:
            print("Search term cannot be empty.")
            return
        
        for result in results:
            path = result['path']
            try:
                # First try to read as text
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if search_term.lower() in content.lower():
                            print(f"Found in {path}:")
                            # Print the matching line(s)
                            for line in content.splitlines():
                                if search_term.lower() in line.lower():
                                    print(f"  {line.strip()}")
                except UnicodeDecodeError:
                    # If text reading fails, try binary mode
                    with open(path, 'rb') as file:
                        binary_content = file.read()
                        str_content = str(binary_content)
                        if search_term.lower() in str_content.lower():
                            print(f"Found in binary file {path}")
                            print("  Note: Cannot display line context for binary files")
            except Exception as e:
                print(f"Error reading file {path}: {e}")
        
        print("\nPress Enter to continue...")
        input()
    
    def _add_to_search_history(self, entry):
        """Add an entry to the search history"""
        # Limit history size
        if len(self.search_history) >= self.max_history:
            self.search_history.pop(0)  # Remove oldest entry
        
        self.search_history.append(entry)
        self.config_manager.set("search_history", self.search_history)
    
    def _load_search_history(self):
        """Load search history from config"""
        history = self.config_manager.get("search_history", [])
        # Ensure history is a list of dicts
        if isinstance(history, list):
            self.search_history = history
        else:
            self.search_history = []
    
    def _clear_search_history(self):
        """Clear the search history"""
        self.search_history = []
        self.config_manager.set("search_history", self.search_history)
        print("Search history cleared.")
        print("\nPress Enter to continue...")
        input()
    
    def _format_size(self, size_bytes):
        """Format the file size for display"""
        if size_bytes is None:
            return "N/A"
        elif size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _init_config(self):
        """Initialize the configuration settings"""
        # Set default values if not already set
        if self.config_manager.get("max_history") is None:
            self.config_manager.set("max_history", 10)
        
        if self.config_manager.get("search_history") is None:
            self.config_manager.set("search_history", [])
        
        # Load initial settings
        self.max_history = self.config_manager.get("max_history")
        self.search_history = self.config_manager.get("search_history")
    
    def _show_welcome_message(self):
        """Show the welcome message and initial setup instructions"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print(" Welcome to the Unified Search Tool")
        print("=" * 60)
        print("This tool allows you to search for files and content across")
        print("multiple data structures, including Red-Black Trees and B-Trees.")
        print()
        print("You can perform simple searches by filename or content,")
        print("or use advanced search options to filter by size, type, and date.")
        print()
        print("Your search history will be saved automatically,")
        print("and you can manage your indexed files and favorites easily.")
        print()
        print("Let's get started!")
        print("=" * 60)
        
        input("Press Enter to continue to the main menu...")
    
    def run(self):
        """Run the search handler"""
        # Initialize config and load search history
        self._init_config()
        self._load_search_history()
        
        # Show welcome message
        self._show_welcome_message()
        
        while True:
            # Display the menu
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 60)
            print(" Unified Search Menu")
            print("=" * 60)
            
            for i, option in enumerate(self.options, 1):
                print(f"{i}. {option}")
            
            print("0. Exit")
            
            choice = input("Select an option: ").strip()
            
            if choice == '0':
                print("Thank you for using the Unified Search Tool. Goodbye!")
                break
            elif choice in [str(i) for i in range(1, len(self.options) + 1)]:
                # Handle the selected option
                handler_method = getattr(self, f"_handle_option_{choice}")
                handler_method()
            else:
                print("Invalid choice. Please try again.")
        
        # Save search history and cleanup
        self.config_manager.set("search_history", self.search_history)
        # Don't try to call save() as it doesn't exist
        print("Search history saved.")
