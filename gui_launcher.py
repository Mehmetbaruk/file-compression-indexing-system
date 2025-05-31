#!/usr/bin/env python
"""
File Compression and Indexing System - GUI Launcher
Version: 2.0.0
"""

import sys
import os
from gui.app import main as start_gui

# Try to import CLI interface, but don't fail if it doesn't exist or doesn't have main
try:
    from cli.interface import main as start_cli
except (ImportError, AttributeError):
    # Define a fallback function if the CLI interface is not available
    def start_cli():
        print("CLI interface is not available or properly implemented.")
        print("Starting the GUI interface instead...")
        start_gui()

def show_help():
    """Display command-line help information"""
    print("File Compression and Indexing System")
    print("Usage: python gui_launcher.py [options]")
    print("\nOptions:")
    print("  --cli          Start in command line interface mode")
    print("  --gui          Start in graphical user interface mode (default)")
    print("  --help, -h     Show this help message")
    print("\nExamples:")
    print("  python gui_launcher.py            # Start GUI")
    print("  python gui_launcher.py --cli      # Start CLI")

def main():
    """Main entry point for the application"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--cli":
            print("Starting command line interface...")
            start_cli()
            return
        elif arg == "--gui":
            pass  # Default is GUI
        elif arg in ["--help", "-h"]:
            show_help()
            return
        else:
            print(f"Unknown option: {arg}")
            show_help()
            return

    # Default: Start GUI
    print("Starting graphical user interface...")
    start_gui()

if __name__ == "__main__":
    main()