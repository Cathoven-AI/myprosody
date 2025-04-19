"""
Configuration management for MyProsody package
"""

import os
from pathlib import Path

class ProsodyConfig:
    def __init__(self):
        # Find package root directory (where this config.py file is)
        self.package_root = os.path.dirname(os.path.abspath(__file__))
        
        # Dataset directory is a subdirectory of the package
        self.dataset_dir = os.path.join(self.package_root, 'dataset')
        
        # Ensure dataset directory exists
        if not os.path.exists(self.dataset_dir):
            raise RuntimeError(f"Dataset directory not found at {self.dataset_dir}")
        
        # Audio files directory
        self.audio_dir = os.path.join(self.dataset_dir, 'audioFiles', 'temp')
        
        # Praat script paths
        self.praat_scripts = {
            'solution': os.path.join(self.dataset_dir, 'essen', 'myspsolution.praat'),
            'MLTRNL': os.path.join(self.dataset_dir, 'essen', 'MLTRNL_fix.praat')
        }
        
        # Verify Praat scripts exist
        for script_name, script_path in self.praat_scripts.items():
            if not os.path.exists(script_path):
                raise RuntimeError(f"Praat script {script_name} not found at {script_path}")
        
        # Default audio processing parameters
        self.params = {
            'silence_threshold': -20,  # dB
            'min_dip': 2.0,           # dB
            'min_pause': 0.3,         # seconds
            'min_pitch': 80,          # Hz
            'max_pitch': 400,         # Hz
            'time_step': 0.01         # seconds
        }
        
        # Output directories
        self.output_dirs = {
            'textgrid': os.path.join(self.dataset_dir, 'textgrid'),  # lowercase for consistency
            'csv': os.path.join(self.dataset_dir, 'csv'),
            'audio': self.audio_dir
        }
        
        # Create output directories
        self.create_output_dirs()
        
    def create_output_dirs(self):
        """Create output directories if they don't exist"""
        for dir_path in self.output_dirs.values():
            try:
                # Create directory with full permissions
                os.makedirs(dir_path, mode=0o777, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not create directory {dir_path}: {e}")
            
    def update_params(self, **kwargs):
        """Update processing parameters"""
        self.params.update(kwargs)
        
    def __str__(self):
        """String representation showing current configuration"""
        return f"""MyProsody Configuration:
- Package root: {self.package_root}
- Dataset directory: {self.dataset_dir}
- Audio directory: {self.audio_dir}
- Praat scripts: {self.praat_scripts}
- Output directories: {self.output_dirs}""" 