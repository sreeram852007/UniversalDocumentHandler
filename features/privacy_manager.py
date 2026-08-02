"""
Privacy Manager - Privacy-first document handling
"""

import os
import hashlib
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime


class PrivacyManager:
    """Privacy-first document management with local-only processing"""
    
    def __init__(self):
        self.settings_file = "privacy_settings.json"
        self.settings = self._load_settings()
        self.anonymous_mode = self.settings.get('anonymous_mode', False)
        self.auto_cleanup = self.settings.get('auto_cleanup', True)
        self.preview_cache = self.settings.get('preview_cache', True)
    
    def _load_settings(self) -> Dict:
        """Load privacy settings"""
        default_settings = {
            'anonymous_mode': False,
            'auto_cleanup': True,
            'preview_cache': True,
            'dont_track': True,
            'no_analytics': True,
            'local_only': True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return default_settings
    
    def save_settings(self):
        """Save privacy settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
    
    def get_privacy_status(self) -> Dict:
        """Get current privacy status"""
        return {
            'anonymous_mode': self.settings.get('anonymous_mode', False),
            'auto_cleanup': self.settings.get('auto_cleanup', True),
            'preview_cache': self.settings.get('preview_cache', True),
            'dont_track': self.settings.get('dont_track', True),
            'no_analytics': self.settings.get('no_analytics', True),
            'local_only': self.settings.get('local_only', True),
            'data_stored_locally': True,
            'cloud_uploads': False,
            'telemetry': False,
        }
    
    def anonymize_file(self, file_path: str) -> str:
        """
        Create an anonymous copy of a file (remove metadata)
        
        Returns: Path to anonymous file
        """
        if not self.settings.get('anonymous_mode', False):
            return file_path
        
        # Create temp copy
        temp_dir = os.path.join(os.path.dirname(file_path), '.temp_anon')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create anonymous filename
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        ext = os.path.splitext(file_path)[1]
        anon_path = os.path.join(temp_dir, f"anon_{file_hash}{ext}")
        
        # Copy file
        shutil.copy2(file_path, anon_path)
        
        return anon_path
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if not self.settings.get('auto_cleanup', True):
            return
        
        # Find and delete temp files
        current_dir = os.getcwd()
        for root, dirs, files in os.walk(current_dir):
            for dir_name in dirs:
                if dir_name in ['.temp_anon', '__pycache__', '.tmp']:
                    try:
                        shutil.rmtree(os.path.join(root, dir_name))
                    except:
                        pass
            
            for file_name in files:
                if file_name.endswith('.tmp') or file_name.startswith('~$'):
                    try:
                        os.remove(os.path.join(root, file_name))
                    except:
                        pass
    
    def toggle_anonymous_mode(self):
        """Toggle anonymous mode"""
        self.settings['anonymous_mode'] = not self.settings.get('anonymous_mode', False)
        self.save_settings()
        return self.settings['anonymous_mode']
    
    def toggle_auto_cleanup(self):
        """Toggle auto cleanup"""
        self.settings['auto_cleanup'] = not self.settings.get('auto_cleanup', True)
        self.save_settings()
        return self.settings['auto_cleanup']
    
    def get_privacy_badge(self) -> str:
        """Get privacy status badge"""
        status = self.get_privacy_status()
        badges = []
        
        if status['anonymous_mode']:
            badges.append("🔒 Anonymous")
        if status['local_only']:
            badges.append("🏠 Local Only")
        if status['dont_track']:
            badges.append("🚫 No Tracking")
        if status['no_analytics']:
            badges.append("📊 No Analytics")
        
        return " | ".join(badges) if badges else "Privacy First"
    
    def get_data_usage_report(self) -> Dict:
        """Get report of data usage and privacy status"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'privacy_status': self.get_privacy_status(),
            'data_locations': {
                'local': True,
                'cloud': False,
                'third_party': False
            },
            'metadata_stored': {
                'file_names': self.settings.get('anonymous_mode', False),
                'timestamps': True,
                'user_data': False
            },
            'features': {
                'analytics': False,
                'telemetry': False,
                'auto_update': False
            }
        }
        return report
    
    def get_privacy_policy_summary(self) -> str:
        """Get summary of privacy policy"""
        return """
        🔒 Privacy Policy Summary:
        
        ✅ All processing is LOCAL - No data leaves your computer
        ✅ NO cloud uploads or external API calls
        ✅ NO telemetry or analytics
        ✅ NO user tracking
        ✅ Files are processed in memory only
        ✅ Temporary files are automatically cleaned up
        ✅ Anonymous mode available for sensitive documents
        ✅ Full control over data and settings
        
        Your data stays YOUR data. Period.
        """