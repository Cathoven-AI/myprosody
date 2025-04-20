"""
MyProsody Package - Speech Prosody Analysis Tools
Copyright (C) 2017-2024 Shahab Sabahi

This module provides tools for analyzing speech prosody features including:
- Syllable detection and analysis
- Pause detection and analysis 
- Speech rate analysis
- Pitch analysis (F0)
- Formant analysis
"""

import os
import shutil
import numpy as np
import pandas as pd
import scipy.stats
from scipy.stats import binom, ks_2samp, ttest_ind
from parselmouth.praat import run_file
from .utils import AudioPreprocessor
from .config import ProsodyConfig

class ProsodyAnalyzer:
    """
    Main class for prosody analysis of speech audio files.
    Provides methods for analyzing various aspects of speech prosody including:
    - Syllable and pause detection
    - Speech rate and rhythm
    - Pitch (F0) statistics
    - Gender and mood detection
    - Pronunciation scoring
    """
    
    def __init__(self, config=None, debug=False):
        """Initialize prosody analyzer with configuration"""
        self.debug = debug
        self.config = config or ProsodyConfig()
        self.preprocessor = AudioPreprocessor()
        self.config.create_output_dirs()

    def __del__(self):
        """Cleanup temporary files on object destruction"""
        self.cleanup()

    def cleanup(self):
        """Clean up all temporary directories and files"""
        try:
            if hasattr(self, 'preprocessor'):
                self.preprocessor.cleanup()
            
            if os.path.exists(self.config.output_dirs['textgrid']):
                shutil.rmtree(self.config.output_dirs['textgrid'])
            
            if os.path.exists(self.config.output_dirs['csv']):
                shutil.rmtree(self.config.output_dirs['csv'])
                
            audio_temp = os.path.join(self.config.dataset_dir, 'audioFiles', 'temp')
            if os.path.exists(audio_temp):
                shutil.rmtree(audio_temp)
                
        except Exception as e:
            self._debug_print(f"Error during cleanup: {str(e)}")

    def _debug_print(self, message):
        """Print message only if debug is enabled"""
        if self.debug:
            print(message)

    def run_praat_script(self, audio_path, script_type='solution'):
        """Run Praat script on audio file"""
        try:
            processed_audio = self.preprocessor.preprocess_audio(audio_path)
            if not os.path.isfile(processed_audio):
                raise FileNotFoundError(f"Processed audio not found: {processed_audio}")

            script_path = self.config.praat_scripts.get(script_type)
            if not script_path or not os.path.isfile(script_path):
                raise ValueError(f"Invalid script type or missing script: {script_type}")

            # Ensure TextGrid directory exists with write permissions
            textgrid_dir = self.config.output_dirs['textgrid']
            os.makedirs(textgrid_dir, mode=0o777, exist_ok=True)
            
            # Clean up any existing TextGrid files
            if os.path.exists(textgrid_dir):
                for f in os.listdir(textgrid_dir):
                    if f.endswith('.TextGrid'):
                        try:
                            os.remove(os.path.join(textgrid_dir, f))
                        except OSError:
                            pass

            self._debug_print(f"Running Praat script: {script_path}")
            self._debug_print(f"On audio file: {processed_audio}")
            
            # Run the Praat script
            try:
                objects = run_file(
                    script_path,
                    self.config.params['silence_threshold'],
                    self.config.params['min_dip'],
                    self.config.params['min_pause'],
                    "yes",
                    processed_audio,
                    textgrid_dir,
                    self.config.params['min_pitch'],
                    self.config.params['max_pitch'],
                    self.config.params['time_step'],
                    capture_output=True,
                )                
                if not objects:
                    self._debug_print("Praat script returned no objects")
                    return None
                    
                if len(objects) < 2:
                    self._debug_print(f"Unexpected number of objects returned: {len(objects)}")
                    return None
                    
                self._debug_print(f"Script execution successful. Number of objects: {len(objects)}")
                return objects
                
            except Exception as script_error:
                self._debug_print(f"Error executing Praat script: {str(script_error)}")
                self._debug_print(f"Script path: {script_path}")
                self._debug_print(f"Audio path: {processed_audio}")
                return None
                
        except Exception as e:
            self._debug_print(f"Error in run_praat_script: {str(e)}")
            return None

    def _get_basic(self, audio_path):
        """Get basic prosody metrics using solution script"""
        try:
            objects = self.run_praat_script(audio_path, 'solution')
            if not objects:
                self._debug_print("No objects returned from Praat script")
                return None

            try:
                result_text = str(objects[1])
                if not result_text.strip():
                    self._debug_print("Empty result from Praat script")
                    return None
                    
                results = result_text.strip().split()
                self._debug_print(f"Raw results from Praat: {results}")
                
                if len(results) < 14:
                    self._debug_print(f"Insufficient results from Praat (got {len(results)}, expected at least 14)")
                    return None

                metrics = {}
                
                metrics['n_syllables'] = int(results[0])
                metrics['n_pauses'] = int(results[1])
                metrics['speech_rate_w_pause'] = float(results[2])
                metrics['speech_rate_wo_pause'] = float(results[3])
                metrics['speaking_dur'] = float(results[4])
                metrics['total_dur'] = float(results[5])
                metrics['pct_speaking'] = float(results[6])
                metrics['f0_mean'] = float(results[7])
                metrics['f0_std'] = float(results[8])
                metrics['f0_median'] = float(results[9])
                metrics['f0_min'] = int(results[10])
                metrics['f0_max'] = int(results[11])
                metrics['f0_q25'] = int(results[12])
                metrics['f0_q75'] = int(results[13])
                
                # Add gender and mood analysis
                gender_info = self._get_gender(float(results[7]), float(results[8]))
                if gender_info:
                    metrics['gender'] = gender_info['gender']
                    metrics['mood'] = gender_info['mood']
                
                # Add pronunciation score
                pron_score = self._get_pron_score(round(float(results[14]),3))
                if pron_score is not None:
                    metrics['pron_score'] = pron_score
                
                return metrics
                
            except Exception as parse_error:
                self._debug_print(f"Error parsing Praat results: {str(parse_error)}")
                if objects and len(objects) > 1:
                    self._debug_print(f"Raw output: {str(objects[1])}")
                return None
                
        except Exception as e:
            self._debug_print(f"Error in basic metrics analysis: {str(e)}")
            return None


    def _get_gender(self, f0_mean, f0_std):
        """Analyze gender and mood based on F0 statistics"""
        try:
            gender_mood = {
                (0, 114): ('Male', 'normal', 101, 3.4),
                (114, 135): ('Male', 'reading', 128, 4.35),
                (135, 163): ('Male', 'passionate', 142, 4.85),
                (163, 197): ('Female', 'normal', 182, 2.7),
                (197, 226): ('Female', 'reading', 213, 4.5),
                (226, float('inf')): ('Female', 'passionate', 239, 5.3)
            }

            for (lower, upper), (gender, mood, g, j) in gender_mood.items():
                if lower < f0_mean <= upper:
                    # Statistical validation
                    d1 = np.random.wald(g, 1, 1000)
                    d2 = np.random.wald(j, 1, 1000)
                    ks_stat = ks_2samp(d1, d2)
                    
                    c1 = np.random.normal(g, f0_mean, 1000)
                    c2 = np.random.normal(j, f0_std, 1000)
                    t_stat = ttest_ind(c1, c2)
                    
                    # p_value = t_stat[1] if t_stat[1] <= 0.09 else 0.35
                    return {
                        'gender': gender,
                        'mood': mood,
                        # 'confidence': 1 - p_value
                    }

            return {'gender': 'Unknown', 'mood': 'Unknown'}
        except Exception as e:
            self._debug_print(f"Error in gender/mood analysis: {str(e)}")
            return None

    def _get_pron_score(self, z4):
        """Calculate pronunciation score using solution script"""
        try:
            db = binom.rvs(n=10, p=z4, size=10000)
            score = np.mean(db) * 100 / 10
            return score
        except Exception as e:
            self._debug_print(f"Error in pronunciation analysis: {str(e)}")
            return None

    def _get_prosody(self, audio_path):
        """Compare prosody features with native speech."""
        try:
            objects = self.run_praat_script(audio_path, 'MLTRNL')
            if not objects:
                self._debug_print("No objects returned from get_prosody: Praat script MLTRNL")
                return None

            raw_output = str(objects[1]).strip().split()
            
            raw_columns = ['avepauseduratin', 'avelongpause', 'speakingtot', 'avenumberofwords',
                'articulationrate', 'inpro', 'f1norm', 'mr', 'q25', 'q50', 'q75', 'std', 'fmax',
                'fmin', 'vowelinx1', 'vowelinx2', 'formantmean', 'formantstd', 'nuofwrds',
                'npause', 'ins', 'fillerratio', 'xx', 'xxx', 'totsco', 'xxban', 'speakingrate']
            
            display_names = ['avg_pause_dur_per_syll', 'n_long_pause', 'speaking_time',
                'speaking_wpm', 'articulation_rate', 'total_wpm',
                'formants_index', 'f0_index', 'f0_25', 'f0_50', 'f0_75', 'f0_std', 'f0_max', 'f0_min', 'n_detected_vowel',
                'pct_correct_vowel', 'f2_f1_mean', 'f2_f1_std', 'n_words',
                'n_pause', 'intonation_index', 'n_syllable/n_pause',
                'TOEFL_Score', 'Shannon_Score', 'speaking_rate']

            df = pd.DataFrame([raw_output], columns=raw_columns)
            scored_data = df.drop(['xxx', 'xxban'], axis=1)
            
            stats_path = os.path.join(self.config.package_root, "dataset/essen/stats.csv")
            reference_data = pd.read_csv(stats_path)
            
            metrics = {}
            for i in range(min(len(display_names), scored_data.shape[1])):
                try:
                    # ref_values = reference_data.values[4:7:1, i+1]
                    current_score = float(scored_data.values[0, i])
                    metrics[display_names[i]] = round(current_score,3)
                        # 'reference_values': ref_values,

                except Exception as e:
                    self._debug_print(f"Error processing feature {display_names[i]}: {str(e)}")
                    continue

            filter_out = ['n_words', 'n_pause', 'n_long_pause', 'speaking_time', 'f0_25', 'f0_50', 'f0_75', 'f0_std', 'f0_max', 'f0_min']
            metrics = {k: v for k, v in metrics.items() if k not in filter_out}
            
            return metrics
            
        except Exception as e:
            self._debug_print(f"Error in prosody analysis: {str(e)}")
            return None
        
    def mysptotal(self, audio_path):
        """
        Comprehensive prosody analysis including:
        - Basic prosody metrics
        - Gender and mood analysis
        - Pronunciation scoring
        - Comparison with native speech
        
        Args:
            audio_path (str): Path to the audio file to analyze
            
        Returns:
            dict: Dictionary containing:
                - basic_metrics (DataFrame): Basic prosody measurements
                - gender_mood (DataFrame): Gender and mood analysis
                - pron_score (float): Pronunciation score
                - prosody (DataFrame): Comparison with native speech
        """
        try:
            basic_metrics = self._get_basic(audio_path)
            if not basic_metrics:
                self._debug_print("Error in basic metrics analysis")
                basic_metrics = None

            prosody = self._get_prosody(audio_path)
            if not prosody:
                self._debug_print("Error in prosody analysis")
                prosody = None

            results = {
                'basic': basic_metrics,
                'prosody': prosody
            }
            self.cleanup()
            return results
        except Exception as e:
            self._debug_print(f"Error in total analysis: {str(e)}")
            self.cleanup()
            return None 