"""
Storage module for data structure implementations
"""
import os
from datetime import datetime

class FileMetadata:
    """
    Standard metadata structure for files across all tree implementations.
    This ensures consistency in how files are represented regardless of storage structure.
    """
    REQUIRED_FIELDS = ['path', 'size', 'creation_date', 'modified_date', 'compression_status']
    
    @staticmethod
    def create(filepath=None, size=None, compression_status=False, categories=None, additional_metadata=None):
        """
        Create a standardized metadata dictionary for a file
        
        Args:
            filepath: Path to the file
            size: Size of the file in bytes
            compression_status: Whether the file is compressed
            categories: List of categories the file belongs to
            additional_metadata: Any additional metadata to include
            
        Returns:
            Dictionary containing standardized metadata
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Base metadata structure
        metadata = {
            'path': filepath or '',
            'size': size,
            'creation_date': current_time,
            'modified_date': current_time,
            'compression_status': compression_status,
            'categories': categories or [],
        }
        
        # Attempt to get file size from path if not provided
        if filepath and metadata['size'] is None:
            try:
                metadata['size'] = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            except:
                metadata['size'] = 0
                
        # Attempt to get file modification time if path exists
        if filepath and os.path.exists(filepath):
            try:
                mtime = os.path.getmtime(filepath)
                metadata['modified_date'] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except:
                # Keep the current time as fallback
                pass
                
        # Add any additional metadata
        if additional_metadata:
            metadata.update(additional_metadata)
            
        return metadata
    
    @staticmethod
    def validate(metadata):
        """
        Validate that metadata contains all required fields
        
        Args:
            metadata: The metadata dictionary to validate
            
        Returns:
            Boolean indicating if metadata is valid
        """
        return all(field in metadata for field in FileMetadata.REQUIRED_FIELDS)
    
    @staticmethod
    def update(existing_metadata, new_metadata):
        """
        Update existing metadata with new values
        
        Args:
            existing_metadata: Existing metadata dictionary
            new_metadata: New metadata to merge
            
        Returns:
            Updated metadata dictionary
        """
        # Make a copy to avoid modifying the original
        updated = existing_metadata.copy()
        
        # Update with new metadata
        updated.update(new_metadata)
        
        # Update modified date
        updated['modified_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return updated
    
    @staticmethod
    def normalize(metadata):
        """
        Normalize metadata to ensure all required fields exist
        
        Args:
            metadata: The metadata dictionary to normalize
            
        Returns:
            Normalized metadata dictionary
        """
        normalized = metadata.copy()
        
        # Add missing required fields with default values
        for field in FileMetadata.REQUIRED_FIELDS:
            if field not in normalized:
                if field == 'path':
                    normalized[field] = ''
                elif field in ['creation_date', 'modified_date']:
                    normalized[field] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                elif field == 'size':
                    normalized[field] = 0
                elif field == 'compression_status':
                    normalized[field] = False
        
        # Ensure categories exist
        if 'categories' not in normalized:
            normalized['categories'] = []
            
        return normalized