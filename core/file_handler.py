"""
File Handler Module - Detects file types and manages supported formats
"""

from pathlib import Path
import magic


class FileHandler:
    """Enhanced file type detection and handling"""
    
    SUPPORTED_TYPES = {
        'pdf': ['application/pdf', '.pdf'],
        'word': [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
            '.docx', '.doc',
        ],
        'excel': [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
            '.xlsx', '.xls',
        ],
        'csv': ['text/csv', '.csv'],
        'powerpoint': [
            'application/vnd.openxmlformats-officedocument.presentationml.presentation', 
            '.pptx', '.ppt',
        ],
        'image': [
            'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
            'image/webp', 'image/tiff', 'image/svg+xml',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'
        ],
        'text': ['text/plain', '.txt', '.log', '.ini', '.cfg'],
        'markdown': ['text/markdown', '.md', '.markdown'],
        'epub': ['application/epub+zip', '.epub'],
        'html': ['text/html', '.html', '.htm'],
        'json': ['application/json', '.json'],
        'xml': ['application/xml', '.xml'],
        'yaml': ['application/x-yaml', '.yaml', '.yml'],
        'rtf': ['application/rtf', '.rtf'],
        'odt': ['application/vnd.oasis.opendocument.text', '.odt'],
        'ods': ['application/vnd.oasis.opendocument.spreadsheet', '.ods'],
        'odp': ['application/vnd.oasis.opendocument.presentation', '.odp'],
    }
    
    @staticmethod
    def detect_file_type(file_path):
        """Detect file type with improved accuracy"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        # Check by extension first
        for file_type, extensions in FileHandler.SUPPORTED_TYPES.items():
            if extension in [ext for ext in extensions if ext.startswith('.')]:
                return file_type
        
        # Fallback to content-based detection
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(str(file_path))
            for file_type, mime_types in FileHandler.SUPPORTED_TYPES.items():
                if mime_type in [m for m in mime_types if '/' in m]:
                    return file_type
        except:
            pass
        
        return 'unknown'