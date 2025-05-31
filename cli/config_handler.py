"""
Handler for configuration operations
"""
import os
import json
from cli.handler_base import MenuHandler
from utils.config_manager import ConfigManager

class ConfigurationHandler(MenuHandler):
    """
    Handler for application configuration operations
    """
    def __init__(self):
        """Initialize the configuration handler"""
        super().__init__()
        self.title = "Configuration Settings"
        self.options = [
            "View current configuration",
            "Edit configuration",
            "Save configuration to file",
            "Load configuration from file",
            "Reset to default configuration"
        ]
        
        # Initialize the config manager
        self.config_manager = ConfigManager()
        self.config_file = self.config_manager.config_file
        self.config = self.config_manager.config
    
    def _handle_option_1(self):
        """View current configuration"""
        print("\nCurrent Configuration:")
        print("=" * 50)
        
        self._print_config(self.config)
        print("\nPress Enter to continue...")
        input()
    
    def _handle_option_2(self):
        """Edit configuration"""
        print("\nEdit Configuration")
        print("=" * 50)
        print("Select a section to edit:")
        
        sections = list(self.config.keys())
        for i, section in enumerate(sections, start=1):
            print(f"{i}. {section}")
        
        print("0. Back")
        
        try:
            choice = int(input(f"Enter your choice (0-{len(sections)}): "))
            
            if 1 <= choice <= len(sections):
                section = sections[choice - 1]
                self._edit_section(section)
            elif choice != 0:
                print(f"Invalid choice. Please select 0-{len(sections)}")
        except ValueError:
            print("Please enter a number.")
    
    def _edit_section(self, section):
        """
        Edit a specific configuration section
        
        Args:
            section (str): Section name to edit
        """
        print(f"\nEditing {section} settings:")
        print("=" * 50)
        
        settings = self.config[section]
        keys = list(settings.keys())
        
        for i, key in enumerate(keys, start=1):
            value = settings[key]
            value_type = type(value).__name__
            print(f"{i}. {key} ({value_type}): {value}")
        
        print("0. Back")
        
        try:
            choice = int(input(f"Enter setting to change (0-{len(keys)}): "))
            
            if 1 <= choice <= len(keys):
                key = keys[choice - 1]
                current_value = settings[key]
                value_type = type(current_value)
                
                print(f"Current value of {key}: {current_value}")
                new_value = input(f"Enter new value ({value_type.__name__}): ")
                
                # Convert input to the correct type
                if value_type == bool:
                    new_value = new_value.lower() in ['true', 'yes', 'y', '1']
                elif value_type == int:
                    new_value = int(new_value)
                elif value_type == float:
                    new_value = float(new_value)
                # else string is already fine
                
                settings[key] = new_value
                print(f"Updated {key} to {new_value}")
                
                # Ask to save changes
                save = input("Save changes to configuration file? (y/n): ").lower()
                if save == 'y':
                    self._save_config()
            elif choice != 0:
                print(f"Invalid choice. Please select 0-{len(keys)}")
        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"Error updating setting: {str(e)}")
    
    def _handle_option_3(self):
        """Save configuration to file"""
        print("\nSave Configuration")
        print("=" * 50)
        
        file_path = input(f"Enter file path (or press Enter for default {self.config_file}): ").strip()
        
        if not file_path:
            file_path = self.config_file
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"✓ Configuration saved to {file_path}")
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
        
        print("\nPress Enter to continue...")
        input()
    
    def _handle_option_4(self):
        """Load configuration from file"""
        print("\nLoad Configuration")
        print("=" * 50)
        
        file_path = input("Enter path to configuration file: ").strip()
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return
        
        try:
            with open(file_path, 'r') as f:
                new_config = json.load(f)
            
            # Validate the configuration structure
            required_sections = ["compression", "storage", "visualization", "interface", "batch"]
            missing_sections = [s for s in required_sections if s not in new_config]
            
            if missing_sections:
                print(f"Warning: Configuration file is missing sections: {', '.join(missing_sections)}")
                confirm = input("Continue loading partial configuration? (y/n): ").lower()
                if confirm != 'y':
                    return
            
            # Update configuration
            self.config.update(new_config)
            print("✓ Configuration loaded successfully")
            
            # Ask to save as default
            save_default = input("Save as default configuration? (y/n): ").lower()
            if save_default == 'y':
                self._save_config()
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in configuration file.")
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
        
        print("\nPress Enter to continue...")
        input()
    
    def _handle_option_5(self):
        """Reset to default configuration"""
        print("\nReset to Default Configuration")
        print("=" * 50)
        
        confirm = input("Are you sure you want to reset to default configuration? (y/n): ").lower()
        
        if confirm == 'y':
            self.config = self._create_default_config()
            print("✓ Configuration reset to defaults")
            
            save_default = input("Save default configuration to file? (y/n): ").lower()
            if save_default == 'y':
                self._save_config()
        
        print("\nPress Enter to continue...")
        input()
    
    def _save_config(self):
        """Save the current configuration to the default file"""
        return self.config_manager._save_config()
    
    def _create_default_config(self):
        """
        Create default configuration
        
        Returns:
            dict: Default configuration dictionary
        """
        return {
            "compression": {
                "default_extension": ".bin",
                "show_huffman_tree_after_compression": False,
                "default_analysis_export_format": "txt"
            },
            "storage": {
                "default_index_location": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "indexes"),
                "auto_update_indexes": True,
                "default_tree_type": "rbtree"  # rbtree or btree
            },
            "visualization": {
                "default_output_format": "txt",  # txt, png, html
                "color_output": True,
                "detailed_node_info": True
            },
            "interface": {
                "show_welcome_message": True,
                "verbose_output": True,
                "confirm_operations": True
            },
            "batch": {
                "max_parallel_processes": 4,
                "log_batch_operations": True
            }
        }
    
    def _print_config(self, config, indent=0):
        """
        Recursively print configuration with nice formatting
        
        Args:
            config: Configuration dictionary or value to print
            indent: Current indentation level
        """
        if isinstance(config, dict):
            for key, value in config.items():
                print("  " * indent + f"{key}:")
                self._print_config(value, indent + 1)
        else:
            value_str = str(config)
            if isinstance(config, bool):
                value_str = "enabled" if config else "disabled"
            elif isinstance(config, (int, float)):
                value_str = str(config)
            
            print("  " * indent + f"• {value_str}")
    
    def get_config(self):
        """
        Get the current configuration
        
        Returns:
            dict: Current configuration
        """
        return self.config