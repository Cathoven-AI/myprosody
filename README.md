[![GitHub stars](https://img.shields.io/github/stars/Shahabks/myprosody?style=flat-square)](https://github.com/Shahabks/myprosody/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Shahabks/myprosody?style=flat-square&color=blueviolet)](https://github.com/Shahabks/myprosody/network/members)

# MyProsody

A modified Python package for analyzing speech prosody features, including pronunciation scoring, speech rate analysis, and various acoustic measurements.

## Features

- Speech rate and rhythm analysis
- Pronunciation scoring
- Pitch (F0) statistics
- Syllable and pause detection
- TOEFL and Shannon score calculations
- Acoustic measurements (formants, intonation)

## Installation

### Prerequisites

- Python 3.6 or higher
- Praat (speech analysis software)

### Installing from GitHub

```bash
# Clone the repository
git clone https://github.com/yourusername/myprosody.git

# Install in editable mode
cd myprosody
pip install -e .
```

### Updating the Package

If you installed the package in editable mode (-e), you can update it by:

```bash
cd myprosody
git pull origin main
```

## Package Structure

```
myprosody/
├── myprosody/
│   ├── __init__.py           # Package initialization
│   ├── prosody_analyzer.py   # Main analyzer class
│   ├── config.py            # Configuration settings
│   ├── utils.py             # Utility functions
│   ├── dataset/             # Reference datasets
│   └── temp/                # Temporary files directory
├── setup.py                 # Package setup file
└── README.md               # This file
```

## Usage

```python
from myprosody import ProsodyAnalyzer

analyzer = ProsodyAnalyzer(debug=False)  # Set debug=True for detailed output

result = analyzer.mysptotal("path/to/audio.wav")

if result:
    basic_metrics = result.get('basic', {})
    prosody_metrics = result.get('prosody', {})
    
    # Print specific features
    print(f"Pronunciation Score: {basic_metrics.get('pron_score')}")
    print(f"Speech Rate: {basic_metrics.get('speaking_rate')}")
    print(f"TOEFL Score: {prosody_metrics.get('TOEFL_Score')}")
```

## Available Features

The package returns two main dictionaries of features: `basic` and `prosody`. Here's a detailed description of each feature:

### [basic] Features
- `speaking_dur`: Total duration of speech segments (seconds)
- `total_dur`: Total duration including pauses (seconds)
- `pct_speaking`: Percentage of time spent speaking vs total duration
- `n_syllables`: Total number of detected syllables
- `n_pauses`: Number of pauses detected in speech
- `speech_rate_w_pause`: Speech rate including pauses (syllables/second)
- `speech_rate_wo_pause`: Speech rate excluding pauses (syllables/second)
- `speaking_rate`: Number of words per minute
- `avg_pause_dur_per_syll`: Average pause duration per syllable
- `speaking_wpm`: Words per minute during speech segments
- `total_wpm`: Words per minute including pauses
- `articulation_rate`: Number of syllables per second during speech segments (sometimes different than speech_rate_w_pause, both kept for comparison)

### [prosody] Features
- `f0_mean`: Mean fundamental frequency (pitch)
- `f0_std`: Standard deviation of fundamental frequency
- `f0_median`: Median fundamental frequency
- `f0_min`: Minimum fundamental frequency
- `f0_max`: Maximum fundamental frequency
- `f0_q25`: 25th percentile of fundamental frequency
- `f0_q75`: 75th percentile of fundamental frequency
- `f0_index`: Composite index of pitch variation based on mean and quantile ratios
- `formants_index`: Composite index calculated from:
  - Vowel Space Area (VSA) using F1 and F2 measurements
  - F2/F1 ratios for vowel identification
  - Percentage of vowels within expected formant ranges
- `n_detected_vowel`: Number of detected vowels
- `pct_correct_vowel`: Percentage of correctly pronounced vowels within valid pitch range (ignore syllabic differences)
- `f2_f1_mean`: Mean ratio of second to first formant
- `f2_f1_std`: Standard deviation of formant ratio
- `intonation_index`: Calculated from:
  - Pitch variation (ins) score based on quartile ratios (q25, q75) and mean ratio (mr)
  - Balance between speaking rate and articulation rate
  - Score ranges from 4-10 based on pitch stability and variation patterns
- `n_syllable/n_pause`: Ratio of syllables to pauses
- `TOEFL_Score`: Estimated score (0-30) calculated from:
  - Weighted combination of rhythm (l), intonation (z), fluency (o), pronunciation (qr), articulation (w), and speech rate (r) scores
  - Formula: totalscore = (l*2 + z*4 + o*3 + qr*3 + w*4 + r*4)/20
  - Mapped to TOEFL scale: A1(<10), A2(10-16), B1(16-20), B2(20-25), C(>25)
- `Shannon_Score`: Information entropy score calculated from:
  - Normalized weighted sum of prosodic features
  - Uses natural logarithm ratios of component scores
  - Component weights:
    - Rhythm (l): ln(4)*1/4 weight
    - Articulation (w): ln(2)*1/2 + ln(3.25)*1/3.25 weights
    - Speech rate (inpro): ln(4)*1/4*inpro*4/125 weight
    - Pronunciation (r): ln(7/4)*4/7 weight
    - Fluency (qr): ln(7/2)*2/7 weight
    - Intonation (z): ln(7)*1/7 weight
    - Balance (o): ln(3.25/2)*2/3.25 weight

## Usage Example with Feature Access

```python
from myprosody import ProsodyAnalyzer

analyzer = ProsodyAnalyzer(debug=False)

result = analyzer.mysptotal("path/to/audio.wav")

if result:
    basic = result.get('basic', {})
    print(f"Speaking Duration: {basic.get('speaking_dur')} seconds")
    print(f"Speech Rate: {basic.get('speech_rate_wo_pause')} syllables/second")
    print(f"Pronunciation Score: {basic.get('pron_score')}/100")
    
    prosody = result.get('prosody', {})
    print(f"TOEFL Score Estimate: {prosody.get('TOEFL_Score')}")
    print(f"Average Pitch: {prosody.get('f0_mean')} Hz")
    print(f"Intonation Index: {prosody.get('intonation_index')}")
```

## Debug Mode

You can enable debug output to see detailed information about the analysis process:

```python
analyzer = ProsodyAnalyzer(debug=True)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your License Here]

## Authors

- Original Author: Shahab Sabahi
- Contributors: [List any contributors]

## Acknowledgments

- [Any acknowledgments or credits]

## NOTE:
    1- Both My-Voice-Analysis and Myprosody work on Python 3.7 
    2- If you install My-Voice-Analysis through PyPi, please use: 
          mysp=__import__("my-voice-analysis") instead of import myspsolution as mysp
    3- It it better to keep the folder names as single entities for instance "Name_Folder" or "NameFolder" without space in the dirctoy path

A Python library for measuring the acoustic features of speech (simultaneous speech, high entropy) compared to ones of native speech.

Prosody is the study of the tune and rhythm of speech and how these features contribute to meaning. Prosody is the study of those aspects of speech that typically apply to a level above that of the individual phoneme and very often to sequences of words (in prosodic phrases). Features above the level of the phoneme (or "segment") are referred to as suprasegmentals. 
A phonetic study of prosody is a study of the suprasegmental features of speech. At the phonetic level, prosody is characterised by: 

1.	vocal pitch (fundamental frequency)
2.	acoustic intensity
3.	rhythm (phoneme and syllable duration)

MyProsody is a Python library for measuring these acoustic features of speech (simultaneous speech, high entropy) compared to ones of native speech. The acoustic features of native speech patterns have been observed and established by employing Machine Learning algorithms. An acoustic model (algorithm) breaks recorded utterances (48 kHz & 32 bit sampling rate and bit depth respectively) and detects syllable boundaries, fundamental frequency contours, and formants. Its built-in functions recognize/measures:

                         o	Average_syll_pause_duration 
                         o	No._long_pause /o	Speaking-time 
                         o	No._of_words_in_minutes
                         o	Articulation_rate
                         o	No._words_in_minutes
                         o	formants_index
                         o	f0_index ((f0 is for fundamental frequency)
                         o	f0_quantile_25_index 
                         o	f0_quantile_50_index 
                         o	f0_quantile_75_index 
                         o	f0_std 
                         o	f0_max 
                         o	f0_min 
                         o	No._detected_vowel 
                         o	perc%._correct_vowel
                         o	(f2/f1)_mean (1st and 2nd formant frequencies)
                         o	(f2/f1)_std
                         o	no._of_words
                         o	no._of_pauses
                         o	intonation_index 
                         o	(voiced_syll_count)/(no_of_pause)
                         o	TOEFL_Scale_Score 
                         o	Score_Shannon_index
                         o	speaking_rate
                         o	gender recognition
                         o	speech mood (semantic analysis)
                         o	pronunciation posterior score
                         o	articulation-rate 
                         o	speech rate 
                         o	filler words
                         o	f0 statistics
                         -------------
                         NEW
                         --------------
                         o level (CEFR level)
                         o prosody-aspects (comparison, native level)

The library was developed based upon the idea introduced by Klaus Zechner et al "Automatic scoring of non-native spontaneous speech in tests of spoken English" Speech Communicaion vol 51-2009, Nivja DeJong and Ton Wempe [1], Paul Boersma and David Weenink [2], Carlo Gussenhoven [3], S.M Witt and S.J. Young [4] , and Yannick Jadoul [5].

Peaks in intensity (dB) that are preceded and followed by dips in intensity are considered as potential syllable cores. 
MyProsody is unique in its aim to provide a complete quantitative and analytical way to study acoustic features of a speech. Moreover, those features could be analysed further by employing Python's functionality to provide more fascinating insights into speech patterns. 

This library is for Linguists, scientists, developers, speech and language therapy clinics and researchers.  

Please note that MyProsody Analysis is currently in initial state though in active development. While the amount of functionality that is currently present is not huge, more will be added over the next few months.


## Installation

Myprosody can be installed like any other Python library, using (a recent version of) the Python package manager pip, on Linux, macOS, and Windows:

                                        pip install myprosody

or, to update your installed version to the latest release:

                                        pip install -u myprosody

you need also 

                                        import pickle
                                        
to run those functions of "Myprosody" which predict the spoken language proficiency level of your audio files. You need the pickle library to activate the trained acoustic and language models

## NOTE: 

After installing Myprosody, download the folder called:  

                                      myprosody

                                  
from

   https://github.com/Shahabks/myprosody

and save on your computer. The folder includes the audio files folder where you will save your audio files 
for analysis.

### Audio files must be in *.wav format, recorded at 48 kHz sample frame and 24-32 bits of resolution.

To check how the myprosody functions behave, please check 

                                    EXAMPLES.pdf
                                    testpro.py
                                    
on

  https://github.com/Shahabks/myprosody

## Development

Myprosody was developed by MYOLUTIONS Lab in Japan. It is part of New Generation of Voice Recognition and Acoustic & Language modelling Project in MYSOLUTIONS Lab. That is planned to enrich the functionality of Myprosody by adding more advanced functions. 

## Pronunciation
My-Voice-Analysis and MYprosody repos are two capsulated libraries from one of our main projects on speech scoring. The main project (its early version) employed ASR and used the Hidden Markov Model framework to train simple Gaussian acoustic models for each phoneme for each speaker in the given available audio datasets, then calculating all the symmetric K-L divergences for each pair of models for each speaker. What you see in these repos are just an approximate of those model without paying attention to level of accuracy of each phenome rather on fluency 
In the project's machine learning model we considered audio files of speakers who possessed an appropriate degree of pronunciation, either in general or for a specific utterance, word or phoneme, (in effect they had been rated with expert-human graders). Here below the figure illustrates some of the factors that the expert-human grader had considered in rating as an overall score

![image](https://user-images.githubusercontent.com/27753966/98312800-cf583a80-2015-11eb-9ecb-99658ecabdbb.png)

> [S. M. Witt, 2012 "Automatic error detection in pronunciation training: Where we are and where we need to go," ](https://www.researchgate.net/publication/250306074_Automatic_Error_Detection_in_Pronunciation_Training_Where_we_are_and_where_we_need_to_go)


## References and Acknowledgements

1.	DeJong N.H, and Ton Wempe [2009]; "Praat script to detect syllable nuclei and measure speech rate automatically"; Behavior Research Methods, 41(2).385-390.

2.	 Paul Boersma and David Weenink;  http://www.fon.hum.uva.nl/praat/

3.	Gussenhoven C. [2002]; " Intonation and Interpretation: Phonetics and Phonology"; Centre for Language Studies, Univerity of Nijmegen, The Netherlands.  

4.	Witt S.M and Young S.J [2000]; "Phone-level pronunciation scoring and assessment or interactive language learning"; Speech Communication, 30 (2000) 95-108.

5.	Jadoul, Y., Thompson, B., & de Boer, B. (2018). Introducing Parselmouth: A Python interface to Praat. Journal of Phonetics, 71, 1-15. https://doi.org/10.1016/j.wocn.2018.07.001 (https://parselmouth.readthedocs.io/en/latest/)

6. "Automatic scoring of non-native spontaneous speech in tests of spoken English", Speech Communication, Volume 51, Issue 10, October 2009, Pages 883-895

7. "A three-stage approach to the automated scoring of spontaneous spoken responses", Computer Speech & Language, Volume 25, Issue 2, April 2011, Pages 282-306

8. "Automated Scoring of Nonnative Speech Using the SpeechRaterSM v. 5.0 Engine", ETS research report, Volume 2018, Issue 1, December 2018, Pages: 1-28

