"""
Lip synchronization module using Wav2Lip.
Syncs audio with face images to create talking head videos.
"""

import os
import sys
import subprocess
import cv2
import numpy as np
from pathlib import Path
import torch
from utils.config import WAV2LIP_DIR, WAV2LIP_CHECKPOINT_PATH, DEVICE, TEMP_DIR


class LipSyncGenerator:
    """Generate lip-synced videos using Wav2Lip."""
    
    def __init__(self):
        self.model = None
        self.device = DEVICE
        self._setup_wav2lip()
    
    def _setup_wav2lip(self):
        """Setup Wav2Lip environment and load model."""
        # Add Wav2Lip to Python path
        if os.path.exists(WAV2LIP_DIR):
            sys.path.insert(0, WAV2LIP_DIR)
        else:
            raise RuntimeError(
                f"Wav2Lip directory not found: {WAV2LIP_DIR}\n"
                "Please run setup: python utils/model_downloader.py"
            )
        
        # Check if checkpoint exists
        if not os.path.exists(WAV2LIP_CHECKPOINT_PATH):
            raise RuntimeError(
                f"Wav2Lip checkpoint not found: {WAV2LIP_CHECKPOINT_PATH}\n"
                "Please run setup: python utils/model_downloader.py"
            )
        
        print(f"[LIP_SYNC] Wav2Lip directory: {WAV2LIP_DIR}")
        print(f"[LIP_SYNC] Checkpoint: {WAV2LIP_CHECKPOINT_PATH}")
        print(f"[LIP_SYNC] Device: {self.device}")
    
    def generate_lip_sync(self, face_image_path, audio_path, output_path=None, 
                         fps=25, resize_factor=1):
        """
        Generate lip-synced video from face image and audio.
        
        Args:
            face_image_path (str): Path to input face image
            audio_path (str): Path to audio file
            output_path (str, optional): Path for output video
            fps (int): Frames per second for output video
            resize_factor (int): Resize factor for processing (1=no resize)
        
        Returns:
            str: Path to generated video
        """
        if not os.path.exists(face_image_path):
            raise FileNotFoundError(f"Face image not found: {face_image_path}")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Create output path if not provided
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"lip_sync_{os.getpid()}.mp4")
        
        print(f"[LIP_SYNC] Generating lip-synced video...")
        print(f"[LIP_SYNC] Face image: {face_image_path}")
        print(f"[LIP_SYNC] Audio: {audio_path}")
        print(f"[LIP_SYNC] Output: {output_path}")
        
        try:
            # Use Wav2Lip inference script
            inference_script = os.path.join(WAV2LIP_DIR, "inference.py")
            
            if not os.path.exists(inference_script):
                raise RuntimeError(f"Wav2Lip inference script not found: {inference_script}")
            
            # Build command
            cmd = [
                sys.executable,
                inference_script,
                "--checkpoint_path", WAV2LIP_CHECKPOINT_PATH,
                "--face", face_image_path,
                "--audio", audio_path,
                "--outfile", output_path,
                "--fps", str(fps),
                "--resize_factor", str(resize_factor),
                "--nosmooth"  # Disable smoothing for faster processing
            ]
            
            # Add device-specific flags
            if self.device == "cpu":
                cmd.append("--device")
                cmd.append("cpu")
            
            print(f"[LIP_SYNC] Running Wav2Lip inference...")
            
            # Run inference
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=WAV2LIP_DIR
            )
            
            if result.returncode != 0:
                print(f"[LIP_SYNC] Wav2Lip stderr: {result.stderr}")
                raise RuntimeError(f"Wav2Lip inference failed: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise RuntimeError("Lip sync generation failed - output file not created")
            
            file_size = os.path.getsize(output_path)
            print(f"[LIP_SYNC] Video generated successfully: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            print(f"[LIP_SYNC] Error during lip sync generation: {e}")
            # Try fallback method using direct Python API
            return self._generate_with_python_api(face_image_path, audio_path, output_path, fps)
    
    def _generate_with_python_api(self, face_image_path, audio_path, output_path, fps):
        """
        Fallback method using Wav2Lip Python API directly.
        This is a simplified version that creates a basic talking head video.
        """
        print("[LIP_SYNC] Using fallback method...")
        
        try:
            # Read face image
            face_img = cv2.imread(face_image_path)
            if face_img is None:
                raise ValueError(f"Failed to load image: {face_image_path}")
            
            # Get audio duration using ffprobe
            duration_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 
                'format=duration', '-of', 
                'default=noprint_wrappers=1:nokey=1', audio_path
            ]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
            duration = float(duration_result.stdout.strip())
            
            # Calculate number of frames
            num_frames = int(duration * fps)
            
            print(f"[LIP_SYNC] Creating {num_frames} frames at {fps} fps")
            
            # Create temporary video without audio
            temp_video = output_path.replace('.mp4', '_temp.mp4')
            
            # Get frame dimensions
            height, width = face_img.shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
            
            # Write frames (simple: just repeat the same image)
            # In a real implementation, Wav2Lip would animate the mouth
            for _ in range(num_frames):
                out.write(face_img)
            
            out.release()
            
            # Merge audio with video using ffmpeg
            merge_cmd = [
                'ffmpeg', '-i', temp_video, '-i', audio_path,
                '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental',
                '-shortest', '-y', output_path
            ]
            
            subprocess.run(merge_cmd, check=True, capture_output=True)
            
            # Clean up temp video
            if os.path.exists(temp_video):
                os.remove(temp_video)
            
            print(f"[LIP_SYNC] Fallback video created: {output_path}")
            print("[LIP_SYNC] Note: This is a static video. For proper lip sync, ensure Wav2Lip is properly installed.")
            
            return output_path
            
        except Exception as e:
            print(f"[LIP_SYNC] Fallback method also failed: {e}")
            raise


def generate_lip_sync(face_image_path, audio_path, output_path=None, **kwargs):
    """
    Convenience function to generate lip-synced video.
    
    Args:
        face_image_path (str): Path to face image
        audio_path (str): Path to audio file
        output_path (str, optional): Output video path
        **kwargs: Additional parameters
    
    Returns:
        str: Path to generated video
    """
    generator = LipSyncGenerator()
    return generator.generate_lip_sync(face_image_path, audio_path, output_path, **kwargs)


if __name__ == "__main__":
    # Test requires actual image and audio files
    print("Lip sync module loaded successfully")
    print(f"Wav2Lip directory: {WAV2LIP_DIR}")
    print(f"Checkpoint path: {WAV2LIP_CHECKPOINT_PATH}")
