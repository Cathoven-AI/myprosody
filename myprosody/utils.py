"""
Minimal audio preprocessing utilities
"""

import os
from pathlib import Path
from pydub import AudioSegment

class AudioPreprocessor:
    def __init__(self, temp_dir=None):
        """Initialize with optional custom temp directory"""
        self.temp_dir = Path(temp_dir) if temp_dir else Path(os.path.dirname(__file__)) / 'temp'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def preprocess_audio(self, input_file):
        """
        Preprocess audio to standard format (mono, 48kHz, 24-bit)
        Returns: path to processed file
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Audio file not found: {input_file}")
            
        temp_path = self.temp_dir / f"proc_{os.path.basename(input_file)}"
        
        (AudioSegment.from_file(input_file)
            .set_channels(1)
            .set_frame_rate(48000)
            .set_sample_width(3)
            .normalize()
            .export(str(temp_path), format='wav'))
            
        return str(temp_path)
    
    def cleanup(self):
        """Remove processed files"""
        if self.temp_dir.exists():
            for f in self.temp_dir.glob('*'):
                try:
                    os.remove(f)
                except OSError:
                    pass 