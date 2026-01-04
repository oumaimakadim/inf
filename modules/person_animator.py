"""
Person animation module.
Adds simple movements and animations to person images.
"""

import os
import cv2
import numpy as np
from PIL import Image
from utils.config import TEMP_DIR, ANIMATION_DURATION, DEFAULT_FPS


class PersonAnimator:
    """Animate person images with simple movements."""
    
    def __init__(self):
        self.fps = DEFAULT_FPS
    
    def create_animated_clip(self, image_path, duration, output_path=None, 
                            animation_type="pan", **kwargs):
        """
        Create an animated video clip from a static image.
        
        Args:
            image_path (str): Path to input image
            duration (float): Duration in seconds
            output_path (str, optional): Output video path
            animation_type (str): Type of animation ('pan', 'zoom', 'static')
            **kwargs: Additional animation parameters
        
        Returns:
            str: Path to generated video clip
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"animated_{os.getpid()}.mp4")
        
        print(f"[ANIMATOR] Creating animated clip...")
        print(f"[ANIMATOR] Image: {image_path}")
        print(f"[ANIMATOR] Duration: {duration}s")
        print(f"[ANIMATOR] Animation: {animation_type}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        height, width = img.shape[:2]
        num_frames = int(duration * self.fps)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
        
        # Generate frames based on animation type
        if animation_type == "pan":
            frames = self._create_pan_animation(img, num_frames, **kwargs)
        elif animation_type == "zoom":
            frames = self._create_zoom_animation(img, num_frames, **kwargs)
        else:  # static
            frames = [img] * num_frames
        
        # Write frames
        for frame in frames:
            out.write(frame)
        
        out.release()
        
        file_size = os.path.getsize(output_path)
        print(f"[ANIMATOR] Animation created: {output_path} ({file_size} bytes)")
        
        return output_path
    
    def _create_pan_animation(self, img, num_frames, direction="left_to_right"):
        """Create panning animation."""
        height, width = img.shape[:2]
        frames = []
        
        # Create a slightly larger canvas for panning
        scale = 1.2
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        large_img = cv2.resize(img, (new_width, new_height))
        
        # Calculate pan range
        pan_range = new_width - width
        
        for i in range(num_frames):
            progress = i / max(num_frames - 1, 1)
            
            if direction == "left_to_right":
                x_offset = int(pan_range * progress)
            else:  # right_to_left
                x_offset = int(pan_range * (1 - progress))
            
            # Crop frame
            frame = large_img[0:height, x_offset:x_offset+width]
            frames.append(frame)
        
        return frames
    
    def _create_zoom_animation(self, img, num_frames, zoom_in=True):
        """Create zoom animation."""
        height, width = img.shape[:2]
        frames = []
        
        for i in range(num_frames):
            progress = i / max(num_frames - 1, 1)
            
            if zoom_in:
                scale = 1.0 + (0.2 * progress)  # Zoom from 1.0 to 1.2
            else:
                scale = 1.2 - (0.2 * progress)  # Zoom from 1.2 to 1.0
            
            # Calculate new dimensions
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize image
            resized = cv2.resize(img, (new_width, new_height))
            
            # Crop to original size (centered)
            x_offset = (new_width - width) // 2
            y_offset = (new_height - height) // 2
            
            if scale >= 1.0:
                frame = resized[y_offset:y_offset+height, x_offset:x_offset+width]
            else:
                # If zooming out beyond original, pad with black
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
            
            frames.append(frame)
        
        return frames
    
    def overlay_on_background(self, person_video_path, background_path, 
                             output_path=None, position="center"):
        """
        Overlay person video on a background image.
        
        Args:
            person_video_path (str): Path to person video
            background_path (str): Path to background image
            output_path (str, optional): Output video path
            position (str): Position of person ('center', 'left', 'right')
        
        Returns:
            str: Path to composited video
        """
        if output_path is None:
            output_path = os.path.join(TEMP_DIR, f"composited_{os.getpid()}.mp4")
        
        print(f"[ANIMATOR] Overlaying person on background...")
        
        # Load background
        bg = cv2.imread(background_path)
        if bg is None:
            raise ValueError(f"Failed to load background: {background_path}")
        
        bg_height, bg_width = bg.shape[:2]
        
        # Open person video
        cap = cv2.VideoCapture(person_video_path)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {person_video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Create output video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (bg_width, bg_height))
        
        while True:
            ret, person_frame = cap.read()
            if not ret:
                break
            
            # Resize person frame to fit background
            person_height, person_width = person_frame.shape[:2]
            scale = min(bg_height / person_height, bg_width / person_width) * 0.6
            
            new_person_width = int(person_width * scale)
            new_person_height = int(person_height * scale)
            
            person_resized = cv2.resize(person_frame, (new_person_width, new_person_height))
            
            # Calculate position
            if position == "center":
                x_offset = (bg_width - new_person_width) // 2
                y_offset = (bg_height - new_person_height) // 2
            elif position == "left":
                x_offset = bg_width // 4 - new_person_width // 2
                y_offset = (bg_height - new_person_height) // 2
            else:  # right
                x_offset = 3 * bg_width // 4 - new_person_width // 2
                y_offset = (bg_height - new_person_height) // 2
            
            # Create composite frame
            composite = bg.copy()
            composite[y_offset:y_offset+new_person_height, 
                     x_offset:x_offset+new_person_width] = person_resized
            
            out.write(composite)
        
        cap.release()
        out.release()
        
        print(f"[ANIMATOR] Composite video created: {output_path}")
        
        return output_path


def create_animated_person(image_path, duration, animation_type="pan", **kwargs):
    """
    Convenience function to create animated person clip.
    
    Args:
        image_path (str): Path to person image
        duration (float): Duration in seconds
        animation_type (str): Animation type
        **kwargs: Additional parameters
    
    Returns:
        str: Path to animated video
    """
    animator = PersonAnimator()
    return animator.create_animated_clip(image_path, duration, animation_type=animation_type, **kwargs)


if __name__ == "__main__":
    print("Person animator module loaded successfully")
