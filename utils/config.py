"""
Configuration management for the video generation pipeline.
Handles model paths, URLs, and device selection.
"""

import os
import torch

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
WAV2LIP_DIR = os.path.join(BASE_DIR, "Wav2Lip")

# Create directories if they don't exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Model URLs and paths
WAV2LIP_CHECKPOINT_URL = "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip_gan.pth"
WAV2LIP_CHECKPOINT_PATH = os.path.join(MODELS_DIR, "wav2lip_gan.pth")

# Stable Diffusion model
SD_MODEL_ID = "runwayml/stable-diffusion-v1-5"  # Can be changed to smaller models if needed
SD_MODEL_CACHE = os.path.join(MODELS_DIR, "stable_diffusion")

# Device configuration
def get_device():
    """Detect and return the best available device (CUDA, MPS, or CPU)."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

DEVICE = get_device()

# Video settings
DEFAULT_FPS = 25
DEFAULT_RESOLUTION = (720, 1280)  # height, width
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"

# TTS settings
TTS_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"  # Coqui TTS model
TTS_SAMPLE_RATE = 22050

# Animation settings
ANIMATION_DURATION = 0.5  # seconds per keyframe
TRANSITION_DURATION = 0.3  # seconds for transitions

# Cleanup settings
AUTO_CLEANUP = True  # Automatically delete temporary files

print(f"[CONFIG] Device selected: {DEVICE}")
print(f"[CONFIG] Models directory: {MODELS_DIR}")
print(f"[CONFIG] Temp directory: {TEMP_DIR}")
