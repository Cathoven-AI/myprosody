"""
MyProsody Package
================

A Python package for analyzing speech prosody features.
"""

from .prosody_analyzer import ProsodyAnalyzer
from .config import ProsodyConfig
from .utils import AudioPreprocessor

__version__ = '0.1.0'
__author__ = 'Shahab Sabahi'
__email__ = 'shahab.sabahi@gmail.com'

# Expose main classes
__all__ = ['ProsodyConfig', 'ProsodyAnalyzer', 'AudioPreprocessor'] 