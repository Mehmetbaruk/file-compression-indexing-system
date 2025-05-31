#!/usr/bin/env python3
"""
File Compression and Indexing System
Main application entry point
"""

import sys
from cli.interface import UserInterface

def main():
    """
    Main entry point of the application
    """
    # Create the user interface
    ui = UserInterface()
    
    try:
        # Start the user interface
        ui.start()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()