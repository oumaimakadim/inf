"""
Automated model downloading and verification.
Handles downloading of Wav2Lip checkpoints and Stable Diffusion models.
"""

import os
import requests
import subprocess
from pathlib import Path
import streamlit as st
from utils.config import (
    WAV2LIP_CHECKPOINT_URL,
    WAV2LIP_CHECKPOINT_PATH,
    WAV2LIP_DIR,
    MODELS_DIR,
    SD_MODEL_CACHE,
    SD_MODEL_ID
)


def download_file(url, destination, description="File"):
    """Download a file with progress tracking."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        
        with open(destination, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"[DOWNLOAD] {description}: {progress:.1f}%")
        
        print(f"[DOWNLOAD] {description} completed: {destination}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download {description}: {e}")
        return False


def clone_wav2lip():
    """Clone Wav2Lip repository if not present."""
    if os.path.exists(WAV2LIP_DIR):
        print("[SETUP] Wav2Lip repository already exists")
        return True
    
    try:
        print("[SETUP] Cloning Wav2Lip repository...")
        result = subprocess.run(
            ["git", "clone", "https://github.com/Rudrabha/Wav2Lip.git", WAV2LIP_DIR],
            capture_output=True,
            text=True,
            check=True
        )
        print("[SETUP] Wav2Lip repository cloned successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to clone Wav2Lip: {e.stderr}")
        return False
    except FileNotFoundError:
        print("[ERROR] Git not found. Please install git.")
        return False


def download_wav2lip_checkpoint():
    """Download Wav2Lip pre-trained model checkpoint."""
    if os.path.exists(WAV2LIP_CHECKPOINT_PATH):
        print("[SETUP] Wav2Lip checkpoint already exists")
        return True
    
    print("[SETUP] Downloading Wav2Lip checkpoint (this may take a few minutes)...")
    return download_file(
        WAV2LIP_CHECKPOINT_URL,
        WAV2LIP_CHECKPOINT_PATH,
        "Wav2Lip checkpoint"
    )


def setup_stable_diffusion():
    """Verify Stable Diffusion model availability."""
    try:
        from diffusers import StableDiffusionPipeline
        
        # Check if model is already cached
        if os.path.exists(SD_MODEL_CACHE):
            print("[SETUP] Stable Diffusion model already cached")
            return True
        
        print("[SETUP] Stable Diffusion model will be downloaded on first use")
        print(f"[SETUP] Model: {SD_MODEL_ID}")
        return True
    except ImportError:
        print("[ERROR] diffusers library not installed")
        return False


def verify_ffmpeg():
    """Verify FFmpeg is installed."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("[SETUP] FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] FFmpeg not found. Please install FFmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False


def setup_all():
    """Run all setup tasks."""
    print("\n" + "="*60)
    print("SETTING UP VIDEO GENERATION PIPELINE")
    print("="*60 + "\n")
    
    tasks = [
        ("Verifying FFmpeg", verify_ffmpeg),
        ("Cloning Wav2Lip repository", clone_wav2lip),
        ("Downloading Wav2Lip checkpoint", download_wav2lip_checkpoint),
        ("Setting up Stable Diffusion", setup_stable_diffusion),
    ]
    
    results = []
    for task_name, task_func in tasks:
        print(f"\n[TASK] {task_name}...")
        success = task_func()
        results.append((task_name, success))
        
        if not success:
            print(f"[WARNING] {task_name} failed")
    
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    all_success = True
    for task_name, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {task_name}")
        if not success:
            all_success = False
    
    print("="*60 + "\n")
    
    return all_success


if __name__ == "__main__":
    setup_all()
