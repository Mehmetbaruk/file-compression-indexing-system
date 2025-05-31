"""
Configuration Manager utility class
Provides centralized access to user configuration settings
"""
import os
import json

class ConfigManager:
    """
    Configuration Manager utility class
    Provides easy access to configuration settings across the application
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the configuration manager"""
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        self.config = self._load_or_create_config()
        
        # Create benchmark results directory if it doesn't exist
        self.benchmark_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmark_results")
        os.makedirs(self.benchmark_dir, exist_ok=True)
        
        # Create indexes directory if it doesn't exist
        self.indexes_dir = self.get("storage.default_index_location")
        os.makedirs(self.indexes_dir, exist_ok=True)
    
    def _load_or_create_config(self):
        """
        Load existing configuration or create default
        
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
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
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default configuration
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return default_config
    
    def get(self, path, default=None):
        """
        Get a configuration value by path
        
        Args:
            path (str): Path to the configuration value (dot notation)
            default: Default value to return if path not found
        
        Returns:
            Configuration value or default
        """
        parts = path.split(".")
        value = self.config
        
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path, value):
        """
        Set a configuration value by path
        
        Args:
            path (str): Path to the configuration value (dot notation)
            value: Value to set
        
        Returns:
            bool: True if successful, False otherwise
        """
        parts = path.split(".")
        config = self.config
        
        try:
            # Navigate to the correct nested dict
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
                
            # Set the final value
            config[parts[-1]] = value
            
            # Save the configuration
            return self._save_config()
        except Exception:
            return False
    
    def _save_config(self):
        """
        Save the current configuration to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception:
            return False
    
    def reload(self):
        """
        Reload configuration from file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                return True
            return False
        except Exception:
            return False