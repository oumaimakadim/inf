"""
Text-to-Speech generation module.
Uses Coqui TTS as primary engine with gTTS as fallback.
"""

import os
import tempfile
from pathlib import Path
import streamlit as st
from utils.config import TTS_MODEL, TTS_SAMPLE_RATE, TEMP_DIR


class TTSGenerator:
    """Text-to-Speech generator using Coqui TTS or gTTS."""
    
    def __init__(self):
        self.tts = None
        self.use_gtts = False
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialize TTS engine (Coqui TTS with gTTS fallback)."""
        try:
            from TTS.api import TTS
            print("[TTS] Initializing Coqui TTS...")
            self.tts = TTS(model_name=TTS_MODEL, progress_bar=False)
            print("[TTS] Coqui TTS initialized successfully")
        except Exception as e:
            print(f"[TTS] Coqui TTS initialization failed: {e}")
            print("[TTS] Falling back to gTTS")
            self.use_gtts = True
    
    def generate_speech(self, text, output_path=None):
        """
        Generate speech from text.
        
        Args:
            text (str): Input text to convert to speech
            output_path (str, optional): Path to save audio file. If None, creates temp file.
        
        Returns:
            str: Path to generated audio file
        """
        if not text or not text.strip():
            raise ValueError("Text input cannot be empty")
        
        # Create output path if not provided
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"tts_output_{os.getpid()}.wav")
        
        try:
            if self.use_gtts:
                return self._generate_with_gtts(text, output_path)
            else:
                return self._generate_with_coqui(text, output_path)
        except Exception as e:
            print(f"[TTS] Error generating speech: {e}")
            # Try fallback if primary method fails
            if not self.use_gtts:
                print("[TTS] Trying gTTS fallback...")
                return self._generate_with_gtts(text, output_path)
            raise
    
    def _generate_with_coqui(self, text, output_path):
        """Generate speech using Coqui TTS."""
        print(f"[TTS] Generating speech with Coqui TTS...")
        print(f"[TTS] Text length: {len(text)} characters")
        
        # Generate speech
        self.tts.tts_to_file(text=text, file_path=output_path)
        
        if not os.path.exists(output_path):
            raise RuntimeError("TTS generation failed - output file not created")
        
        file_size = os.path.getsize(output_path)
        print(f"[TTS] Speech generated successfully: {output_path} ({file_size} bytes)")
        
        return output_path
    
    def _generate_with_gtts(self, text, output_path):
        """Generate speech using gTTS (fallback)."""
        from gtts import gTTS
        import subprocess
        
        print(f"[TTS] Generating speech with gTTS...")
        print(f"[TTS] Text length: {len(text)} characters")
        
        # gTTS outputs MP3, so we need a temp file
        temp_mp3 = output_path.replace('.wav', '_temp.mp3')
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(temp_mp3)
        
        # Convert MP3 to WAV using ffmpeg
        try:
            subprocess.run(
                ['ffmpeg', '-i', temp_mp3, '-ar', str(TTS_SAMPLE_RATE), 
                 '-ac', '1', '-y', output_path],
                check=True,
                capture_output=True
            )
            
            # Clean up temp MP3
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            
            if not os.path.exists(output_path):
                raise RuntimeError("gTTS conversion failed - output file not created")
            
            file_size = os.path.getsize(output_path)
            print(f"[TTS] Speech generated successfully: {output_path} ({file_size} bytes)")
            
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"[TTS] FFmpeg conversion failed: {e.stderr}")
            # If conversion fails, return MP3 file
            if os.path.exists(temp_mp3):
                os.rename(temp_mp3, output_path.replace('.wav', '.mp3'))
                return output_path.replace('.wav', '.mp3')
            raise


def generate_tts(text, output_path=None):
    """
    Convenience function to generate TTS.
    
    Args:
        text (str): Text to convert to speech
        output_path (str, optional): Output file path
    
    Returns:
        str: Path to generated audio file
    """
    generator = TTSGenerator()
    return generator.generate_speech(text, output_path)


if __name__ == "__main__":
    # Test the TTS generator
    test_text = "Hello! This is a test of the text to speech system."
    output = generate_tts(test_text)
    print(f"Test audio generated: {output}")
